import json

from .db_centralised_function import read_data_func


def value_to_id_converter(request, master_column, master_table, input_value, condition):
    master_identifier = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": master_table,
                "Columns": ["id"],
            },
            "condition": [
                {
                    "column_name": master_column,
                    "condition": condition,
                    "input_value": input_value,
                    "and_or": "",
                }
            ],
        },
    )
    return master_identifier


def multi_select_value_converter(value, master_data):
    if value:
        if value.startswith("{"):
            value = json.loads(value.replace("'", '"'))
            input_values = value.keys()
            try:
                input_values = [int(i) for i in input_values]
                value_identifiers = value
            except Exception as e:
                value_identifiers = {
                    master_data[i.strip()]: value[i] for i in value if i.strip() in master_data
                }
        else:
            input_values = value.split(",")
            value_identifiers = {master_data[i.strip()]: "" for i in input_values if i.strip() in master_data}
        return json.dumps(value_identifiers)
    else:
        return value


def upload_data_multi_select_converter(request, data, field_name, multi_select_config):
    master_table = multi_select_config["value"][0]
    master_field = multi_select_config["masterColumn"][0]
    raw_condition = multi_select_config["condition"][0]
    filter_condition = []
    for i in raw_condition:
        filter_condition.append(
            {
                "column_name": i["condColumn"],
                "condition": i["cond"],
                "input_value": i["condValue"],
                "and_or": "",
                "constraintName": i["constraint"],
                "ruleSet": i["ruleSet"],
            }
        )
    master_data = (
        read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": master_table,
                    "Columns": ["id", master_field],
                },
                "condition": filter_condition,
            },
        )
        .set_index(master_field)
        .to_dict()["id"]
    )
    data[field_name] = data[field_name].map(
        lambda x: multi_select_value_converter(x, master_data), na_action="ignore"
    )
    return data


def multi_select_id_to_value_converter(request, data, field_name, multi_select_config):
    master_table = multi_select_config["value"][0]
    master_field = multi_select_config["masterColumn"][0]
    data[field_name] = data[field_name].map(lambda x: list(json.loads(x).keys()), na_action="ignore")
    input_value = []
    for i in data[field_name].dropna().tolist():
        input_value.extend(i)
    if input_value:
        master_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": master_table,
                    "Columns": ["id", master_field],
                },
                "condition": [
                    {
                        "column_name": "id",
                        "condition": "IN",
                        "input_value": input_value,
                        "and_or": "",
                    }
                ],
            },
        )
        master_data["id"] = master_data["id"].astype(str)
        master_data = master_data.set_index("id").to_dict()[master_field]
    else:
        master_data = {}
    data[field_name] = data[field_name].map(
        lambda x: [master_data[i] for i in x if i in master_data], na_action="ignore"
    )
    return data


def fk_id_to_value_converter(request, data, field_name, parent):
    input_value = data[field_name].dropna().unique().tolist()
    if input_value:
        master_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": parent,
                    "Columns": ["id", field_name],
                },
                "condition": [
                    {
                        "column_name": "id",
                        "condition": "IN",
                        "input_value": input_value,
                        "and_or": "",
                    }
                ],
            },
        )
        master_data["id"] = master_data["id"].astype(str)
        master_data = master_data.set_index("id").to_dict()[field_name]
    else:
        master_data = {}
    data[field_name] = data[field_name].replace(to_replace=master_data)
    return data
