import base64
import io
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from kore_investment.users.computations.db_centralised_function import read_data_func


def plot_VaR(scenario_df, copula_result_df):
    total_loss = copula_result_df["Total_Loss"]
    ax = total_loss.plot.bar(rot=0, figsize=(10, 8), fontsize=12, color="grey")
    ax.set_facecolor("white")
    scenario_df.reset_index(inplace=True)
    var_plot_line = []
    counter = 0
    color_shade_list = [
        "#b58d2b",
        "#bc9840",
        "#c3a355",
        "#cbaf6a",
        "#d2ba7f",
        "#dac695",
        "#e1d1aa",
        "#e8dcbf",
        "#f0e8d4",
        "#f7f3e9",
    ]
    for var_row in scenario_df.index:
        VaR_level = scenario_df.iloc[var_row]["VaR"]
        line_plot = plt.axhline(VaR_level, color=color_shade_list[counter])
        var_plot_line.append(line_plot)
        counter += 1
        if counter == len(color_shade_list):
            counter = 0
    plt.legend(var_plot_line, scenario_df["Percentile"].tolist(), loc="upper right")
    plt.show()
    figfile = io.BytesIO()
    plt.savefig(figfile, format="png")
    plt.close()
    figdata_png = figfile.getvalue()
    figdata_png = base64.b64encode(figdata_png)
    resultplot = figdata_png.decode("utf8")
    return resultplot


def var_computation_copula(loss_data_by_risk_type, dist_parameters_by_risk_type, n, scenario_dict):
    percentiles = scenario_dict["Percentile"]
    corr_mat = loss_data_by_risk_type.corr()
    A = np.linalg.cholesky(corr_mat)
    dimensions = len(loss_data_by_risk_type.keys())
    simulated_cdf_values = []
    for i in range(n):
        Z = np.random.normal(size=dimensions)
        X = np.matmul(A, Z)
        U = stats.norm.cdf(list(X))
        simulated_cdf_values.append(U)
    copula_result_df = pd.DataFrame(simulated_cdf_values, columns=list(loss_data_by_risk_type.keys()))
    for key in copula_result_df.keys():
        best_fit_params = dist_parameters_by_risk_type[key]
        distribution = list(best_fit_params.keys())[0]
        parameters = best_fit_params[distribution]
        shape = []
        for k in parameters.keys():
            if k != "loc" and k != "scale":
                shape.append(parameters[k])
        loc = parameters["loc"]
        scale = parameters["scale"]
        if len(shape) == 0:
            copula_result_df[key] = eval(
                "stats." + distribution + f".ppf(copula_result_df[key], loc = {loc}, scale = {scale})"
            )
        if len(shape) == 1:
            copula_result_df[key] = eval(
                "stats."
                + distribution
                + f".ppf(copula_result_df[key], shape[0], loc = {loc}, scale = {scale})"
            )
        if len(shape) == 2:
            copula_result_df[key] = eval(
                "stats."
                + distribution
                + f".ppf(copula_result_df[key], shape[0], shape[1], loc = {loc}, scale = {scale})"
            )
    total_loss = np.zeros(n)
    for key in copula_result_df.keys():
        total_loss = np.add(total_loss, copula_result_df[key])
    copula_result_df["Total_Loss"] = list(total_loss)
    total_loss = np.sort(total_loss)
    VaR = np.percentile(total_loss, percentiles)
    scenario_dict["VaR"] = list(VaR)
    scenario_df = pd.DataFrame(scenario_dict)
    corr_matrix_df = pd.DataFrame(corr_mat)
    corr_matrix_df.index = corr_matrix_df.columns.tolist()
    corr_matrix_df.reset_index(inplace=True)
    var_plot = plot_VaR(scenario_df, copula_result_df)

    return {
        "Correlation_matrix": corr_matrix_df.to_dict("records"),
        "VaR_data": scenario_df.to_dict("records"),
        "VaR_plot": var_plot,
        "Simulated_data": copula_result_df.to_dict("records"),
    }


def copula_result(loss_amt_df, scenerio_dict, config_dict, request):
    usecase_list = []
    usecase_list = json.loads(config_dict["inputs"]["use_case_input"])
    usecase_list = usecase_list["val_text"]
    simulation_count = json.loads(config_dict["inputs"]["simulation_input"])
    simulation_count = int(simulation_count["val_number"])
    distribution_dict = {}
    if type(usecase_list) == str:
        usecase_list = [usecase_list]
    result_dict = {"Correlation_matrix": "", "VaR_data": "", "Simulated_data": ""}
    if len(usecase_list) > 0:
        for i in range(len(usecase_list)):
            element_df = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ml_model_repository",
                        "Columns": ["element_id", "model_output"],
                    },
                    "condition": [
                        {
                            "column_name": "use_case",
                            "condition": "Equal to",
                            "input_value": usecase_list[i],
                            "and_or": "",
                        },
                    ],
                },
            )
            if not element_df.empty:
                distribution_dict[usecase_list[i]] = json.loads(element_df["model_output"].iloc[0])
    if len(distribution_dict) > 0:
        result_dict = var_computation_copula(
            loss_amt_df, distribution_dict, n=simulation_count, scenario_dict=scenerio_dict
        )
    return result_dict
