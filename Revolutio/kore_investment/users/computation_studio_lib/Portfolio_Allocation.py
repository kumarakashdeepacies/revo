## Importing the neccessary packages


import pickle

import numpy as np
import pandas as pd
from pypfopt import expected_returns

from config.settings.base import redis_instance
from kore_investment.users.computations.db_centralised_function import read_data_func


## Portfolio Allocation Model ##
class Portfolio_Allocation:

    # Calculation of expected return using historical returns and current yields
    def expected_return(self, securities_data, securities_market_quotes, valuation_date):
        security_val_date = securities_market_quotes.loc[
            (securities_market_quotes["extract_date"] == valuation_date)
        ]
        if "return_basis" in securities_data and "unique_reference_id" in securities_data:
            yield_based_securities = (
                pd.merge(
                    securities_data.loc[securities_data["return_basis"] == "Yield based"],
                    security_val_date.loc[:, ["security_identifier", "yield"]],
                    left_on="unique_reference_id",
                    right_on="security_identifier",
                    how="left",
                )
                .drop(columns=["security_identifier"])
                .rename(columns={"yield": "expected_return"})
            )
            equities_mfs_invits = securities_data.loc[
                securities_data["return_basis"] == "Historic", "unique_reference_id"
            ].tolist()
            historic_prices = (
                securities_market_quotes.loc[
                    securities_market_quotes["security_identifier"].isin(equities_mfs_invits)
                ]
                .reset_index()
                .pivot(index="extract_date", columns="security_identifier")["quoted_price"]
            )
            historic_return = (
                expected_returns.mean_historical_return(historic_prices)
                .reset_index()
                .rename(columns={0: "historic_return"})
            )
            historic_return_based_securities = (
                pd.merge(
                    securities_data.loc[securities_data["return_basis"] == "Historic"],
                    historic_return,
                    left_on="unique_reference_id",
                    right_on="security_identifier",
                    how="left",
                )
                .drop(columns=["security_identifier"])
                .rename(columns={"historic_return": "expected_return"})
            )
            securities_data = pd.concat(
                [yield_based_securities, historic_return_based_securities], ignore_index=True
            )
            result = securities_data.loc[
                securities_data["expected_return"].notnull(),
                ["unique_reference_id", "product_variant_name", "issuer", "return_basis", "expected_return"],
            ]
        else:
            yield_based_securities = (
                pd.merge(
                    securities_data.loc[securities_data["return_type"] == "yield"],
                    security_val_date.loc[:, ["security_identifier", "yield"]],
                    left_on="benchmark_variant",
                    right_on="security_identifier",
                    how="left",
                )
                .drop(columns=["security_identifier"])
                .rename(columns={"yield": "expected_return"})
            )
            equities_mfs_invits = securities_data.loc[
                securities_data["return_type"] == "historic returns", "benchmark_variant"
            ].tolist()
            historic_prices = (
                securities_market_quotes.loc[
                    securities_market_quotes["security_identifier"].isin(equities_mfs_invits)
                ]
                .reset_index()
                .pivot(index="extract_date", columns="security_identifier")["quoted_price"]
            )
            historic_return = (
                expected_returns.mean_historical_return(historic_prices)
                .reset_index()
                .rename(columns={0: "historic_return"})
            )
            historic_return_based_securities = (
                pd.merge(
                    securities_data.loc[securities_data["return_type"] == "historic returns"],
                    historic_return,
                    left_on="benchmark_variant",
                    right_on="security_identifier",
                    how="left",
                )
                .drop(columns=["security_identifier"])
                .rename(columns={"historic_return": "expected_return"})
            )
            securities_data = pd.concat(
                [yield_based_securities, historic_return_based_securities], ignore_index=True
            )
            result = securities_data.loc[
                securities_data["expected_return"].notnull(),
                [
                    "benchmark_variant",
                    "tenor",
                    "tenor_unit",
                    "asset_class",
                    "sector",
                    "rating",
                    "return_type",
                    "expected_return",
                ],
            ]
            result["expected_return"] = result["expected_return"].round(4)
        return result

    # Calulation of liquidity limit
    def portfolio_liquidity(self, valuation_date, liquidity, securities_data):
        securities_data["volume_traded"] = securities_data["volume_traded"].replace(np.nan, 0)
        required_data = securities_data["volume_traded"]
        required_data = securities_data[(securities_data["extract_date"] == valuation_date)]
        required_data["volume_traded"] = required_data["volume_traded"] * liquidity
        required_data["volume_traded"] = required_data["volume_traded"].round(4)
        required_data.rename(
            columns={
                "extract_date": "Valuation Date",
                "security_identifier": "Security Reference ID",
                "volume_traded": "Volume Limit",
            },
            inplace=True,
        )
        return required_data

    # Calculation of current exposure and available limits
    def portfolio_limit_utlisation(self, valuation_date, limit_config, data_mapper, value_column, scenario):
        positions_data_key = data_mapper["positions"]
        positions_data = pickle.loads(redis_instance.get(positions_data_key))
        required_data_columns = [
            "Scenario",
            "Issuer Name",
            "Issuer ID",
            "Issuer Limit",
            "Limit Type",
            "Exposure",
        ]
        required_data = pd.DataFrame(columns=required_data_columns)
        if limit_config["source"] == "manual_entry_PLU":
            req_limits = limit_config["manual_limits"]
            for key, value in req_limits.items():
                col_name = value["col_name"]
                data = positions_data[(positions_data[col_name] == key)].reset_index()
                data = data[(data["reporting_date"] == valuation_date)]
                book_value = data[value_column].sum()
                if value["type"] == "Relative":
                    req_volume = str(float(value["value"]["input_value"]) * 100) + "%"
                elif value["type"] == "Absolute":
                    req_volume = value["value"]["input_value"]
                required_data_dict = {
                    "Scenario": scenario,
                    "Issuer Name": key,
                    "Issuer ID": "-",
                    "Issuer Limit": req_volume,
                    "Limit Type": value["type"],
                    "Exposure": round(float(book_value), 4),
                }
                required_data_df1 = pd.DataFrame.from_dict([required_data_dict])
                required_data = pd.concat(
                    [required_data, required_data_df1],
                    ignore_index=True,
                )

        elif limit_config["source"] == "upload_data_PLU":
            uploaded_data_key = limit_config["uploaded_data"]
            uploaded_data = pickle.loads(redis_instance.get(uploaded_data_key))
            issuer_list = list(uploaded_data["issuer_name"])
            limit_type_list = list(uploaded_data["limit_type"])
            value_list = list(uploaded_data["issuer_limit"])
            req_limits = {}
            for issuer, limit_type, value in zip(issuer_list, limit_type_list, value_list):
                limit = {"type": limit_type, "value": value}
                req_limits[issuer] = limit
            exposure_list = []
            for key, value in req_limits.items():
                data = positions_data[(positions_data["issuer"] == key)].reset_index()
                data = data[(data["reporting_date"] == valuation_date)]
                book_value = data[value_column].sum()
                exposure_list.append(round(book_value, 4))
            uploaded_data["Exposure"] = exposure_list
            required_data = uploaded_data
            required_data.rename(
                columns={
                    "scenario": "Scenario",
                    "issuer_name": "Issuer Name",
                    "issuer_id": "Issuer ID",
                    "limit_type": "Limit Type",
                    "issuer_limit": "Issuer Limit",
                },
                inplace=True,
            )
        return required_data

    # Computation of investment allocation
    def portfolio_allocation(
        self,
        positions_data,
        asset_class_data,
        liquidity_data,
        issuer_limit_data,
        expected_returns_data,
        investment,
        valuation_date,
        final_securities_data,
        rounding_view=4,
    ):
        investment = float(investment)
        final_securities_data.sort_values("expected_return", ascending=False, inplace=True)
        total_bv = (positions_data[(positions_data["reporting_date"] == valuation_date)])[
            "ammortised_bookvalue"
        ].sum()
        total_investment = total_bv + investment
        asset_class_data["Allocation"] = asset_class_data["Allocation"] * investment
        relative_limits = issuer_limit_data.loc[issuer_limit_data["Limit Type"] == "Relative"]
        absolute_limits = issuer_limit_data.loc[issuer_limit_data["Limit Type"] == "Absolute"]
        relative_limits["Available Limit"] = (
            (relative_limits["Issuer Limit"].str.slice(start=0, stop=-1).astype("float") / 100.0)
            * total_investment
        ) - (relative_limits["Exposure"])
        absolute_limits["Available Limit"] = (absolute_limits["Issuer Limit"]).astype(
            "float"
        ) - absolute_limits["Exposure"]
        required_data = pd.concat([relative_limits, absolute_limits], ignore_index=True)
        required_data["Available Limit"] = np.where(
            required_data["Available Limit"] > 0, required_data["Available Limit"], 0
        )
        asset_class_limits = dict(zip(asset_class_data["asset_class"], asset_class_data["Allocation"]))
        issuer_limits = dict(zip(required_data["Issuer Name"], required_data["Available Limit"]))
        final_securities_data = final_securities_data.to_dict("records")
        investment_original = investment
        portfolio_allocation = []
        entity_limit = 0.1 * total_investment
        market_lot = 50000000
        for i in final_securities_data:
            if investment <= 0:
                break
            else:
                if i["return_basis"] != "Historic":
                    volume_limit_cap = i["Volume Limit"]
                else:
                    volume_limit_cap = investment
                issuer = i["issuer"]
                if issuer in issuer_limits.keys():
                    issuer_limit_cap = issuer_limits[issuer]
                else:
                    issuer_limit_cap = investment
                asset_class = i["asset_class"]
                if asset_class in asset_class_limits.keys():
                    asset_class_cap = asset_class_limits[asset_class]
                else:
                    asset_class_cap = 0

                allocated_amount = min(volume_limit_cap, issuer_limit_cap, asset_class_cap, entity_limit)
                if allocated_amount > investment:
                    allocated_amount = investment
                else:
                    pass
                if i["product_variant_name"] not in [
                    "Equity",
                    "Mutual Funds",
                    "Infrastructure Investment Trusts",
                ]:
                    if allocated_amount < market_lot:
                        allocated_amount = 0
                    else:
                        allocated_amount = allocated_amount
                i["allocated_amount"] = round(allocated_amount, rounding_view)
                i["allocated_amount_percentage"] = allocated_amount / investment_original
                i["percentage_allocated"] = (
                    str(round(allocated_amount / investment_original * 100, rounding_view)) + "%"
                )
                investment = investment - allocated_amount
                if issuer in issuer_limits.keys():
                    issuer_limits[issuer] = issuer_limits[issuer] - allocated_amount
                if asset_class in asset_class_limits.keys():
                    asset_class_limits[asset_class] = asset_class_limits[asset_class] - allocated_amount
                if allocated_amount != 0:
                    portfolio_allocation.append(i)

        portfolio_allocation_df = pd.DataFrame(portfolio_allocation)
        portfolio_allocation_df = (
            portfolio_allocation_df.loc[
                :,
                [
                    "unique_reference_id",
                    "product_variant_name",
                    "allocated_amount",
                    "percentage_allocated",
                    "allocated_amount_percentage",
                    "Valuation Date",
                    "issuer",
                ],
            ]
            .rename(
                columns={
                    "Valuation Date": "valuation_date",
                    "allocated_amount_percentage": "percentage_allocated_decimals",
                }
            )
            .sort_values("allocated_amount", ascending=False)
        )
        return portfolio_allocation_df


portfolio_allocation_base = Portfolio_Allocation()


## Master JSON Extraction Function ##
def PFA_Base_JSON(config_dict, request):
    if config_dict["function"] == "Expected Return":
        securities_data = pickle.loads(redis_instance.get(config_dict["inputs"]["securities_data"]))
        securities_market_quotes = pickle.loads(
            redis_instance.get(config_dict["inputs"]["securities_market_quotes"])
        )
        valuation_date = pd.to_datetime(config_dict["inputs"]["valuation_date"]["val_date"])
        if "return_basis" in securities_data and "unique_reference_id" in securities_data:
            product_master = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Product_Master",
                        "Columns": ["id", "product_variant_name"],
                    },
                    "condition": [],
                },
            )
            expected_return = portfolio_allocation_base.expected_return(
                securities_data, securities_market_quotes, valuation_date
            )
            expected_return = (
                pd.merge(expected_return, product_master, left_on="product_variant_name", right_on="id")
                .drop(columns=["id", "product_variant_name_x"])
                .rename(columns={"product_variant_name_y": "product_variant_name"})
            )
            expected_return = expected_return.loc[
                :,
                ["unique_reference_id", "product_variant_name", "return_basis", "expected_return", "issuer"],
            ]
        else:
            expected_return = portfolio_allocation_base.expected_return(
                securities_data, securities_market_quotes, valuation_date
            )
        return expected_return

    elif config_dict["function"] == "Portfolio Liquidity":
        valuation_date = pd.to_datetime(config_dict["inputs"]["valuation_date"]["val_date"])
        liquidity = float(config_dict["inputs"]["liquidity"]["liquidity_val"])
        securities_data = pickle.loads(redis_instance.get(config_dict["data"][0]))
        required_data = portfolio_allocation_base.portfolio_liquidity(
            valuation_date, liquidity, securities_data
        )
        return required_data

    elif config_dict["function"] == "Portfolio Limit Utilisation":
        valuation_date = pd.to_datetime(config_dict["inputs"]["valuation_date"]["val_date"])
        limit_config = config_dict["inputs"]["limits"]
        data_mapper = config_dict["data"]
        value_column = config_dict["inputs"]["value_column"]
        scenario = config_dict["inputs"]["scenario_name"]
        required_data = portfolio_allocation_base.portfolio_limit_utlisation(
            valuation_date, limit_config, data_mapper, value_column, scenario
        )
        return required_data

    elif config_dict["function"] == "Portfolio Allocation":
        positions_data = pickle.loads(redis_instance.get(config_dict["inputs"]["positions_data"]))
        asset_class_data = pickle.loads(redis_instance.get(config_dict["inputs"]["asset_class_data"]))
        liquidity_data = pickle.loads(redis_instance.get(config_dict["inputs"]["liquidity_data"]))
        issuer_limit_data = pickle.loads(redis_instance.get(config_dict["inputs"]["issuer_limit_data"]))
        expected_returns_data = pickle.loads(
            redis_instance.get(config_dict["inputs"]["expected_returns_data"])
        )
        investment = float(config_dict["inputs"]["investment"]["investment_val"])
        valuation_date = pd.to_datetime(config_dict["inputs"]["valuation_date"]["val_date"])
        final_securities_data = pd.merge(
            expected_returns_data,
            liquidity_data,
            left_on="unique_reference_id",
            right_on="Security Reference ID",
        ).drop(columns=["Security Reference ID"])
        product_master = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Product_Master",
                    "Columns": ["id", "asset_class", "product_variant_name"],
                },
                "condition": [],
            },
        )
        asset_class_master = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Asset_Class_Master",
                    "Columns": ["id", "asset_class"],
                },
                "condition": [],
            },
        )
        final_securities_data = (
            pd.merge(
                final_securities_data,
                product_master,
                left_on="product_variant_name",
                right_on="product_variant_name",
            )
            .drop(columns=["id"])
            .rename(columns={"asset_class": "asset_class_id"})
        )
        final_securities_data["asset_class_id"] = final_securities_data["asset_class_id"].astype("int64")
        final_securities_data = pd.merge(
            final_securities_data, asset_class_master, left_on="asset_class_id", right_on="id"
        ).drop(columns=["id", "asset_class_id"])
        positions_data = (
            pd.merge(positions_data, product_master, left_on="product_variant_name", right_on="id")
            .drop(columns=["id"])
            .rename(columns={"asset_class": "asset_class_id"})
        )
        positions_data["asset_class_id"] = positions_data["asset_class_id"].astype("int64")
        positions_data = pd.merge(
            positions_data, asset_class_master, left_on="asset_class_id", right_on="id"
        ).drop(columns=["id", "asset_class_id"])
        rounding_view = 4
        required_data = portfolio_allocation_base.portfolio_allocation(
            positions_data,
            asset_class_data,
            liquidity_data,
            issuer_limit_data,
            expected_returns_data,
            investment,
            valuation_date,
            final_securities_data,
            rounding_view,
        )
        return required_data
