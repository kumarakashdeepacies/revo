import json
import multiprocessing

from joblib import Parallel, delayed
import numpy as np
import pandas as pd

from kore_investment.users.computation_studio_lib import Valuation_Models
from kore_investment.users.computations.db_centralised_function import read_data_func, data_handling
import pyarrow as pa
import pyarrow.parquet as pq
import random
from pathlib import Path
import os
from config.settings.base import DISKSTORE_PATH
from numba import float64, guvectorize, int64, njit, void
from datetime import date, datetime
import logging

cpu_total_count = multiprocessing.cpu_count() - 1
def applyParallel(
                config_dict,
                column_index_dict,
                pos_data,
                curve_repo_data,
                curve_components_data,
                cs_curve_repo_data,
                cs_curve_components_data,
                vol_repo_data,
                vol_components_data,
                holiday_calendar,
                currency_data,
                NMD_adjustments,
                repayment_schedule,
                func,
                vix_data,
                cf_analysis_id,
                cashflow_uploaded_data,
                underlying_position_data,
                custom_daycount_conventions,
                dpd_ruleset,
                overdue_bucketing_data,
                dpd_schedule,
                product_holiday_code,
                request,
                market_data
            ):
                retLst, cashflow_model_results, measures_output = zip(
                    *Parallel(n_jobs=cpu_total_count)(
                        delayed(func)(
                            row,
                            column_index_dict,
                            config_dict,
                            curve_repo_data,
                            curve_components_data,
                            cs_curve_repo_data,
                            cs_curve_components_data,
                            vol_repo_data,
                            vol_components_data,
                            holiday_calendar,
                            currency_data,
                            NMD_adjustments,
                            repayment_schedule,
                            market_data,
                            vix_data,
                            cf_analysis_id,
                            cashflow_uploaded_data,
                            underlying_position_data,
                            custom_daycount_conventions,
                            dpd_ruleset,
                            overdue_bucketing_data,
                            dpd_schedule,
                            product_holiday_code,
                            request,
                        )
                        for row in pos_data
                    )
                )
                cashflow_output = pd.concat(cashflow_model_results, ignore_index=True)
                measures_output = pd.concat(measures_output, ignore_index=True)
                final_output = pd.DataFrame(retLst)
                return final_output, cashflow_output, measures_output

def final_valuation_fn(config_dict, request, data=None):
    logging.warning(f"ENTERED PORTFOLIO VALUATION FUNCTION")
    start_date = datetime.now()
    request_user = request.user.username
    valuation_date = config_dict["inputs"]["Valuation_Date"]["val_date"]
    cf_analysis_id = config_dict["inputs"]["CF_Analysis_Id"]["cf_analysis_id"]
    val_date_filtered = data["positions_table"].copy()
    if data["nmd_data"] is not None:
        NMD_adjustments = data["nmd_data"].copy()
    else:
        NMD_adjustments = pd.DataFrame()
    if data["product_data"] is not None:
        product_data = data["product_data"].copy()
    else:
        product_data = pd.DataFrame()
    if data["dpd_data"] is not None:
        dpd_ruleset = data["dpd_data"].copy()
    else:
        dpd_ruleset = pd.DataFrame()
    if data["overdue_data"] is not None:
        overdue_bucketing_data = data["overdue_data"].copy()
    else:
        overdue_bucketing_data = pd.DataFrame()
    if data["dpd_schedule"] is not None:
        dpd_schedule = data["dpd_schedule"].copy()
    else:
        dpd_schedule = pd.DataFrame()
    if data["cashflow_data_uploaded"] is not None:
        cashflow_uploaded_data = data["cashflow_data_uploaded"].copy()
    else:
        cashflow_uploaded_data = pd.DataFrame()
    if data["market_data"] is not None and len(data["market_data"])>0:
        mtm_data = data["market_data"].copy()
    else:
        mtm_data = pd.DataFrame(columns=['extract_date','security_identifier','asset_class','quoted_price','yield','volatility'])
    
    if data["repayment_data"] is not None:
        repayment_schedule = data["repayment_data"].copy()
    else:
        repayment_schedule = pd.DataFrame()
    if data["product_model_mapper_table"] is not None:
        product_model_mapper = data["product_model_mapper_table"].copy()
    else:
        product_model_mapper = pd.DataFrame()

    if (
        "hierarchy_name" in val_date_filtered.columns
        and "product_variant_name" not in val_date_filtered.columns
    ):
        val_date_filtered.rename(columns={"hierarchy_name": "product_variant_name"}, inplace=True)
    data = None
    del data
    val_date_filtered = val_date_filtered[
        val_date_filtered["reporting_date"] == pd.to_datetime(valuation_date)
    ]

    product_model_mapper = product_model_mapper.set_index("product_variant_name").to_dict()["model_code"]

    val_date_filtered["model_code"] = val_date_filtered["product_variant_name"].replace(product_model_mapper)

    holiday_code_generation = np.vectorize(holiday_code_generator)

    weekday_data = json.dumps(
        read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "week_definition",
                    "Columns": ["id", "day"],
                },
                "condition": [],
            },
        ).to_dict("list")
    )

    product_holiday_code = pd.concat(
        holiday_code_generation(product_data.fillna("None").to_dict("records"), weekday_data),
        ignore_index=True,
    )

    curve_repo_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "ir_curve_repository",
                "Columns": [
                    "configuration_date",
                    "curve_name",
                    "curve_components",
                    "interpolation_algorithm",
                    "extrapolation_algorithm",
                    "compounding_frequency_output",
                ],
            },
            "condition": [
                {
                    "column_name": "configuration_date",
                    "condition": "Smaller than equal to",
                    "input_value": str(valuation_date),
                    "and_or": "",
                },
            ],
        },
    )
    curve_repo_data = curve_repo_data.sort_values("configuration_date", ascending=False).drop_duplicates(
        subset=["curve_name"]
    )
    curve_components_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "ir_curve_components",
                "Columns": ["id", "curve_component", "tenor_value", "tenor_unit"],
            },
            "condition": [],
        },
    )
    if any(
        model in ["M027", "M014", "M015", "M016", "M017", "M040", "M041", "M042", "M043", "M044"]
        for model in val_date_filtered["model_code"].tolist()
    ):
        vol_repo_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "volatility_surface_repository",
                    "Columns": [
                        "configuration_date",
                        "vol_surface_name",
                        "vol_surface_components",
                        "interpolation_smile",
                        "interpolation_tenor",
                        "extrapolation_smile",
                        "extrapolation_tenor",
                        "tenor_interpolation_parameter",
                        "smile_interpolation_parameter",
                        "asset_class",
                    ],
                },
                "condition": [
                    {
                        "column_name": "configuration_date",
                        "condition": "Smaller than equal to",
                        "input_value": str(valuation_date),
                        "and_or": "",
                    },
                ],
            },
        )
        vol_repo_data = vol_repo_data.sort_values("configuration_date", ascending=False).drop_duplicates(
            subset=["vol_surface_name"]
        )
        vol_components_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "volatility_surface_components",
                    "Columns": ["id", "surface_component", "tenor_value", "tenor_unit", "delta"],
                },
                "condition": [],
            },
        )
    else:
        vol_repo_data = pd.DataFrame()
        vol_components_data = pd.DataFrame()

    cs_curve_repo_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "cs_curve_repository",
                "Columns": [
                    "configuration_date",
                    "curve_name",
                    "curve_components",
                    "interpolation_algorithm",
                    "extrapolation_algorithm",
                ],
            },
            "condition": [
                {
                    "column_name": "configuration_date",
                    "condition": "Smaller than equal to",
                    "input_value": str(valuation_date),
                    "and_or": "",
                },
            ],
        },
    )
    cs_curve_repo_data = cs_curve_repo_data.sort_values(
        "configuration_date", ascending=False
    ).drop_duplicates(subset=["curve_name"])
    cs_curve_components_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "cs_curve_components",
                "Columns": ["id", "curve_component", "tenor_value", "tenor_unit"],
            },
            "condition": [],
        },
    )
    custom_daycount_conventions = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "custom_daycount_conventions",
                "Columns": [
                    "convention_name",
                    "numerator",
                    "denominator",
                    "numerator_adjustment",
                    "denominator_adjustment",
                ],
            },
            "condition": [],
        },
    )
    if "strike_price" in val_date_filtered.columns and "put_call_type" in val_date_filtered.columns:
        underlying_position_data = val_date_filtered.loc[
            :,
            [
                "underlying_position_id",
                "unique_reference_id",
                "maturity_date",
                "reporting_date",
                "strike_price",
                "put_call_type",
                "product_variant_name",
            ],
        ]
    else:
        underlying_position_data = pd.DataFrame(
            columns=[
                "underlying_position_id",
                "unique_reference_id",
                "maturity_date",
                "reporting_date",
                "strike_price",
                "put_call_type",
                "product_variant_name",
            ]
        )

    position_security_id = (
        val_date_filtered[val_date_filtered["unique_reference_id"].notna()]["unique_reference_id"]
        .unique()
        .tolist()
    )
    if (val_date_filtered["underlying_position_id"].str.contains(",")).any():
        a = val_date_filtered["underlying_position_id"].unique().tolist()
        b = set()
        for i in range(len(a)):
            temp = a[i].split(",")
            for j in temp:
                b.add(j)
        c = list(b)
        position_security_id += c
    else:
        position_security_id += (
            val_date_filtered[val_date_filtered["underlying_position_id"].notna()]["underlying_position_id"]
            .unique()
            .tolist()
        )
    position_security_id += curve_components_data["curve_component"].unique().tolist()
    position_security_id += (
        underlying_position_data[underlying_position_data["underlying_position_id"].notna()][
            "underlying_position_id"
        ]
        .unique()
        .tolist()
    )
    position_security_id += cs_curve_components_data["curve_component"].unique().tolist()
    mtm_data = pd.concat(
        (
            mtm_data.loc[mtm_data["security_identifier"].isin(position_security_id)],
            mtm_data.loc[mtm_data["asset_class"] == "FX"],
        ),
        ignore_index=True,
    )
    mtm_data["extract_date"] = mtm_data["extract_date"].astype('datetime64[ns]')
    holiday_calendar = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Holiday_Calendar_Repository",
                "Columns": ["holiday_calendar", "holiday_date"],
            },
            "condition": [],
        },
    )
    currency_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "CurrencyMaster",
                "Columns": ["currency_code", "default_holiday_calendar"],
            },
            "condition": [],
        },
    )

    vix_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "vix",
                "Columns": ["extract_date", "vix"],
            },
            "condition": [
                {
                    "column_name": "extract_date",
                    "condition": "Equal to",
                    "input_value": str(valuation_date),
                    "and_or": "",
                },
            ],
        },
    )

    table_cols = val_date_filtered.columns
    index_list = []

    def col_index_func(table_cols):
        index_list.append(val_date_filtered.columns.get_loc(table_cols))

    np.vectorize(col_index_func)(table_cols)
    index_list.pop(0)

    column_index_dict = dict(zip(table_cols, index_list))
    
        
    val_date_filtered_deposits_aggregate_model = val_date_filtered.loc[
        val_date_filtered["model_code"].isin(["M048", "M049"])
    ]

    val_date_filtered_cashflow_uploaded_aggregate_model = val_date_filtered.loc[
        val_date_filtered["model_code"].isin(["M053"])
    ]
    final_output_main = pd.DataFrame()
    run_id = "run_" + str(random.random()).replace(".","")
    chunk_size = 10**5
    
    if len(val_date_filtered_deposits_aggregate_model) > 0:
        val_date_filtered_deposits_CA_aggregated = val_date_filtered_deposits_aggregate_model.loc[
            val_date_filtered_deposits_aggregate_model["model_code"] == "M048"
        ]
        if len(val_date_filtered_deposits_CA_aggregated) > 0:
            val_date_filtered_new_CA_position = val_date_filtered_deposits_CA_aggregated.head(1)
            base_rate_CA = (
                sum(
                    val_date_filtered_deposits_CA_aggregated["outstanding_amount"]
                    * val_date_filtered_deposits_CA_aggregated["base_rate"]
                )
                / val_date_filtered_deposits_CA_aggregated["outstanding_amount"].sum()
            )
            fixed_spread_CA = (
                sum(
                    val_date_filtered_deposits_CA_aggregated["outstanding_amount"]
                    * val_date_filtered_deposits_CA_aggregated["fixed_spread"]
                )
                / val_date_filtered_deposits_CA_aggregated["outstanding_amount"].sum()
            )
            val_date_filtered_new_CA_position = val_date_filtered_new_CA_position.assign(
                outstanding_amount=val_date_filtered_deposits_CA_aggregated["outstanding_amount"].sum(),
                position_id=val_date_filtered_deposits_CA_aggregated["product_variant_name"]
                .iloc[0]
                .replace(" ", "_")
                + "_Aggregated",
                unique_reference_id=val_date_filtered_deposits_CA_aggregated["product_variant_name"]
                .iloc[0]
                .replace(" ", "_")
                + "_Aggregated",
                model_code="M021",
                base_rate=base_rate_CA,
                fixed_spread=fixed_spread_CA,
                accrued_interest=val_date_filtered_deposits_CA_aggregated["accrued_interest"].sum(),
            )
            val_date_filtered = pd.concat(
                [
                    val_date_filtered.loc[~(val_date_filtered["model_code"].isin(["M048"]))],
                    val_date_filtered_new_CA_position,
                ],
                ignore_index=True,
            )

        val_date_filtered_deposits_SA_aggregated = val_date_filtered_deposits_aggregate_model.loc[
            val_date_filtered_deposits_aggregate_model["model_code"] == "M049"
        ]
        if len(val_date_filtered_deposits_SA_aggregated) > 0:
            val_date_filtered_new_SA_position = val_date_filtered_deposits_SA_aggregated.head(1)
            base_rate_SA = (
                sum(
                    val_date_filtered_deposits_SA_aggregated["outstanding_amount"]
                    * val_date_filtered_deposits_SA_aggregated["base_rate"]
                )
                / val_date_filtered_deposits_SA_aggregated["outstanding_amount"].sum()
            )
            fixed_spread_SA = (
                sum(
                    val_date_filtered_deposits_SA_aggregated["outstanding_amount"]
                    * val_date_filtered_deposits_SA_aggregated["fixed_spread"]
                )
                / val_date_filtered_deposits_SA_aggregated["outstanding_amount"].sum()
            )
            val_date_filtered_new_SA_position = val_date_filtered_new_SA_position.assign(
                outstanding_amount=val_date_filtered_deposits_SA_aggregated["outstanding_amount"].sum(),
                position_id=val_date_filtered_deposits_SA_aggregated["product_variant_name"]
                .iloc[0]
                .replace(" ", "_")
                + "_Aggregated",
                unique_reference_id=val_date_filtered_deposits_SA_aggregated["product_variant_name"]
                .iloc[0]
                .replace(" ", "_")
                + "_Aggregated",
                model_code="M021",
                base_rate=base_rate_SA,
                fixed_spread=fixed_spread_SA,
                accrued_interest=val_date_filtered_deposits_SA_aggregated["accrued_interest"].sum(),
            )
            val_date_filtered = pd.concat(
                [
                    val_date_filtered.loc[~(val_date_filtered["model_code"].isin(["M049"]))],
                    val_date_filtered_new_SA_position,
                ],
                ignore_index=True,
            )

    
    pos = 0
    if len(val_date_filtered_cashflow_uploaded_aggregate_model)>0:
        for chunk_pos_data_cashflow in np.array_split(val_date_filtered, len(val_date_filtered)/chunk_size if len(val_date_filtered)>chunk_size else 1):
            logging.warning(f"ENTERED M053 AGGREGATE MODEL - {pos}")
            cashflow_data_filtered = cashflow_uploaded_data.loc[cashflow_uploaded_data['position_id'].isin(chunk_pos_data_cashflow['position_id'])]
            cashflow_data_filtered = pd.merge(cashflow_data_filtered, chunk_pos_data_cashflow[['position_id','discount_daycount_convention','discounting_curve','credit_spread_rate','credit_spread_curve','fixed_or_float_flag','next_reset_date','quantity']], left_on='position_id', right_on='position_id', how='left')
            chunk_pos_data  = []
            del chunk_pos_data
            cashflow_data_filtered['quantity'] = cashflow_data_filtered['quantity'].fillna(1) 
            cashflow_data_filtered["time_to_maturity"] = cashflow_data_filtered["time_to_maturity"].to_numpy(dtype="float64")

            logging.warning(f"M053 - CASHFLOW DATA READY FOR PROCESSING")

            discount_curves = cashflow_data_filtered['discounting_curve'].unique().tolist()
            curve_component_transformation_vect = np.vectorize(curve_component_transformation)
            curve_component_transformation_result = curve_component_transformation_vect(
                curve_repo_data.loc[curve_repo_data['curve_name'].isin(discount_curves)].to_dict("records")
            )
            curve_data = pd.concat(curve_component_transformation_result, ignore_index=True)
            del curve_component_transformation_result
            curve_data = curve_data.merge(
                curve_components_data, left_on="curve_components", right_on="id", how="left"
            ).drop(columns=["curve_components", "id"])
            curve_data["tenor"] = np.where(
                curve_data["tenor_unit"] == "D",
                curve_data["tenor_value"] / 365.25,
                np.where(curve_data["tenor_unit"] == "M", curve_data["tenor_value"] / 12, curve_data["tenor_value"]),
            )
            curve_data = (
                curve_data.merge(
                    mtm_data.loc[
                        mtm_data["extract_date"]
                        == pd.to_datetime(valuation_date, dayfirst=True),
                        ["security_identifier", "quoted_price"],
                    ],
                    left_on="curve_component",
                    right_on="security_identifier",
                    how="left",
                )
                .drop(columns=["security_identifier"])
                .rename(columns={"quoted_price": "rate"})
            )
            curve_data.sort_values(by=["curve_name", "tenor"], inplace=True)

            credit_spread_curves = cashflow_data_filtered.loc[(cashflow_data_filtered['credit_spread_curve'].notna())&(~cashflow_data_filtered['credit_spread_curve'].isin(['None','',None,'-'])),"credit_spread_curve"].unique().tolist()
            if len(credit_spread_curves)>0:
                cs_curve_component_transformation_result = curve_component_transformation_vect(
                    cs_curve_repo_data.loc[cs_curve_repo_data['curve_name'].isin(credit_spread_curves)].to_dict("records")
                )
                cs_curve_data = pd.concat(cs_curve_component_transformation_result, ignore_index=True)
                del cs_curve_component_transformation_result
                cs_curve_data = cs_curve_data.merge(
                    cs_curve_components_data, left_on="curve_components", right_on="id", how="left"
                ).drop(columns=["curve_components", "id"])
                cs_curve_data["tenor"] = np.where(
                    cs_curve_data["tenor_unit"] == "D",
                    cs_curve_data["tenor_value"] / 365.25,
                    np.where(
                        cs_curve_data["tenor_unit"] == "M",
                        cs_curve_data["tenor_value"] / 12,
                        cs_curve_data["tenor_value"],
                    ),
                )
                credit_spread_data = (
                    cs_curve_data.merge(
                        mtm_data.loc[
                            mtm_data["extract_date"]
                            == pd.to_datetime(valuation_date, dayfirst=True),
                            ["security_identifier", "quoted_price"],
                        ],
                        left_on="curve_component",
                        right_on="security_identifier",
                        how="left",
                    )
                    .drop(columns=["security_identifier"])
                    .rename(columns={"quoted_price": "spread_value", "curve_name": "credit_spread_curve_name"})
                )
                del cs_curve_data
                credit_spread_data.sort_values(by=["credit_spread_curve_name", "tenor"], inplace=True)
            else:
                credit_spread_data = pd.DataFrame()

            logging.warning(f"M053 - MARKET DATA READY FOR PROCESSING")
            
            cashflow_data_after_discount_rate = []
            for i in discount_curves:
                tenor = curve_data.loc[curve_data['curve_name'] == i,"tenor"].to_numpy(dtype="float64")
                rates = curve_data.loc[curve_data['curve_name'] == i,"rate"].to_numpy(dtype="float64")
                interpolation_algorithm = curve_data.loc[curve_data['curve_name'] == i,"interpolation_algorithm"].iloc[0]
                extrapolation_algorithm = curve_data.loc[curve_data['curve_name'] == i,"extrapolation_algorithm"].iloc[0]
                curve_compounding_frequency = curve_data["compounding_frequency_output"].iloc[0]
                cashflow_data_filtered_curve = cashflow_data_filtered.loc[cashflow_data_filtered['discounting_curve']==i]
                cashflow_data_filtered_curve.loc[:,"discount_rate"] = cashflow_data_filtered_curve['time_to_maturity'].apply(discount_rate_calc, args=(tenor,rates,interpolation_algorithm,extrapolation_algorithm))
                cashflow_data_filtered_curve.loc[:,"curve_compounding_frequency"] = curve_compounding_frequency
                cashflow_data_after_discount_rate.append(cashflow_data_filtered_curve)
            
            cashflow_data_after_discount_rate = pd.concat(cashflow_data_after_discount_rate, ignore_index=True)
            cashflow_data_filtered = []
            del cashflow_data_filtered
            cashflow_data_after_discount_rate['spread_rate_curve'] = np.where(cashflow_data_after_discount_rate['credit_spread_rate'].notna(),cashflow_data_after_discount_rate['credit_spread_rate'],np.where(((cashflow_data_after_discount_rate["credit_spread_curve"].isin([np.nan,None,'None','-','']))|~(cashflow_data_after_discount_rate["credit_spread_curve"].isin(credit_spread_curves))),0,"Curve based"))
            cashflow_data_after_discount_rate.loc[cashflow_data_after_discount_rate['spread_rate_curve']!="Curve based",'spread_rate'] = cashflow_data_after_discount_rate.loc[cashflow_data_after_discount_rate['spread_rate_curve']!="Curve based",'spread_rate_curve']
            cashflow_data_after_discount_and_credit_spread_rate = [cashflow_data_after_discount_rate.loc[cashflow_data_after_discount_rate['spread_rate_curve']!="Curve based"]]
            for i in credit_spread_curves:
                tenor = credit_spread_data.loc[credit_spread_data['credit_spread_curve_name'] == i,"tenor"].to_numpy(dtype="float64")
                rates = credit_spread_data.loc[credit_spread_data['credit_spread_curve_name'] == i,"spread_value"].to_numpy(dtype="float64")
                interpolation_algorithm = credit_spread_data.loc[credit_spread_data['credit_spread_curve_name'] == i,"interpolation_algorithm"].iloc[0]
                extrapolation_algorithm = credit_spread_data.loc[credit_spread_data['credit_spread_curve_name'] == i,"extrapolation_algorithm"].iloc[0]
                cashflow_data_after_discount_rate_credit_spread = cashflow_data_after_discount_rate.loc[(cashflow_data_after_discount_rate['spread_rate_curve']=="Curve based")&(cashflow_data_after_discount_rate['credit_spread_curve']==i)]
                if len(cashflow_data_after_discount_rate_credit_spread)>0:
                    cashflow_data_after_discount_rate_credit_spread["spread_rate"] = cashflow_data_after_discount_rate_credit_spread['time_to_maturity'].apply(discount_rate_calc, args=(tenor,rates,interpolation_algorithm,extrapolation_algorithm))
                else:
                    cashflow_data_after_discount_rate_credit_spread["spread_rate"] = 0
                cashflow_data_after_discount_and_credit_spread_rate.append(cashflow_data_after_discount_rate_credit_spread)


            final_cashflow_data = pd.concat(cashflow_data_after_discount_and_credit_spread_rate, ignore_index=True)
            final_cashflow_data['interest_rate'] = final_cashflow_data['discount_rate'] + final_cashflow_data['spread_rate'].astype('float64')
            cashflow_data_after_discount_rate = []
            del cashflow_data_after_discount_rate

            cashflow_data_after_discount_rate_credit_spread = []
            del cashflow_data_after_discount_rate_credit_spread
            
            logging.warning(f"M053 - DISCOUNT RATE CALCULATION COMPLETED")

            final_cashflow_data['interest_rate_+1bps'] = final_cashflow_data['interest_rate'] + 0.0001
            final_cashflow_data['interest_rate_-1bps'] = final_cashflow_data['interest_rate'] - 0.0001

            final_cashflow_data['discount_factor'] = final_cashflow_data.apply(lambda row: discount_factor_calculation(row), axis =1)
            final_cashflow_data['discount_factor_+1bps'] = final_cashflow_data.apply(lambda row: discount_factor_calculation_plus_1bps(row), axis =1)
            final_cashflow_data['discount_factor_-1bps'] = final_cashflow_data.apply(lambda row: discount_factor_calculation_minus_1bps(row), axis =1)
            
            final_cashflow_data['present_value'] = final_cashflow_data['cashflow']*final_cashflow_data['discount_factor'] 
            final_cashflow_data['present_value_+1bps'] = final_cashflow_data['cashflow']*final_cashflow_data['discount_factor_+1bps']
            final_cashflow_data['present_value_-1bps'] = final_cashflow_data['cashflow']*final_cashflow_data['discount_factor_-1bps']

            final_cashflow_data["pv*t"] = final_cashflow_data['present_value']*final_cashflow_data['time_to_maturity']
            
            final_cashflow_data_aggregation = final_cashflow_data.loc[final_cashflow_data['cashflow_type']!="Accrued Interest"].groupby(['position_id'])[['present_value','present_value_+1bps','present_value_-1bps','pv*t']].aggregate("sum", engine="cython").reset_index().rename(columns= {'present_value':'present_value_position','present_value_+1bps':'present_value_position_+1bps', 'present_value_-1bps':'present_value_position_-1bps','pv*t':'pv*t_position'})
            final_cashflow_data = final_cashflow_data.merge(final_cashflow_data_aggregation, left_on='position_id',right_on='position_id',how='left')
            final_cashflow_data.loc[final_cashflow_data['cashflow_type']=="Accrued Interest","present_value"] = 0
            final_cashflow_data.loc[final_cashflow_data['cashflow_type']=="Accrued Interest","discount_factor"] = 0
            final_cashflow_data["Fair Value per unit"] = final_cashflow_data["present_value_position"]/final_cashflow_data["quantity"] 
            final_cashflow_data["macaulay_duration"] = final_cashflow_data["pv*t_position"] / final_cashflow_data["present_value_position"] 
            final_cashflow_data["pv01"] = (abs(final_cashflow_data["present_value_position_+1bps"] - final_cashflow_data["present_value_position"]) + abs(final_cashflow_data["present_value_position_-1bps"] - final_cashflow_data["present_value_position"])) / 2
            final_cashflow_data["PV01 per unit"] =final_cashflow_data["pv01"]/final_cashflow_data["quantity"]
            final_cashflow_data["modified_duration"] = (10000*final_cashflow_data["pv01"])/final_cashflow_data["present_value_position"]
            
            logging.warning(f"M053 - VALUATION AND SENSITIVITY CALCULATION COMPLETED")

            cashflow_output = final_cashflow_data.loc[:,["extract_date",'transaction_date','unique_reference_id','reference_dimension','cashflow_type','cashflow_status','cashflow','time_to_maturity','discount_factor','present_value','currency','asset_liability_type','product_variant_name','fund','portfolio','entity','cohort','position_id']]
            cashflow_output["cf_analysis_id"] = cf_analysis_id
            
            final_cashflow_data.rename(columns={'present_value_position':'Fair Value','macaulay_duration':'Macaulay Duration','modified_duration':'Modified Duration','pv01':'PV01'}, inplace=True)
            final_cashflow_data_unique = final_cashflow_data.drop_duplicates(['position_id']) 
            measures_output = pd.melt(final_cashflow_data_unique, id_vars=['position_id','unique_reference_id'], value_vars=['Fair Value per unit','Fair Value','Macaulay Duration','Modified Duration','PV01'], var_name="measure_type", value_name='measure_value')
            measures_output['measure_run_date'] = datetime.now()
            measures_output['absolute_relative'] = np.where(measures_output['measure_type'].isin(['Modified Duration','Effective Duration']),"Relative","Absolute")
            measures_output = measures_output.merge(final_cashflow_data_unique[['position_id','extract_date','reference_dimension','asset_liability_type','product_variant_name','portfolio','cohort','entity']]).rename(columns={'extract_date':'valuation_date'})
            max_ttm = final_cashflow_data.groupby('position_id')['time_to_maturity'].max().reset_index().rename(columns={"time_to_maturity":'residual_maturity'})
            measures_output = measures_output.merge(max_ttm,left_on="position_id",right_on="position_id",how="left")
            max_ttm = []
            del max_ttm
            measures_output["cf_analysis_id"] = cf_analysis_id
            cashflow_output = cashflow_output.loc[cashflow_output["cashflow"].notnull()]
            if "measure_value" in measures_output.columns:
                measures_output = measures_output.loc[measures_output["measure_value"].notnull()]
            
            final_output = final_cashflow_data_unique.head(100).copy()
            final_cashflow_data_unique = []
            del final_cashflow_data_unique

            final_output.rename(columns={'unique_reference_id':"Unique_Reference_ID",'position_id':"Position_Id",'product_variant_name':"Product_Variant_Name","extract_date":"Valuation_Date", 'Fair Value per unit': 'Fair_Value_Per_Unit','Fair Value':'Total_Holding','quantity':"Quantity"}, inplace=True)
            final_output["Sensitivity"] = final_output.apply(lambda row: sensitivity_dict_generation(row), axis=1)
            final_output["Cashflow_Result"] = final_output["Position_Id"].apply(cashflow_dict_generation,cashflow_output_data=cashflow_output)
            final_output_main = pd.concat([final_output_main,final_output[['Unique_Reference_ID','Position_Id','Product_Variant_Name','Valuation_Date','Cashflow_Result', 'Fair_Value_Per_Unit','Quantity','Total_Holding','Sensitivity']]], ignore_index=True)

            logging.warning(f"M053 - ALL OUTPUT DATA GENERATION COMPLETED")

            if len(cashflow_output)>0:
                cashflow_output = pa.Table.from_pandas(cashflow_output)
                pq.write_table(cashflow_output,f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Cashflow/cashflow_output_m053_{pos}_{run_id}.parquet')

            if len(measures_output)>0:
                measures_output = pa.Table.from_pandas(measures_output)
                pq.write_table(measures_output,f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Measures/measures_output_m053_{pos}_{run_id}.parquet')

            cashflow_output = []
            measures_output = []
            final_output = []
            del cashflow_output
            del measures_output
            del final_output
            pos += 1
            logging.warning(f"M053 - PARQUET FILE CREATION COMPLETED COMPLETED")

        val_date_filtered = val_date_filtered.loc[val_date_filtered['model_code']!="M053"]

    if len(val_date_filtered)>0:
        val_date_filtered_array = np.array(val_date_filtered)
    else:
        val_date_filtered_array = []
    
    val_date_filtered = []
    del val_date_filtered
    
    func = Valuation_Models.Value_extraction_pf
    
    if len(val_date_filtered_array)>0:
        if config_dict["inputs"]["Technical_Conf"] == "Joblib":
            identifier = 0
            for chunk_pos_data in np.array_split(val_date_filtered_array, len(val_date_filtered_array)/chunk_size if len(val_date_filtered_array)>chunk_size else 1):
                if len(cashflow_uploaded_data) > 0:
                    cashflow_uploaded_data_filtered = cashflow_uploaded_data.loc[cashflow_uploaded_data["position_id"].isin(chunk_pos_data[:,column_index_dict["position_id"]])]
                else:
                    cashflow_uploaded_data_filtered = pd.DataFrame()
                final_output, cashflow_output, measures_output = applyParallel(
                    config_dict,
                    column_index_dict,
                    chunk_pos_data,
                    curve_repo_data,
                    curve_components_data,
                    cs_curve_repo_data,
                    cs_curve_components_data,
                    vol_repo_data,
                    vol_components_data,
                    holiday_calendar,
                    currency_data,
                    NMD_adjustments,
                    repayment_schedule,
                    func,
                    vix_data,
                    cf_analysis_id,
                    cashflow_uploaded_data_filtered,
                    underlying_position_data,
                    custom_daycount_conventions,
                    dpd_ruleset,
                    overdue_bucketing_data,
                    dpd_schedule,
                    product_holiday_code,
                    request,
                    mtm_data
                )
                cashflow_uploaded_data_filtered = []
                del cashflow_uploaded_data_filtered

                if "cf_analysis_id" not in cashflow_output.columns:
                    cashflow_columns = ["cf_analysis_id"] + cashflow_output.columns.tolist()
                else:
                    cashflow_columns = ["cf_analysis_id"] + cashflow_output.drop(columns=["cf_analysis_id"]).columns.tolist()

                cashflow_output["cf_analysis_id"] = cf_analysis_id
                measures_output["cf_analysis_id"] = cf_analysis_id
                cashflow_output = cashflow_output.loc[:, cashflow_columns]
                cashflow_output = cashflow_output.loc[cashflow_output["cashflow"].notnull()]
                if "measure_value" in measures_output.columns:
                    measures_output = measures_output.loc[measures_output["measure_value"].notnull()]
                
                if len(cashflow_output)>0:
                    cashflow_output = pa.Table.from_pandas(cashflow_output)
                    pq.write_table(cashflow_output,f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Cashflow/cashflow_output_{identifier}_{run_id}.parquet')

                if len(measures_output)>0:
                    measures_output = pa.Table.from_pandas(measures_output)
                    pq.write_table(measures_output,f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Measures/measures_output_{identifier}_{run_id}.parquet')

                cashflow_output = []
                measures_output = []
                del cashflow_output
                del measures_output
                identifier += 1
                if len(final_output_main) < 100:
                    final_output_main = pd.concat([final_output_main,final_output], ignore_index=True)

    cashflow_uploaded_data = []
    del cashflow_uploaded_data

    holiday_calendar = []
    del holiday_calendar
    
    currency_data = []
    del currency_data

    NMD_adjustments = []
    del NMD_adjustments

    repayment_schedule = []
    del repayment_schedule

    mtm_data = []
    del mtm_data

    underlying_position_data = []
    del underlying_position_data

    output_dict = {}

    created_date = datetime.now()
    modified_date = datetime.now()

    logging.warning(f"PREPARING FOR EXPORT")

    if config_dict['outputs']['cashflows']['save']['source'] != "":
        data_dir = Path(f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Cashflow')
        for parquet_file in data_dir.glob(f'*_{run_id}.parquet'):
            output_df = pd.read_parquet(parquet_file)
            output_df["created_by"] = request_user
            output_df["modified_by"] = request_user
            output_df["created_date"] = created_date
            output_df["modified_date"] = modified_date
            data_handling(request, output_df, config_dict['outputs']['cashflows']['save']['table'])
            os.remove(parquet_file)
            output_df = []
            del output_df

        config_dict['outputs']['cashflows']['save']['source'] = ""
        config_dict['outputs']['cashflows']['save']['table'] = ""

    if config_dict['outputs']['measures']['save']['source'] != "":
        data_dir = Path(f'{DISKSTORE_PATH}/Cashflow_Engine_Outputs/Measures')
        for parquet_file in data_dir.glob(f'*_{run_id}.parquet'):
            output_df = pd.read_parquet(parquet_file)
            output_df["created_by"] = request_user
            output_df["modified_by"] = request_user
            output_df["created_date"] = created_date
            output_df["modified_date"] = modified_date
            data_handling(request, output_df, config_dict['outputs']['measures']['save']['table'])
            os.remove(parquet_file)
            output_df = []
            del output_df

        config_dict['outputs']['measures']['save']['source'] = ""
        config_dict['outputs']['measures']['save']['table'] = ""

    output_dict["Cashflow_Output"] = []
    output_dict["Measures_Output"] = []

    logging.warning(f"ALL EXPORTS COMPLETED")

    var_plot = ""
    final_output_main["Fair_Value_Per_Unit"] = final_output_main["Fair_Value_Per_Unit"].fillna("-").astype(str)
    final_output_main["Total_Holding"] = final_output_main["Total_Holding"].fillna("-").astype(str)
    final_output_main.fillna("None", inplace=True)
    final_output_main = final_output_main.head(100)
    logging.warning(f"FINAL OUTPUTS SENT")

    logging.warning(f"TOTAL TIME TAKEN = {datetime.now() - start_date}")

    return final_output_main, output_dict, var_plot


def holiday_code_generator(product_data_row, weekday_data):
    if product_data_row["weekend_definition"] != "None":
        holiday_weekends = list(json.loads(product_data_row["weekend_definition"]).keys())
    else:
        holiday_weekends = "None"
    weekday_data = json.loads(weekday_data)
    weekday_dataframe = pd.DataFrame(weekday_data)
    if holiday_weekends != "None":
        holidays = []
        for i in holiday_weekends:
            holiday = weekday_dataframe.loc[weekday_dataframe["id"] == int(i), "day"].iloc[0]
            holidays.append(holiday)
        business_days = ""
        for j in weekday_data["day"]:
            if j in holidays:
                business_days += "0"
            else:
                business_days += "1"
    else:
        holidays = []
        business_days = "1111100"

    product_variant_name = product_data_row["product_variant_name"]
    z_spread_calculation = product_data_row["z_spread_calculation"]
    product_data_df = pd.DataFrame(
        [
            {
                "product_variant_name": product_variant_name,
                "weekend": holidays,
                "business_days": business_days,
                "z_spread_calculation": z_spread_calculation,
            }
        ]
    )
    return product_data_df

def curve_component_transformation(curve_repo_data_ind):
    curve_components = {"curve_components": list(json.loads(curve_repo_data_ind["curve_components"]).keys())}
    components_new_df = pd.DataFrame(curve_components)
    components_new_df["curve_components"] = components_new_df["curve_components"].astype("int")
    components_new_df["curve_name"] = curve_repo_data_ind["curve_name"]
    components_new_df["interpolation_algorithm"] = curve_repo_data_ind["interpolation_algorithm"]
    components_new_df["extrapolation_algorithm"] = curve_repo_data_ind["extrapolation_algorithm"]
    if "compounding_frequency_output" in curve_repo_data_ind.keys():
        components_new_df["compounding_frequency_output"] = curve_repo_data_ind[
            "compounding_frequency_output"
        ]
    del curve_components
    return components_new_df

def daycount_convention_code(daycount_convention):
    if daycount_convention in ["30/360_Bond_Basis", "30/360"]:
        c = 1
        return c
    elif daycount_convention == "30/360_US":
        c = 2
        return c
    elif daycount_convention == "30E/360":
        c = 3
        return c
    elif daycount_convention == "30E/360_ISDA":
        c = 4
        return c
    elif daycount_convention == "30E+/360_ISDA":
        c = 5
        return c
    elif daycount_convention == "ACT/360":
        c = 6
        return c
    elif daycount_convention in ["ACT/365", "ACTUAL/365", "Act/365"]:
        c = 7
        return c
    elif daycount_convention == "ACT/365L":
        c = 8
        return c
    elif daycount_convention == "ACT/365A":
        c = 9
        return c
    elif daycount_convention == "NL/365":
        c = 10
        return c
    elif daycount_convention == "ACT/ACT_ISDA":
        c = 11
        return c
    elif daycount_convention == "ACT/ACT_ICMA":
        c = 12
        return c
    elif daycount_convention == "Business/252":
        c = 13
        return c
    elif daycount_convention in ["ACT/ACT", "ACTUAL/ACTUAL"]:
        c = 14
        return c
    else:
        return daycount_convention

def discount_rate_calc(ttm,tenor,rates,interpolation_algorithm,extrapolation_algorithm):
    if interpolation_algorithm == "Linear":
        calculated_rate = linearinterp(tenor, rates, np.float64(ttm))
        if calculated_rate is None:
            if extrapolation_algorithm == "Linear":
                calculated_rate = linearexterp(tenor, rates, np.float64(ttm))
            else:
                calculated_rate = flatexterp(tenor, rates, np.float64(ttm))
        else:
            calculated_rate = calculated_rate
    return calculated_rate

def discount_factor_calculation(row):
    if row["curve_compounding_frequency"] in ["Continuous", "continuous", "continuously"]:
        df = np.exp(-row["time_to_maturity"] * row["interest_rate"])
    elif row["curve_compounding_frequency"] in ["monthly", "Monthly"]:
        df = np.power(1 + row["interest_rate"] / 12, -12 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["quarterly", "Quarterly"]:
        df = np.power(1 + row["interest_rate"] / 4, -4 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["semi-annualised", "Semi-Annual", "semi-annually"]:
        df = np.power(1 + row["interest_rate"] / 2, -2 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["bi-annual", "Bi-Annual", "bi-annually"]:
        df = np.power(1 + row["interest_rate"] / 0.5, -0.5 * row["time_to_maturity"])
    else:
        df = np.power(1 + row["interest_rate"], -row["time_to_maturity"])
    return df

def discount_factor_calculation_plus_1bps(row):
    if row["curve_compounding_frequency"] in ["Continuous", "continuous", "continuously"]:
        df = np.exp(-row["time_to_maturity"] * row["interest_rate_+1bps"])
    elif row["curve_compounding_frequency"] in ["monthly", "Monthly"]:
        df = np.power(1 + row["interest_rate_+1bps"] / 12, -12 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["quarterly", "Quarterly"]:
        df = np.power(1 + row["interest_rate_+1bps"] / 4, -4 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["semi-annualised", "Semi-Annual", "semi-annually"]:
        df = np.power(1 + row["interest_rate_+1bps"] / 2, -2 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["bi-annual", "Bi-Annual", "bi-annually"]:
        df = np.power(1 + row["interest_rate_+1bps"] / 0.5, -0.5 * row["time_to_maturity"])
    else:
        df = np.power(1 + row["interest_rate_+1bps"], -row["time_to_maturity"])
    return df

def discount_factor_calculation_minus_1bps(row):
    if row["curve_compounding_frequency"] in ["Continuous", "continuous", "continuously"]:
        df = np.exp(-row["time_to_maturity"] * row["interest_rate_-1bps"])
    elif row["curve_compounding_frequency"] in ["monthly", "Monthly"]:
        df = np.power(1 + row["interest_rate_-1bps"] / 12, -12 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["quarterly", "Quarterly"]:
        df = np.power(1 + row["interest_rate_-1bps"] / 4, -4 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["semi-annualised", "Semi-Annual", "semi-annually"]:
        df = np.power(1 + row["interest_rate_-1bps"] / 2, -2 * row["time_to_maturity"])
    elif row["curve_compounding_frequency"] in ["bi-annual", "Bi-Annual", "bi-annually"]:
        df = np.power(1 + row["interest_rate_-1bps"] / 0.5, -0.5 * row["time_to_maturity"])
    else:
        df = np.power(1 + row["interest_rate_-1bps"], -row["time_to_maturity"])
    return df

# linear interpolation
@njit(cache=True, fastmath=True)
def linearinterp(x, y, independent_var_value):
    n = len(x)
    for j in range(1, n):
        if (x[j - 1]) <= independent_var_value <= (x[j]):
            return y[j - 1] + ((y[j] - y[j - 1]) * (independent_var_value - x[j - 1]) / (x[j] - x[j - 1]))


# linear extrapolation
@njit(cache=True, fastmath=True)
def linearexterp(x, y, independent_var_value):
    if independent_var_value > (x[-1]):
        return y[-1] + (independent_var_value - x[-1]) * (y[-1] - y[-2]) / (x[-1] - x[-2])
    elif independent_var_value < x[0]:
        return y[0] + (independent_var_value - x[0]) * (y[1] - y[0]) / (x[1] - x[0])


# cubic spline
def cubicspline(x, y, independent_var_value):
    check = CubicSpline(x, y)
    return check(independent_var_value)


@njit(cache=True, fastmath=True)
def flatexterp(x, y, independent_var_value):
    if independent_var_value > (x[-1]):
        return y[-1]
    elif independent_var_value < x[0]:
        return y[0]


@guvectorize([void(float64[:], float64[:], float64, float64[:])], "(n),(n),()->()")
def linforward(x, y, independent_var_value, result):
    n = len(x)
    for j in range(1, n):
        if (x[j - 1]) < independent_var_value < (x[j]):
            forward0 = (x[j] * y[j] - x[j - 1] * y[j - 1]) / (x[j] - x[j - 1])
            forward1 = (x[j + 1] * y[j + 1] - x[j] * y[j]) / (x[j + 1] - x[j])
            interpolated_forward = forward0 + (
                (forward1 - forward0) * (independent_var_value - x[j - 1]) / (x[j] - x[j - 1])
            )

            result[:] = (
                y[j - 1] * x[j - 1] + interpolated_forward * (independent_var_value - x[j - 1])
            ) / independent_var_value


# piecewise linear
@njit(cache=True, fastmath=True)
def bilinearint(x, y, f, x0, y0):
    w = []
    n = len(x)
    xu = min(c for c in x if c >= x0)
    xl = max(d for d in x if d <= x0)
    yu = min(g for g in y if g >= y0)
    yl = max(h for h in y if h <= y0)
    for j in range(0, n):
        if xl <= x[j] <= xu and yl <= y[j] <= yu:
            w.append([x[j], y[j], f[j]])
    return (
        (w[0][2] * (w[2][0] - x0) * (w[1][1] - y0))
        + (w[2][2] * (x0 - w[0][0]) * (w[1][1] - y0))
        + (w[1][2] * (w[2][0] - x0) * (y0 - w[0][1]))
        + (w[3][2] * (x0 - w[0][0]) * (y0 - w[0][1]))
    ) / ((w[2][0] - w[0][0]) * (w[1][1] - w[0][1]))

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.datetime64):
            return str(obj)
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return super().default(obj)

def cashflow_dict_generation(position_id, cashflow_output_data):
    cashflow_dict = json.dumps(cashflow_output_data.loc[cashflow_output_data['position_id']==position_id].replace("", "-").fillna("-").to_dict("records"), cls=NpEncoder)
    return cashflow_dict

def sensitivity_dict_generation(sensitivity_output_data):
    sensitivity_dict = json.dumps([{"Macaulay Duration":sensitivity_output_data["Macaulay Duration"],"Modified Duration":sensitivity_output_data["Modified Duration"],"PV01 per unit":sensitivity_output_data["PV01 per unit"]}])
    return sensitivity_dict

