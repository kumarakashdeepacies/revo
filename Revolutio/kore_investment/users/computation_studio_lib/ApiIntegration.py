import json
import os

import requests

from config.settings.base import PLATFORM_FILE_PATH


def send_data(config_dict, data):
    connection_name = config_dict["inputs"]["connection_name"]
    base_url = ""
    params_list = config_dict["inputs"]["param_data"]
    req_method = ""
    context = {}
    with open(f"{PLATFORM_FILE_PATH}api.json", "r+") as fout:
        content = json.load(fout)
        base_url = content[connection_name]["url"]
        req_method = content[connection_name]["req_method"]

    fout.close()
    context["msg"] = "Data exported to API successfully"
    for i in range(len(data)):
        payload = {}
        for param in params_list:
            if param["static_val"] and param["static_val"] is not None:
                payload[param["param_name"]] = param["static_val"]
            elif param["col_val"] and param["col_val"] is not None:
                payload[param["param_name"]] = data.loc[i, param["col_val"]]
        if req_method == "get":
            r = requests.get(base_url, params=payload)
            if not r.ok:
                context["error"] = "error"
                context["msg"] = "Failed to export data to API"
        elif req_method == "post":
            r = requests.post(base_url, data=payload)
            if not r.ok:
                context["error"] = "error"
                context["msg"] = "Failed to export data to API"

    return context


def save_api_details(configList, connection_name):
    if not os.path.exists(f"{PLATFORM_FILE_PATH}api.json"):
        with open(f"{PLATFORM_FILE_PATH}api.json", "w") as fp:
            fp.write("{}")
            fp.close()
    temp_data = {}
    with open(f"{PLATFORM_FILE_PATH}api.json") as f:
        temp_data = json.load(f)
        temp_data[connection_name] = configList
        f.close()
    with open(f"{PLATFORM_FILE_PATH}api.json", "w") as f:
        json.dump(temp_data, f, indent=4)
        f.close()
    return connection_name
