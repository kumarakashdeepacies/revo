import json
import os

from config.settings.base import PLATFORM_FILE_PATH
from kore_investment.users.computations.db_centralised_function import (
    db_engine_extractor,
    read_data_func,
    update_data_func_multiple,
)


def system_update_handler(
    request, tenant, db_connection_name, user_db_engine, db_type, system_update_tracker
):
    print(
        f"Updating---------------------------------------------------------------------------------------->{db_connection_name}"
    )
    system_tables_to_update = {
        "UserConfig": ["created_by", "modified_by"],
        "NavigationSideBar": ["created_by"],
        "ProcessScheduler": ["created_by"],
        "DraftProcess": ["created_by"],
        "computation_model_run_history": ["created_by", "modified_by"],
        "ApprovalTable": ["created_by", "modified_by"],
        "external_application_master": ["created_by"],
        "Upload_Error_History": ["created_by"],
        "Plans": ["created_by", "modified_by"],
        "Plan_Buckets": ["created_by", "modified_by"],
        "Tasks_Planner": ["created_by", "modified_by"],
        "Curve_Repository": ["created_by", "modified_by"],
        "Curve_Data": ["created_by", "modified_by"],
        "Holiday_Calendar_Repository": ["created_by", "modified_by"],
        "Model_Repository": ["created_by", "modified_by"],
        "Draft_FormData": ["created_by", "modified_by"],
        "ConfigTable": ["created_by", "modified_by"],
        "group_config": ["created_by", "modified_by"],
        "Ocr_Template": ["created_by", "modified_by"],
        "data_mapping_error_report": ["created_by", "modified_by"],
        "ml_model_repository": ["created_by", "modified_by"],
        "UserProfile": ["username"],
        "Process_flow_model": ["created_by", "modified_by"],
        "flow_monitor_error_log": ["created_by", "modified_by"],
        "computation_scenario_repository": ["created_by", "modified_by"],
        "alerts": ["created_by", "modified_by"],
        "alertslog": ["created_by"],
        "static_page_config": ["created_by", "modified_by"],
        "application_theme": ["created_by", "modified_by"],
    }

    # System config update
    for table_name, columns_list in system_tables_to_update.items():
        print("table_name ---------------------------------------------------------------------->")
        print(table_name, columns_list)
        try:
            existing_data = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": table_name,
                        "Columns": ["id", *columns_list],
                    },
                    "condition": [],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if not existing_data.empty:
                for column in columns_list:
                    existing_data[column] += f".{tenant}"
                update_config_dict = {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": table_name,
                        "Columns": [],
                    },
                    "condition": [
                        {
                            "column_name": "id",
                            "condition": "Equal to",
                            "and_or": "",
                        }
                    ],
                }
                for up_col in columns_list:
                    column_dict = {
                        "column_name": up_col,
                        "separator": ",",
                    }
                    update_config_dict["inputs"]["Columns"].append(column_dict)
                update_config_dict["inputs"]["Columns"][-1]["separator"] = ""
                update_data_func_multiple(
                    request,
                    update_config_dict,
                    existing_data,
                    engine2=user_db_engine,
                    db_type=db_type,
                    if_app_db=True,
                    engine_override=True,
                )
            else:
                continue
        except Exception as e:
            print(f"Error updating {table_name} - {e}")

    # User defined table update
    user_defined_tables = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [
                {
                    "column_name": "model_type",
                    "condition": "Equal to",
                    "input_value": "user defined",
                    "and_or": "",
                },
            ],
        },
        engine2=user_db_engine,
        db_type=db_type,
        engine_override=True,
    )
    if not user_defined_tables.empty:
        for idx, row in user_defined_tables.iterrows():
            table_name = row["tablename"]
            fields = row["fields"]
            columns_list = ["created_by", "modified_by"]
            if "UserField" in fields:
                fields = json.loads(fields)
                user_field_list = [i for i in fields if fields[i]["internal_type"] == "UserField"]
                columns_list.extend(user_field_list)
            else:
                pass
            try:
                existing_data = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": table_name,
                            "Columns": ["id", *columns_list],
                        },
                        "condition": [],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if not existing_data.empty:
                    for column in columns_list:
                        existing_data[column] += f".{tenant}"
                    update_config_dict = {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": table_name,
                            "Columns": [],
                        },
                        "condition": [
                            {
                                "column_name": "id",
                                "condition": "Equal to",
                                "and_or": "",
                            }
                        ],
                    }
                    for up_col in columns_list:
                        column_dict = {
                            "column_name": up_col,
                            "separator": ",",
                        }
                        update_config_dict["inputs"]["Columns"].append(column_dict)
                    update_config_dict["inputs"]["Columns"][-1]["separator"] = ""
                    update_data_func_multiple(
                        request,
                        update_config_dict,
                        existing_data.fillna("NULL"),
                        engine2=user_db_engine,
                        db_type=db_type,
                        if_app_db=True,
                        engine_override=True,
                    )
                else:
                    continue
            except Exception as e:
                print(f"Error updating user defined table {table_name} - {e}")
    else:
        pass

    if system_update_tracker.get(tenant):
        system_update_tracker[tenant].append(db_connection_name)
    else:
        system_update_tracker[tenant] = [db_connection_name]
    with open(f"{PLATFORM_FILE_PATH}system_update_tracker.json", "w") as outfile:
        json.dump(system_update_tracker, outfile)
        outfile.close()
    return True


tenant_data = []
if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
        tenant_data = list(json.load(json_file).keys())
        json_file.close()
else:
    pass

system_update_tracker = {}
if os.path.exists(f"{PLATFORM_FILE_PATH}system_update_tracker.json"):
    with open(f"{PLATFORM_FILE_PATH}system_update_tracker.json") as json_file:
        system_update_tracker = json.load(json_file)
        json_file.close()
else:
    pass

connected_database = {}
if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
    with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
        connected_database = json.load(json_file)
        json_file.close()
else:
    pass
for tenant in tenant_data:
    if tenant != "public":
        tenant_connected_database = [k for k, v in connected_database.items() if v.get("tenant") == tenant]
        databases_updated = system_update_tracker.get(tenant, [])
        for db_connection_name in tenant_connected_database:
            if db_connection_name not in databases_updated:
                user_db_engine, db_type = db_engine_extractor(db_connection_name)
                system_update_handler(
                    "", tenant, db_connection_name, user_db_engine, db_type, system_update_tracker
                )
            else:
                continue
    else:
        continue
