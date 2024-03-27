import json
import os

from config.settings.base import MEDIA_ROOT, PLATFORM_FILE_PATH
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.models import sys_tables

from . import dynamic_model_create
from .db_centralised_function import read_data_func


def update_user_tables(request, db_connection_name, user_db_engine, db_type):
    table_fields = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["fields", "tablename"],
            },
            "condition": [
                {
                    "column_name": "model_type",
                    "condition": "Equal to",
                    "input_value": "user defined",
                    "and_or": "",
                }
            ],
        },
        engine2=user_db_engine,
        db_type=db_type,
        engine_override=True,
    )
    table_fields = table_fields[~table_fields["tablename"].isin(sys_tables)]
    table_fields = table_fields.to_dict("records")
    for i in table_fields:
        if i["fields"] is not None:
            fields = json.loads(i["fields"])
            table = i["tablename"]
            if fields.get("is_active_flag") is None:
                field_config = {"fieldName": "is_active_flag"}
                field_config["fieldDatatype"] = "CharField"
                field_config["fieldVerboseName"] = "is_active_flag"
                field_config["fieldNull"] = "Yes"
                field_config["fieldUnique"] = "No"
                field_config["fieldDefault"] = "Yes"
                field_config["fieldChoices"] = ""
                field_config["fieldMaxLength"] = "255"
                field_config["fieldFKTable"] = ""
                field_config["fieldRelatedName"] = ""
                field_config["fieldEditable"] = "No"
                field_config["fieldAutoNow"] = "No"
                field_config["validators"] = []
                dynamic_model_create.add_element(table, field_config, request, db_connection_name)
            elif fields.get("active_to") is None:
                field_config = {"fieldName": "active_to"}
                field_config["fieldDatatype"] = "DateTimeField"
                field_config["fieldVerboseName"] = "Active To"
                field_config["fieldNull"] = "Yes"
                field_config["fieldUnique"] = "No"
                field_config["fieldDefault"] = ""
                field_config["fieldChoices"] = ""
                field_config["fieldMaxLength"] = ""
                field_config["fieldFKTable"] = ""
                field_config["fieldRelatedName"] = ""
                field_config["fieldEditable"] = "Yes"
                field_config["fieldAutoNow"] = "No"
                field_config["validators"] = []
                dynamic_model_create.add_element(table, field_config, request, db_connection_name)
            if fields.get("active_from") is None:
                field_config = {"fieldName": "active_from"}
                field_config["fieldDatatype"] = "DateTimeField"
                field_config["fieldVerboseName"] = "Active From"
                field_config["fieldNull"] = "Yes"
                field_config["fieldUnique"] = "No"
                field_config["fieldDefault"] = ""
                field_config["fieldChoices"] = ""
                field_config["fieldMaxLength"] = ""
                field_config["fieldFKTable"] = ""
                field_config["fieldRelatedName"] = ""
                field_config["fieldEditable"] = "Yes"
                field_config["fieldAutoNow"] = "No"
                field_config["validators"] = []
                dynamic_model_create.add_element(table, field_config, request, db_connection_name)
    return None


def update_rtf_data_json(request, db_connection_name, user_db_engine, db_type):
    with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
        user_db_mapping = json.load(json_file)
        json_file.close()
    db_server, port, db_name, username, password = decrypt_existing_db_credentials(
        user_db_mapping[db_connection_name]["server"],
        user_db_mapping[db_connection_name]["port"],
        user_db_mapping[db_connection_name]["db_name"],
        user_db_mapping[db_connection_name]["username"],
        user_db_mapping[db_connection_name]["password"],
        user_db_mapping[db_connection_name]["connection_code"],
    )
    if os.path.exists(f"{MEDIA_ROOT}/rtf_files_master/{db_name}/rtf_data.json"):
        rtf_data = {}
        with open(f"{MEDIA_ROOT}/rtf_files_master/{db_name}/rtf_data.json") as f:
            rtf_data = json.load(f)
            f.close()
        rtf_tables = list(rtf_data.keys())
        table_fields = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Tables",
                    "Columns": ["fields", "tablename"],
                },
                "condition": [
                    {
                        "column_name": "model_type",
                        "condition": "Equal to",
                        "input_value": "user defined",
                        "and_or": "and",
                    },
                    {
                        "column_name": "tablename",
                        "condition": "IN",
                        "input_value": rtf_tables,
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        for idx, row in table_fields.iterrows():
            table_name = row["tablename"]
            if rtf_data.get(table_name):
                table_rtf_data = rtf_data[table_name].copy()
                fields = json.loads(row["fields"])
                rtf_fields = [i for i in fields if fields[i]["internal_type"] == "RTFField"]
                if rtf_fields:
                    field_name = rtf_fields[0]
                    for key, value in table_rtf_data.items():
                        if "_" not in key:
                            new_key = f"{key}_{field_name}"
                            rtf_data[table_name][new_key] = value
                            del rtf_data[table_name][key]
                        else:
                            continue
                else:
                    continue
            else:
                continue
        with open(f"{MEDIA_ROOT}/rtf_files_master/{db_name}/rtf_data.json", "w") as f:
            json.dump(rtf_data, f, indent=4)
            f.close()
    else:
        pass
    return None
