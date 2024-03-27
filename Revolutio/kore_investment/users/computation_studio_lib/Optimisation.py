from ast import literal_eval
import base64
import copy
from datetime import datetime
from io import BytesIO
import itertools
import json
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pypfopt import (
    BlackLittermanModel,
    EfficientFrontier,
    expected_returns,
    objective_functions,
    plotting,
    risk_models,
)

from config.settings.base import redis_instance
from kore_investment.users.computations.db_centralised_function import read_data_func


class Optimiser:
    def plot_eff_frontier(self, efff_for_eff_curve, ef, riskfreerate):
        fig, ax = plt.subplots()
        plotting.plot_efficient_frontier(efff_for_eff_curve, ax=ax, color="black", show_assets=False)
        ret_tangent, std_tangent, _ = ef.portfolio_performance(risk_free_rate=riskfreerate)
        ax.scatter(std_tangent, ret_tangent, s=80, c="var(--primary-color)", label="Max Sharpe")
        ax.set_facecolor("white")
        plt.title(f"Efficient frontier curve", size=20)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.15)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        return resultplot

    def mean_variance(self, prices, market_benchmarks, common_constraints, config_dict):
        output = {}
        prices = prices.reset_index().pivot(index="extract_date", columns="security_identifier")[
            "quoted_price"
        ]
        if "pool_id" in market_benchmarks.columns.tolist():
            pool_name = market_benchmarks.loc[:, "pool_id"]
        else:
            pool_name = "Pool_id"
        if config_dict["inputs"].get("optimizerOutput"):
            optimizer_output = config_dict["inputs"]["optimizerOutput"]
        else:
            optimizer_output = ["model_portfolio_allocation"]

        constraint_dict = config_dict["inputs"]["constraint_dict"]
        scenario_name = config_dict["inputs"]["scenario_name"]["scenarioName"]
        valuation_date = config_dict["inputs"]["valuation_date"]["valuation_date"]
        optimiser = config_dict["inputs"]["optimiser"]
        views_dict = config_dict["inputs"]["views_dict"]
        riskfreerate = float(config_dict["inputs"]["risk_free_rate"]["riskFreeRate"])
        targetVolatility = config_dict["inputs"]["target_volatility"]["targetVolatility"]
        targetReturn = config_dict["inputs"]["target_return"]["targetRreturn"]
        mu = expected_returns.mean_historical_return(prices, compounding=True, frequency=252)
        S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
        if optimiser == "black_litterman":
            ret_bl, S_bl = black_litterman(prices, views_dict, risk_free_rate=riskfreerate)
            ef = EfficientFrontier(ret_bl, S_bl)
        else:
            ef = EfficientFrontier(mu, S)
        if optimiser == "black_litterman":
            ef.add_objective(objective_functions.L2_reg)
        constraints_already_handled = []
        market_benchmarks.replace(" ", "_")
        if len(constraint_dict.keys()) >= 1:
            for key, value in constraint_dict.items():
                if key not in constraints_already_handled:
                    unique_id = constraint_dict[key]["unique_id"]
                    connected_constraints = common_constraints[unique_id]
                    related_constraint_ids = []
                    constraint_type = value["constraint_type"]
                    for i in connected_constraints:
                        if i != key:
                            related_constraint_ids.append(i)
                    if constraint_type == "matrix":
                        mapper = constraint_dict[key]["mapping_column"]
                        constraint_list = value["constraint_list"]
                        for inputs in constraint_list:
                            column_name = constraint_dict[key]["column_name"]
                            input_value = inputs["input_value"]
                            condition1 = inputs["condition"]
                            condition = condition1.lower()
                            condition = condition.replace(" ", "_")
                            inputs["condition"] = condition
                            duration_list = market_benchmarks.loc[:, column_name].to_list()
                            duration_array = np.array(duration_list)
                            duration_array.shape = (len(duration_list), 1)
                            if "equal_to" in condition:
                                ef.add_constraint(lambda w: w @ duration_array == input_value)
                            if "greater_than" in condition:
                                ef.add_constraint(lambda w: w @ duration_array >= input_value)
                            if "smaller_than" in condition:
                                ef.add_constraint(lambda w: w @ duration_array <= input_value)
                    else:
                        mapper = constraint_dict[key]["mapping_column"]
                        market_benchmarks_copy = market_benchmarks
                        column_name = constraint_dict[key]["column_name"]
                        constraint_list = value["constraint_list"][0]
                        constraint_parameter_value = value["constraint_list"][0]["column_value"]
                        condition1 = value["constraint_list"][0]["condition"].lower()
                        condition = condition1.replace(" ", "_")
                        constraint_list["condition"] = condition
                        if len(related_constraint_ids) > 0:
                            if type(constraint_parameter_value) == list:
                                market_benchmarks_copy = market_benchmarks_copy.loc[
                                    market_benchmarks_copy[column_name].isin(constraint_parameter_value)
                                ]
                            else:
                                market_benchmarks_copy = market_benchmarks_copy.loc[
                                    market_benchmarks_copy[column_name] == constraint_parameter_value
                                ]
                            for j in range(0, len(related_constraint_ids)):
                                constraints_already_handled.append(related_constraint_ids[j])
                                if (
                                    related_constraint_ids[j]
                                    == related_constraint_ids[len(related_constraint_ids) - 1]
                                ):
                                    mapper = constraint_dict[related_constraint_ids[j]]["mapping_column"]
                                    constraint_mapper = pd.Series(
                                        market_benchmarks.loc[
                                            :, constraint_dict[related_constraint_ids[j]]["column_name"]
                                        ].values,
                                        index=market_benchmarks.loc[:, mapper],
                                    ).to_dict()
                                    constraint_mapper_filtered = pd.Series(
                                        market_benchmarks_copy.loc[
                                            :, constraint_dict[related_constraint_ids[j]]["column_name"]
                                        ].values,
                                        index=market_benchmarks_copy.loc[:, mapper],
                                    ).to_dict()
                                    constraint_list = constraint_dict[related_constraint_ids[j]][
                                        "constraint_list"
                                    ][0]
                                    constraint_type = constraint_dict[related_constraint_ids[j]][
                                        "constraint_type"
                                    ]
                                    constraint_lower = {}
                                    constraint_upper = {}
                                    condition1 = constraint_list["condition"].lower()
                                    condition1 = condition1.replace(" ", "_")
                                    constraint_list["condition"] = condition1
                                    if type(constraint_list["column_value"]) == list:
                                        for l, m in constraint_mapper_filtered.items():
                                            if m in constraint_list["column_value"]:
                                                constraint_mapper[l] = "pseudo_mapper"
                                        if "smaller_than" in constraint_list["condition"]:
                                            constraint_upper["pseudo_mapper"] = constraint_list["input_value"]
                                            constraint_lower["pseudo_mapper"] = 0

                                        if "greater_than" in constraint_list["condition"]:
                                            constraint_lower["pseudo_mapper"] = constraint_list["input_value"]
                                            constraint_upper["pseudo_mapper"] = 1

                                        if "equal_to" in constraint_list["condition"]:
                                            constraint_lower["pseudo_mapper"] = constraint_list["input_value"]
                                            constraint_upper["pseudo_mapper"] = constraint_list["input_value"]
                                    else:
                                        if "smaller_than" in constraint_list["condition"]:
                                            constraint_upper[constraint_list["column_value"]] = (
                                                constraint_list["input_value"]
                                            )
                                            constraint_lower[constraint_list["column_value"]] = 0

                                        if "greater_than" in constraint_list["condition"]:
                                            constraint_lower[constraint_list["column_value"]] = (
                                                constraint_list["input_value"]
                                            )
                                            constraint_upper[constraint_list["column_value"]] = 1

                                        if "equal_to" in constraint_list["condition"]:
                                            constraint_lower[constraint_list["column_value"]] = (
                                                constraint_list["input_value"]
                                            )
                                            constraint_upper[constraint_list["column_value"]] = (
                                                constraint_list["input_value"]
                                            )
                                    ef.add_sector_constraints(
                                        constraint_mapper, constraint_lower, constraint_upper
                                    )
                                else:
                                    mapper = constraint_dict[related_constraint_ids[j]]["mapping_column"]
                                    column_name = constraint_dict[related_constraint_ids[j]]["column_name"]
                                    constraint_parameter_value = constraint_dict[related_constraint_ids[j]][
                                        "constraint_list"
                                    ][0]["column_value"]
                                    condition1 = constraint_dict[related_constraint_ids[j]][
                                        "constraint_list"
                                    ][0]["condition"].lower()
                                    condition = condition1.replace(" ", "_")
                                    if type(constraint_parameter_value) == list:
                                        market_benchmarks_copy = market_benchmarks_copy.loc[
                                            market_benchmarks_copy[column_name].isin(
                                                constraint_parameter_value
                                            )
                                        ]
                                    else:
                                        market_benchmarks_copy = market_benchmarks_copy.loc[
                                            market_benchmarks_copy[column_name] == constraint_parameter_value
                                        ]
                        else:
                            constraint_mapper = pd.Series(
                                market_benchmarks_copy.loc[:, column_name].values,
                                index=market_benchmarks_copy.loc[:, mapper],
                            ).to_dict()
                            constraint_list = value["constraint_list"][0]
                            constraint_type = value["constraint_type"]
                            constraint_lower = {}
                            constraint_upper = {}
                            condition1 = constraint_list["condition"].lower()
                            condition1 = condition1.replace(" ", "_")
                            constraint_list["condition"] = condition1
                            if type(constraint_list["column_value"]) == list:
                                for l, m in constraint_mapper.items():
                                    if m in constraint_list["column_value"]:
                                        constraint_mapper[l] = "pseudo_mapper"
                                if "smaller_than" in constraint_list["condition"]:
                                    constraint_upper["pseudo_mapper"] = constraint_list["input_value"]
                                    constraint_lower["pseudo_mapper"] = 0

                                if "greater_than" in constraint_list["condition"]:
                                    constraint_lower["pseudo_mapper"] = constraint_list["input_value"]
                                    constraint_upper["pseudo_mapper"] = 1

                                if "equal_to" in constraint_list["condition"]:
                                    constraint_lower["pseudo_mapper"] = constraint_list["input_value"]
                                    constraint_upper["pseudo_mapper"] = constraint_list["input_value"]
                            else:
                                if "smaller_than" in constraint_list["condition"]:
                                    constraint_upper[constraint_list["column_value"]] = constraint_list[
                                        "input_value"
                                    ]
                                    constraint_lower[constraint_list["column_value"]] = 0

                                if "greater_than" in constraint_list["condition"]:
                                    constraint_lower[constraint_list["column_value"]] = constraint_list[
                                        "input_value"
                                    ]
                                    constraint_upper[constraint_list["column_value"]] = 1

                                if "equal_to" in constraint_list["condition"]:
                                    constraint_lower[constraint_list["column_value"]] = constraint_list[
                                        "input_value"
                                    ]
                                    constraint_upper[constraint_list["column_value"]] = constraint_list[
                                        "input_value"
                                    ]
                            ef.add_sector_constraints(constraint_mapper, constraint_lower, constraint_upper)

        efff_for_eff_curve = copy.deepcopy(ef)
        if config_dict["inputs"]["method"] == "max_sharpe":
            ef.max_sharpe(risk_free_rate=riskfreerate)
        elif config_dict["inputs"]["method"] == "min_volatility":
            ef.min_volatility()
        elif config_dict["inputs"]["method"] == "efficient_risk":
            targetVolatility = float(targetVolatility)
            ef.efficient_risk(target_volatility=targetVolatility)
        elif config_dict["inputs"]["method"] == "efficient_return":
            targetReturn = float(targetReturn)
            ef.efficient_return(target_return=targetReturn)
        else:
            return "No Method Selected"

        weights = ef.clean_weights()
        ret_tangent, std_tangent, _ = ef.portfolio_performance(risk_free_rate=riskfreerate)
        sharpe_ratio_output = (ret_tangent - riskfreerate) / std_tangent
        Final = pd.DataFrame.from_dict(weights, orient="index")
        Final = Final.rename(columns={Final.columns[0]: "Allocation"})
        Final.reset_index(inplace=True)
        Final = Final.rename(columns={Final.columns[0]: "Security_identifier"})

        Final["Valuation_date"] = valuation_date
        Final["Scenario"] = scenario_name
        Final["Pool_id"] = pool_name
        Final["Run_date"] = datetime.now()
        Final_data = pd.merge(
            left=Final.copy(),
            right=market_benchmarks[
                [
                    "benchmark_variant",
                    "tenor",
                    "tenor_unit",
                    "asset_class",
                    "tenor_with_unit",
                    "sector",
                    "rating",
                ]
            ]
            .copy()
            .rename(columns={"benchmark_variant": "Security_identifier", "tenor_with_unit": "tenor_name"}),
            how="left",
            left_on="Security_identifier",
            right_on="Security_identifier",
        )
        Final_data = Final_data.reindex(
            columns=[
                "Security_identifier",
                "tenor",
                "tenor_unit",
                "sector",
                "rating",
                "asset_class",
                "tenor_name",
                "Allocation",
                "Valuation_date",
                "Scenario",
                "Pool_id",
                "Run_date",
            ]
        )
        Final_data["expected_return"] = ret_tangent
        Final_data["standard_deviation"] = std_tangent
        Final_data["sharpe_ratio"] = sharpe_ratio_output
        Final_data.sort_values(by=["Allocation"], ascending=False, inplace=True)
        output["portfolio_allocation"] = Final_data.to_dict("records")
        if "constraint_report" in optimizer_output:
            master_data_for_constraint_report = pd.merge(
                left=Final.copy().drop(columns=["Valuation_date", "Scenario", "Pool_id", "Run_date"]),
                right=market_benchmarks.copy(),
                how="left",
                left_on="Security_identifier",
                right_on="benchmark_variant",
            )
            constraint_data = pd.DataFrame(list(constraint_dict.values()))
            constraint_data.drop(columns=["mapping_column"], inplace=True)
            constraint_dataframe_list = list(
                itertools.chain.from_iterable(constraint_data.constraint_list.tolist())
            )
            constraint_dataframe = pd.DataFrame(constraint_dataframe_list)
            constraint_dataframe_raw = pd.concat(
                [
                    constraint_data[["constraint_name", "column_name", "constraint_type", "unique_id"]],
                    constraint_dataframe,
                ],
                axis=1,
            )
            constraint_dataframe_raw["allocation"] = "None"
            constraint_dataframe_raw["result"] = "None"
            constraint_report_already_handled = []

            for con_row in range(len(constraint_dataframe_raw)):
                if (
                    str(con_row + 1) not in constraint_report_already_handled
                    or constraint_dataframe_raw.iloc[con_row]["constraint_type"] == "matrix"
                ):
                    trow = constraint_dataframe_raw.iloc[con_row]
                    t_constraint_type = trow["constraint_type"]
                    t_column = trow["column_name"]
                    t_column_value = trow["column_value"]
                    t_condition = trow["condition"]
                    t_input_value = trow["input_value"]
                    unique_id = trow["unique_id"]
                    connected_constraints = common_constraints[unique_id]
                    related_constraint_ids = []
                    constraint_type = trow["constraint_type"]
                    constraint_description = ""
                    for i in connected_constraints:
                        if int(i) != con_row + 1:
                            related_constraint_ids.append(i)
                    master_data_for_constraint_report_copy = master_data_for_constraint_report
                    if len(related_constraint_ids) > 0:
                        if t_constraint_type in ["grouped", "individual"]:
                            if isinstance(t_column_value, list):
                                master_data_for_constraint_report_copy = (
                                    master_data_for_constraint_report_copy.loc[
                                        master_data_for_constraint_report_copy[t_column].isin(t_column_value)
                                    ]
                                )
                                constraint_description += t_column + " in " + str(t_column_value) + " and "
                            else:
                                master_data_for_constraint_report_copy = (
                                    master_data_for_constraint_report_copy.loc[
                                        master_data_for_constraint_report_copy[t_column] == t_column_value
                                    ]
                                )
                                constraint_description += (
                                    t_column + " equal to " + str(t_column_value) + " and "
                                )
                        for j in range(0, len(related_constraint_ids)):
                            constraint_report_already_handled.append(related_constraint_ids[j])
                            trow = constraint_dataframe_raw.iloc[int(related_constraint_ids[j]) - 1]
                            if (
                                related_constraint_ids[j]
                                == related_constraint_ids[len(related_constraint_ids) - 1]
                            ):
                                t_constraint_type = trow["constraint_type"]
                                t_column = trow["column_name"]
                                t_column_value = trow["column_value"]
                                t_condition = trow["condition"]
                                t_input_value = trow["input_value"]
                                if t_constraint_type in ["grouped", "individual"]:
                                    if isinstance(t_column_value, list):
                                        cumm_allocation = master_data_for_constraint_report_copy[
                                            master_data_for_constraint_report_copy[t_column].isin(
                                                t_column_value
                                            )
                                        ]["Allocation"].sum()
                                        constraint_description += t_column + " in " + str(t_column_value)
                                    else:
                                        cumm_allocation = master_data_for_constraint_report_copy[
                                            master_data_for_constraint_report_copy[t_column] == t_column_value
                                        ]["Allocation"].sum()
                                        constraint_description += (
                                            t_column + " equal to " + str(t_column_value)
                                        )
                                elif t_constraint_type == "matrix":
                                    cumm_allocation = (
                                        master_data_for_constraint_report_copy["Allocation"]
                                        @ master_data_for_constraint_report_copy[t_column]
                                    )
                                    constraint_description = t_column + " - " + "entire portfolio"

                                constraint_dataframe_raw["allocation"].iloc[con_row] = cumm_allocation
                                if isinstance(t_input_value, (str)):
                                    t_input_value = float(t_input_value)
                                if t_condition == "greater_than":
                                    if cumm_allocation > (t_input_value - 0.01):
                                        constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                                    else:
                                        constraint_dataframe_raw["result"].iloc[con_row] = "Breach"
                                if t_condition == "smaller_than":
                                    if cumm_allocation < (t_input_value + 0.01):
                                        constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                                    else:
                                        constraint_dataframe_raw["result"].iloc[con_row] = "Breach"
                                if t_condition == "equal_to":
                                    if (t_input_value + 0.01) > cumm_allocation > (t_input_value - 0.01):
                                        constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                                    else:
                                        constraint_dataframe_raw["result"].iloc[con_row] = "Breach"

                            else:
                                t_constraint_type = trow["constraint_type"]
                                t_column = trow["column_name"]
                                t_column_value = trow["column_value"]
                                t_condition = trow["condition"]
                                t_input_value = trow["input_value"]
                                if t_constraint_type in ["grouped", "individual"]:
                                    if isinstance(t_column_value, list):
                                        master_data_for_constraint_report_copy = (
                                            master_data_for_constraint_report_copy.loc[
                                                master_data_for_constraint_report_copy[t_column].isin(
                                                    t_column_value
                                                )
                                            ]
                                        )
                                    else:
                                        master_data_for_constraint_report_copy = (
                                            master_data_for_constraint_report_copy.loc[
                                                master_data_for_constraint_report_copy[t_column]
                                                == t_column_value
                                            ]
                                        )
                    else:
                        if t_constraint_type in ["grouped", "individual"]:
                            if isinstance(t_column_value, list):
                                cumm_allocation = master_data_for_constraint_report_copy[
                                    master_data_for_constraint_report_copy[t_column].isin(t_column_value)
                                ]["Allocation"].sum()
                                constraint_description += t_column + " in " + str(t_column_value)
                            else:
                                cumm_allocation = master_data_for_constraint_report_copy[
                                    master_data_for_constraint_report_copy[t_column] == t_column_value
                                ]["Allocation"].sum()
                                constraint_description += t_column + " equal to " + str(t_column_value)
                        elif t_constraint_type == "matrix":
                            cumm_allocation = (
                                master_data_for_constraint_report_copy["Allocation"].to_numpy()
                                @ master_data_for_constraint_report_copy[t_column].to_numpy()
                            )
                            constraint_description = t_column + " - " + "entire portfolio"
                        constraint_dataframe_raw["allocation"].iloc[con_row] = cumm_allocation
                        if isinstance(t_input_value, (str)):
                            t_input_value = float(t_input_value)
                        if t_condition == "greater_than":
                            if cumm_allocation > (t_input_value - 0.01):
                                constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                            else:
                                constraint_dataframe_raw["result"].iloc[con_row] = "Breach"
                        if t_condition == "smaller_than":
                            if cumm_allocation < (t_input_value + 0.01):
                                constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                            else:
                                constraint_dataframe_raw["result"].iloc[con_row] = "Breach"
                        if t_condition == "equal_to":
                            if (t_input_value + 0.01) > cumm_allocation > (t_input_value - 0.01):
                                constraint_dataframe_raw["result"].iloc[con_row] = "No breach"
                            else:
                                constraint_dataframe_raw["result"].iloc[con_row] = "Breach"
                    if constraint_description != "":
                        constraint_dataframe_raw["column_value"].iloc[con_row] = constraint_description
            constraint_dataframe_raw.drop(
                columns=["column_name", "constraint_type", "unique_id"], inplace=True
            )
            #     if constraint_report_already_handled.iloc[i]
            constraint_dataframe_raw = constraint_dataframe_raw.loc[
                (constraint_dataframe_raw["result"] != "None")
            ]
            constraint_dataframe_raw["allocation"] = (
                constraint_dataframe_raw["allocation"].astype("float").round(decimals=4)
            )
            constraint_dataframe_raw["input_value"] = (
                constraint_dataframe_raw["input_value"].astype("float").round(decimals=5)
            )
            constraint_dataframe_raw = constraint_dataframe_raw.rename(
                columns={
                    "constraint_name": "constraint_parameter",
                    "column_value": "constraint_parameter_value",
                    "input_value": "threshold",
                }
            )

            def list_to_json(x):
                if isinstance(x, list):
                    return json.dumps(x)
                else:
                    return x

            constraint_dataframe_raw["constraint_parameter_value"] = constraint_dataframe_raw[
                "constraint_parameter_value"
            ].apply(list_to_json)
            output["constraint_report"] = constraint_dataframe_raw.to_dict("records")
        # Efficient frontier curve
        if "efficient_frontier" in optimizer_output:
            output["efficient_frontier"] = self.plot_eff_frontier(efff_for_eff_curve, ef, riskfreerate)
        return output

    def security_allocation(
        self,
        uploaded_constraints_security_allocation,
        security_data,
        position_data,
        security_liquidity_data,
        benchmark_allocation_data,
        investment,
        pool_id,
    ):
        security_data["issuer_group"] = security_data["issuer_group"].str.strip()
        position_data = position_data.loc[position_data["Pool_id"] == pool_id]
        position_data = pd.merge(
            position_data,
            security_data[["unique_reference_id", "issuer_group"]],
            left_on="unique_reference_id",
            right_on="unique_reference_id",
            how="left",
        )
        security_data = security_data.loc[security_data["proxy_benchmark"] != ""]
        security_benchmarks = (
            security_data[["proxy_benchmark", "unique_reference_id"]]
            .groupby(["proxy_benchmark"])
            .agg({"unique_reference_id": "count"})
            .reset_index()
        )
        benchmark_allocation_data = pd.DataFrame(benchmark_allocation_data)
        security_benchmarks = pd.merge(
            security_benchmarks,
            benchmark_allocation_data[["Security_identifier", "Allocation"]],
            left_on="proxy_benchmark",
            right_on="Security_identifier",
            how="left",
        ).rename(columns={"proxy_benchmark": "benchmark", "unique_reference_id": "count_of_securities"})
        security_benchmarks["investment"] = investment
        security_benchmarks["initial_allocation_total"] = (
            security_benchmarks["Allocation"] * security_benchmarks["investment"]
        )
        security_benchmarks["initial_allocation_proportionate"] = (
            security_benchmarks["initial_allocation_total"] / security_benchmarks["count_of_securities"]
        )
        security_data = pd.merge(
            security_data,
            security_benchmarks[["benchmark", "initial_allocation_proportionate"]],
            left_on="proxy_benchmark",
            right_on="benchmark",
            how="left",
        ).drop(columns=["benchmark"])
        security_data["liquidity_limit"] = None
        if "Liquidity limit" in uploaded_constraints_security_allocation["constraint_name"].tolist():
            liquidity_limit = float(
                uploaded_constraints_security_allocation.loc[
                    uploaded_constraints_security_allocation["constraint_name"] == "Liquidity limit",
                    "threshold",
                ].iloc[0]
            )
            liquidity_limit_category = uploaded_constraints_security_allocation.loc[
                uploaded_constraints_security_allocation["constraint_name"] == "Liquidity limit",
                "constraint_category",
            ].iloc[0]
            security_data = pd.merge(
                security_data,
                security_liquidity_data,
                left_on="unique_reference_id",
                right_on="security_identifier",
                how="left",
            ).drop(columns=["security_identifier"])
            if liquidity_limit_category == "Relative":
                security_data["liquidity_limit"] = security_data["volume_traded"] * liquidity_limit
            else:
                security_data["liquidity_limit"] = liquidity_limit

        equity_limit_available = None
        pool_position_size = position_data["ammortised_bookvalue"].sum()
        if "Asset class limit" in uploaded_constraints_security_allocation["constraint_name"].tolist():
            equity_asset_class_limit = float(
                uploaded_constraints_security_allocation.loc[
                    (uploaded_constraints_security_allocation["constraint_name"] == "Asset class limit")
                    & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["EQ"]'),
                    "threshold",
                ].iloc[0]
            )
            equity_asset_class_limit_category = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Asset class limit")
                & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["EQ"]'),
                "constraint_category",
            ].iloc[0]
            if equity_asset_class_limit_category == "Relative":
                equity_asset_class_limit = equity_asset_class_limit * pool_position_size
            else:
                equity_asset_class_limit = equity_asset_class_limit
            equity_limit_utilised = position_data.loc[
                position_data["asset_class"] == "EQ", "ammortised_bookvalue"
            ].sum()
            equity_limit_available = equity_asset_class_limit - equity_limit_utilised
        market_lot_limit = None
        if "Market lot limit" in uploaded_constraints_security_allocation["constraint_name"].tolist():
            market_lot_limit = float(
                uploaded_constraints_security_allocation.loc[
                    (uploaded_constraints_security_allocation["constraint_name"] == "Market lot limit")
                    & (
                        uploaded_constraints_security_allocation["constraint_parameter_value"]
                        == '["CG","SG"]'
                    ),
                    "threshold",
                ].iloc[0]
            )
            market_lot_limit_category = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Market lot limit")
                & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["CG","SG"]'),
                "constraint_category",
            ].iloc[0]
            if market_lot_limit_category == "Relative":
                market_lot_limit = market_lot_limit * pool_position_size
            else:
                market_lot_limit = market_lot_limit
        equity_issuer_limit_dict = {}
        equity_issuer_group_limit_dict = {}
        mf_issuer_limit_dict = {}
        mf_issuer_group_limit_dict = {}
        bond_issuer_limit_dict = {}
        bond_issuer_group_limit_dict = {}
        if "Equity issuer limit" in uploaded_constraints_security_allocation["constraint_name"].tolist():
            equity_issuer_limit = float(
                uploaded_constraints_security_allocation.loc[
                    (uploaded_constraints_security_allocation["constraint_name"] == "Equity issuer limit")
                    & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                    & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer"),
                    "threshold",
                ].iloc[0]
            )
            equity_issuer_limit_category = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Equity issuer limit")
                & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer"),
                "constraint_category",
            ].iloc[0]
            if equity_issuer_limit_category == "Relative":
                equity_issuer_limit = equity_issuer_limit * pool_position_size
            else:
                equity_issuer_limit = equity_issuer_limit
            equity_issuer_list = security_data.loc[security_data["asset_class"] == "EQ"][
                "issuer"
            ].reset_index()
            equity_issuer_list["issuer_limit"] = equity_issuer_limit
            equity_issuer_limit_utilised = (
                position_data.loc[position_data["asset_class"] == "EQ"]
                .groupby("issuer")["ammortised_bookvalue"]
                .sum()
                .reset_index()
                .rename(columns={"issuer": "issuer_name"})
            )
            if len(equity_issuer_limit_utilised) > 0:
                equity_issuer_list = (
                    equity_issuer_list.merge(
                        equity_issuer_limit_utilised, left_on="issuer", right_on="issuer_name", how="left"
                    )
                    .drop(columns=["issuer_name"])
                    .rename(columns={"ammortised_bookvalue": "issuer_limit_utilised"})
                )
            else:
                equity_issuer_list["issuer_limit_utilised"] = 0
            equity_issuer_list["issuer_available_limit"] = (
                equity_issuer_list["issuer_limit"] - equity_issuer_list["issuer_limit_utilised"]
            )
            equity_issuer_limit_dict = dict(
                zip(equity_issuer_list["issuer"], equity_issuer_list["issuer_available_limit"])
            )
            equity_issuer_group_limit = float(
                uploaded_constraints_security_allocation.loc[
                    (uploaded_constraints_security_allocation["constraint_name"] == "Equity issuer limit")
                    & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                    & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer_group"),
                    "threshold",
                ].iloc[0]
            )
            equity_issuer_group_limit_category = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Equity issuer limit")
                & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer_group"),
                "constraint_category",
            ].iloc[0]
            if equity_issuer_group_limit_category == "Relative":
                equity_issuer_group_limit = equity_issuer_group_limit * pool_position_size
            else:
                equity_issuer_group_limit = equity_issuer_group_limit
            equity_issuer_group_list = security_data.loc[security_data["asset_class"] == "EQ"][
                "issuer_group"
            ].reset_index()
            equity_issuer_group_list["issuer_group_limit"] = equity_issuer_group_limit
            equity_issuer_group_limit_utilised = (
                position_data.loc[position_data["asset_class"] == "EQ"]
                .groupby("issuer_group")["ammortised_bookvalue"]
                .sum()
                .reset_index()
                .rename(columns={"issuer_group": "issuer_group_name"})
            )
            if len(equity_issuer_group_limit_utilised) > 0:
                equity_issuer_group_list = (
                    equity_issuer_group_list.merge(
                        equity_issuer_group_limit_utilised,
                        left_on="issuer_group",
                        right_on="issuer_group_name",
                        how="left",
                    )
                    .drop(columns=["issuer_group_name"])
                    .rename(columns={"ammortised_bookvalue": "issuer_group_limit_utilised"})
                )
            else:
                equity_issuer_group_list["issuer_group_limit_utilised"] = 0
            equity_issuer_group_list["issuer_group_available_limit"] = (
                equity_issuer_group_list["issuer_group_limit"]
                - equity_issuer_group_list["issuer_group_limit_utilised"]
            )
            equity_issuer_group_limit_dict = dict(
                zip(
                    equity_issuer_group_list["issuer_group"],
                    equity_issuer_group_list["issuer_group_available_limit"],
                )
            )
        if "MF issuer limit" in uploaded_constraints_security_allocation["constraint_name"].tolist():
            mf_issuer_limit = float(
                uploaded_constraints_security_allocation.loc[
                    (uploaded_constraints_security_allocation["constraint_name"] == "MF issuer limit")
                    & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                    & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer"),
                    "threshold",
                ].iloc[0]
            )
            mf_issuer_limit_category = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "MF issuer limit")
                & (uploaded_constraints_security_allocation["constraint_parameter_value"] == '["All"]')
                & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer"),
                "constraint_category",
            ].iloc[0]
            if mf_issuer_limit_category == "Relative":
                mf_issuer_limit = mf_issuer_limit * pool_position_size
            else:
                mf_issuer_limit = mf_issuer_limit
            mf_issuer_list = security_data.loc[security_data["asset_class"] == "MF"]["issuer"].reset_index()
            mf_issuer_list["issuer_limit"] = mf_issuer_limit
            mf_issuer_limit_utilised = (
                position_data.loc[position_data["asset_class"] == "MF"]
                .groupby("issuer")["ammortised_bookvalue"]
                .sum()
                .reset_index()
                .rename(columns={"issuer": "issuer_name"})
            )
            if len(mf_issuer_limit_utilised) > 0:
                mf_issuer_list = (
                    mf_issuer_list.merge(
                        mf_issuer_limit_utilised, left_on="issuer", right_on="issuer_name", how="left"
                    )
                    .drop(columns=["issuer_name"])
                    .rename(columns={"ammortised_bookvalue": "issuer_limit_utilised"})
                )
            else:
                mf_issuer_list["issuer_limit_utilised"] = 0
            mf_issuer_list["issuer_available_limit"] = (
                mf_issuer_list["issuer_limit"] - mf_issuer_list["issuer_limit_utilised"]
            )
            mf_issuer_limit_dict = dict(
                zip(mf_issuer_list["issuer"], mf_issuer_list["issuer_available_limit"])
            )
        if (
            "Corporate bond issuer limit"
            in uploaded_constraints_security_allocation["constraint_name"].tolist()
        ):
            bond_issuer_limit = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Corporate bond issuer limit")
                & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer"),
                ["constraint_category", "constraint_parameter_value", "threshold"],
            ]

            def clean_alt_list(list_):
                return literal_eval(list_)[0]

            bond_issuer_limit["constraint_parameter_value"] = bond_issuer_limit[
                "constraint_parameter_value"
            ].apply(clean_alt_list)
            bond_issuer_limit["issuer_limit"] = np.where(
                bond_issuer_limit["constraint_category"] == "Relative",
                bond_issuer_limit["threshold"] * pool_position_size,
                bond_issuer_limit["threshold"],
            )
            bond_issuer_limit_utilised = (
                position_data.loc[position_data["asset_class"].isin(["NCD", "CP"])]
                .groupby("issuer")["ammortised_bookvalue"]
                .sum()
                .reset_index()
                .rename(columns={"issuer": "issuer_name"})
            )
            if len(bond_issuer_limit_utilised) > 0:
                bond_issuer_limit = (
                    bond_issuer_limit.merge(
                        bond_issuer_limit_utilised,
                        left_on="constraint_parameter_value",
                        right_on="issuer_name",
                        how="left",
                    )
                    .drop(columns=["issuer_name"])
                    .rename(
                        columns={
                            "ammortised_bookvalue": "issuer_limit_utilised",
                            "constraint_parameter_value": "issuer",
                        }
                    )
                )
            else:
                bond_issuer_limit["issuer_limit_utilised"] = 0
            bond_issuer_limit["issuer_limit_utilised"].fillna(0, inplace=True)
            bond_issuer_limit["issuer_available_limit"] = (
                bond_issuer_limit["issuer_limit"] - bond_issuer_limit["issuer_limit_utilised"]
            )
            bond_issuer_limit["issuer_available_limit"] = np.where(
                bond_issuer_limit["issuer_available_limit"] < 0,
                0,
                bond_issuer_limit["issuer_available_limit"],
            )
            bond_issuer_limit_dict = dict(
                zip(bond_issuer_limit["issuer"], bond_issuer_limit["issuer_available_limit"])
            )
            bond_issuer_group_limit = uploaded_constraints_security_allocation.loc[
                (uploaded_constraints_security_allocation["constraint_name"] == "Corporate bond issuer limit")
                & (uploaded_constraints_security_allocation["constraint_parameter"] == "issuer_group"),
                ["constraint_category", "constraint_parameter_value", "threshold"],
            ]
            bond_issuer_group_limit["constraint_parameter_value"] = bond_issuer_group_limit[
                "constraint_parameter_value"
            ].apply(clean_alt_list)
            bond_issuer_group_limit["issuer_group_limit"] = np.where(
                bond_issuer_group_limit["constraint_category"] == "Relative",
                bond_issuer_group_limit["threshold"] * pool_position_size,
                bond_issuer_group_limit["threshold"],
            )
            bond_issuer_group_limit_utilised = (
                position_data.loc[position_data["asset_class"].isin(["NCD", "CP"])]
                .groupby("issuer_group")["ammortised_bookvalue"]
                .sum()
                .reset_index()
                .rename(columns={"issuer_group": "issuer_group_name"})
            )
            if len(bond_issuer_group_limit_utilised) > 0:
                bond_issuer_group_limit = (
                    bond_issuer_group_limit.merge(
                        bond_issuer_group_limit_utilised,
                        left_on="constraint_parameter_value",
                        right_on="issuer_group_name",
                        how="left",
                    )
                    .drop(columns=["issuer_group_name"])
                    .rename(
                        columns={
                            "ammortised_bookvalue": "issuer_group_limit_utilised",
                            "constraint_parameter_value": "issuer_group",
                        }
                    )
                )
            else:
                bond_issuer_group_limit["issuer_group_limit_utilised"] = 0
            bond_issuer_group_limit["issuer_group_limit_utilised"].fillna(0, inplace=True)
            bond_issuer_group_limit["issuer_group_available_limit"] = (
                bond_issuer_group_limit["issuer_group_limit"]
                - bond_issuer_group_limit["issuer_group_limit_utilised"]
            )
            bond_issuer_group_limit["issuer_group_available_limit"] = np.where(
                bond_issuer_group_limit["issuer_group_available_limit"] < 0,
                0,
                bond_issuer_group_limit["issuer_group_available_limit"],
            )
            bond_issuer_group_limit_dict = dict(
                zip(
                    bond_issuer_group_limit["issuer_group"],
                    bond_issuer_group_limit["issuer_group_available_limit"],
                )
            )
        security_data = security_data.loc[security_data["initial_allocation_proportionate"] != 0]
        investment_original = investment
        rounding_view = 4
        final_securities_data = security_data[
            [
                "unique_reference_id",
                "proxy_benchmark",
                "asset_class",
                "initial_allocation_proportionate",
                "liquidity_limit",
                "issuer",
                "issuer_group",
            ]
        ].to_dict("records")
        portfolio_allocation = []
        for i in final_securities_data:
            if investment <= 0:
                break
            else:
                initial_allocation = i["initial_allocation_proportionate"]
                # Liquidity limit for Bonds,T-Bills,NCDs,CDs and CPs
                if i["asset_class"] in ["CG", "SG", "CD", "NCD", "CP"] and i["liquidity_limit"] != np.nan:
                    liquidity_limit_cap = i["liquidity_limit"]
                else:
                    liquidity_limit_cap = investment
                # Issuer limit
                issuer = i["issuer"]
                if i["asset_class"] == "EQ":
                    if issuer in equity_issuer_limit_dict.keys():
                        issuer_limit_cap = equity_issuer_limit_dict[issuer]
                    else:
                        issuer_limit_cap = investment
                elif i["asset_class"] == "MF":
                    if issuer in mf_issuer_limit_dict.keys():
                        issuer_limit_cap = mf_issuer_limit_dict[issuer]
                    else:
                        issuer_limit_cap = investment
                elif i["asset_class"] in ["NCD", "CP"]:
                    if issuer in bond_issuer_limit_dict.keys():
                        issuer_limit_cap = bond_issuer_limit_dict[issuer]
                    else:
                        issuer_limit_cap = investment
                else:
                    issuer_limit_cap = investment
                # Issuer Group limit
                issuer_group = i["issuer_group"]
                if i["asset_class"] == "EQ":
                    if issuer_group in equity_issuer_group_limit_dict.keys():
                        issuer_group_limit_cap = equity_issuer_group_limit_dict[issuer_group]
                    else:
                        issuer_group_limit_cap = investment
                elif i["asset_class"] == "MF":
                    if issuer_group in mf_issuer_group_limit_dict.keys():
                        issuer_group_limit_cap = mf_issuer_group_limit_dict[issuer_group]
                    else:
                        issuer_group_limit_cap = investment
                elif i["asset_class"] in ["NCD", "CP"]:
                    if issuer_group in bond_issuer_group_limit_dict.keys():
                        issuer_group_limit_cap = bond_issuer_group_limit_dict[issuer_group]
                    else:
                        issuer_group_limit_cap = investment
                else:
                    issuer_group_limit_cap = investment
                # Equity asset class limit
                equity_limit_cap = equity_limit_available
                # Market Lot limit for CG and SG securities
                if i["asset_class"] == "EQ":
                    allocated_amount = min(
                        initial_allocation,
                        liquidity_limit_cap,
                        issuer_limit_cap,
                        issuer_group_limit_cap,
                        equity_limit_cap,
                    )
                else:
                    allocated_amount = min(
                        initial_allocation, liquidity_limit_cap, issuer_limit_cap, issuer_group_limit_cap
                    )
                if allocated_amount > investment:
                    allocated_amount = investment
                else:
                    pass
                i["allocated_amount"] = round(allocated_amount, rounding_view)
                i["allocated_amount_percentage"] = allocated_amount / investment_original
                i["percentage_allocated"] = (
                    str(round(allocated_amount / investment_original * 100, rounding_view)) + "%"
                )
                investment = investment - allocated_amount
                if i["asset_class"] == "EQ":
                    if issuer in equity_issuer_limit_dict.keys():
                        equity_issuer_limit_dict[issuer] = equity_issuer_limit_dict[issuer] - allocated_amount
                    if issuer_group in equity_issuer_group_limit_dict.keys():
                        equity_issuer_group_limit_dict[issuer_group] = (
                            equity_issuer_group_limit_dict[issuer_group] - allocated_amount
                        )
                    equity_limit_available = equity_limit_available - allocated_amount
                elif i["asset_class"] == "MF":
                    if issuer in mf_issuer_limit_dict.keys():
                        mf_issuer_limit_dict[issuer] = mf_issuer_limit_dict[issuer] - allocated_amount
                    if issuer_group in mf_issuer_group_limit_dict.keys():
                        mf_issuer_group_limit_dict[issuer_group] = (
                            mf_issuer_group_limit_dict[issuer_group] - allocated_amount
                        )
                elif i["asset_class"] in ["NCD", "CP"]:
                    if issuer in bond_issuer_limit_dict.keys():
                        bond_issuer_limit_dict[issuer] = bond_issuer_limit_dict[issuer] - allocated_amount
                    if issuer_group in bond_issuer_group_limit_dict.keys():
                        bond_issuer_group_limit_dict[issuer_group] = (
                            bond_issuer_group_limit_dict[issuer_group] - allocated_amount
                        )
                if allocated_amount != 0:
                    portfolio_allocation.append(i)
        portfolio_allocation_df = pd.DataFrame(portfolio_allocation)
        portfolio_allocation_df = (
            portfolio_allocation_df[
                [
                    "unique_reference_id",
                    "proxy_benchmark",
                    "asset_class",
                    "allocated_amount",
                    "percentage_allocated",
                    "allocated_amount_percentage",
                    "issuer",
                    "issuer_group",
                ]
            ]
            .rename(
                columns={
                    "allocated_amount_percentage": "percentage_allocated_decimals",
                }
            )
            .sort_values("allocated_amount", ascending=False)
        )
        return portfolio_allocation_df, investment


def data_cleaning(
    uploaded_constraints,
    market_benchmarks,
    position_data,
    cashflow_data,
    security_data,
    measure_data,
    benchmark_cashflow_data,
    config_dict,
    request,
):
    constraint_dict = config_dict["inputs"]["constraint_dict"]
    constraint_hierarchy = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Hierarchy_table",
                "Columns": [
                    "Hierarchy_name",
                    "Hierarchy_parent_name",
                    "Hierarchy_level",
                    "Hierarchy_level_name",
                    "Hierarchy_type",
                    "Hierarchy_group",
                ],
            },
            "condition": [
                {
                    "column_name": "Hierarchy_type",
                    "condition": "Equal to",
                    "input_value": "Liability Hierarchy",
                    "and_or": "and",
                },
                {
                    "column_name": "Hierarchy_group",
                    "condition": "Equal to",
                    "input_value": "Liability Pooling",
                    "and_or": "",
                },
            ],
        },
    )
    constraint_hierarchy_levels = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Hierarchy_levels",
                "Columns": ["Hierarchy_level_name", "Hierarchy_level", "Hierarchy_type", "Hierarchy_group"],
            },
            "condition": [
                {
                    "column_name": "Hierarchy_type",
                    "condition": "Equal to",
                    "input_value": "Liability Hierarchy",
                    "and_or": "and",
                },
                {
                    "column_name": "Hierarchy_group",
                    "condition": "Equal to",
                    "input_value": "Liability Pooling",
                    "and_or": "",
                },
            ],
        },
    )
    uploaded_constraints = (
        pd.merge(
            uploaded_constraints,
            constraint_hierarchy_levels,
            left_on="liability_hierarchy_level",
            right_on="Hierarchy_level_name",
            how="left",
        )
        .drop(columns=["Hierarchy_level_name", "Hierarchy_type", "Hierarchy_group"])
        .rename(columns={"Hierarchy_level": "hierarchy_level"})
    )
    uploaded_constraints["unique_constraint_identifier"] = (
        uploaded_constraints["use_case"]
        + "_"
        + uploaded_constraints["constraint_name"]
        + "_"
        + uploaded_constraints["rule_set"]
    )
    uploaded_constraints["unique_constraint_identifier_hierarchy"] = (
        uploaded_constraints["use_case"]
        + "_"
        + uploaded_constraints["constraint_name"]
        + "_"
        + uploaded_constraints["rule_set"]
        + "_"
        + uploaded_constraints["liability_hierarchy_level"]
    )
    uploaded_constraints_duplicate = uploaded_constraints[
        uploaded_constraints.duplicated("unique_constraint_identifier")
    ]

    def is_unique(s):
        a = s.to_numpy()
        return (a[0] == a).all()

    duplicate_constraint_list = []
    for i in uploaded_constraints_duplicate["unique_constraint_identifier"].unique():
        duplicate_rulesets = uploaded_constraints[uploaded_constraints["unique_constraint_identifier"] == i]
        same_hierarchy_group_check = is_unique(duplicate_rulesets["unique_constraint_identifier_hierarchy"])
        if not same_hierarchy_group_check:
            duplicate_rulesets_final = (
                duplicate_rulesets[
                    duplicate_rulesets["hierarchy_level"] != duplicate_rulesets["hierarchy_level"].max()
                ]["unique_constraint_identifier_hierarchy"]
                .unique()
                .tolist()
            )
            duplicate_constraint_list += duplicate_rulesets_final

    uploaded_constraints = uploaded_constraints.loc[
        ~uploaded_constraints["unique_constraint_identifier_hierarchy"].isin(duplicate_constraint_list)
    ]
    constraints_data = uploaded_constraints.to_dict("records")
    hierarchy_level_dict = dict(
        zip(
            constraint_hierarchy_levels["Hierarchy_level_name"],
            constraint_hierarchy_levels["Hierarchy_level"],
        )
    )
    optimisation_hierarchy_level_name = "Portfolio"
    optimisation_hierarchy_level = hierarchy_level_dict[optimisation_hierarchy_level_name]
    new_investment = float(config_dict["inputs"]["investment_amount"]["investment_amount_allocation"])
    if "pool_id" in market_benchmarks.columns.tolist():
        optimisation_hierarchy_name = market_benchmarks.loc[:, "pool_id"].iloc[0]
    else:
        optimisation_hierarchy_name = "Pool_id"
    current_hierarchy_parent_levels = get_hierarchy_parents(
        optimisation_hierarchy_name, optimisation_hierarchy_level, constraint_hierarchy
    )
    hierarchy_level_name_position_data_mapper = {
        "Entity": "entity",
        "Business": "business",
        "Portfolio": "Pool_id",
        "Fund": "fund_code",
    }
    hierarchy_level_name_cashflow_data_mapper = {
        "Entity": {"column_name": "entity", "value": ["PNB MetLife India Insurance Ltd"]},
        "Portfolio": {"column_name": "portfolio", "value": [optimisation_hierarchy_name]},
        "Fund": {"column_name": "fund", "value": []},
    }
    cashflow_data = cashflow_data.loc[(cashflow_data["alm_bucket"] != "")]
    position_quantity = position_data.loc[:, ["position_id", "quantity"]]
    cashflow_data = pd.merge(
        cashflow_data, position_quantity, left_on="unique_reference_id", right_on="position_id", how="left"
    )
    asset_cashflows = cashflow_data.loc[
        (cashflow_data["asset_liability_type"] == "Asset") & (cashflow_data["quantity"].notnull())
    ]
    asset_cashflows["cashflow"] = asset_cashflows["cashflow"] * asset_cashflows["quantity"]
    liability_cashflows = cashflow_data.loc[cashflow_data["asset_liability_type"] == "Liability"]
    alm_constraints_list_criteria_not_met = []
    for i in constraints_data:
        if i["cascade_logic"] == "Proportionate allocation":
            liability_hierarchy_level_name = i["liability_hierarchy_level"]
            liability_hierarchy_level_current = hierarchy_level_dict[liability_hierarchy_level_name]
            liability_hierarchy_level_base = hierarchy_level_dict[liability_hierarchy_level_name]
            hierarchy_computation_output_dict = {
                "hierarchy_level_name": i["liability_hierarchy_level"],
                "constraint_category": i["constraint_category"],
            }
            original_threshold = float(i["threshold"])
            while liability_hierarchy_level_current <= optimisation_hierarchy_level:
                if (int(liability_hierarchy_level_current)) in hierarchy_level_dict.values():
                    current_hierarchy_level = int(liability_hierarchy_level_current)
                    current_hierarchy_level_name = list(hierarchy_level_dict.keys())[
                        list(hierarchy_level_dict.values()).index(int(liability_hierarchy_level_current))
                    ]
                else:
                    current_hierarchy_level_name = ""
                if current_hierarchy_level_name != "":
                    hierarchy = constraint_hierarchy.loc[
                        constraint_hierarchy["Hierarchy_level_name"] == current_hierarchy_level_name
                    ]
                    if liability_hierarchy_level_current == liability_hierarchy_level_base:
                        original_book_value = position_data.loc[
                            position_data[
                                hierarchy_level_name_position_data_mapper[current_hierarchy_level_name]
                            ]
                            == current_hierarchy_parent_levels[current_hierarchy_level],
                            "ammortised_bookvalue",
                        ].sum()
                    if optimisation_hierarchy_name in hierarchy["Hierarchy_name"].tolist():
                        position_size = position_data.loc[
                            position_data[
                                hierarchy_level_name_position_data_mapper[current_hierarchy_level_name]
                            ]
                            == optimisation_hierarchy_name,
                            "ammortised_bookvalue",
                        ].sum()
                        position_size_proportion_of_portfolio = (position_size + new_investment) / (
                            original_book_value + new_investment
                        )
                        new_threshold = position_size_proportion_of_portfolio * original_threshold
                        hierarchy_computation_output_dict["hierarchy_name"] = optimisation_hierarchy_name
                        hierarchy_computation_output_dict["hierarchy_level_name"] = (
                            current_hierarchy_level_name
                        )
                        hierarchy_computation_output_dict["threshold"] = new_threshold
                    else:
                        hierarchy_computation_output_dict["hierarchy_name"] = optimisation_hierarchy_name
                    liability_hierarchy_level_current += 1
            i["liability_hierarchy_level"] = hierarchy_computation_output_dict["hierarchy_level_name"]
            i["threshold"] = hierarchy_computation_output_dict["threshold"]
        elif i["constraint_category"] == "Dynamic":
            if i["constraint_name"] == "ALM mismatch limit":
                asset_cashflow = asset_cashflows.loc[
                    (
                        asset_cashflows[
                            hierarchy_level_name_cashflow_data_mapper[i["liability_hierarchy_level"]][
                                "column_name"
                            ]
                        ].isin(
                            hierarchy_level_name_cashflow_data_mapper[i["liability_hierarchy_level"]]["value"]
                        )
                    )
                    & (asset_cashflows["alm_bucket"] == i["constraint_parameter_value"]),
                    "cashflow",
                ].sum()
                liability_cashflow = liability_cashflows.loc[
                    (
                        liability_cashflows[
                            hierarchy_level_name_cashflow_data_mapper[i["liability_hierarchy_level"]][
                                "column_name"
                            ]
                        ].isin(
                            hierarchy_level_name_cashflow_data_mapper[i["liability_hierarchy_level"]]["value"]
                        )
                    )
                    & (liability_cashflows["alm_bucket"] == i["constraint_parameter_value"]),
                    "cashflow",
                ].sum()
                mismatch_ratio = asset_cashflow / liability_cashflow
                if mismatch_ratio >= 0.8:
                    i["threshold"] = 0
                    i["condition"] = "Greater than"
                    i["constraint_parameter"] = "alm_bucket"

                else:
                    alm_constraints_list_criteria_not_met.append(
                        {
                            "constraint_parameter_value": i["constraint_parameter_value"],
                            "asset_cashflow": asset_cashflow,
                            "liability_cashflow": liability_cashflow,
                            "mismatch_ratio": mismatch_ratio,
                            "unique_id": i["unique_constraint_identifier_hierarchy"],
                        }
                    )

    alm_constraints_list_criteria_not_met_df = pd.DataFrame(alm_constraints_list_criteria_not_met)
    uploaded_constraints = pd.DataFrame(constraints_data)
    uploaded_constraints_security_allocation = uploaded_constraints.loc[
        uploaded_constraints["table_name"] == "Position_Master"
    ]
    uploaded_constraints = uploaded_constraints.loc[uploaded_constraints["table_name"] != "Position_Master"]
    if len(alm_constraints_list_criteria_not_met_df) > 0:
        alm_constraints_preprocessing_results = alm_constraints_generator(
            alm_constraints_list_criteria_not_met_df, new_investment
        )
        uploaded_constraints = (
            pd.merge(
                uploaded_constraints,
                alm_constraints_preprocessing_results,
                left_on="unique_constraint_identifier_hierarchy",
                right_on="unique_id",
                how="outer",
            )
            .drop(
                columns=[
                    "constraint_parameter_value_y",
                    "asset_cashflow",
                    "liability_cashflow",
                    "mismatch_ratio",
                    "new_investment",
                    "unique_id",
                    "mismatch_breach",
                ]
            )
            .rename(columns={"constraint_parameter_value_x": "constraint_parameter_value"})
        )
        uploaded_constraints["threshold"] = np.where(
            uploaded_constraints["threshold_y"].isnull(),
            uploaded_constraints["threshold_x"],
            uploaded_constraints["threshold_y"],
        )
        uploaded_constraints["condition"] = np.where(
            uploaded_constraints["condition_y"].isnull(),
            uploaded_constraints["condition_x"],
            uploaded_constraints["condition_y"],
        )
        uploaded_constraints.drop(
            columns=["threshold_x", "condition_x", "threshold_y", "condition_y"], inplace=True
        )
    market_benchmarks = (
        pd.merge(
            market_benchmarks,
            measure_data,
            left_on="benchmark_variant",
            right_on="unique_reference_id",
            how="left",
        )
        .drop(
            columns=[
                "measure_run_date",
                "valuation_date",
                "unique_reference_id",
                "reference_dimension",
                "measure_type",
            ]
        )
        .rename(columns={"measure_value": "duration"})
    )
    market_benchmarks["duration"].fillna(0, inplace=True)
    market_benchmarks = pd.merge(
        market_benchmarks,
        benchmark_cashflow_data.loc[:, ["unique_reference_id", "alm_bucket"]],
        left_on="benchmark_variant",
        right_on="unique_reference_id",
        how="left",
    ).drop(columns=["unique_reference_id"])
    market_benchmarks.replace("", "No value", inplace=True)
    constraint_name_list = uploaded_constraints.loc[:, "constraint_name"].to_list()
    constraint_type_list = uploaded_constraints.loc[:, "constraint_type"].to_list()
    constraint_mapper_list = uploaded_constraints.loc[:, "unique_constraint_column"].to_list()
    constraint_column_list = uploaded_constraints.loc[:, "constraint_parameter"].to_list()
    constraint_column_value_list = uploaded_constraints.loc[:, "constraint_parameter_value"].to_list()
    constraint_condition_list = uploaded_constraints.loc[:, "condition"].to_list()
    constraint_input_value_list = uploaded_constraints.loc[:, "threshold"].to_list()
    constraint_rule_set_list = uploaded_constraints.loc[:, "rule_set"].to_list()
    constraint_unique_id_list = uploaded_constraints.loc[
        :, "unique_constraint_identifier_hierarchy"
    ].to_list()
    constraint_dict1 = {}
    constraint_list1 = []
    constraint_list3 = []
    for column_value, condition, input_value in zip(
        constraint_column_value_list, constraint_condition_list, constraint_input_value_list
    ):
        if len(column_value) > 0 and column_value.startswith("["):
            column_value = json.loads(column_value)
        constraint_dict3 = {"column_value": column_value, "condition": condition, "input_value": input_value}
        constraint_list2 = [constraint_dict3]
        constraint_list3.append(constraint_list2)

    for name, constraint_type, mapper, column, constraint_list, rule_set, unique_id in zip(
        constraint_name_list,
        constraint_type_list,
        constraint_mapper_list,
        constraint_column_list,
        constraint_list3,
        constraint_rule_set_list,
        constraint_unique_id_list,
    ):
        constraint_dict1 = {
            "mapping_column": mapper,
            "constraint_name": name,
            "column_name": column,
            "constraint_type": constraint_type,
            "constraint_list": constraint_list,
            "constraint_ruleset": rule_set,
            "unique_id": unique_id,
        }
        constraint_list1.append(constraint_dict1)
    common_constraints = {}
    for ind, dictionary in enumerate(constraint_list1):
        number = ind + 1
        number = str(number)
        if dictionary["unique_id"] in common_constraints.keys():
            related_ids = common_constraints[dictionary["unique_id"]]
            related_ids.append(number)
            common_constraints[dictionary["unique_id"]] = related_ids
        else:
            common_constraints[dictionary["unique_id"]] = [number]
        constraint_dict[number] = dictionary
    return config_dict, market_benchmarks, common_constraints, uploaded_constraints_security_allocation


def black_litterman(prices, views_dict, risk_free_rate):
    prior = expected_returns.mean_historical_return(prices, compounding=True, frequency=252)
    views_source = views_dict["source"]
    if views_source == "upload_data_views":
        views1 = {}
        uploaded_views = pickle.loads(redis_instance.get(views_dict["uploaded_views"]))
        column_names_list = uploaded_views.loc[:, "benchmark_variant"].to_list()
        views_values_list = uploaded_views.loc[:, "yield"].to_list()
        confidences_list = uploaded_views.loc[:, "confidence"].to_list()
        for a, b in zip(column_names_list, views_values_list):
            views1[a] = float(b)
        views_dict["views"] = views1
        views_dict["confidences"] = confidences_list
    S = risk_models.CovarianceShrinkage(prices).ledoit_wolf()
    views = views_dict["views"]
    for key, value in views.items():
        views[key] = float(value)
    confidences = views_dict["confidences"]
    confidences = list(map(float, confidences))
    for i in prior.index:
        if views.get(i):
            prior[i] = views.get(i)
    bl = BlackLittermanModel(S, pi=prior, absolute_views=views, view_confidences=confidences)
    ret_bl = bl.bl_returns()
    S_bl = bl.bl_cov()
    return ret_bl, S_bl


def alm_constraints_generator(alm_constraints_list_criteria_not_met_df, new_investment):
    new_investment = 20
    alm_constraints_list_criteria_not_met_df["new_investment"] = new_investment
    alm_constraints_list_criteria_not_met_df["mismatch_breach"] = (
        0.8 * alm_constraints_list_criteria_not_met_df["liability_cashflow"]
        - alm_constraints_list_criteria_not_met_df["asset_cashflow"]
    )
    if len(alm_constraints_list_criteria_not_met_df) == 1:
        alm_constraints_list_criteria_not_met_df["threshold"] = np.where(
            alm_constraints_list_criteria_not_met_df["new_investment"]
            >= alm_constraints_list_criteria_not_met_df["mismatch_breach"],
            alm_constraints_list_criteria_not_met_df["mismatch_breach"]
            / alm_constraints_list_criteria_not_met_df["new_investment"],
            1,
        )
        alm_constraints_list_criteria_not_met_df["condition"] = np.where(
            alm_constraints_list_criteria_not_met_df["new_investment"]
            >= alm_constraints_list_criteria_not_met_df["mismatch_breach"],
            "Greater than",
            "Equal to",
        )
    else:
        alm_constraints_list_criteria_not_met_df["threshold"] = (
            alm_constraints_list_criteria_not_met_df["mismatch_breach"]
            / alm_constraints_list_criteria_not_met_df["mismatch_breach"].sum()
        )
        alm_constraints_list_criteria_not_met_df["condition"] = "Greater than"
    return alm_constraints_list_criteria_not_met_df


def get_hierarchy_parents(hierarchy_name, optimisation_hierarchy_level, hierarchy_table):
    hierarchy_parent_dict = {}
    while optimisation_hierarchy_level != 0:
        hierarchy_parent_name = hierarchy_table.loc[
            hierarchy_table["Hierarchy_name"] == hierarchy_name, "Hierarchy_parent_name"
        ].iloc[0]
        hierarchy_parent_level = hierarchy_table.loc[
            hierarchy_table["Hierarchy_name"] == hierarchy_parent_name, "Hierarchy_level"
        ].iloc[0]
        hierarchy_parent_dict[hierarchy_parent_level] = hierarchy_parent_name
        hierarchy_name = hierarchy_parent_name
        optimisation_hierarchy_level = hierarchy_parent_level
    return hierarchy_parent_dict
