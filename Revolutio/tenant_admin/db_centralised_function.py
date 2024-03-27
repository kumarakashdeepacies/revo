import json
import logging
import multiprocessing as mp
import os
import urllib

import bcpy
from django.apps import apps
import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
import pyarrow as pa
from sqlalchemy import create_engine
from turbodbc import connect, make_options

## Cache
from config.settings.base import (
    PLATFORM_FILE_PATH,
    central_database_config,
    database_engine_dict,
    database_type,
    engine,
    redis_instance,
    sql_config,
    turbodbc_connection,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.computations.model_field_info import ModelInfo
from tenant_admin.utilities import tenant_schema_from_request

admin_tables = [
    "auditlog_logentry",
    "django_apscheduler_djangojobexecution",
    "user",
    "User",
    "Profile",
    "auth_group",
    "user_groups",
    "configuration_parameter",
    "UserPermission_Master",
    "permissionaccess",
    "usergroup_approval",
    "user_approval",
    "allocated_licences",
    "user_model",
    "userpermission_interim",
    "group_details",
    "user_navbar",
    "login_trail",
    "audit_trail",
    "notification_management",
    "Instance",
    "applicationAccess",
]


def get_model_class(model_name, request, db_connection_name="", db_engine=["", {}]):
    admin_tables_inter = [
        "User",
        "Profile",
        "user_groups",
        "configuration_parameter",
        "UserPermission_Master",
        "permissionaccess",
        "usergroup_approval",
        "user_approval",
        "allocated_licences",
        "user_model",
        "userpermission_interim",
        "group_details",
        "user_navbar",
        "Instance",
        "applicationAccess",
    ]
    if model_name in admin_tables_inter:
        model = apps.get_model("users", model_name)
        model = model._meta
    else:
        if db_engine[0] != "" and db_engine[1] != {}:
            user_db_engine = db_engine
        else:
            if db_connection_name != "":
                user_db_engine, db_type = database_engine_dict[db_connection_name]
            else:
                user_db_engine, db_type, schema = app_engine_generator(request)
        json_data = non_standard_read_data_func(
            f"SELECT fields FROM users_tables WHERE tablename='{model_name}'", user_db_engine
        )
        json_data = json.loads(json_data.fields.iloc[0])
        model = ModelInfo(model_name, json_data)
    return model


def data_handling(
    request,
    table,
    original_table_name,
    con=[engine, turbodbc_connection],
    if_exists="append",
    chunksize=10**5,
    db_type=database_type,
    sql_config=sql_config,
    if_app_db=True,
    connection_name="",
    engine_override=False,
    schema="",
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

    if request != "" and schema == "":
        schema = tenant_schema_from_request(request)
    db_connection_name = ""
    app_db_transaction = True
    if if_app_db:
        DB_table_name = "users_" + original_table_name.lower()
        table.replace("None", np.nan, inplace=True)
        if original_table_name:
            table_name = original_table_name
        if original_table_name not in admin_tables:
            if not engine_override:
                curr_app_code, db_connection_name = current_app_db_extractor(request)
                user_app_db_engine, db_type, schema = app_engine_generator(request)
                if user_app_db_engine != "":
                    con = user_app_db_engine
        else:
            app_db_transaction = False
    else:
        DB_table_name = original_table_name

    if if_exists == "replace":
        delete_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                },
                "condition": [],
            },
            engine2=con,
            engine_override=True,
            db_type=db_type,
        )
    if db_type == "MSSQL":
        column_type_query = f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{DB_table_name}' AND DATA_TYPE in ('datetime','datetime2') "
        datecolumns = list(
            set(non_standard_read_data_func(column_type_query, con).iloc[:, 0].to_list())
            & set(table.columns.to_list())
        )
        if len(datecolumns) > 1:
            table[datecolumns] = table[datecolumns].apply(pd.to_datetime)

        if len(table) * len(table.columns) <= 2 * (10**5):
            try:
                ### TurbODBC Push
                turbodbc_push(table, DB_table_name, con)
            except Exception as e:
                logging.warning(f"Following exception occured while pushing data using Turbodbc - {e}")
                ## Pandas push if turbodbc fails
                pandas_push(table, DB_table_name, con[0], "append", chunksize)
            redis_instance.delete(db_connection_name + DB_table_name)
        else:
            column_type = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "information_schema.columns",
                        "Columns": ["COLUMN_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Equal to",
                            "input_value": DB_table_name,
                            "and_or": "",
                        }
                    ],
                },
                engine2=con,
                engine_override=True,
                db_type=db_type,
            )
            col_names = list(column_type["COLUMN_NAME"])
            try:
                # #### If table size is large, using BCPY ####
                # ## Reindex columns since bcpy needs all columns to be in the same order as SQL ##
                bcpy_push(table, DB_table_name, col_names, db_connection_name)
                redis_instance.delete(db_connection_name + DB_table_name)
            except Exception as e:
                logging.warning(f"Following exception occured while pushing data using BCPY - {e}")
                # Pandas push if bcpy fails
                table.drop(columns=["id"], inplace=True, errors="ignore")
                try:
                    ### TurbODBC Push
                    turbodbc_push(table, DB_table_name, con)
                except Exception as e:
                    logging.warning(f"Following exception occured while pushing data using Turbodbc - {e}")
                    ## Pandas push if turbodbc fails
                    pandas_push(table, DB_table_name, con[0], "append", chunksize)
                redis_instance.delete(db_connection_name + DB_table_name)
        return ["Push Successful"]

    elif db_type == "PostgreSQL":
        if original_table_name in admin_tables:
            con[0]["schema"] = schema
        else:
            pass

        column_name = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "information_schema.columns",
                    "Columns": ["column_name"],
                },
                "condition": [
                    {
                        "column_name": "table_schema",
                        "condition": "Equal to",
                        "input_value": schema,
                        "and_or": "and",
                    },
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": DB_table_name,
                        "and_or": "and",
                    },
                    {
                        "column_name": "data_type",
                        "condition": "Equal to",
                        "input_value": "timestamp with time zone",
                        "and_or": "",
                    },
                ],
            },
            engine2=con,
            db_type=db_type,
            if_app_db=False,
            chunksize=chunksize,
            engine_override=True,
        )
        column_name = column_name.to_dict("list")["column_name"]
        for i in column_name:
            if i in table.columns.tolist():
                table[i] = pd.to_datetime(table[i]).dt.strftime("%Y-%m-%d %H:%M:%S")

        postgres_push(table, DB_table_name, schema, con=con, app_db_transaction=app_db_transaction)
        redis_instance.delete(db_connection_name + DB_table_name)

        return ["Push Successful"]


############## READ QUERY ####################


def read_data_func(
    request,
    config_dict,
    engine2=[engine, turbodbc_connection],
    chunksize=10**5,
    db_type=database_type,
    if_app_db=True,
    engine_override=False,
    schema="",
):
    if request != "" and schema == "":
        schema = tenant_schema_from_request(request)
    table = config_dict["inputs"]["Table"]
    if if_app_db:
        if table not in [
            "information_schema.columns",
            "information_schema.tables",
            "auth_group",
            "auditlog_logentry",
            "django_apscheduler_djangojobexecution",
            "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
            "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
            "master.dbo.sysdatabases",
            "sys.default_constraints",
        ]:
            sql_table_name = "users_" + table.lower()
        else:
            sql_table_name = table
    else:
        sql_table_name = table
    columnlist = config_dict["inputs"]["Columns"]
    column = ",".join(columnlist)
    agg_query = ""
    order_query = ""
    if table not in admin_tables:
        if not engine_override:
            user_app_db_engine, db_type2, schema = app_engine_generator(request)
            if db_type2:
                db_type = db_type2
            if user_app_db_engine != ["", {}]:
                engine2 = user_app_db_engine
    if db_type == "MSSQL":
        if "Agg_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Agg_Type"] != "":
                agg_query = agg_query + " " + config_dict["inputs"]["Agg_Type"] + " "
        if "Order_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Order_Type"] != "":
                order_query = order_query + " " + config_dict["inputs"]["Order_Type"] + " "
        query_tag = ""
        query_tag2 = ""
        sql_query2 = ""
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []
            if table not in admin_tables + [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]:
                try:
                    modelName = get_model_class(table, request, db_engine=engine2)
                    cond_date_list = [
                        field.name
                        for field in modelName.concrete_fields
                        if field.get_internal_type() in ["DateField"]
                    ]
                    cond_datetime_list = [
                        field.name
                        for field in modelName.concrete_fields
                        if field.get_internal_type() in ["DateTimeField"]
                    ]

                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            for i in range(0, len(config_dict["condition"])):

                if (
                    config_dict["condition"][i]["condition"] != "Between"
                    and config_dict["condition"][i]["condition"] != "IN"
                    and config_dict["condition"][i]["condition"] != "NOT IN"
                    and config_dict["condition"][i]["input_value"] != "NULL"
                ):
                    if config_dict["condition"][i]["column_name"] in cond_date_list:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"]
                        ).strftime("%Y-%m-%d")

                    if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"]
                        ).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if (
                        config_dict["condition"][i]["condition"] != "IN"
                        and config_dict["condition"][i]["condition"] != "NOT IN"
                        and config_dict["condition"][i].get("input_value") != "NULL"
                    ):
                        if config_dict["condition"][i]["column_name"] in cond_date_list:
                            config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_lower"]
                            ).strftime("%Y-%m-%d")
                            config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_upper"]
                            ).strftime("%Y-%m-%d")
                        if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                            config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_lower"]
                            ).strftime("%Y-%m-%d %H:%M:%S")
                            config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_upper"]
                            ).strftime("%Y-%m-%d %H:%M:%S")

                if config_dict["condition"][i]["condition"] == "Greater than":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NOT NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        try:
                            bool(float(config_dict["condition"][i]["input_value"]))
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + ">"
                                + " "
                                + "'"
                                + config_dict["condition"][i]["input_value"]
                                + "'"
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                        else:
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + ">"
                                + " "
                                + config_dict["condition"][i]["input_value"]
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                elif config_dict["condition"][i]["condition"] == "Smaller than":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NOT NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        try:
                            bool(float(config_dict["condition"][i]["input_value"]))
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + "<"
                                + " "
                                + "'"
                                + config_dict["condition"][i]["input_value"]
                                + "'"
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                        else:
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + "<"
                                + " "
                                + config_dict["condition"][i]["input_value"]
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                elif config_dict["condition"][i]["condition"] == "Smaller than equal to":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NOT NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        try:
                            bool(float(config_dict["condition"][i]["input_value"]))
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + "<="
                                + " "
                                + "'"
                                + config_dict["condition"][i]["input_value"]
                                + "'"
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                        else:
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + "<="
                                + " "
                                + config_dict["condition"][i]["input_value"]
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                elif config_dict["condition"][i]["condition"] == "Greater than equal to":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NOT NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        try:
                            bool(float(config_dict["condition"][i]["input_value"]))
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + ">="
                                + " "
                                + "'"
                                + config_dict["condition"][i]["input_value"]
                                + "'"
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                        else:
                            query_tag = (
                                query_tag
                                + " "
                                + (config_dict["condition"][i]["column_name"])
                                + " "
                                + ">="
                                + " "
                                + config_dict["condition"][i]["input_value"]
                                + " "
                                + config_dict["condition"][i]["and_or"]
                            )
                elif config_dict["condition"][i]["condition"] == "Equal to":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "="
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Between":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "BETWEEN"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value_lower"]
                        + "'"
                        + " "
                        + "AND"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value_upper"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "IN":
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        tuple_ = "("
                        for k in config_dict["condition"][i]["input_value"]:
                            tuple_ = tuple_ + f"'{k}',"
                        tuple_ = tuple_ + ")"
                        tuple_ = tuple_.replace(",)", ")")
                        defaultVal = tuple_
                    else:
                        defaultVal = config_dict["condition"][i]["input_value"]
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "IN"
                        + " "
                        + defaultVal
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "NOT IN":
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        tuple_ = "("
                        for k in config_dict["condition"][i]["input_value"]:
                            tuple_ = tuple_ + f"'{k}',"
                        tuple_ = tuple_ + ")"
                        tuple_ = tuple_.replace(",)", ")")
                        defaultVal = tuple_
                    else:
                        defaultVal = config_dict["condition"][i]["input_value"]
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT IN"
                        + " "
                        + defaultVal
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Equal to":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NOT NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "!="
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value"]
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%"
                        + config_dict["condition"][i]["input_value"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%" + config_dict["condition"][i]["input_value"] + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value"]
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%"
                        + config_dict["condition"][i]["input_value"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%" + config_dict["condition"][i]["input_value"] + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )

            if bool(config_dict.get("adv_condition")):
                cond_date_list = []
                cond_datetime_list = []
                if table not in admin_tables + [
                    "information_schema.columns",
                    "information_schema.tables",
                    "auth_group",
                    "auditlog_logentry",
                    "django_apscheduler_djangojobexecution",
                    "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                    "master.dbo.sysdatabases",
                    "sys.default_constraints",
                ]:
                    try:
                        modelName = get_model_class(table, request, db_engine=engine2)
                        cond_date_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateField"]
                        ]
                        cond_datetime_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateTimeField"]
                        ]

                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                for i in range(0, len(config_dict["adv_condition"])):
                    col_name = config_dict["adv_condition"][i]["column_name"]
                    agg_cond = config_dict["adv_condition"][i]["agg_condition"]
                    if (
                        config_dict["adv_condition"][i]["condition"] != "Between"
                        and config_dict["adv_condition"][i]["condition"] != "IN"
                        and config_dict["adv_condition"][i]["condition"] != "NOT IN"
                        and config_dict["adv_condition"][i]["input_value"] != "NULL"
                    ):
                        if config_dict["adv_condition"][i]["column_name"] in cond_date_list:
                            if config_dict["adv_condition"][i]["input_value"] != "":
                                config_dict["adv_condition"][i]["input_value"] = pd.to_datetime(
                                    config_dict["adv_condition"][i]["input_value"]
                                ).strftime("%Y-%m-%d")

                        if config_dict["adv_condition"][i]["column_name"] in cond_datetime_list:
                            if config_dict["adv_condition"][i]["input_value"] != "":
                                config_dict["adv_condition"][i]["input_value"] = pd.to_datetime(
                                    config_dict["adv_condition"][i]["input_value"]
                                ).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        if (
                            config_dict["adv_condition"][i]["condition"] != "IN"
                            and config_dict["adv_condition"][i]["condition"] != "NOT IN"
                            and config_dict["adv_condition"][i].get("input_value") != "NULL"
                        ):
                            if config_dict["adv_condition"][i]["column_name"] in cond_date_list:
                                if config_dict["adv_condition"][i]["input_value_lower"] != "":
                                    config_dict["adv_condition"][i]["input_value_lower"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_lower"]
                                    ).strftime("%Y-%m-%d")
                                    config_dict["adv_condition"][i]["input_value_upper"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_upper"]
                                    ).strftime("%Y-%m-%d")
                            if config_dict["adv_condition"][i]["column_name"] in cond_datetime_list:
                                if config_dict["adv_condition"][i]["input_value_lower"] != "":
                                    config_dict["adv_condition"][i]["input_value_lower"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_lower"]
                                    ).strftime("%Y-%m-%d %H:%M:%S")
                                    config_dict["adv_condition"][i]["input_value_upper"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_upper"]
                                    ).strftime("%Y-%m-%d %H:%M:%S")

                    query_tag2 = adv_query_generator(config_dict["adv_condition"][i])

                    if query_tag2 == "":
                        sql_query2 = f"{sql_query2} and {col_name} = (select {agg_cond}({col_name}) from {sql_table_name})"
                    else:
                        sql_query2 = f"{sql_query2} and {col_name} = (select {agg_cond}({col_name}) from {sql_table_name} where {query_tag2})"

                    query_tag2 = ""

            sql_query = f"select {agg_query} {column} from {sql_table_name} where {query_tag} {sql_query2} {order_query};"

        else:
            if bool(config_dict.get("adv_condition")):
                cond_date_list = []
                cond_datetime_list = []
                if table not in admin_tables + [
                    "information_schema.columns",
                    "information_schema.tables",
                    "auth_group",
                    "auditlog_logentry",
                    "django_apscheduler_djangojobexecution",
                    "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                    "master.dbo.sysdatabases",
                    "sys.default_constraints",
                ]:
                    try:
                        modelName = get_model_class(table, request, db_engine=engine2)
                        cond_date_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateField"]
                        ]
                        cond_datetime_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateTimeField"]
                        ]

                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                for i in range(0, len(config_dict["adv_condition"])):
                    col_name = config_dict["adv_condition"][i]["column_name"]
                    agg_cond = config_dict["adv_condition"][i]["agg_condition"]
                    if (
                        config_dict["adv_condition"][i]["condition"] != "Between"
                        and config_dict["adv_condition"][i]["condition"] != "IN"
                        and config_dict["adv_condition"][i]["condition"] != "NOT IN"
                        and config_dict["adv_condition"][i]["input_value"] != "NULL"
                    ):
                        if config_dict["adv_condition"][i]["column_name"] in cond_date_list:
                            if config_dict["adv_condition"][i]["input_value"] != "":
                                config_dict["adv_condition"][i]["input_value"] = pd.to_datetime(
                                    config_dict["adv_condition"][i]["input_value"]
                                ).strftime("%Y-%m-%d")

                        if config_dict["adv_condition"][i]["column_name"] in cond_datetime_list:
                            if config_dict["adv_condition"][i]["input_value"] != "":
                                config_dict["adv_condition"][i]["input_value"] = pd.to_datetime(
                                    config_dict["adv_condition"][i]["input_value"]
                                ).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        if (
                            config_dict["adv_condition"][i]["condition"] != "IN"
                            and config_dict["adv_condition"][i]["condition"] != "NOT IN"
                            and config_dict["adv_condition"][i].get("input_value") != "NULL"
                        ):
                            if config_dict["adv_condition"][i]["column_name"] in cond_date_list:
                                if config_dict["adv_condition"][i]["input_value_lower"] != "":
                                    config_dict["adv_condition"][i]["input_value_lower"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_lower"]
                                    ).strftime("%Y-%m-%d")
                                    config_dict["adv_condition"][i]["input_value_upper"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_upper"]
                                    ).strftime("%Y-%m-%d")
                            if config_dict["adv_condition"][i]["column_name"] in cond_datetime_list:
                                if config_dict["adv_condition"][i]["input_value_lower"] != "":
                                    config_dict["adv_condition"][i]["input_value_lower"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_lower"]
                                    ).strftime("%Y-%m-%d %H:%M:%S")
                                    config_dict["adv_condition"][i]["input_value_upper"] = pd.to_datetime(
                                        config_dict["adv_condition"][i]["input_value_upper"]
                                    ).strftime("%Y-%m-%d %H:%M:%S")

                    query_tag2 = adv_query_generator(config_dict["adv_condition"][i])

                    if i == 0:
                        if query_tag2 != "":
                            sql_query2 = f"{sql_query2} where {col_name} = (select {agg_cond}({col_name}) from {sql_table_name} where {query_tag2})"
                        else:
                            sql_query2 = f"{sql_query2} where {col_name} = (select {agg_cond}({col_name}) from {sql_table_name})"
                    else:
                        if query_tag2 != "":
                            sql_query2 = f"{sql_query2} and {col_name} = (select {agg_cond}({col_name}) from {sql_table_name} where {query_tag2})"
                        else:
                            sql_query2 = f"{sql_query2} and {col_name} = (select {agg_cond}({col_name}) from {sql_table_name})"

                    query_tag2 = ""

            sql_query = f"select {agg_query} {column} from {sql_table_name} {sql_query2} {order_query};"

        table = execute_read_query(sql_query, engine2, chunksize=chunksize)
        return table
    elif db_type == "PostgreSQL":
        central_db_call = False
        if table in admin_tables:
            central_db_call = True
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]
        column_list = []
        if columnlist != ["*"]:
            column = sql.SQL(", ").join([sql.Identifier(field) for field in columnlist])
        else:
            column = sql.SQL("*")
            cursor1 = sql_engine.cursor()
            if central_db_call:
                pass
            else:
                pass
            cursor1.execute(
                f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = '{sql_table_name}' AND table_schema = '{schema}'"
            )
            columns_records = cursor1.fetchall()
            cursor1.close()
            column_list = [i[0] for i in np.array(columns_records)]

        if not central_db_call and sql_table_name.lower() not in [
            "information_schema.columns",
            "information_schema.tables",
        ]:
            postgres_table_name = sql.Identifier(schema, sql_table_name)
        else:
            postgres_table_name = sql.Identifier(sql_table_name)

        agg_query = sql.SQL("")
        order_query = sql.SQL("")
        is_limit = False
        if "Agg_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Agg_Type"] != "":
                if config_dict["inputs"]["Agg_Type"].startswith("LIMIT"):
                    is_limit = True
                    agg_query = sql.SQL(config_dict["inputs"]["Agg_Type"])
                else:
                    agg_query = sql.SQL(config_dict["inputs"]["Agg_Type"])
        if "Order_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Order_Type"] != "":
                order_query = sql.SQL(config_dict["inputs"]["Order_Type"])
        query_tag = ""
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []
            if table not in admin_tables + [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]:
                try:
                    modelName = get_model_class(table, request, db_engine=engine2)
                    cond_date_list = [
                        field.name
                        for field in modelName._meta.concrete_fields
                        if field.get_internal_type() in ["DateField"]
                    ]
                    cond_datetime_list = [
                        field.name
                        for field in modelName._meta.concrete_fields
                        if field.get_internal_type() in ["DateTimeField"]
                    ]
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            query_tag = postgres_condition_generator(config_dict, cond_date_list, cond_datetime_list)
            if sql_table_name.lower() == "information_schema.columns":
                sql_query = sql.SQL(
                    "select {fields} from information_schema.columns where {condition_query}"
                ).format(fields=column, condition_query=query_tag)
            elif sql_table_name.lower() == "information_schema.tables":
                sql_query = sql.SQL(
                    "select {fields} from information_schema.tables where {condition_query}"
                ).format(fields=column, condition_query=query_tag)
            else:
                sql_query = sql.SQL("select {fields} from {table} where {condition_query}").format(
                    fields=column, table=postgres_table_name, condition_query=query_tag
                )
        else:
            if is_limit:
                sql_query = sql.SQL("select {fields} from {table} {order_query} {agg_query}").format(
                    fields=column, table=postgres_table_name, order_query=order_query, agg_query=agg_query
                )
            else:
                sql_query = sql.SQL("select {fields} from {table}").format(
                    fields=column, table=postgres_table_name
                )
        cursor = sql_engine.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        if columnlist != ["*"]:
            table = pd.DataFrame(records, columns=columnlist)
        else:
            table = pd.DataFrame(records, columns=column_list)
        cursor.close()
        sql_engine.close()
        return table


############## UPDATE QUERY ####################
def update_data_func(
    request,
    config_dict,
    engine2=[engine, turbodbc_connection],
    db_type=database_type,
    if_app_db=True,
    engine_override=False,
    schema="",
):
    if request != "" and schema == "":
        schema = tenant_schema_from_request(request)
    table = config_dict["inputs"]["Table"]
    if if_app_db:
        sql_table_name = "users_" + table.lower()
    else:
        sql_table_name = table
    update_data_dict = config_dict["inputs"]["Columns"]
    query_tag = ""
    update_data = ""
    if table not in admin_tables:
        if not engine_override:
            user_app_db_engine, db_type, schema = app_engine_generator(request)
            if user_app_db_engine != "":
                engine2 = user_app_db_engine
    if db_type == "MSSQL":
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []
            if table not in admin_tables:
                try:
                    if if_app_db:
                        modelName = get_model_class(table, request, db_engine=engine2)
                        cond_date_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateField"]
                        ]
                        cond_datetime_list = [
                            field.name
                            for field in modelName.concrete_fields
                            if field.get_internal_type() in ["DateTimeField"]
                        ]
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")

            for i in range(0, len(update_data_dict)):
                if update_data_dict[i]["input_value"] != "NULL":
                    if update_data_dict[i]["column_name"] in cond_date_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d")
                    if update_data_dict[i]["column_name"] in cond_datetime_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d %H:%M:%S")

                    update_data = (
                        update_data
                        + " "
                        + update_data_dict[i]["column_name"]
                        + " "
                        + "="
                        + " "
                        + "'"
                        + update_data_dict[i]["input_value"]
                        + "'"
                        + " "
                        + update_data_dict[i]["separator"]
                    )
                else:
                    update_data = (
                        update_data
                        + " "
                        + update_data_dict[i]["column_name"]
                        + " "
                        + "="
                        + " "
                        + "NULL"
                        + " "
                        + update_data_dict[i]["separator"]
                    )

            for i in range(0, len(config_dict["condition"])):
                if config_dict["condition"][i]["column_name"] in cond_date_list:
                    try:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"]
                        ).strftime("%Y-%m-%d")
                    except Exception:
                        config_dict["condition"][i]["input_value"] = "NULL"

                if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                    try:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"], errors="coerce"
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        config_dict["condition"][i]["input_value"] = "NULL"

                if config_dict["condition"][i]["condition"] == "Greater than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">"
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">"
                            + " "
                            + config_dict["condition"][i]["input_value"]
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Greater than equal to":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">="
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">="
                            + " "
                            + config_dict["condition"][i]["input_value"]
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Smaller than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<"
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<"
                            + " "
                            + config_dict["condition"][i]["input_value"]
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Smaller than equal to":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<="
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<="
                            + " "
                            + config_dict["condition"][i]["input_value"]
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Equal to":
                    if config_dict["condition"][i]["input_value"] == "NULL":
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "IS"
                            + " "
                            + "NULL"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "="
                            + " "
                            + "'"
                            + config_dict["condition"][i]["input_value"]
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Between":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "BETWEEN"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value_lower"]
                        + "'"
                        + " "
                        + "AND"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value_upper"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "IN":
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        tuple_ = "("
                        for k in config_dict["condition"][i]["input_value"]:
                            tuple_ = tuple_ + f"'{k}',"
                        tuple_ = tuple_ + ")"
                        tuple_ = tuple_.replace(",)", ")")
                        defaultVal = tuple_
                    else:
                        defaultVal = config_dict["condition"][i]["input_value"]
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "IN"
                        + " "
                        + defaultVal
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "NOT IN":
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        tuple_ = "("
                        for k in config_dict["condition"][i]["input_value"]:
                            tuple_ = tuple_ + f"'{k}',"
                        tuple_ = tuple_ + ")"
                        tuple_ = tuple_.replace(",)", ")")
                        defaultVal = tuple_
                    else:
                        defaultVal = config_dict["condition"][i]["input_value"]
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT IN"
                        + " "
                        + defaultVal
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Equal to":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "!="
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value"]
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%"
                        + config_dict["condition"][i]["input_value"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%" + config_dict["condition"][i]["input_value"] + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        + config_dict["condition"][i]["input_value"]
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%"
                        + config_dict["condition"][i]["input_value"]
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%" + config_dict["condition"][i]["input_value"] + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
            sql_query = f"update {sql_table_name} set {update_data} where {query_tag} ;"
        else:
            sql_query = f"update {sql_table_name} set {update_data} ;"

        with engine2[0].begin() as conn:
            conn.execute(sql_query)
        return None

    elif db_type == "PostgreSQL":
        central_db_call = False
        if table in admin_tables:
            central_db_call = True
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]
        if not central_db_call:
            postgres_table_name = sql.Identifier(schema, sql_table_name)
        else:
            postgres_table_name = sql.Identifier(sql_table_name)

        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables:
                try:
                    if if_app_db:
                        modelName = get_model_class(table, request, db_engine=engine2)
                        cond_date_list = [
                            field.name
                            for field in modelName._meta.concrete_fields
                            if field.get_internal_type() in ["DateField"]
                        ]
                        cond_datetime_list = [
                            field.name
                            for field in modelName._meta.concrete_fields
                            if field.get_internal_type() in ["DateTimeField"]
                        ]
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")

            update_string_list = []
            for i in range(0, len(update_data_dict)):
                if update_data_dict[i]["input_value"] != "NULL":
                    if update_data_dict[i]["column_name"] in cond_date_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d")
                    if update_data_dict[i]["column_name"] in cond_datetime_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d %H:%M:%S")

                    update_string_list.append(
                        sql.SQL("{field} = {value} {separator}").format(
                            field=sql.Identifier(update_data_dict[i]["column_name"]),
                            value=sql.Literal(update_data_dict[i]["input_value"]),
                            separator=sql.SQL(update_data_dict[i]["separator"]),
                        )
                    )
                else:
                    update_string_list.append(
                        sql.SQL("{field} = {value} {separator}").format(
                            field=sql.Identifier(update_data_dict[i]["column_name"]),
                            value=sql.SQL("NULL"),
                            separator=sql.SQL(update_data_dict[i]["separator"]),
                        )
                    )
            update_col_string = sql.SQL(" ").join([i for i in update_string_list])
            query_tag = postgres_condition_generator(config_dict, cond_date_list, cond_datetime_list)
            sql_query = sql.SQL("update {table} set {update_data} where {query_tag}").format(
                table=postgres_table_name, update_data=update_col_string, query_tag=query_tag
            )
        else:
            sql_query = sql.SQL("update {table} set {update_data}").format(
                table=postgres_table_name, update_data=update_col_string
            )
        cursor = sql_engine.cursor()
        cursor.execute(sql_query)
        sql_engine.commit()
        cursor.close()
        sql_engine.close()
        return None


############## DELETE QUERY ####################
def delete_data_func(
    request,
    config_dict,
    engine2=[engine, turbodbc_connection],
    db_type=database_type,
    engine_override=False,
    schema="",
):
    if request != "" and schema == "":
        schema = tenant_schema_from_request(request)
    table = config_dict["inputs"]["Table"]
    sql_table_name = "users_" + table.lower()
    query_tag = ""
    if table not in admin_tables:
        if not engine_override:
            user_app_db_engine, db_type, schema = app_engine_generator(request)
            if user_app_db_engine != "":
                engine2 = user_app_db_engine
    if db_type == "MSSQL":
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables:
                modelName = get_model_class(table, request, db_engine=engine2)
                cond_date_list = [
                    field.name
                    for field in modelName.concrete_fields
                    if field.get_internal_type() in ["DateField"]
                ]
                cond_datetime_list = [
                    field.name
                    for field in modelName.concrete_fields
                    if field.get_internal_type() in ["DateTimeField"]
                ]

            for i in range(0, len(config_dict["condition"])):
                if config_dict["condition"][i]["column_name"] in cond_date_list:
                    config_dict["condition"][i]["input_value"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value"]
                    ).strftime("%Y-%m-%d")

                if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                    config_dict["condition"][i]["input_value"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value"]
                    ).strftime("%Y-%m-%d %H:%M:%S")

                if config_dict["condition"][i]["condition"] == "Greater than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">"
                            + " "
                            + "'"
                            + str(config_dict["condition"][i]["input_value"])
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + ">"
                            + " "
                            + str(config_dict["condition"][i]["input_value"])
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Smaller than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<"
                            + " "
                            + "'"
                            + str(config_dict["condition"][i]["input_value"])
                            + "'"
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                    else:
                        query_tag = (
                            query_tag
                            + " "
                            + (config_dict["condition"][i]["column_name"])
                            + " "
                            + "<"
                            + " "
                            + str(config_dict["condition"][i]["input_value"])
                            + " "
                            + config_dict["condition"][i]["and_or"]
                        )
                elif config_dict["condition"][i]["condition"] == "Equal to":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "="
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value"])
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )

                elif config_dict["condition"][i]["condition"] == "Between":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "BETWEEN"
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value_lower"])
                        + "'"
                        + " "
                        + "AND"
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value_upper"])
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "IN":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "IN"
                        + " "
                        + str(config_dict["condition"][i]["input_value"])
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "NOT IN":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT IN"
                        + " "
                        + str(config_dict["condition"][i]["input_value"])
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Equal to":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "!="
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value"])
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value"])
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%"
                        + str(config_dict["condition"][i]["input_value"])
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "LIKE"
                        + " "
                        + "'"
                        "%" + config_dict["condition"][i]["input_value"] + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Starts with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        + str(config_dict["condition"][i]["input_value"])
                        + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Ends with":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%"
                        + str(config_dict["condition"][i]["input_value"])
                        + "'"
                        + " "
                        + config_dict["condition"][i]["and_or"]
                    )
                elif config_dict["condition"][i]["condition"] == "Not Contains":
                    query_tag = (
                        query_tag
                        + " "
                        + (config_dict["condition"][i]["column_name"])
                        + " "
                        + "NOT LIKE"
                        + " "
                        + "'"
                        "%" + str(config_dict["condition"][i]["input_value"]) + "%"
                        "'" + " " + config_dict["condition"][i]["and_or"]
                    )
            sql_query = f"delete from {sql_table_name} where {query_tag}"

        else:
            sql_query = f"delete from {sql_table_name}"

        sql_query = sql_query.split(";")[0]
        with engine2[0].begin() as conn:
            conn.execute(sql_query)
        return None

    elif db_type == "PostgreSQL":
        central_db_call = False
        if table in admin_tables:
            central_db_call = True
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]

        if not central_db_call:
            postgres_table_name = sql.Identifier(schema, sql_table_name)
        else:
            postgres_table_name = sql.Identifier(sql_table_name)

        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables:
                modelName = get_model_class(table, request, db_engine=engine2)
                cond_date_list = [
                    field.name
                    for field in modelName._meta.concrete_fields
                    if field.get_internal_type() in ["DateField"]
                ]
                cond_datetime_list = [
                    field.name
                    for field in modelName._meta.concrete_fields
                    if field.get_internal_type() in ["DateTimeField"]
                ]

            query_tag = postgres_condition_generator(config_dict, cond_date_list, cond_datetime_list)
            sql_query = sql.SQL("delete from {table} where {query_tag}").format(
                table=postgres_table_name, query_tag=query_tag
            )
        else:
            sql_query = sql.SQL("delete from {table}").format(table=postgres_table_name)
        cursor = sql_engine.cursor()
        cursor.execute(sql_query)
        sql_engine.commit()
        cursor.close()
        sql_engine.close()
        return None


def app_engine_generator(request):
    # request.username/ redis username -> combination
    user_db_engine = ["", {}]
    db_type = ""
    db_connection_name = ""
    schema = tenant_schema_from_request(request)
    tenant = tenant_schema_from_request(request, original=True)
    url_string = request.path
    app_code, db_connection_name = current_app_db_extractor_url(request.user.username, url_string, tenant)
    if app_code != "":
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = schema + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
            global database_engine_dict
            engine_dict = database_engine_dict.copy()
            if engine_dict.get(db_connection_name):
                user_db_engine, db_type = engine_dict[db_connection_name]
            else:
                user_db_engine = sql_engine_gen(db_connection_name)
        if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
            with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                db_data = json.load(json_file)
                db_type = db_data[db_connection_name].get("db_type")
                json_file.close()
    return user_db_engine, db_type, schema


def current_app_db_extractor_url(username, url_string, tenant):
    # request.username/ redis username -> combination
    app_code = ""
    db_connection_name = ""
    logging.warning(url_string)
    logging.warning(url_string)
    if (
        not any(
            url_match in url_string
            for url_match in [
                "/users/selectApplication/",
                "/users/adminPanel/",
                "/users/customizeTheme/",
                "/users/dashboard/",
                "/users/selectDashboard/",
                "/users/previewTheme/",
                "/users/planner/",
                "/users/forum/",
                "/users/profile/",
                "/users/changeprofilename/",
                "/users/ajax/profilephoto_upload/",
                "/users/ajax/coverphoto_upload/",
                "/accounts/login/",
                "/accounts/logout/",
                "forum",
                "/media/",
            ]
        )
        and "/create_new/dev/application" not in url_string.lower()
        and not url_string.startswith("/account")
        and not url_string.startswith("/static")
    ):
        f_occ = url_string.find("/", url_string.find("/") + 1)
        s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
        app_code = url_string[f_occ + 1 : s_occ]
    else:
        app_code = ""
    if app_code:
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = tenant + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
    return app_code, db_connection_name


def current_app_db_extractor(request):
    # request.username/ redis username -> combination
    app_code = ""
    db_connection_name = ""
    tenant = tenant_schema_from_request(request)
    url_string = request.path
    app_code, db_connection_name = current_app_db_extractor_url(request.user.username, url_string, tenant)
    return app_code, db_connection_name


def engine_geneartor(app_code, request):
    user_db_engine = ["", {}]
    tenant = tenant_schema_from_request(request)
    if app_code:
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = tenant + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
            global database_engine_dict
            engine_dict = database_engine_dict.copy()
            user_db_engine, db_type = engine_dict[db_connection_name]
    return user_db_engine, db_type


def db_engine_extractor(db_connection_name):
    global database_engine_dict
    engine_dict = database_engine_dict.copy()
    if database_engine_dict.get(db_connection_name):
        user_db_engine, db_type = engine_dict[db_connection_name]
    else:
        user_db_engine, db_type = sql_engine_gen(db_connection_name)
    return user_db_engine, db_type


def sql_engine_gen(db_connection_name):
    engine_temp, turbodbc_con = "", []
    db_type = ""
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            db_data = db_data[db_connection_name]
            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                db_data["server"],
                db_data["port"],
                db_data["db_name"],
                db_data["username"],
                db_data["password"],
                db_data["connection_code"],
            )
            db_data["HOST"] = db_server
            db_data["PORT"] = port
            db_data["NAME"] = db_name
            db_data["USER"] = username
            db_data["PASSWORD"] = password
            del db_data["server"]
            del db_data["port"]
            del db_data["db_name"]
            del db_data["username"]
            del db_data["password"]
            db_type = db_data["db_type"]
            if db_data["db_type"] == "MSSQL":
                del db_data["db_type"]
                try:
                    quoted_temp = urllib.parse.quote_plus(
                        "driver={ODBC Driver 18 for SQL Server};server="
                        + db_data["HOST"]
                        + ","
                        + db_data["PORT"]
                        + ";database="
                        + db_data["NAME"]
                        + ";Uid="
                        + db_data["USER"]
                        + ";Pwd="
                        + db_data["PASSWORD"]
                        + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                    )
                    engine_temp = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_temp}")
                    turbodbc_con = connect(
                        driver="ODBC Driver 18 for SQL Server",
                        server=db_data["HOST"] + "," + db_data["PORT"],
                        database=db_data["NAME"],
                        uid=db_data["USER"],
                        pwd=db_data["PASSWORD"] + ";Encrypt=yes;TrustServerCertificate=yes;",
                        turbodbc_options=make_options(
                            prefer_unicode=True,
                            use_async_io=True,
                            varchar_max_character_limit=10000000,
                            autocommit=True,
                        ),
                    )
                    conn = engine_temp.connect()
                    conn.close()
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_con], "MSSQL"
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            elif db_data["db_type"] == "PostgreSQL":
                del db_data["db_type"]
                try:
                    engine_temp = {
                        "dbname": db_data["NAME"],
                        "user": db_data["USER"],
                        "password": db_data["PASSWORD"],
                        "host": db_data["HOST"],
                        "port": db_data["PORT"],
                        "schema": db_data["schema"],
                    }
                    turbodbc_con = None
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_con], "PostgreSQL"
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            json_file.close()
    return [engine_temp, turbodbc_con], db_type


def execute_read_query(sql_query, con_detail, chunksize=10**5):
    sql_query = sql_query.split(";")[0]
    sql_engine, turb_connection = con_detail
    if turb_connection not in ["", {}]:
        try:
            cursor = turb_connection.cursor()
            table = cursor.execute(sql_query).fetchallarrow().to_pandas(use_threads=True)
            cursor.close()
        except Exception as e:
            logging.warning(f"Following exception occured while reading data using Turbodbc - {e}")
            table = pd.DataFrame()
            for chunk in pd.read_sql_query(sql_query, sql_engine, chunksize=chunksize):
                table = pd.concat([table, chunk], ignore_index=True)
    else:
        table = pd.DataFrame()
        for chunk in pd.read_sql_query(sql_query, sql_engine, chunksize=chunksize):
            table = pd.concat([table, chunk], ignore_index=True)
    return table


def turbodbc_push(data_table, db_table_name, con_details):
    data_table.drop(columns=data_table.columns[data_table.isna().all()], inplace=True)
    # preparing columns
    columnnames = "("
    columnnames += ", ".join(data_table.columns)
    columnnames += ")"

    # preparing value place holders
    val_place_holder = ["?" for col in data_table.columns]
    sql_val = "("
    sql_val += ", ".join(val_place_holder)
    sql_val += ")"
    # writing sql query for turbodbc
    sql = f"""    INSERT INTO {db_table_name} {columnnames}    VALUES {sql_val}    """
    __eng, turb_connection = con_details
    cursor = turb_connection.cursor()

    try:
        # Using executemanycolumns
        cursor.executemanycolumns(
            sql, pa.Table.from_pandas(data_table, nthreads=mp.cpu_count() - 1, preserve_index=False)
        )
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        # ## Using executemany
        cursor.fast_executemany = True
        cursor.executemany(sql, data_table.to_numpy().tolist())
    cursor.close()
    return True


def pandas_push(table, db_table_name, con, if_exists="append", chunksize=10**5):
    table.to_sql(
        db_table_name,
        con=con,
        if_exists=if_exists,
        chunksize=chunksize,
        index=False,
    )
    return True


def bcpy_push(data_table, db_table_name, col_names, db_connection_name):
    server_config = bcpy_server_config(db_connection_name)
    if server_config:
        data_table["id"] = 0
        data_table = data_table.reindex(columns=col_names)
        # ## Converting to bcpy Dataframe and Pushing to SQL ##
        bdf = bcpy.DataFrame(data_table)
        sql_table = bcpy.SqlTable(sql_config, table=db_table_name)
        bdf.to_sql(sql_table, use_existing_sql_table=True)
        return True
    else:
        raise Exception("Server config not found!")


def non_standard_read_data_func(sql_query, engine2=[engine, turbodbc_connection]):
    table = execute_read_query(sql_query, engine2)
    return table


def bcpy_server_config(db_connection_name):
    server_config = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            if db_data.get(db_connection_name):
                db_data = db_data[db_connection_name]
                db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                    db_data["server"],
                    db_data["port"],
                    db_data["db_name"],
                    db_data["username"],
                    db_data["password"],
                    db_data["connection_code"],
                )
                server_config = {
                    "server": db_server + "," + port,
                    "database": db_name,
                    "schema": "dbo",
                    "username": username,
                    "password": password,
                }
            json_file.close()
    return server_config


def postgres_push(
    data_table, db_table_name, schema, con=[engine, turbodbc_connection], app_db_transaction=False
):
    if not app_db_transaction:
        sql_engine = psycopg2.connect(
            dbname=central_database_config["dbname"],
            user=central_database_config["user"],
            password=central_database_config["password"],
            host=central_database_config["host"],
            port=central_database_config["port"],
        )
    else:
        sql_engine = postgreSQL_engine_generator(con[0])
        schema = con[0]["schema"]

    data_table.drop(columns=data_table.columns[data_table.isna().all()], inplace=True)
    column = sql.SQL(", ").join([sql.Identifier(field) for field in data_table.columns])

    # preparing value place holders
    val_place_holder = ["%s" for col in data_table.columns]
    sql_val = "("
    sql_val += ", ".join(val_place_holder)
    sql_val += ")"

    if app_db_transaction:
        postgres_table_name = sql.Identifier(schema, db_table_name)
    else:
        postgres_table_name = sql.Identifier(db_table_name)
    # writing sql query for postgres
    sql_query = sql.SQL("INSERT INTO {table} ({columnnames}) VALUES {sql_val}").format(
        table=postgres_table_name, columnnames=column, sql_val=sql.SQL(sql_val)
    )

    cursor = sql_engine.cursor()
    cursor.executemany(sql_query, data_table.to_numpy().tolist())
    sql_engine.commit()
    cursor.close()
    sql_engine.close()
    return True


def adv_query_generator(adv_condition):
    query_tag2 = ""
    if adv_condition["condition"] == "Greater than":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "IS"
                + " "
                + "NOT NULL"
                + " "
                + adv_condition["and_or"]
            )
        else:
            try:
                bool(float(adv_condition["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                query_tag2 = (
                    query_tag2
                    + " "
                    + (adv_condition["column_name"])
                    + " "
                    + ">"
                    + " "
                    + "'"
                    + adv_condition["input_value"]
                    + "'"
                    + " "
                    + adv_condition["and_or"]
                )
            else:
                query_tag2 = (
                    query_tag2
                    + " "
                    + (adv_condition["column_name"])
                    + " "
                    + ">"
                    + " "
                    + adv_condition["input_value"]
                    + " "
                    + adv_condition["and_or"]
                )
    elif adv_condition["condition"] == "Smaller than":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "IS"
                + " "
                + "NOT NULL"
                + " "
                + adv_condition["and_or"]
            )
        else:
            try:
                bool(float(adv_condition["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                query_tag2 = (
                    query_tag2
                    + " "
                    + (adv_condition["column_name"])
                    + " "
                    + "<"
                    + " "
                    + "'"
                    + adv_condition["input_value"]
                    + "'"
                    + " "
                    + adv_condition["and_or"]
                )
            else:
                query_tag2 = (
                    query_tag2
                    + " "
                    + (adv_condition["column_name"])
                    + " "
                    + "<"
                    + " "
                    + adv_condition["input_value"]
                    + " "
                    + adv_condition["and_or"]
                )
    elif adv_condition["condition"] == "Equal to":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "IS"
                + " "
                + "NULL"
                + " "
                + adv_condition["and_or"]
            )
        else:
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "="
                + " "
                + "'"
                + adv_condition["input_value"]
                + "'"
                + " "
                + adv_condition["and_or"]
            )
    elif adv_condition["condition"] == "IN":
        if type(adv_condition["input_value"]) == list:
            tuple_ = "("
            for k in adv_condition["input_value"]:
                tuple_ = tuple_ + f"'{k}',"
            tuple_ = tuple_ + ")"
            tuple_ = tuple_.replace(",)", ")")
            defaultVal = tuple_
        else:
            defaultVal = adv_condition["input_value"]
        query_tag2 = (
            query_tag2
            + " "
            + (adv_condition["column_name"])
            + " "
            + "IN"
            + " "
            + defaultVal
            + " "
            + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "NOT IN":
        if type(adv_condition["input_value"]) == list:
            tuple_ = "("
            for k in adv_condition["input_value"]:
                tuple_ = tuple_ + f"'{k}',"
            tuple_ = tuple_ + ")"
            tuple_ = tuple_.replace(",)", ")")
            defaultVal = tuple_
        else:
            defaultVal = adv_condition["input_value"]
        query_tag2 = (
            query_tag2
            + " "
            + (adv_condition["column_name"])
            + " "
            + "NOT IN"
            + " "
            + defaultVal
            + " "
            + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Not Equal to":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "IS"
                + " "
                + "NOT NULL"
                + " "
                + adv_condition["and_or"]
            )
        else:
            query_tag2 = (
                query_tag2
                + " "
                + (adv_condition["column_name"])
                + " "
                + "!="
                + " "
                + "'"
                + adv_condition["input_value"]
                + "'"
                + " "
                + adv_condition["and_or"]
            )

    return query_tag2


def postgres_condition_generator(config_dict, cond_date_list, cond_datetime_list):
    condition_string = ""
    condition_list = []
    for i in range(0, len(config_dict["condition"])):
        if (
            config_dict["condition"][i]["condition"] != "Between"
            and config_dict["condition"][i]["condition"] != "IN"
        ):
            if config_dict["condition"][i]["column_name"] in cond_date_list:
                config_dict["condition"][i]["input_value"] = pd.to_datetime(
                    config_dict["condition"][i]["input_value"]
                ).strftime("%Y-%m-%d")

            if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                config_dict["condition"][i]["input_value"] = pd.to_datetime(
                    config_dict["condition"][i]["input_value"]
                ).strftime("%Y-%m-%d %H:%M:%S")
        else:
            if config_dict["condition"][i]["condition"] != "IN":
                if config_dict["condition"][i]["column_name"] in cond_date_list:
                    config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value_lower"]
                    ).strftime("%Y-%m-%d")
                    config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value_upper"]
                    ).strftime("%Y-%m-%d")

                if config_dict["condition"][i]["column_name"] in cond_datetime_list:
                    config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value_lower"]
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                        config_dict["condition"][i]["input_value_upper"]
                    ).strftime("%Y-%m-%d %H:%M:%S")

        if config_dict["condition"][i]["condition"] == "Greater than":
            try:
                bool(float(config_dict["condition"][i]["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                condition_list.append(
                    sql.SQL("{field} > {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
            else:
                condition_list.append(
                    sql.SQL("{field} > {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
        elif config_dict["condition"][i]["condition"] == "Smaller than":
            try:
                bool(float(config_dict["condition"][i]["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                condition_list.append(
                    sql.SQL("{field} < {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
            else:
                condition_list.append(
                    sql.SQL("{field} < {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
        elif config_dict["condition"][i]["condition"] == "Smaller than equal to":
            try:
                bool(float(config_dict["condition"][i]["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                condition_list.append(
                    sql.SQL("{field} <= {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
            else:
                condition_list.append(
                    sql.SQL("{field} <= {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
        elif config_dict["condition"][i]["condition"] == "Greater than equal to":
            try:
                bool(float(config_dict["condition"][i]["input_value"]))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                condition_list.append(
                    sql.SQL("{field} >= {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
            else:
                condition_list.append(
                    sql.SQL("{field} >= {value} {and_or}").format(
                        field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                        value=sql.Literal(config_dict["condition"][i]["input_value"]),
                        and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                    )
                )
        elif config_dict["condition"][i]["condition"] == "Equal to":
            condition_list.append(
                sql.SQL("{field} = {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal(config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Between":
            condition_list.append(
                "{field} BETWEEN {input_value_lower} AND {input_value_upper} {and_or}".format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    input_value_lower=sql.Literal(config_dict["condition"][i]["input_value_lower"]),
                    input_value_upper=sql.Literal(config_dict["condition"][i]["input_value_upper"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "IN":
            condition_list.append(
                sql.SQL("{field} IN {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.SQL(config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "NOT IN":
            condition_list.append(
                sql.SQL("{field} NOT IN {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.SQL(config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Not Equal to":
            condition_list.append(
                sql.SQL("{field} != {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal(config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Starts with":
            condition_list.append(
                sql.SQL("{field} LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal(config_dict["condition"][i]["input_value"] + "%%"),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Ends with":
            condition_list.append(
                sql.SQL("{field} LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal("%%" + config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Contains":
            condition_list.append(
                sql.SQL("{field} LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal("%%" + config_dict["condition"][i]["input_value"] + "%%"),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Not Starts with":
            condition_list.append(
                sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal("%%" + config_dict["condition"][i]["input_value"]),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Not Ends with":
            condition_list.append(
                sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal(config_dict["condition"][i]["input_value"] + "%%"),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )
        elif config_dict["condition"][i]["condition"] == "Not Contains":
            condition_list.append(
                sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                    field=sql.Identifier(config_dict["condition"][i]["column_name"]),
                    value=sql.Literal("%%" + config_dict["condition"][i]["input_value"] + "%%"),
                    and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                )
            )

    condition_string = sql.SQL(" ").join([i for i in condition_list])
    return condition_string


def postgreSQL_engine_generator(connection_details):
    sql_engine = psycopg2.connect(
        dbname=connection_details["dbname"],
        user=connection_details["user"],
        password=connection_details["password"],
        host=connection_details["host"],
        port=connection_details["port"],
    )
    return sql_engine
