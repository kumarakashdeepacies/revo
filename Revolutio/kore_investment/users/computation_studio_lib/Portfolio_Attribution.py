import json
import pickle

import numpy as np
import pandas as pd

from config.settings.base import redis_instance
from kore_investment.users.computation_studio_lib import Valuation_Models
from kore_investment.users.computations.db_centralised_function import read_data_func


# Master class call that has the required functions to calculate the measures
class Portfolio_Attribution:
    def TWRR(self, pool_name, run_date, twrr_data_key, pooling_rule_master_key):
        twrr_data = pickle.loads(redis_instance.get(twrr_data_key))
        pooling_rule_master = pickle.loads(redis_instance.get(pooling_rule_master_key))
        pooling_rule_master = pooling_rule_master[(pooling_rule_master["table_name"] == "Fund_Master")]
        pooling_rule_master = pooling_rule_master.loc[
            :, ["table_name", "constraint_type", "threshold", "constraint_parameter_value"]
        ]

        twrr_data["Run_date"] = pd.to_datetime(twrr_data["Run_date"].dt.strftime("%Y-%m-%d"))
        twrr_data = twrr_data[
            (twrr_data["Run_date"] == pd.to_datetime(run_date).strftime("%Y-%m-%d"))
        ].reset_index()
        twrr_data.drop_duplicates(subset=["Fund_code"], keep="last", inplace=True, ignore_index=True)

        # Fund to pool mapping df created here
        pooling_rule_master = pooling_rule_master.loc[
            :, ["constraint_parameter_value", "constraint_type"]
        ].set_index(pooling_rule_master["threshold"])
        pooling_rule_master = pooling_rule_master.to_dict()
        pool_mapper = {}
        for i, j in pooling_rule_master["constraint_type"].items():
            if j == "Group":
                fund_list = pooling_rule_master["constraint_parameter_value"][i].strip("][").split(", ")
                # the funds in the list were in the for of a string of type '"81B"', this has been done to make the funds uniform throughout
                #'"81A" ' was an odd one out and had space after its closing quote
                for fund in fund_list:
                    if fund == '"81A" ':
                        fund = fund[1:-2]
                    else:
                        fund = fund[1:-1]
                    pool_mapper[fund] = i
            else:
                pool_mapper[pooling_rule_master["constraint_parameter_value"][i]] = i

        pool_mapper = {"Fund_code": list(pool_mapper.keys()), "Pool": list(pool_mapper.values())}
        pool_mapper_df = pd.DataFrame.from_dict(pool_mapper)
        twrr_data = twrr_data.merge(pool_mapper_df, how="left", on="Fund_code")
        pool_mapping = twrr_data.loc[:, ["Fund_code", "Pool"]]
        pool_mapping = pool_mapping.rename(columns={pool_mapping.columns[0]: "fund_code"})
        pool_mapping.fillna("None", inplace=True)
        twrr_data = twrr_data[(twrr_data["Pool"] == pool_name)].reset_index()
        start_date = pd.to_datetime(twrr_data.loc[0, "Start_date"])
        end_date = pd.to_datetime(twrr_data.loc[0, "End_date"])

        # Taking average of opening and ending values to get allocation
        twrr_data["Average Value"] = (twrr_data["Opening_value"] + twrr_data["Ending_value"]) / 2
        twrr_data["Allocation"] = (twrr_data["Average Value"]) / (twrr_data["Average Value"].sum())

        # TWRR of pool by taking weighted average using allocation as weights
        twrr_data["Returns"] = twrr_data["Allocation"] * twrr_data["TWRR"]
        TWRR = twrr_data["Returns"].sum()
        return TWRR, pool_mapping, start_date, end_date

    def R1(
        self,
        start_date,
        end_date,
        pooling_mapper,
        pool_name,
        allocation_data_key,
        benchmark_master_data_key,
        quoted_prices_data_key,
        quoted_data_start,
        quoted_data_end,
    ):
        portfolio_allocation = pickle.loads(redis_instance.get(allocation_data_key))
        # Filtering required data as per the pool name and valuation date
        portfolio_allocation["Valuation_date"] = pd.to_datetime(
            portfolio_allocation["Valuation_date"].dt.strftime("%Y-%m-%d")
        )
        portfolio_allocation = portfolio_allocation[
            (portfolio_allocation["Valuation_date"] == pd.to_datetime(start_date).strftime("%Y-%m-%d"))
        ]
        portfolio_allocation.drop_duplicates(
            subset=["Pool_id", "Valuation_date", "Security_identifier"], keep="last", inplace=True
        )

        market_benchmark_master = pickle.loads(redis_instance.get(benchmark_master_data_key))
        market_benchmark_master = market_benchmark_master.loc[:, ["return_type", "benchmark_variant"]]

        # Adding the Column Return Type to each benchmarks
        portfolio_allocation.rename(columns={"Security_identifier": "benchmark_variant"}, inplace=True)
        portfolio_allocation = portfolio_allocation.merge(
            market_benchmark_master, on="benchmark_variant", how="left"
        )
        portfolio_allocation["Return_rate"] = None

        # Getting the return based on return_type from quoted prices as on start date (On 1st October quotes for benchmarks are available)
        portfolio_allocation_yield = portfolio_allocation[portfolio_allocation["return_type"] == "yield"]
        portfolio_allocation_yield.rename(columns={"benchmark_variant": "security_identifier"}, inplace=True)
        portfolio_allocation_yield = portfolio_allocation_yield.merge(
            quoted_data_start, on="security_identifier", how="left"
        )
        portfolio_allocation_yield["Return_rate"] = portfolio_allocation_yield["Return_rate"].fillna(
            portfolio_allocation_yield["yield"]
        )
        time_frac = (np.timedelta64(end_date - start_date, "D").astype(int)) / 365
        portfolio_allocation_yield["Return_rate"] = portfolio_allocation_yield["Return_rate"]
        portfolio_allocation_yield.drop(["quoted_price", "yield"], axis=1, inplace=True)

        portfolio_allocation_historic = portfolio_allocation[portfolio_allocation["return_type"] != "yield"]
        portfolio_allocation_historic.rename(
            columns={"benchmark_variant": "security_identifier"}, inplace=True
        )
        portfolio_allocation_historic = portfolio_allocation_historic.merge(
            quoted_data_start, on="security_identifier", how="left"
        )
        portfolio_allocation_historic.rename(columns={"quoted_price": "start_price"}, inplace=True)
        portfolio_allocation_historic = portfolio_allocation_historic.merge(
            quoted_data_end, on="security_identifier", how="left"
        )
        portfolio_allocation_historic.rename(columns={"quoted_price": "end_price"}, inplace=True)
        portfolio_allocation_historic["Return_rate"] = (
            portfolio_allocation_historic["end_price"] - portfolio_allocation_historic["start_price"]
        ) / portfolio_allocation_historic["start_price"]
        time_delta_days = np.timedelta64(end_date - start_date, "D").astype(int)
        portfolio_allocation_historic["Return_rate"] = (
            (1 + portfolio_allocation_historic["Return_rate"]) ** (365.25 / time_delta_days)
        ) - 1
        portfolio_allocation_historic.drop(
            ["start_price", "end_price", "yield_x", "yield_y"], axis=1, inplace=True
        )
        R1_Table = portfolio_allocation_yield.append(portfolio_allocation_historic)
        R1_Table["Return"] = R1_Table["Return_rate"] * R1_Table["Allocation"]
        R1 = R1_Table["Return"].sum()
        R1_Table_req = R1_Table.loc[:, ["security_identifier", "Return_rate", "return_type"]]
        R1_Table_req.rename(columns={"security_identifier": "benchmark_variant"}, inplace=True)

        # Table for intermediate output
        R1_table_intermediate = pd.DataFrame()
        R1_table_intermediate["security_code"] = R1_Table["security_identifier"]
        R1_table_intermediate["asset_class"] = R1_Table["asset_class"]
        R1_table_intermediate["period_start"] = start_date
        R1_table_intermediate["period_end"] = end_date
        R1_table_intermediate["return_type"] = R1_Table["return_type"]
        R1_table_intermediate["time_fraction"] = time_frac
        R1_table_intermediate["allocation"] = R1_Table["Allocation"]
        R1_table_intermediate["return_rate"] = R1_Table["Return_rate"]
        R1_table_intermediate["final_return"] = R1_Table["Return"]
        R1_table_intermediate["market_benchmark"] = R1_Table["security_identifier"]
        R1_table_intermediate["measure_name"] = "R1"

        return R1, R1_Table_req, R1_table_intermediate

    def R2(
        self,
        start_date,
        end_date,
        pool_name,
        pool_mapping,
        quoted_prices_data_key,
        benchmark_master_data_key,
        R2_Table_input,
        positions_table,
        request,
    ):
        # Pass the Start and the End dates as variables
        positions_start_pools = positions_table[positions_table["reporting_date"] == start_date]

        positions_end_pools = positions_table[positions_table["reporting_date"] == end_date]

        ref_ids_start = list(positions_start_pools["position_id"])
        ref_ids_end = list(positions_end_pools["position_id"])

        late_buys = list(set(ref_ids_end) - set(ref_ids_start))
        early_sells = list(set(ref_ids_start) - set(ref_ids_end))
        common_positions = list(set(ref_ids_start) & set(ref_ids_end))

        R2_list = []

        if len(early_sells) > 0:
            for i in range(len(early_sells)):
                R2_dict = {}
                early_sell_df = positions_start_pools[
                    positions_start_pools["position_id"] == early_sells[i]
                ].reset_index()
                R2_dict["Security_Code"] = early_sell_df["unique_reference_id"][0]
                R2_dict["Product_variant"] = early_sell_df["product_variant_name"][0]
                if early_sell_df["maturity_date"][0] < end_date:
                    R2_dict["Tenor"] = (
                        np.timedelta64(early_sell_df["maturity_date"][0] - start_date, "D").astype(int) / 365
                    )
                else:
                    R2_dict["Tenor"] = np.timedelta64(end_date - start_date, "D").astype(int) / 365
                R2_dict["Sector"] = early_sell_df["sector"][0]
                R2_dict["Internal_Rating"] = early_sell_df["internal_rating"][0]
                R2_dict["Period_start"] = start_date
                if early_sell_df["maturity_date"][0] < end_date:
                    R2_dict["Period_end"] = early_sell_df["maturity_date"][0]
                else:
                    R2_dict["Period_end"] = end_date
                R2_dict["Balance"] = (early_sell_df["ammortised_bookvalue"][0]) / 2

                R2_list.append(R2_dict)

        if len(late_buys) > 0:
            for i in range(len(late_buys)):
                R2_dict = {}
                late_buy_df = positions_end_pools[
                    positions_end_pools["position_id"] == late_buys[i]
                ].reset_index()
                R2_dict["Security_Code"] = late_buy_df["unique_reference_id"][0]
                R2_dict["Product_variant"] = late_buy_df["product_variant_name"][0]
                if late_buy_df["start_date"][0] > start_date:
                    R2_dict["Tenor"] = (
                        np.timedelta64(end_date - late_buy_df["start_date"][0], "D").astype(int) / 365
                    )
                else:
                    R2_dict["Tenor"] = np.timedelta64(end_date - start_date, "D").astype(int) / 365
                R2_dict["Sector"] = late_buy_df["sector"][0]
                R2_dict["Internal_Rating"] = late_buy_df["internal_rating"][0]
                R2_dict["Period_start"] = late_buy_df["start_date"][0]
                R2_dict["Period_end"] = end_date
                R2_dict["Balance"] = (late_buy_df["ammortised_bookvalue"][0]) / 2

                R2_list.append(R2_dict)

        if len(common_positions) > 0:
            for i in range(len(common_positions)):
                R2_dict = {}
                common_positions_start_df = positions_start_pools[
                    positions_start_pools["position_id"] == common_positions[i]
                ].reset_index()
                common_positions_end_df = positions_end_pools[
                    positions_end_pools["position_id"] == common_positions[i]
                ].reset_index()
                R2_dict["Security_Code"] = common_positions_start_df["unique_reference_id"][0]
                R2_dict["Product_variant"] = common_positions_start_df["product_variant_name"][0]
                R2_dict["Tenor"] = np.timedelta64(end_date - start_date, "D").astype(int) / 365
                R2_dict["Sector"] = common_positions_start_df["sector"][0]
                R2_dict["Internal_Rating"] = common_positions_start_df["internal_rating"][0]
                R2_dict["Period_start"] = start_date
                R2_dict["Period_end"] = end_date
                R2_dict["Balance"] = (
                    common_positions_start_df["ammortised_bookvalue"][0]
                    + common_positions_end_df["ammortised_bookvalue"][0]
                ) / 2

                R2_list.append(R2_dict)

        R2_Table = pd.DataFrame(R2_list)
        R2_Table.fillna("None", inplace=True)
        R2_Table.reset_index(inplace=True)
        R2_Table.insert(3, "Tenor_Unit", "")
        R2_Table.insert(6, "benchmark_variant", "")
        R2_Table["Allocation"] = R2_Table["Balance"] / R2_Table["Balance"].sum()

        R2_Table["Time_fraction"] = (
            (
                pd.to_datetime(R2_Table["Period_end"]) - pd.to_datetime(R2_Table["Period_start"])
            ).dt.days.astype(int)
        ) / 365
        product_master = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Product_Master",
                    "Columns": ["id", "asset_class"],
                },
                "condition": [],
            },
        )
        market_benchmark_master = pickle.loads(redis_instance.get(benchmark_master_data_key))

        # Product to benchmark mapping
        for i in range(len(R2_Table)):
            product_var_name = R2_Table["Product_variant"][i]
            market_benchmark_master_req = market_benchmark_master
            for j in range(len(market_benchmark_master_req["tenor_unit"])):
                if market_benchmark_master_req["tenor_unit"][j] == "D":
                    market_benchmark_master_req["tenor"][j] = (
                        float(market_benchmark_master_req["tenor"][j])
                    ) / 365
                    market_benchmark_master_req["tenor_unit"][j] = "Y"

                elif market_benchmark_master_req["tenor_unit"][j] == "M":
                    market_benchmark_master_req["tenor"][j] = (
                        float(market_benchmark_master_req["tenor"][j])
                    ) / 12
                    market_benchmark_master_req["tenor_unit"][j] = "Y"

                else:
                    pass

            market_benchmark_list = []
            market_benchmark_master_req.reset_index(inplace=True, drop=True)
            for k in range(len(market_benchmark_master_req["product_list"])):
                if market_benchmark_master_req["product_list"][k].startswith("{"):
                    product_list = list(json.loads(market_benchmark_master_req["product_list"][k]).keys())
                else:
                    product_list = []
                if str(product_var_name) in product_list:
                    market_benchmark_list.append(k)
            market_benchmark_master_req = market_benchmark_master_req.iloc[market_benchmark_list]
            sector = R2_Table["Sector"][i]
            rating = R2_Table["Internal_Rating"][i]
            if rating == "SOVEREIGN":
                rating = "SOV"
            market_benchmark_master_req = market_benchmark_master_req[
                (market_benchmark_master_req["sector"] == sector)
                & (market_benchmark_master_req["rating"] == rating)
            ]
            tenor_list = list(market_benchmark_master_req["tenor"])
            tenor_list.sort()
            individual_tenor = R2_Table["Tenor"][i]
            diff_list = []
            for tenor in tenor_list:
                diff_list.append(abs(tenor - individual_tenor))
            min_index = diff_list.index(min(diff_list))
            required_tenor = tenor_list[min_index]
            required_benchmark = (
                market_benchmark_master_req[
                    (market_benchmark_master_req["tenor"] == required_tenor)
                ].reset_index(drop=True)
            )["benchmark_variant"][0]
            R2_Table["benchmark_variant"][i] = required_benchmark

        # Adding the Column Return Type to each benchmarks
        R2_table_req = R2_Table.merge(R2_Table_input, on="benchmark_variant", how="left")
        R2_table_req = R2_table_req.dropna()
        R2_table_req["Return"] = R2_table_req["Return_rate"] * R2_table_req["Allocation"]
        R2 = R2_table_req["Return"].sum()

        # Table for intermediate output
        product_master = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Product_Master",
                    "Columns": ["product_variant", "id"],
                },
                "condition": [],
            },
        )
        product_master.rename(columns={"id": "asset_class"}, inplace=True)
        R2_table_intermediate = pd.DataFrame()
        R2_table_intermediate["security_code"] = R2_table_req["Security_Code"]
        R2_table_intermediate["asset_class"] = R2_table_req["Product_variant"]
        R2_table_intermediate["period_start"] = R2_table_req["Period_start"]
        R2_table_intermediate["period_end"] = R2_table_req["Period_end"]
        R2_table_intermediate["return_type"] = R2_table_req["return_type"]
        R2_table_intermediate["time_fraction"] = R2_table_req["Time_fraction"]
        R2_table_intermediate["allocation"] = R2_table_req["Allocation"]
        R2_table_intermediate["return_rate"] = R2_table_req["Return_rate"]
        R2_table_intermediate["final_return"] = R2_table_req["Return"]
        R2_table_intermediate["market_benchmark"] = R2_table_req["benchmark_variant"]
        R2_table_intermediate["measure_name"] = "R2"
        R2_table_intermediate1 = R2_table_intermediate.merge(product_master, on="asset_class", how="left")
        R2_table_intermediate["asset_class"] = R2_table_intermediate1["product_variant"]
        R2_Table_req = R2_table_req.drop(["Return_rate", "Return"], axis=1)
        return R2, R2_Table_req, R2_table_intermediate

    def R3(
        self,
        R3_Table,
        start_date,
        end_date,
        securities_data_key,
        quoted_data_start,
        quoted_data_end,
        positions_table,
        mtm_data,
        request,
    ):
        # Here allocation is gotten from R2 where the calculation was done according to ammortised bookvalue, R3_Table is the R2_Table_req from R2 function
        credit_spread_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Credit_Spread_Curve_Data",
                    "Columns": [
                        "credit_spread_curve_name",
                        "tenor",
                        "tenor_unit",
                        "spread_value",
                    ],
                },
                "condition": [],
            },
        )
        curve_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Curve_Data",
                    "Columns": ["curve_name", "quote_date", "curve_points", "interpolation_algorithm"],
                },
                "condition": [],
            },
        )
        holiday_calendar = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Holiday_Calendar_Repository",
                    "Columns": ["holiday_calendar_tag", "holiday_date"],
                },
                "condition": [],
            },
        )
        securities_master = pickle.loads(redis_instance.get(securities_data_key)).loc[
            :, ["unique_reference_id", "return_basis"]
        ]
        positions_table = positions_table.merge(securities_master, on="unique_reference_id", how="left")

        # For return_type yield
        position_master_yield = positions_table[positions_table["return_basis"] == "Yield based"]
        positions_table_start = position_master_yield[(position_master_yield["reporting_date"] == start_date)]
        positions_table_end = position_master_yield[(position_master_yield["reporting_date"] == end_date)]

        ref_ids_start = list(positions_table_start["position_id"])
        ref_ids_end = list(positions_table_end["position_id"])

        late_buys = list(set(ref_ids_end) - set(ref_ids_start))
        early_sells = list(set(ref_ids_start) - set(ref_ids_end))
        common_positions = list(set(ref_ids_start) & set(ref_ids_end))

        R3_list = []

        if len(early_sells) > 0:
            for i in range(len(early_sells)):
                R3_dict = {}
                early_sell_df = positions_table_start[
                    positions_table_start["position_id"] == early_sells[i]
                ].reset_index()
                R3_dict["unique_reference_id"] = early_sell_df["unique_reference_id"][0]
                R3_dict["product_variant_name"] = early_sell_df["product_variant_name"][0]
                R3_dict["maturity_date"] = early_sell_df["maturity_date"][0]
                R3_dict["issue_date"] = early_sell_df["issue_date"][0]
                R3_dict["settlement_date"] = early_sell_df["settlement_date"][0]
                R3_dict["reporting_date"] = early_sell_df["reporting_date"][0]
                R3_dict["accrual_daycount_convention"] = early_sell_df["accrual_daycount_convention"][0]
                R3_dict["discount_daycount_convention"] = early_sell_df["discount_daycount_convention"][0]
                R3_dict["next_reset_date"] = early_sell_df["next_reset_date"][0]
                R3_dict["reset_frequency"] = early_sell_df["reset_frequency"][0]
                R3_dict["reset_frequency_unit"] = early_sell_df["reset_frequency_unit"][0]
                R3_dict["purchase_price"] = early_sell_df["purchase_price"][0]
                R3_dict["credit_spread_rate"] = early_sell_df["credit_spread_rate"][0]
                R3_dict["credit_spread_curve"] = early_sell_df["credit_spread_curve"][0]
                R3_dict["base_rate"] = early_sell_df["base_rate"][0]
                R3_dict["face_value"] = early_sell_df["face_value"][0]
                R3_dict["redemption_amount"] = early_sell_df["redemption_amount"][0]
                R3_dict["business_convention"] = early_sell_df["business_convention"][0]
                R3_dict["payment_frequency"] = early_sell_df["payment_frequency"][0]
                R3_dict["payment_frequency_units"] = early_sell_df["payment_frequency_units"][0]
                R3_dict["amortization_type"] = early_sell_df["amortization_type"][0]
                R3_dict["principal_payment_frequency"] = early_sell_df["principal_payment_frequency"][0]
                R3_dict["principal_payment_frequency_unit"] = early_sell_df[
                    "principal_payment_frequency_unit"
                ][0]
                R3_dict["last_payment_date"] = early_sell_df["last_payment_date"][0]
                R3_dict["last_principal_payment_date"] = early_sell_df["last_principal_payment_date"][0]
                R3_dict["quantity"] = early_sell_df["quantity"][0]
                R3_dict["spot_yield"] = early_sell_df["spot_yield"][0]
                R3_dict["redemption_premium"] = early_sell_df["redemption_premium"][0]
                R3_dict["ammortised_bookvalue"] = early_sell_df["ammortised_bookvalue"][0]
                R3_dict["mtm_value"] = early_sell_df["mtm_value"][0]
                R3_dict["tenor"] = (
                    np.timedelta64(
                        early_sell_df["maturity_date"][0] - early_sell_df["issue_date"][0], "D"
                    ).astype(int)
                    / 365
                )
                R3_dict["sector"] = early_sell_df["sector"][0]
                R3_dict["internal_rating"] = early_sell_df["internal_rating"][0]
                R3_dict["balance"] = (early_sell_df["ammortised_bookvalue"][0]) / 2
                R3_dict["wac"] = early_sell_df["wac"][0]
                R3_dict["position_id"] = early_sell_df["position_id"][0]
                R3_dict["discounting_curve"] = early_sell_df["discounting_curve"][0]
                R3_list.append(R3_dict)

        if len(late_buys) > 0:
            for i in range(len(late_buys)):
                R3_dict = {}
                late_buy_df = positions_table_end[
                    positions_table_end["position_id"] == late_buys[i]
                ].reset_index()
                R3_dict["unique_reference_id"] = late_buy_df["unique_reference_id"][0]
                R3_dict["product_variant_name"] = late_buy_df["product_variant_name"][0]
                R3_dict["maturity_date"] = late_buy_df["maturity_date"][0]
                R3_dict["issue_date"] = late_buy_df["issue_date"][0]
                R3_dict["settlement_date"] = late_buy_df["settlement_date"][0]
                R3_dict["reporting_date"] = late_buy_df["reporting_date"][0]
                R3_dict["accrual_daycount_convention"] = late_buy_df["accrual_daycount_convention"][0]
                R3_dict["discount_daycount_convention"] = late_buy_df["discount_daycount_convention"][0]
                R3_dict["next_reset_date"] = late_buy_df["next_reset_date"][0]
                R3_dict["reset_frequency"] = late_buy_df["reset_frequency"][0]
                R3_dict["reset_frequency_unit"] = late_buy_df["reset_frequency_unit"][0]
                R3_dict["purchase_price"] = late_buy_df["purchase_price"][0]
                R3_dict["credit_spread_rate"] = late_buy_df["credit_spread_rate"][0]
                R3_dict["credit_spread_curve"] = late_buy_df["credit_spread_curve"][0]
                R3_dict["base_rate"] = late_buy_df["base_rate"][0]
                R3_dict["face_value"] = late_buy_df["face_value"][0]
                R3_dict["redemption_amount"] = late_buy_df["redemption_amount"][0]
                R3_dict["business_convention"] = late_buy_df["business_convention"][0]
                R3_dict["payment_frequency"] = late_buy_df["payment_frequency"][0]
                R3_dict["payment_frequency_units"] = late_buy_df["payment_frequency_units"][0]
                R3_dict["amortization_type"] = late_buy_df["amortization_type"][0]
                R3_dict["principal_payment_frequency"] = late_buy_df["principal_payment_frequency"][0]
                R3_dict["principal_payment_frequency_unit"] = late_buy_df["principal_payment_frequency_unit"][
                    0
                ]
                R3_dict["last_payment_date"] = late_buy_df["last_payment_date"][0]
                R3_dict["last_principal_payment_date"] = late_buy_df["last_principal_payment_date"][0]
                R3_dict["quantity"] = late_buy_df["quantity"][0]
                R3_dict["spot_yield"] = late_buy_df["spot_yield"][0]
                R3_dict["redemption_premium"] = late_buy_df["redemption_premium"][0]
                R3_dict["ammortised_bookvalue"] = late_buy_df["ammortised_bookvalue"][0]
                R3_dict["mtm_value"] = late_buy_df["mtm_value"][0]
                R3_dict["tenor"] = (
                    np.timedelta64(
                        late_buy_df["maturity_date"][0] - late_buy_df["issue_date"][0], "D"
                    ).astype(int)
                    / 365
                )
                R3_dict["sector"] = late_buy_df["sector"][0]
                R3_dict["internal_rating"] = late_buy_df["internal_rating"][0]
                R3_dict["balance"] = (late_buy_df["ammortised_bookvalue"][0]) / 2
                R3_dict["wac"] = late_buy_df["wac"][0]
                R3_dict["position_id"] = late_buy_df["position_id"][0]
                R3_dict["discounting_curve"] = late_buy_df["discounting_curve"][0]
                R3_list.append(R3_dict)

        if len(common_positions) > 0:
            for i in range(len(common_positions)):
                R3_dict = {}
                common_positions_start_df = positions_table_start[
                    positions_table_start["position_id"] == common_positions[i]
                ].reset_index()
                common_positions_end_df = positions_table_end[
                    positions_table_end["position_id"] == common_positions[i]
                ].reset_index()
                R3_dict["unique_reference_id"] = common_positions_start_df["unique_reference_id"][0]
                R3_dict["product_variant_name"] = common_positions_start_df["product_variant_name"][0]
                R3_dict["maturity_date"] = common_positions_start_df["maturity_date"][0]
                R3_dict["issue_date"] = common_positions_start_df["issue_date"][0]
                R3_dict["settlement_date"] = common_positions_start_df["settlement_date"][0]
                R3_dict["reporting_date"] = common_positions_start_df["reporting_date"][0]
                R3_dict["accrual_daycount_convention"] = common_positions_start_df[
                    "accrual_daycount_convention"
                ][0]
                R3_dict["discount_daycount_convention"] = common_positions_start_df[
                    "discount_daycount_convention"
                ][0]
                R3_dict["next_reset_date"] = common_positions_start_df["next_reset_date"][0]
                R3_dict["reset_frequency"] = common_positions_start_df["reset_frequency"][0]
                R3_dict["reset_frequency_unit"] = common_positions_start_df["reset_frequency_unit"][0]
                R3_dict["purchase_price"] = common_positions_start_df["purchase_price"][0]
                R3_dict["credit_spread_rate"] = common_positions_start_df["credit_spread_rate"][0]
                R3_dict["credit_spread_curve"] = common_positions_start_df["credit_spread_curve"][0]
                R3_dict["base_rate"] = common_positions_start_df["base_rate"][0]
                R3_dict["face_value"] = common_positions_start_df["face_value"][0]
                R3_dict["redemption_amount"] = common_positions_start_df["redemption_amount"][0]
                R3_dict["business_convention"] = common_positions_start_df["business_convention"][0]
                R3_dict["payment_frequency"] = common_positions_start_df["payment_frequency"][0]
                R3_dict["payment_frequency_units"] = common_positions_start_df["payment_frequency_units"][0]
                R3_dict["amortization_type"] = common_positions_start_df["amortization_type"][0]
                R3_dict["principal_payment_frequency"] = common_positions_start_df[
                    "principal_payment_frequency"
                ][0]
                R3_dict["principal_payment_frequency_unit"] = common_positions_start_df[
                    "principal_payment_frequency_unit"
                ][0]
                R3_dict["last_payment_date"] = common_positions_start_df["last_payment_date"][0]
                R3_dict["last_principal_payment_date"] = common_positions_start_df[
                    "last_principal_payment_date"
                ][0]
                R3_dict["quantity"] = common_positions_start_df["quantity"][0]
                R3_dict["spot_yield"] = common_positions_start_df["spot_yield"][0]
                R3_dict["redemption_premium"] = common_positions_start_df["redemption_premium"][0]
                R3_dict["ammortised_bookvalue"] = common_positions_start_df["ammortised_bookvalue"][0]
                R3_dict["mtm_value"] = common_positions_start_df["mtm_value"][0]
                R3_dict["tenor"] = (
                    np.timedelta64(
                        common_positions_start_df["maturity_date"][0]
                        - common_positions_start_df["issue_date"][0],
                        "D",
                    ).astype(int)
                    / 365
                )
                R3_dict["sector"] = common_positions_start_df["sector"][0]
                R3_dict["internal_rating"] = common_positions_start_df["internal_rating"][0]
                R3_dict["balance"] = (
                    common_positions_start_df["ammortised_bookvalue"][0]
                    + common_positions_end_df["ammortised_bookvalue"][0]
                ) / 2
                R3_dict["wac"] = (common_positions_start_df["wac"][0] + common_positions_end_df["wac"][0]) / 2
                R3_dict["position_id"] = common_positions_start_df["position_id"][0]
                R3_dict["discounting_curve"] = common_positions_start_df["discounting_curve"][0]
                R3_dict["asset_class"] = common_positions_start_df["asset_class"][0]
                R3_list.append(R3_dict)

        R3_Table_pos = pd.DataFrame(R3_list)
        models_list = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Model_Repository",
                    "Columns": ["id", "model_code"],
                },
                "condition": [],
            },
        )
        models_list.rename(columns={"id": "model_id"}, inplace=True)

        product_model_mapper = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Product_to_Model_mapping",
                    "Columns": ["product_variant", "model_code"],
                },
                "condition": [],
            },
        )
        product_model_mapper.rename(columns={"model_code": "model_id"}, inplace=True)
        product_model_code_mapper = product_model_mapper.merge(models_list, on="model_id", how="left")
        product_model_code_mapper.rename(columns={"product_variant": "product_variant_name"}, inplace=True)
        R3_Table_pos = R3_Table_pos.merge(
            product_model_code_mapper, on="product_variant_name", how="left"
        ).reset_index()
        R3_Table_pos.drop(["model_id"], axis=1)
        config_dict = {"outputs": {"Cashflow": "Yes", "Valuation": "No", "Senstivity": ""}}
        table_cols = R3_Table_pos.columns
        index_list = []

        def col_index_func(table_cols):
            index_list.append(R3_Table_pos.columns.get_loc(table_cols))

        np.vectorize(col_index_func)(table_cols)
        index_list.pop(0)

        column_index_dict = dict(zip(table_cols, index_list))

        R3_Table_pos_array = np.array(R3_Table_pos)
        output_dict = {}
        for row in R3_Table_pos_array:
            output = Valuation_Models.Value_extraction_pf(
                row,
                column_index_dict,
                config_dict,
                curve_data,
                credit_spread_data,
                holiday_calendar,
                mtm_data,
            )
            cashflow_result = pd.DataFrame(output["Cashflow_Result"])
            cashflow_result["Valuation Date"].astype(str)
            cashflow_result["Cashflow Dates"].astype(str)
            price = row[-6]
            TTM_list = np.array(cashflow_result["Time Elapsed"])
            CF_list = np.array(cashflow_result["Total Amount"])
            ytm = Valuation_Models.Valuation_Models().CF_ytm(price, TTM_list, CF_list)
            isin = row[1]
            output_dict[isin] = ytm

        output_df = pd.DataFrame(
            {"security_identifier": list(output_dict.keys()), "Return_rate": list(output_dict.values())}
        )

        securities_master.rename(columns={"unique_reference_id": "security_identifier"}, inplace=True)
        R3_Table.rename(columns={"Security_Code": "security_identifier"}, inplace=True)
        R3_Table.drop(
            ["Tenor", "Tenor_Unit", "Internal_Rating", "Sector", "benchmark_variant"], axis=1, inplace=True
        )
        R3_Table = R3_Table.merge(securities_master, on="security_identifier", how="left")

        R3_Table_yield = R3_Table[R3_Table["return_basis"] == "Yield based"]
        R3_Table_yield = R3_Table_yield.merge(output_df, on="security_identifier", how="left")
        #     "Time_fraction"
        R3_Table_yield["Return_rate"] = R3_Table_yield["Return_rate"].astype(float)

        # For return_type historic
        R3_Table_historic = R3_Table[R3_Table["return_basis"] != "Yield based"]
        R3_Table_historic = R3_Table_historic.merge(quoted_data_start, on="security_identifier", how="left")
        R3_Table_historic.rename(columns={"quoted_price": "start_price"}, inplace=True)
        R3_Table_historic = R3_Table_historic.merge(quoted_data_end, on="security_identifier", how="left")
        R3_Table_historic.rename(columns={"quoted_price": "end_price"}, inplace=True)
        R3_Table_historic["Return_rate"] = (
            R3_Table_historic["end_price"] - R3_Table_historic["start_price"]
        ) / R3_Table_historic["start_price"]

        time_delta_days = np.timedelta64(end_date - start_date, "D").astype(int)
        R3_Table_historic["Return_rate"] = (
            (1 + R3_Table_historic["Return_rate"]) ** (365.25 / time_delta_days)
        ) - 1

        R3_Table_historic.drop(["start_price", "end_price", "yield_x", "yield_y"], axis=1, inplace=True)
        R3_Table_req = R3_Table_yield.append(R3_Table_historic)

        # Calculation of return
        R3_Table_req["Return"] = R3_Table_req["Allocation"] * R3_Table_req["Return_rate"]
        R3 = R3_Table_req["Return"].sum()

        # Table for intermediate output
        product_master = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Product_Master",
                    "Columns": ["product_variant", "id"],
                },
                "condition": [],
            },
        )
        product_master.rename(columns={"id": "asset_class"}, inplace=True)
        product_master["asset_class"] = product_master["asset_class"].astype(int)
        R3_table_intermediate = pd.DataFrame()
        R3_table_intermediate["security_code"] = R3_Table_req["security_identifier"]
        R3_table_intermediate["asset_class"] = R3_Table_req["Product_variant"]
        R3_table_intermediate["period_start"] = R3_Table_req["Period_start"]
        R3_table_intermediate["period_end"] = R3_Table_req["Period_end"]
        R3_table_intermediate["return_type"] = R3_Table_req["return_basis"]
        R3_table_intermediate["time_fraction"] = R3_Table_req["Time_fraction"]
        R3_table_intermediate["allocation"] = R3_Table_req["Allocation"]
        R3_table_intermediate["return_rate"] = R3_Table_req["Return_rate"]
        R3_table_intermediate["final_return"] = R3_Table_req["Return"]
        R3_table_intermediate["market_benchmark"] = "NA"
        R3_table_intermediate["measure_name"] = "R3"
        R3_table_intermediate1 = R3_table_intermediate.merge(product_master, on="asset_class", how="left")
        R3_table_intermediate["asset_class"] = R3_table_intermediate1["product_variant"]

        return R3, R3_table_intermediate


port_attr = Portfolio_Attribution()


# Master function to extract inputs
def portfolio_attribution(config_dict, request):
    run_date = config_dict["inputs"]["valuation_date"]["run_date"]
    pool_name = config_dict["inputs"]["pool_name"]["pool_name"]
    data_sources = config_dict["inputs"]["data_sources"]
    scenario_name = config_dict["inputs"]["scenario_name"]["scenario_name"]

    # extraction of all data inputs
    positions_data_key = data_sources["positions"]
    quoted_prices_data_key = data_sources["quoted_prices"]
    benchmark_master_data_key = data_sources["benchmark_master"]
    allocation_data_key = data_sources["allocation"]
    twrr_data_key = data_sources["twrr"]
    securities_data_key = data_sources["securities"]
    pooling_rule_master_key = data_sources["pooling"]

    # Calculation of measures depending on the functions defined above
    TWRR, pool_mapping, start_date, end_date = port_attr.TWRR(
        pool_name, run_date, twrr_data_key, pooling_rule_master_key
    )
    mtm_data = pickle.loads(redis_instance.get(quoted_prices_data_key))
    quoted_data = pickle.loads(redis_instance.get(quoted_prices_data_key)).loc[
        :, ["extract_date", "security_identifier", "quoted_price", "yield"]
    ]
    quoted_data_start = quoted_data[
        (quoted_data["extract_date"] == pd.to_datetime(start_date).strftime("%Y-%m-%d"))
    ]
    quoted_data_start.drop(["extract_date"], axis=1, inplace=True)

    quoted_data_end = quoted_data[
        (quoted_data["extract_date"] == pd.to_datetime(end_date).strftime("%Y-%m-%d"))
    ]
    quoted_data_end.drop(["extract_date"], axis=1, inplace=True)

    positions_table = pickle.loads(redis_instance.get(positions_data_key))
    positions_table = positions_table.merge(pool_mapping, on="fund_code", how="left")
    positions_table = positions_table[positions_table["Pool"] == pool_name]

    R1, R2_Table, R1_table_intermediate = port_attr.R1(
        start_date,
        end_date,
        pool_mapping,
        pool_name,
        allocation_data_key,
        benchmark_master_data_key,
        quoted_prices_data_key,
        quoted_data_start,
        quoted_data_end,
    )
    R2, R3_Table, R2_table_intermediate = port_attr.R2(
        start_date,
        end_date,
        pool_name,
        pool_mapping,
        quoted_prices_data_key,
        benchmark_master_data_key,
        R2_Table,
        positions_table,
        request,
    )
    R3, R3_table_intermediate = port_attr.R3(
        R3_Table,
        start_date,
        end_date,
        securities_data_key,
        quoted_data_start,
        quoted_data_end,
        positions_table,
        mtm_data,
        request,
    )
    intermediate_table = pd.concat(
        [R1_table_intermediate, R2_table_intermediate, R3_table_intermediate], ignore_index=True
    )
    intermediate_table["pool"] = pool_name
    intermediate_table.replace("yield", "Yield based", inplace=True)
    intermediate_table.replace("historic returns", "Historical", inplace=True)

    # Difference calculation
    D1 = TWRR - R1
    D2 = R2 - R1
    D3 = R3 - R2
    Residual = D1 - D2 - D3

    # Passing the output results into the required dataframe
    TWRR_dict = {
        "period_start": pd.to_datetime(start_date).strftime("%Y-%m-%d"),
        "period_end": pd.to_datetime(end_date).strftime("%Y-%m-%d"),
        "pool": pool_name,
        "scenario": scenario_name,
        "measure_name": "TWRR",
        "measure_value": round(TWRR, 4),
        "description": "Time Weighted Rate of Return for the Pool",
        "difference_description": "-",
        "attributed_difference": None,
    }
    R1_dict = {
        "period_start": pd.to_datetime(start_date).strftime("%Y-%m-%d"),
        "period_end": pd.to_datetime(end_date).strftime("%Y-%m-%d"),
        "pool": pool_name,
        "scenario": scenario_name,
        "measure_name": "R1",
        "measure_value": round(R1, 4),
        "description": "Model Portfolio with Benchmark Return",
        "difference_description": "Total difference",
        "attributed_difference": round(D1, 4),
    }
    R2_dict = {
        "period_start": pd.to_datetime(start_date).strftime("%Y-%m-%d"),
        "period_end": pd.to_datetime(end_date).strftime("%Y-%m-%d"),
        "pool": pool_name,
        "scenario": scenario_name,
        "measure_name": "R2",
        "measure_value": round(R2, 4),
        "description": "Actual Portfolio with Benchmark Return",
        "difference_description": "Portfolio mix difference",
        "attributed_difference": round(D2, 4),
    }
    R3_dict = {
        "period_start": pd.to_datetime(start_date).strftime("%Y-%m-%d"),
        "period_end": pd.to_datetime(end_date).strftime("%Y-%m-%d"),
        "pool": pool_name,
        "scenario": scenario_name,
        "measure_name": "R3",
        "measure_value": round(R3, 4),
        "description": "Actual Portfolio with Actual Return",
        "difference_description": "Actual security return difference",
        "attributed_difference": round(D3, 4),
    }
    Residual_dict = {
        "period_start": pd.to_datetime(start_date).strftime("%Y-%m-%d"),
        "period_end": pd.to_datetime(end_date).strftime("%Y-%m-%d"),
        "pool": pool_name,
        "scenario": scenario_name,
        "measure_name": "-",
        "measure_value": None,
        "description": "-",
        "difference_description": "Residual",
        "attributed_difference": round(Residual, 4),
    }

    final_list = [TWRR_dict, R1_dict, R2_dict, R3_dict, Residual_dict]
    portfolio_attribution_df = pd.DataFrame(final_list)
    output_dict = {
        "Portfolio_attribution": portfolio_attribution_df.to_dict("records"),
        "Imtermediate_output": intermediate_table.to_dict("records"),
    }
    return output_dict
