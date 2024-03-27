import json

import numpy as np
import pandas as pd

from kore_investment.users.computation_studio_lib import OIS_Bootstrapping


def curve_component_transformation(curve_repo_data_ind):
    curve_components = {"curve_components": list(json.loads(curve_repo_data_ind["curve_components"]).keys())}
    components_new_df = pd.DataFrame(curve_components)
    components_new_df["curve_components"] = components_new_df["curve_components"].astype("int")
    components_new_df["configuration_date"] = curve_repo_data_ind["configuration_date"]
    components_new_df["curve_name"] = curve_repo_data_ind["curve_name"]
    components_new_df["interpolation_algorithm"] = curve_repo_data_ind["interpolation_algorithm"]
    components_new_df["extrapolation_algorithm"] = curve_repo_data_ind["extrapolation_algorithm"]
    components_new_df["bootstrap_algorithm"] = curve_repo_data_ind["bootstrap_algorithm"]
    components_new_df["currency"] = curve_repo_data_ind["currency"]
    components_new_df["bootstrap_short_term_tenor_limit"] = curve_repo_data_ind[
        "bootstrap_short_term_tenor_limit"
    ]
    components_new_df["bootstrap_medium_term_tenor_limit"] = curve_repo_data_ind[
        "bootstrap_medium_term_tenor_limit"
    ]
    components_new_df["funding_spread"] = curve_repo_data_ind["funding_spread"]
    components_new_df["day_count"] = curve_repo_data_ind["day_count"]
    components_new_df["compounding_frequency_st_tenor"] = curve_repo_data_ind[
        "compounding_frequency_st_tenor"
    ]
    components_new_df["compounding_frequency_after_st_tenor"] = curve_repo_data_ind[
        "compounding_frequency_after_st_tenor"
    ]
    components_new_df["compounding_frequency_output"] = curve_repo_data_ind["compounding_frequency_output"]
    del curve_components
    return components_new_df


def curve_data_preprocessing(data, config_dict, request_user):
    ext_date = pd.to_datetime(config_dict["inputs"]["option_config"]["Extraction Date"])
    if "market_data" in data.keys():
        mtm_data = data["market_data"]
    if "curve_components_data" in data.keys():
        curve_components_data = data["curve_components_data"]
    if "curve_data" in data.keys():
        curve_data = data["curve_data"]
    mtm_data = mtm_data.loc[
        (mtm_data["security_identifier"].isin(curve_components_data["curve_component"].tolist()))
        & (mtm_data["extract_date"] == ext_date)
    ]
    curve_component_transformation_vect = np.vectorize(curve_component_transformation)
    curve_component_transformation_result = curve_component_transformation_vect(curve_data.to_dict("records"))
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
            mtm_data.loc[:, ["security_identifier", "quoted_price"]],
            left_on="curve_component",
            right_on="security_identifier",
            how="left",
        )
        .drop(columns=["security_identifier"])
        .rename(columns={"quoted_price": "rate"})
    )
    curve_data.sort_values(by=["configuration_date", "curve_name", "tenor"], inplace=True)
    curve_data["rate"] = curve_data["rate"] * 100
    curve_data["tenor_concat"] = curve_data["tenor_value"].astype(str) + curve_data["tenor_unit"]
    output_data_multiple = []
    zero_curve_quotes_final = pd.DataFrame()
    curve_data["unique_id"] = (
        curve_data["curve_name"].replace(" ", "_", regex=True)
        + "_"
        + curve_data["configuration_date"].astype(str)
    )
    unique_list = curve_data["unique_id"].unique().tolist()
    for i in unique_list:
        curve_data_filtered = curve_data.loc[curve_data["unique_id"] == i]
        bootstrap_algorithm = curve_data_filtered["bootstrap_algorithm"].iloc[0]
        if bootstrap_algorithm in ["GSEC Bond Curve Bootstrapping", "OIS Curve Bootstrapping"]:
            oisb = OIS_Bootstrapping.OIS_Bootstrapping()
            tenor = "tenor_concat"
            ytm = "rate"
            method = "fbil"
            st_tenor = curve_data_filtered["bootstrap_short_term_tenor_limit"].iloc[0]
            cf_pre_st = curve_data_filtered["compounding_frequency_st_tenor"].iloc[0]
            cf_post_st = curve_data_filtered["compounding_frequency_after_st_tenor"].iloc[0]
            output_cf = curve_data_filtered["compounding_frequency_output"].iloc[0]
            currency = curve_data_filtered["currency"].iloc[0]
            interpolation_algorithm = curve_data_filtered["interpolation_algorithm"].iloc[0]
            extrapolation_algorithm = curve_data_filtered["extrapolation_algorithm"].iloc[0]
            configuration_date = curve_data_filtered["configuration_date"].iloc[0]
            fs = curve_data_filtered["funding_spread"].iloc[0]
            curve_data_filtered = curve_data_filtered.reset_index()
            output_data, zero_curve_quotes = oisb.spot_curve(
                curve_data_filtered,
                tenor,
                ytm,
                ext_date,
                float(st_tenor),
                method,
                float(fs),
                output_cf,
                cf_pre_st,
                cf_post_st,
                curve_name=curve_data_filtered["curve_name"].iloc[0],
                curve_data="Yes",
                request_user=request_user,
                currency=currency,
                interpolation_algorithm=interpolation_algorithm,
                extrapolation_algorithm=extrapolation_algorithm,
                configuration_date=configuration_date,
            )
            zero_curve_quotes_final = zero_curve_quotes_final.append(zero_curve_quotes, ignore_index=True)
            output_data_multiple.append(output_data)
    zero_curve_quotes_final.drop_duplicates(subset=["security_identifier"], inplace=True)
    return output_data_multiple, zero_curve_quotes_final
