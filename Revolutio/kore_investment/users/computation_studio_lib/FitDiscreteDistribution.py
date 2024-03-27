import base64
from datetime import datetime
import io
import json

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import poisson

from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    read_data_func,
    update_data_func,
)


class FitDiscreteDistribution:
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
                    "input_value": "Fit Discrete",
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
            "model_type": "Fit Discrete",
            "element_name": element_name,
            "model_output": element_config,
            "use_case": use_case,
            "created_by": request_user,
            "created_date": datetime.now(),
            "modified_by": request_user,
            "modified_date": datetime.now(),
        }
        fit_result_df1 = pd.DataFrame.from_dict([fit_result_dict])
        fit_result_df = pd.concat(
            [fit_result_df, fit_result_df1],
            ignore_index=True,
        )
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
                        "input_value": "Fit Discrete",
                        "and_or": "",
                    },
                ],
            },
        )
    return "success"


def poisson_fit_function(k, lamb):
    return poisson.pmf(k, lamb)


def fit_discrete(config_dict, data, request):
    column_list = config_dict["inputs"]["column_list"]
    model_name = config_dict["inputs"]["model_name"]
    element_id = config_dict["inputs"]["discrete_element_id"]
    element_name = config_dict["inputs"]["name"]
    use_case = config_dict["inputs"]["use_case"]
    auto_save = False
    if "fit_discrete_autosave" in config_dict["inputs"]:
        auto_save = config_dict["inputs"]["fit_discrete_autosave"]
    info_dict = {
        "model_name": model_name,
        "element_id": element_id,
        "element_name": element_name,
        "use_case": use_case,
        "auto_save": auto_save,
    }
    cdf = ""
    best_fit_params = {}
    resultplot = None
    if column_list:
        data = data[column_list].values
    cdf = config_dict["inputs"]["disturbution_type"]
    if cdf == "poisson":
        ax = plt.axes()
        ax.set_facecolor("white")
        ax.tick_params(color="black", labelcolor="black")
        entries, bin_edges, patches = plt.hist(data, density=True, label="Data", color="gray")
        parameters = sum(data) / len(data)
        plt.plot(
            data,
            poisson_fit_function(data, parameters),
            marker="o",
            linestyle="",
            label="Fit result",
            color="var(--primary-color)",
        )
        for spine in ax.spines.values():
            spine.set_edgecolor("black")
        figfile = io.BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        best_fit_params = {"poisson": {"lambda": parameters}, "pvalue": 0.5}
    if auto_save:
        auto_save_config(info_dict, best_fit_params, request)
    return best_fit_params, resultplot, info_dict
