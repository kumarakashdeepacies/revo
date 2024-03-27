curve_repo_data = Data1.copy()
curve_components_data = Data2.copy()
mtm_data = Data3.copy()
mtm_data = mtm_data.loc[mtm_data["security_identifier"].isin(curve_components_data["curve_component"])]


def curve_component_transformation(curve_repo_data_ind):
    curve_components = {"curve_components": list(json.loads(curve_repo_data_ind["curve_components"]).keys())}
    components_new_df = pd.DataFrame(curve_components)
    components_new_df["curve_components"] = components_new_df["curve_components"].astype("int")
    components_new_df["curve_name"] = curve_repo_data_ind["curve_name"]
    components_new_df["interpolation_algorithm"] = curve_repo_data_ind["interpolation_algorithm"]
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
    del curve_components
    return components_new_df


curve_component_transformation_vect = np.vectorize(curve_component_transformation)
curve_component_transformation_result = curve_component_transformation_vect(
    curve_repo_data.to_dict("records")
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
        mtm_data.loc[:, ["security_identifier", "quoted_price"]],
        left_on="curve_component",
        right_on="security_identifier",
        how="left",
    )
    .drop(columns=["security_identifier"])
    .rename(columns={"quoted_price": "rate"})
)
curve_data.sort_values(by=["curve_name", "tenor"], inplace=True)
curve_data["rate"] = curve_data["rate"] * 100
curve_data["tenor_concat"] = curve_data["tenor_value"].astype(str) + curve_data["tenor_unit"]
output_data = curve_data
