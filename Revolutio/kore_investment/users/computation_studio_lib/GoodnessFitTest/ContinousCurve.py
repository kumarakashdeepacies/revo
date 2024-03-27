import base64
from datetime import datetime
import io
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    read_data_func,
    update_data_func,
)


class ContinousCurve:
    pass


def auto_save_config(info_dict, best_fit_parameters, request):
    request_user = request.user.username
    element_id = info_dict["element_id"]
    element_name = info_dict["element_name"]
    model_name = info_dict["model_name"]
    element_config = json.dumps(best_fit_parameters)
    use_case = info_dict["use_case"]
    element_df = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "ml_model_repository",
                "Columns": ["model_type", "element_name", "model"],
            },
            "condition": [
                {
                    "column_name": "use_case",
                    "condition": "Equal to",
                    "input_value": use_case,
                    "and_or": "AND",
                },
                {
                    "column_name": "model_type",
                    "condition": "Equal to",
                    "input_value": "Goodness of Fit Test",
                    "and_or": "",
                },
            ],
        },
    )
    if element_df.empty:
        fit_result_df = pd.DataFrame(
            columns=[
                "model_name",
                "element_id",
                "model_type",
                "model_output",
                "element_name",
                "use_case",
                "created_by",
                "created_date",
                "modified_by",
                "modified_date",
            ]
        )
        fit_result_dict = {
            "model_name": model_name,
            "element_id": element_id,
            "model_type": "Goodness of Fit Test",
            "element_name": element_name,
            "model_output": element_config,
            "use_case": use_case,
            "created_by": request_user,
            "created_date": datetime.now(),
            "modified_by": request_user,
            "modified_date": datetime.now(),
        }
        fit_result_df1 = pd.DataFrame.from_dict([fit_result_dict])
        fit_result_df = pd.concat([fit_result_df, fit_result_df1], ignore_index=True)
        data_handling(request, fit_result_df, "ml_model_repository")
    else:
        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "ml_model_repository",
                    "Columns": [
                        {
                            "column_name": "element_name",
                            "input_value": element_name,
                            "separator": ",",
                        },
                        {
                            "column_name": "model_output",
                            "input_value": element_config,
                            "separator": ",",
                        },
                        {
                            "column_name": "use_case",
                            "input_value": use_case,
                            "separator": ",",
                        },
                        {
                            "column_name": "element_id",
                            "input_value": element_id,
                            "separator": ",",
                        },
                        {
                            "column_name": "modified_date",
                            "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "separator": ",",
                        },
                        {
                            "column_name": "modified_by",
                            "input_value": request_user,
                            "separator": "",
                        },
                    ],
                },
                "condition": [
                    {
                        "column_name": "use_case",
                        "condition": "Equal to",
                        "input_value": use_case,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "model_type",
                        "condition": "Equal to",
                        "input_value": "Goodness of Fit Test",
                        "and_or": "",
                    },
                ],
            },
        )
    return "success"


def fit_continuous_function(data, cdf):
    # functionality for mapping continuous functions, and performing the kstest
    # fit data set against every probability distribution
    parameters = eval("stats." + cdf + ".fit(data)")
    return parameters


def goodness_of_fit_continuous(data, cdf, fitted_dist):
    kstest_d, kstest_pvalue = stats.kstest(data, cdf, args=fitted_dist)
    return {"kstest_d": kstest_d, "pvalue": kstest_pvalue}


def plot_best_fit(data, best_fit_parameters):
    dist = list(best_fit_parameters.keys())[0]
    parameters = best_fit_parameters[dist]
    shape = []
    for key in parameters.keys():
        if key != "loc" and key != "scale":
            shape.append(parameters[key])
    loc = parameters["loc"]
    scale = parameters["scale"]
    if len(shape) == 0:
        start = eval("stats." + dist + f".ppf(0.01, loc = {loc}, scale = {scale})")
        end = eval("stats." + dist + f".ppf(0.99, loc = {loc}, scale = {scale})")
        x = np.linspace(start, end, 100)
        best_fit_line = eval("stats." + dist + f".pdf(x, loc = {loc}, scale = {scale})")
    if len(shape) == 1:
        start = eval("stats." + dist + f".ppf(0.01, shape[0], loc = {loc}, scale = {scale})")
        end = eval("stats." + dist + f".ppf(0.99, shape[0], loc = {loc}, scale = {scale})")
        x = np.linspace(start, end, 100)
        best_fit_line = eval("stats." + dist + f".pdf(x, shape[0], loc = {loc}, scale = {scale})")
    if len(shape) == 2:
        start = eval("stats." + dist + f".ppf(0.01, shape[0], shape[1], loc = {loc}, scale = {scale})")
        end = eval("stats." + dist + f".ppf(0.99, shape[0], shape[1], loc = {loc}, scale = {scale})")
        x = np.linspace(start, end, 100)
        best_fit_line = eval("stats." + dist + f".pdf(x, shape[0], shape[1], loc = {loc}, scale = {scale})")
    pdf = pd.Series(best_fit_line, x)

    data = pd.Series(data)
    ax = data.plot(kind="hist", bins=50, density=True, alpha=0.5, label="Data", color="gray", legend=True)
    ax.set_ylim(ax.get_ylim())
    pdf.plot(lw=2, label=dist, legend=True, color="var(--primary-color)", ax=ax)
    ax.set_facecolor("white")
    ax.tick_params(color="black", labelcolor="black")
    for spine in ax.spines.values():
        spine.set_edgecolor("black")
    plt.legend(loc="upper right")

    figfile = io.BytesIO()
    plt.savefig(figfile, format="png")
    plt.close()
    figdata_png = figfile.getvalue()
    figdata_png = base64.b64encode(figdata_png)
    resultplot = figdata_png.decode("utf8")
    return resultplot


def best_fit(config_dict, data, request):
    column_list = config_dict["inputs"]["column_list"]
    model_name = config_dict["inputs"]["model_name"]
    element_id = config_dict["inputs"]["fit_element_id"]
    element_name = config_dict["inputs"]["name"]
    use_case = config_dict["inputs"]["use_case"]
    auto_save = False
    if "fit_test_autosave" in config_dict["inputs"]:
        auto_save = config_dict["inputs"]["fit_test_autosave"]
    info_dict = {
        "model_name": model_name,
        "element_id": element_id,
        "element_name": element_name,
        "use_case": use_case,
        "auto_save": auto_save,
    }
    list_of_distributions = []
    if column_list:
        data = data[column_list].values
    list_of_distributions = json.loads(config_dict["inputs"]["list_of_disturbution"])
    parameters = []
    kstest_d = []
    pvalue = []
    best_fit_parameters = pd.DataFrame()
    best_fit_parameters_dict = {}
    resultant_plot = ""
    df = pd.DataFrame(columns=["Distribution", "Pvalues"])
    if len(list_of_distributions) > 0:
        for cdf in list_of_distributions:
            fitted_dist = fit_continuous_function(data, cdf)
            parameters.append(fitted_dist)
            goodness_of_fit = goodness_of_fit_continuous(data, cdf, fitted_dist)
            kstest_d.append(goodness_of_fit["kstest_d"])
            pvalue.append(goodness_of_fit["pvalue"])
        d = {
            "Distribution": list_of_distributions,
            "Parameters": parameters,
            "KS_Statistic": kstest_d,
            "pvalue": pvalue,
        }
        df = pd.DataFrame.from_dict(d, orient="columns")
        min_kstest_d = min(kstest_d)
        best_fit_distribution = df.loc[df["KS_Statistic"] == min_kstest_d]["Distribution"].values[0]
        best_fit_parameters = df.loc[df["Distribution"] == best_fit_distribution]["Parameters"].values[0]
        if len(best_fit_parameters) == 2:
            best_fit_parameters_dict = {
                best_fit_distribution: {"loc": best_fit_parameters[0], "scale": best_fit_parameters[1]},
                "KS_Statistic": min_kstest_d,
            }
        if len(best_fit_parameters) == 3:
            best_fit_parameters_dict = {
                best_fit_distribution: {
                    "shape1": best_fit_parameters[0],
                    "loc": best_fit_parameters[1],
                    "scale": best_fit_parameters[2],
                },
                "KS_Statistic": min_kstest_d,
            }
        if len(best_fit_parameters) == 4:
            best_fit_parameters_dict = {
                best_fit_distribution: {
                    "shape1": best_fit_parameters[0],
                    "shape2": best_fit_parameters[1],
                    "loc": best_fit_parameters[2],
                    "scale": best_fit_parameters[3],
                },
                "KS_Statistic": min_kstest_d,
            }
        resultant_plot = plot_best_fit(data, best_fit_parameters_dict)
    if auto_save:
        auto_save_config(info_dict, best_fit_parameters_dict, request)
    df.drop(columns=["Parameters"], inplace=True)
    df.rename(columns={"pvalues": "P-value", "KS_Statistic": "KS statistic"}, inplace=True)
    df = df.to_dict(orient="records")
    return (df, best_fit_parameters_dict, resultant_plot, info_dict)
