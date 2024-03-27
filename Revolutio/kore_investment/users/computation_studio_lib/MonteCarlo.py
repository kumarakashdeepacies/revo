import json
import pickle

import pandas as pd

from config.settings.base import redis_instance
from kore_investment.users.computations.db_centralised_function import read_data_func


def generate_random(params_dict, n=1000):
    dist = list(params_dict.keys())[0]
    if dist == "poisson":
        mu = params_dict[dist]["lambda"]
        return eval("stats." + dist + f".rvs({mu}, size = {n})")
    else:
        dist = list(params_dict.keys())[0]
        parameters = params_dict[dist]
        shape = []

        for key in parameters.keys():
            if key != "loc" and key != "scale":
                shape.append(parameters[key])

        loc = parameters["loc"]
        scale = parameters["scale"]
        if len(shape) == 0:
            return eval("stats." + dist + f".rvs(loc = {loc}, scale = {scale}, size = {n})")
        if len(shape) == 1:
            return eval("stats." + dist + f".rvs(shape[0], loc = {loc}, scale = {scale}, size = {n})")
        if len(shape) == 2:
            return eval(
                "stats." + dist + f".rvs(shape[0], shape[1], loc = {loc}, scale = {scale}, size = {n})"
            )


def monte_carlo_simulation(config_dict, request):
    list_of_connected = json.loads(config_dict["inputs"]["Data"])
    simulation_count = config_dict["inputs"]["monte_carlo_simulation"]
    element_id = config_dict["inputs"]["montecarlo_element_id"]
    loss_dataframe = pd.DataFrame()
    if len(list_of_connected) > 0:
        for i in range(len(list_of_connected)):
            model_df = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ml_model_repository",
                        "Columns": ["use_case", "model_output"],
                    },
                    "condition": [
                        {
                            "column_name": "element_id",
                            "condition": "Equal to",
                            "input_value": str(list_of_connected[i]),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "model_type",
                            "condition": "IN",
                            "input_value": "('Goodness of Fit Test','Fit Discrete')",
                            "and_or": "",
                        },
                    ],
                },
            )
            if not model_df.empty:
                params_dict = json.loads(model_df["model_output"].values[0])
                use_case = model_df["use_case"].values[0]
                loss_result = generate_random(params_dict, n=int(simulation_count))
                loss_dataframe[use_case] = pd.Series(loss_result)
    redis_instance.set(element_id, pickle.dumps(loss_dataframe))
    return loss_dataframe
