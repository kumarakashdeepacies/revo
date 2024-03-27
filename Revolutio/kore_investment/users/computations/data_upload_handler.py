from datetime import datetime
import json

import pandas as pd

from . import Data_replica_utilities
from .db_centralised_function import data_handling, postgres_push, read_data_func
from .standardised_functions import process_flow_monitor


def push_uploaded_data(
    request,
    data,
    table_name,
    process_flow_handler_args,
    process_flow_handler_kwargs,
    actual_model_name,
    tenant=None,
    instance_id=None,
):
    if isinstance(request, dict):

        class AttrDict:
            def __init__(self, i_dict):
                for key, value in i_dict.items():
                    if key not in ["password", "last_login", "date_joined"]:
                        setattr(self, key, value)
                if i_dict.get("username"):
                    setattr(self, "is_anonymous", False)
                else:
                    setattr(self, "is_anonymous", True)

            def get_host(self):
                return self.host

        request["user"] = AttrDict(request["user"])
        request = AttrDict(request)

    data_handling(request=request, table=data, original_table_name=table_name)
    multi_select_field_dict = {}
    is_multi_select_field = False
    for field in actual_model_name.concrete_fields:
        if field.get_internal_type() in ["MultiselectField"]:
            is_multi_select_field = True
            temp_mul_config = json.loads(field.mulsel_config)
            for attri, conf_val in temp_mul_config.items():
                if (
                    attri == "value"
                    or attri == "masterColumn"
                    or attri == "master"
                    or attri == "add"
                    or attri == "def_MulVal"
                    or attri == "checkBox"
                    or attri == "condition"
                ):
                    if attri in multi_select_field_dict:
                        multi_select_field_dict[attri].append(conf_val[0])
                    else:
                        multi_select_field_dict[attri] = conf_val
                elif attri == "plusBtn" or attri == "popUpOption":
                    if attri in multi_select_field_dict:
                        multi_select_field_dict[attri].update(conf_val)
                    else:
                        multi_select_field_dict[attri] = conf_val
                else:
                    multi_select_field_dict[attri] = conf_val
        else:
            continue

    if is_multi_select_field:
        multi_select_tables = multi_select_field_dict["value"]
        mutli_select_cols = multi_select_field_dict["masterColumn"]
        mutli_select_attr = multi_select_field_dict["master"]

        replica = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Tables",
                    "Columns": ["linked_table"],
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
                        "condition": "Equal to",
                        "input_value": table_name,
                        "and_or": "",
                    },
                ],
            },
        )

        if replica.empty:
            replica = None
        else:
            replica = replica.loc[0, "linked_table"]

        if replica is not None:
            mt = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Tables",
                        "Columns": ["id"],
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
                            "condition": "Equal to",
                            "input_value": table_name + "_mul",
                            "and_or": "",
                        },
                    ],
                },
            )
            if len(mt) > 0:
                records = len(data)
                recent_record_ids = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": table_name,
                            "Agg_Type": f"TOP({records})",
                            "Order_Type": "ORDER BY id DESC",
                            "Columns": ["id"],
                        },
                        "condition": [],
                    },
                )["id"].tolist()
                data["id"] = recent_record_ids

                Data_replica_utilities.insert_delimited_data(
                    elementID="",
                    request=request,
                    table_name_replica=table_name,
                    multi_select_tables=multi_select_tables,
                    mutli_select_cols=mutli_select_cols,
                    mutli_select_attr=mutli_select_attr,
                    existingData=data,
                )
            else:
                pass
        else:
            pass
    else:
        pass

    process_flow_func_args = [*process_flow_handler_args, request]
    process_flow_monitor(*process_flow_func_args, **process_flow_handler_kwargs)
    noti_msg = f"Upload for {table_name} was successful."

    data_df = pd.DataFrame(
        [
            {
                "user_name": request.user.username,
                "category": "system notification",
                "status": "unread",
                "notification_message": noti_msg,
                "created_date": datetime.now(),
                "instance_id": instance_id,
            }
        ]
    )

    postgres_push(
        data_df,
        "users_notification_management",
        schema=tenant,
        app_db_transaction=False,
    )
    return None
