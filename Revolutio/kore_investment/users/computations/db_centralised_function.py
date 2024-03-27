import io
import json
import logging
import multiprocessing as mp
import os
import urllib

import bcpy
from django.apps import apps
from django_multitenant.utils import get_current_tenant
import numpy as np
import oracledb
import pandas as pd
import psycopg2
from psycopg2 import sql
import pyarrow as pa
from sqlalchemy import create_engine, text
from turbodbc import make_options

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
from kore_investment.utils.utilities import tenant_schema_from_request

from ..database_handlers.DB_query_generator import OracleSQLQueryGenerator, postgres_condition_generator
from .db_connection_handlers import (
    db_connection_generator,
    mssql_engine_generator,
    postgreSQL_engine_generator,
)

admin_tables = [
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
    "failed_login_alerts",
    "dashboard_config",
    "login_trail",
    "audit_trail",
    "Instance",
    "notification_management",
    "applicationAccess",
]

auth_tables = [
    "auth_group",
    "user_groups",
]

sys_tables = [
    "Templates",
    "usergroup_approval",
    "CountryMaster",
    "CurrencyMaster",
    "Application",
    "Curve_Repository",
    "computation_model_configuration",
    "Profile",
    "Category_Subelement",
    "Hierarchy_table",
    "Curve_Data",
    "computation_model_flowchart",
    "jobs_scheduled",
    "group_config",
    "Draft_FormData",
    "Error_Master_Table",
    "Business_Models",
    "computation_model_run_history",
    "Users_urlMap",
    "Tasks_Planner",
    "Ocr_Template",
    "NavigationSideBar",
    "Holiday_Calendar_Repository",
    "Process_subprocess_flowchart",
    "UserPermission_Master",
    "Plan_Buckets",
    "permissionaccess",
    "TabScreens",
    "ApprovalTable",
    "Model_Repository",
    "Upload_Error_History",
    "summary_table",
    "DraftProcess",
    "user_approval",
    "configuration_parameter",
    "Tables",
    "allocated_licences",
    "Category_Subelement_Attributes",
    "UserConfig",
    "Plans",
    "computation_output_repository",
    "Hierarchy_levels",
    "data_mapping_error_report",
    "Hierarchy_groups",
    "userpermission_interim",
    "group_details",
    "ml_model_repository",
    "UserProfile",
    "ConfigTable",
    "Process_flow_model",
    "computation_function_repository",
    "computation_scenario_repository",
    "data_management_computed_fields_config",
    "data_management_computed_fields_flow",
    "application_theme",
    "template_theme",
    "flow_monitor_error_log",
    "alerts",
    "static_page_config",
    "audit_operation",
    "external_application_master",
    "system_management_table",
    "smtp_configuration",
    "event_master",
    "system_application_master",
]

sys_tables = [i for i in sys_tables if i not in admin_tables]


def get_model_class(
    model_name, request, db_connection_name="", db_engine=["", None], db_type="MSSQL", tenant=None
):
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
        "failed_login_alerts",
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
                user_db_engine, db_type, schema = app_engine_generator(request, tenant=tenant)
        input_validation_check(model_name)
        if not model_name in sys_tables:
            if db_type == "MSSQL":
                query = f"SELECT fields, other_config FROM users_tables WHERE tablename='{model_name}'"
            elif db_type == "Oracle":
                query = f"SELECT fields, other_config FROM users_tables WHERE tablename='{model_name}'"
            else:
                query = f"SELECT fields, other_config FROM {user_db_engine[0]['schema']}.users_tables WHERE tablename='{model_name}'"
            json_data = non_standard_read_data_func(query, user_db_engine, db_type)
            if json_data.other_config.iloc[0]:
                other_config = json.loads(json_data.other_config.iloc[0])
            else:
                other_config = {}
        else:
            if db_type == "MSSQL":
                query = f"SELECT fields FROM users_tables WHERE tablename='{model_name}'"
            elif db_type == "Oracle":
                query = f"SELECT fields FROM users_tables WHERE tablename='{model_name}'"
            else:
                query = f"SELECT fields FROM {user_db_engine[0]['schema']}.users_tables WHERE tablename='{model_name}'"
            json_data = non_standard_read_data_func(query, user_db_engine, db_type)
            other_config = {}
        json_data = json.loads(json_data.fields.iloc[0])
        model = ModelInfo(model_name, json_data, other_config=other_config)
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
    fast_executemany=False,
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

    instance = get_current_tenant()
    if schema == "":
        if instance:
            schema = instance.name
        else:
            if original_table_name in admin_tables:
                schema = "public"
            else:
                schema = ""
    else:
        pass

    db_connection_name = ""
    app_db_transaction = True
    if if_app_db:
        DB_table_name = "users_" + original_table_name.lower()
        if original_table_name:
            table_name = original_table_name
        if original_table_name not in admin_tables:
            if not engine_override:
                if instance:
                    curr_app_code, db_connection_name, user_app_db_engine, db_type, schema = (
                        application_database_details_extractor(request, tenant=schema)
                    )
                else:
                    curr_app_code, db_connection_name, user_app_db_engine, db_type, schema = (
                        application_database_details_extractor(request, tenant="")
                    )
                if user_app_db_engine != "":
                    con = user_app_db_engine
                else:
                    pass
            else:
                pass
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
                    "Table": original_table_name,
                },
                "condition": [],
            },
            engine2=con,
            engine_override=True,
            db_type=db_type,
            if_app_db=if_app_db,
            schema=schema,
        )
    if db_type == "MSSQL":
        column_type_query = f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{DB_table_name}' AND DATA_TYPE in ('datetime','datetime2','date') "
        datecolumns = list(
            set(non_standard_read_data_func(column_type_query, con, db_type).iloc[:, 0].to_list())
            & set(table.columns.to_list())
        )

        column_type_query2 = f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{DB_table_name}' AND DATA_TYPE in ('date') "
        datecolumns2 = list(
            set(non_standard_read_data_func(column_type_query2, con, db_type).iloc[:, 0].to_list())
            & set(table.columns.to_list())
        )

        if len(datecolumns) > 0:
            for cols in datecolumns:
                if cols in datecolumns2:
                    table[cols] = pd.to_datetime(table[cols]).dt.date
                else:
                    table[cols] = pd.to_datetime(table[cols])
        else:
            pass
        
        if len(table) * len(table.columns) <= 2 * (10**5):
            #     ### TurbODBC Push
            #     ## Pandas push if turbodbc fails
            pandas_push(table, DB_table_name, con[0], "append", chunksize)
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
                #     ### TurbODBC Push
                #     ## Pandas push if turbodbc fails
                if fast_executemany:
                    if if_app_db:
                        app_code, db_connection_name = current_app_db_extractor(request=request)
                        if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                            with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                                connection_details = {}
                                db_data = json.load(json_file)
                                db_data = db_data[db_connection_name]
                                db_server, port, db_name, username, password = (
                                    decrypt_existing_db_credentials(
                                        db_data["server"],
                                        db_data["port"],
                                        db_data["db_name"],
                                        db_data["username"],
                                        db_data["password"],
                                        db_data["connection_code"],
                                    )
                                )
                                connection_details["server"] = db_server
                                connection_details["port"] = port
                                connection_details["db_name"] = db_name
                                connection_details["username"] = username
                                connection_details["password"] = password
                                db_type = db_data["db_type"]
                                engine_temp = mssql_engine_generator(
                                    connection_details, fast_executemany=True
                                )
                                json_file.close()
                            pandas_push(table, DB_table_name, engine_temp, "append", chunksize)
                            engine_temp.dispose()
                    else:
                        filename = f"{PLATFORM_FILE_PATH}external_databases.json"
                        db_data = {}
                        if os.path.exists(filename):
                            with open(filename) as json_file:
                                connection_details = {}
                                db_data = json.load(json_file)
                                db_data = db_data[connection_name]
                                db_server, port, db_name, username, password = (
                                    decrypt_existing_db_credentials(
                                        db_data["server"],
                                        db_data["port"],
                                        db_data["db_name"],
                                        db_data["username"],
                                        db_data["password"],
                                        db_data["connection_code"],
                                    )
                                )
                                connection_details["server"] = db_server
                                connection_details["port"] = port
                                connection_details["db_name"] = db_name
                                connection_details["username"] = username
                                connection_details["password"] = password
                                engine_temp = mssql_engine_generator(
                                    connection_details, fast_executemany=True
                                )
                                json_file.close()
                            pandas_push(table, DB_table_name, engine_temp, "append", chunksize)
                            engine_temp.dispose()

                else:
                    pandas_push(table, DB_table_name, con[0], "append", chunksize)
        return ["Push Successful"]
    elif db_type == "PostgreSQL":
        if original_table_name in admin_tables:
            con[0]["schema"] = schema
        else:
            schema = con[0]["schema"]

        column_name = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "information_schema.columns",
                    "Columns": ["column_name", "data_type"],
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
                        "condition": "IN",
                        "input_value": ["timestamp with time zone", "boolean"],
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
        column_name_datetime = column_name[column_name["data_type"] == "timestamp with time zone"][
            "column_name"
        ].tolist()
        column_name_boolean = column_name[column_name["data_type"] == "boolean"]["column_name"].tolist()
        table.rename({i: i.lower() for i in table.columns}, axis=1, inplace=True)
        for i in column_name_datetime:
            if i in table.columns.tolist():
                table[i] = pd.to_datetime(table[i]).dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                continue
        table = table.replace({np.nan: None})
        for i in column_name_boolean:
            if i in table.columns.tolist():
                table[i] = table[i].astype(object)
                table = table.replace({1: "1", 0: "0", "1.0": "1", "0.0": "0"})
            else:
                continue
        if (
            original_table_name in admin_tables
            and original_table_name not in auth_tables
            and "instance_id" not in table.columns
        ):
            if request != "" and not request.user.is_anonymous:
                instance_id = request.user.instance_id
            else:
                instance = get_current_tenant()
                instance_id = instance.id
                schema = instance.name
            table["instance_id"] = instance_id
        else:
            pass
        postgres_push(table, DB_table_name, schema, con=con, app_db_transaction=app_db_transaction)
        redis_instance.delete(db_connection_name + DB_table_name)

        return ["Push Successful"]
    elif db_type == "Oracle":
        column_data_type = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "all_tab_columns",
                    "Columns": ["column_name", "data_type"],
                },
                "condition": [
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": DB_table_name.upper(),
                        "and_or": "",
                    }
                ],
            },
            engine2=con,
            engine_override=True,
            db_type=db_type,
        )
        column_data_type["column_name"] = column_data_type["column_name"].str.lower()
        date_type_columns = column_data_type[column_data_type["data_type"] == "DATE"]["column_name"].tolist()
        datetime_type_columns = column_data_type[column_data_type["data_type"].str.startswith("TIMESTAMP")][
            "column_name"
        ].tolist()
        blob_type_columns = column_data_type[column_data_type["data_type"] == "BLOB"]["column_name"].tolist()
        if len(datetime_type_columns) > 0:
            for i in datetime_type_columns:
                if i in table.columns:
                    table[i] = pd.to_datetime(table[i])
                else:
                    continue
        else:
            pass
        if len(date_type_columns) > 0:
            for cols in date_type_columns:
                if cols in table.columns:
                    table[cols] = pd.to_datetime(table[cols]).dt.date
                else:
                    continue
        else:
            pass
        #     pass
        table = table.replace({np.nan: None})
        if len(blob_type_columns) > 0:
            columns = ", ".join(table.columns.tolist())
            column_data_type = column_data_type.set_index("column_name")["data_type"].to_dict()
            value_string = "("
            for col in table.columns:
                if column_data_type[col.lower()] == "BLOB":
                    value_string += f":{col}, "
                elif column_data_type[col.lower()] in ["NUMBER", "INTEGER", "FLOAT", "NUMBER(3)"]:
                    value_string += f":{col}, "
                else:
                    value_string += f":{col}, "
            value_string = value_string.rstrip(", ")
            value_string += ")"
            insert_query = f"INSERT INTO {DB_table_name} ({columns}) VALUES {value_string}"
            insert_query = text(insert_query)
            for i in table.columns:
                if i.lower() in blob_type_columns:
                    table[i] = table[i].map(
                        lambda x: io.BytesIO(x.encode("utf-8")).getvalue(), na_action="ignore"
                    )
            data_list = table.to_dict("records")
            with con[0].begin() as conn:
                conn.execute(insert_query, data_list)
                conn.commit()
                conn.close()
        else:
            pandas_push(table, DB_table_name, con[0], "append", chunksize)
        return True


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
    fetch_all_entries=False,
    access_controller=True,
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
    else:
        pass
    is_active_flag_bool = False
    instance = get_current_tenant()
    table = config_dict["inputs"]["Table"]
    if if_app_db:
        if (
            table
            not in [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "INFORMATION_SCHEMA.constraint_column_usage",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]
            and not table.startswith("information_schema")
            and not table.startswith("INFORMATION_SCHEMA")
        ):
            sql_table_name = "users_" + table.lower()
        else:
            sql_table_name = table
    else:
        sql_table_name = table
    columnlist = config_dict["inputs"]["Columns"]

    if if_app_db:
        if table not in admin_tables:
            if not engine_override:
                user_app_db_engine, db_type2, schema = app_engine_generator(request)
                if db_type2:
                    db_type = db_type2
                if user_app_db_engine != ["", None]:
                    engine2 = user_app_db_engine
            else:
                pass
        else:
            pass
    else:
        pass

    if config_dict.get("advanced_query_configs"):
        if config_dict["advanced_query_configs"].get("execute_advanced_query", False):
            if config_dict["advanced_query_configs"].get("advanced_query"):
                query = config_dict["advanced_query_configs"].get("advanced_query")
                if config_dict.get("chunk_size"):
                    return non_standard_read_data_func(query, engine2, db_type,chunksize = config_dict.get("chunk_size",10**5),set_iter_size=True)
                else:
                    return non_standard_read_data_func(query, engine2, db_type)
        else:
            pass
    else:
        pass

    apply_joins = False

    if config_dict.get("apply_join"):
        apply_joins = config_dict.get("apply_join")

    join_table_names = []
    if apply_joins:
        join_table_names = config_dict.get("join_table_names").copy()
        for i in range(len(config_dict.get("join_table_names"))):
            if if_app_db:
                if (
                    config_dict.get("join_table_names")[i]
                    not in [
                        "information_schema.columns",
                        "information_schema.tables",
                        "auth_group",
                        "auditlog_logentry",
                        "django_apscheduler_djangojobexecution",
                        "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                        "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                        "INFORMATION_SCHEMA.constraint_column_usage",
                        "master.dbo.sysdatabases",
                        "sys.default_constraints",
                    ]
                    and not config_dict.get("join_table_names")[i].startswith("information_schema")
                    and not config_dict.get("join_table_names")[i].startswith("INFORMATION_SCHEMA")
                ):
                    config_dict.get("join_table_names")[i] = (
                        "users_" + config_dict.get("join_table_names")[i].lower()
                    )
                else:
                    pass
            else:
                pass
        if config_dict["join_table_data"].get("join_table_level_conditions"):
            join_table_level_conditions_keys = list(
                config_dict["join_table_data"]["join_table_level_conditions"].keys()
            )
            for join_table_key in join_table_level_conditions_keys:
                if if_app_db:
                    if (
                        table
                        not in [
                            "information_schema.columns",
                            "information_schema.tables",
                            "auth_group",
                            "auditlog_logentry",
                            "django_apscheduler_djangojobexecution",
                            "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                            "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                            "INFORMATION_SCHEMA.constraint_column_usage",
                            "master.dbo.sysdatabases",
                            "sys.default_constraints",
                        ]
                        and not join_table_key.startswith("information_schema")
                        and not join_table_key.startswith("INFORMATION_SCHEMA")
                    ):
                        config_dict["join_table_data"]["join_table_level_conditions"][
                            "users_" + join_table_key
                        ] = config_dict["join_table_data"]["join_table_level_conditions"].pop(join_table_key)
                    else:
                        pass
                else:
                    pass
    else:
        pass
    join_table_group_by_select_columns = ""
    join_table_group_by_query = ""
    group_by_aggregations = {}
    if config_dict.get("group_by_configs"):
        group_by_columns = config_dict["group_by_configs"].get("group_by_columns")
        if group_by_columns:
            if apply_joins:
                join_table_group_by_select_columns, join_table_group_by_query, group_by_aggregations = (
                    group_by_query_generator(config_dict, if_app_db)
                )
                config_dict["inputs"]["group_by_aggregation"] = group_by_aggregations
                config_dict["inputs"]["group_by"] = join_table_group_by_query.split(", ")
            else:
                if config_dict["group_by_configs"].get("aggregations"):
                    config_dict["inputs"]["group_by_aggregation"] = config_dict["group_by_configs"][
                        "aggregations"
                    ].get(table, {})
                config_dict["inputs"]["group_by"] = group_by_columns.get(table).copy()
                columnlist = group_by_columns.get(table).copy()
        else:
            pass

    else:
        pass

    if db_type == "MSSQL":
        agg_query = ""
        order_query = ""
        if config_dict.get("aliases"):
            aliases = config_dict.get("aliases")
            alias_columnlist = []
            for field in columnlist:
                if aliases.get(field, "") != "":
                    alias_columnlist.append(f'{field} AS "{aliases.get(field)}"')
                else:
                    alias_columnlist.append(field)
            column = ",".join(alias_columnlist)
        else:
            column = ",".join(columnlist)

        join_columns = ""
        join_query = ""
        if apply_joins:
            join_columns, join_query = join_query_generator(config_dict, request, engine2, db_type)
            table_names = config_dict.get("join_table_names")
            if join_table_group_by_select_columns:
                column = join_table_group_by_select_columns
                join_columns = join_table_group_by_select_columns
            if config_dict["join_table_data"].get("join_conditions"):
                if not config_dict.get("condition"):
                    config_dict["condition"] = []
                else:
                    if config_dict["condition"][-1]["and_or"] == ")":
                        config_dict["condition"][-1]["and_or"] = ") AND "
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                for join_table in config_dict["join_table_data"]["join_conditions"]:
                    for condition in config_dict["join_table_data"]["join_conditions"][join_table]:
                        if "users_" + condition["table_name"] in table_names:
                            condition["table_name"] = "users_" + condition["table_name"]
                        config_dict["condition"].append(condition)
            else:
                pass
        order_by_query_string = ""
        if config_dict.get("order_by_configs"):
            order_by_query_string = order_by_query_generator(config_dict, if_app_db)

        if "Agg_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Agg_Type"] != "":
                agg_query = agg_query + " " + config_dict["inputs"]["Agg_Type"] + " "
        if "Order_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Order_Type"] != "":
                order_query = order_query + " " + config_dict["inputs"]["Order_Type"] + " "
                if "Offset" in config_dict["inputs"]:
                    order_query = order_query + " OFFSET " + str(config_dict["inputs"]["Offset"]) + " ROWS "
                    if "Fetch_next" in config_dict["inputs"]:
                        order_query = (
                            order_query
                            + " FETCH NEXT "
                            + str(config_dict["inputs"]["Fetch_next"])
                            + " ROWS ONLY "
                        )
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
        if config_dict["inputs"].get("group_by_aggregation"):
            for agg_col, aggregation in config_dict["inputs"].get("group_by_aggregation").items():
                if type(aggregation) is list:
                    for item in aggregation:
                        aggregation_type = item.get("agg_type")
                        aggregation_alias = item.get("agg_alias")
                        if not aggregation_alias:
                            aggregation_alias = agg_col
                        if aggregation_type == "sum":
                            column += f', SUM({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "average":
                            column += f', AVG({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "variance":
                            column += f', VARP({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "standard deviation":
                            column += f', STDEVP({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "count":
                            column += f', COUNT({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "count distinct":
                            column += f', COUNT(DISTINCT {agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "maximum":
                            column += f', MAX({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "minimum":
                            column += f', MIN({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "percentage of total":
                            column += (
                                f', SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS "{aggregation_alias}"'
                            )
                        else:
                            continue
                else:
                    if aggregation == "sum":
                        column += f", SUM({agg_col}) AS {agg_col}"
                    elif aggregation == "average":
                        column += f", AVG({agg_col}) AS {agg_col}"
                    elif aggregation == "variance":
                        column += f", VARP({agg_col}) AS {agg_col}"
                    elif aggregation == "standard deviation":
                        column += f", STDEVP({agg_col}) AS {agg_col}"
                    elif aggregation == "count":
                        column += f", COUNT({agg_col}) AS {agg_col}"
                    elif aggregation == "count distinct":
                        column += f", COUNT(DISTINCT {agg_col}) AS {agg_col}"
                    elif aggregation == "maximum":
                        column += f", MAX({agg_col}) AS {agg_col}"
                    elif aggregation == "minimum":
                        column += f", MIN({agg_col}) AS {agg_col}"
                    elif aggregation == "percentage of total":
                        column += f", SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS {agg_col}"
                    else:
                        continue
            column = column.lstrip(", ")
            if apply_joins:
                join_columns = column
        else:
            pass

        group_by_string = ""
        if config_dict["inputs"].get("group_by"):
            group_by_cols = ",".join(config_dict["inputs"]["group_by"])
            group_by_string = f"GROUP BY {group_by_cols}"
        else:
            pass
        query_tag = ""
        query_tag2 = ""
        sql_query2 = ""
        new_config_cond = 0
        new_config_adv_cond = 0
        skip = 0

        if (
            table
            not in [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]
            and table not in admin_tables
            and table not in sys_tables
            and if_app_db
        ):
            modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
            field_list = {field.name: field.verbose_name.title() for field in modelName.concrete_fields}
            if access_controller:
                access_controls = modelName.get_access_controls()
                if access_controls and request:
                    if config_dict.get("condition"):
                        if config_dict["condition"][0].get("constraintName"):
                            new_config_cond = 1
                        else:
                            pass
                    else:
                        pass
                    if access_controls["access_type"] == "created_by_user":
                        if config_dict.get("condition"):
                            if config_dict["condition"][-1]["and_or"] == ")":
                                config_dict["condition"][-1]["and_or"] = ") AND "
                            else:
                                config_dict["condition"][-1]["and_or"] = "AND"
                        else:
                            pass
                        access_control_condition = {
                            "column_name": "created_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "and_or": "OR",
                        }
                        access_control_condition1 = {
                            "column_name": "modified_by",
                            "condition": "Equal to",
                            "input_value": request.user.username,
                            "and_or": ")",
                        }
                        if new_config_cond:
                            access_control_condition["constraintName"] = "access_control_constraint"
                            access_control_condition["ruleSet"] = "access_control_rule1"
                            access_control_condition1["constraintName"] = "access_control_constraint"
                            access_control_condition1["ruleSet"] = "access_control_rule2"
                            access_control_condition1["and_or"] = ""
                        else:
                            access_control_condition["column_name"] = (
                                f"({access_control_condition['column_name']}"
                            )
                            access_control_condition["and_or"] = "OR"
                        config_dict["condition"].append(access_control_condition)
                        config_dict["condition"].append(access_control_condition1)
                    elif access_controls["access_type"] == "custom":
                        if config_dict.get("condition"):
                            if config_dict["condition"][-1]["and_or"] == ")":
                                config_dict["condition"][-1]["and_or"] = ") AND "
                            else:
                                config_dict["condition"][-1]["and_or"] = "AND"
                        else:
                            pass
                        additional_config = access_controls["additional_config"]
                        control_measure = additional_config["controlMeasure"]
                        access_control_condition_list = []
                        for cust_acc_col in additional_config["fields"]:
                            if cust_acc_col in ["created_by", "modified_by"]:
                                access_control_condition_list.append(
                                    {
                                        "column_name": cust_acc_col,
                                        "condition": "Equal to",
                                        "input_value": request.user.username,
                                        "and_or": "",
                                    }
                                )
                            else:
                                if (
                                    modelName.get_field(cust_acc_col).get_internal_type()
                                    == "MultiselectField"
                                ):
                                    multi_select_config = json.loads(
                                        modelName.get_field(cust_acc_col).mulsel_config
                                    )
                                    master_table = multi_select_config["value"][0]
                                    master_column = multi_select_config["masterColumn"][0]
                                    if control_measure in ["any_email", "all_email"]:
                                        input_value = request.user.email
                                    else:
                                        input_value = request.user.username

                                    corresponding_id = execute_read_query(
                                        f"Select id from users_{master_table.lower()} where {master_column} = '{input_value}'",
                                        engine2,
                                        db_type,
                                    )
                                    if not corresponding_id.empty:
                                        input_value = f'"{str(corresponding_id.iloc[0,0])}":'
                                    else:
                                        pass
                                    access_control_condition_list.append(
                                        {
                                            "column_name": cust_acc_col,
                                            "condition": "Contains",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    )
                                else:
                                    if control_measure in ["any_email", "all_email"]:
                                        input_value = request.user.email
                                    else:
                                        input_value = request.user.username
                                    access_control_condition_list.append(
                                        {
                                            "column_name": cust_acc_col,
                                            "condition": "Equal to",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    )
                        if new_config_cond:
                            for i in range(len(access_control_condition_list)):
                                access_control_condition_list[i][
                                    "constraintName"
                                ] = "access_control_constraint"
                                if control_measure in ["any", "any_email"]:
                                    access_control_condition_list[i]["ruleSet"] = f"access_control_rule{i}"
                                else:
                                    access_control_condition_list[i]["ruleSet"] = f"access_control_rule"
                        else:
                            access_control_condition_list[0][
                                "column_name"
                            ] = f'({access_control_condition_list[0]["column_name"]}'
                            access_control_condition_list[-1]["and_or"] = ")"
                            for i in range(len(access_control_condition_list)):
                                if i != len(access_control_condition_list) - 1:
                                    if control_measure in ["any", "any_email"]:
                                        access_control_condition_list[i]["and_or"] = "OR"
                                    else:
                                        access_control_condition_list[i]["and_or"] = "AND"
                                else:
                                    continue
                        if access_control_condition_list:
                            config_dict["condition"] += access_control_condition_list
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            field_list = {}

        if config_dict.get("condition"):
            if config_dict["condition"] is not None:
                if config_dict["condition"][0].get("constraintName"):
                    if config_dict["condition"][0]["constraintName"] != "":
                        new_config_cond = 1
                if config_dict["condition"][0].get("skip"):
                    skip = 1

            if table not in sys_tables and not fetch_all_entries:
                if "is_active_flag" in field_list:
                    is_active_flag_bool = True
                    if "is_active_flag" in config_dict["condition"][-1]["column_name"]:
                        config_dict["condition"][-1]["and_or"] = ") AND "
                    elif config_dict["condition"][-1]["and_or"] == ")":
                        config_dict["condition"][-1]["and_or"] = ") AND "
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                    is_active_condition1 = {
                        "condition": "Equal to",
                        "input_value": "NULL",
                        "and_or": "",
                    }
                    if new_config_cond:
                        is_active_condition1["column_name"] = "is_active_flag"
                    else:
                        is_active_condition1["column_name"] = "(is_active_flag"
                    is_active_condition = {
                        "column_name": "is_active_flag",
                        "condition": "Not Equal to",
                        "input_value": "No",
                        "and_or": ")",
                    }
                    if new_config_cond:
                        is_active_condition1["constraintName"] = "is_active_contraint"
                        is_active_condition1["ruleSet"] = "is_active_rule_set1"
                        is_active_condition["constraintName"] = "is_active_contraint"
                        is_active_condition["ruleSet"] = "is_active_rule_set2"
                        is_active_condition["and_or"] = ""
                    else:
                        is_active_condition1["and_or"] = "OR"

                    config_dict["condition"].append(is_active_condition1)
                    config_dict["condition"].append(is_active_condition)
                else:
                    pass
            else:
                pass

            if apply_joins:
                if new_config_cond:
                    for i, table in enumerate(join_table_names):
                        if i == 0:
                            continue
                        if (
                            table
                            not in [
                                "information_schema.columns",
                                "information_schema.tables",
                                "auth_group",
                                "auditlog_logentry",
                                "django_apscheduler_djangojobexecution",
                                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                                "master.dbo.sysdatabases",
                                "sys.default_constraints",
                            ]
                            and table not in admin_tables
                            and table not in sys_tables
                            and if_app_db
                        ):
                            modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
                            field_list = {
                                field.name: field.verbose_name.title() for field in modelName.concrete_fields
                            }
                            if table not in sys_tables and not fetch_all_entries:
                                if "is_active_flag" in field_list:
                                    config_dict["condition"].append(
                                        {
                                            "table_name": config_dict.get("join_table_names")[i],
                                            "column_name": "is_active_flag",
                                            "condition": "Equal to",
                                            "input_value": "NULL",
                                            "and_or": "",
                                            "constraintName": "is_active_contraint" + str(i),
                                            "ruleSet": "is_active_rule_set" + str(i + 1),
                                        }
                                    )
                                    config_dict["condition"].append(
                                        {
                                            "table_name": config_dict.get("join_table_names")[i],
                                            "column_name": "is_active_flag",
                                            "condition": "Not Equal to",
                                            "input_value": "No",
                                            "and_or": "",
                                            "constraintName": "is_active_contraint" + str(i),
                                            "ruleSet": "is_active_rule_set" + str(i),
                                        }
                                    )
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                else:
                    for i, table in enumerate(join_table_names):
                        if i == 0:
                            continue
                        if (
                            table
                            not in [
                                "information_schema.columns",
                                "information_schema.tables",
                                "auth_group",
                                "auditlog_logentry",
                                "django_apscheduler_djangojobexecution",
                                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                                "master.dbo.sysdatabases",
                                "sys.default_constraints",
                            ]
                            and table not in admin_tables
                            and table not in sys_tables
                            and if_app_db
                        ):
                            modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
                            field_list = {
                                field.name: field.verbose_name.title() for field in modelName.concrete_fields
                            }
                            if table not in sys_tables and not fetch_all_entries:
                                if "is_active_flag" in field_list:
                                    if "is_active_flag" in config_dict["condition"][-1]["column_name"]:
                                        config_dict["condition"][-1]["and_or"] = ") AND "
                                    elif config_dict["condition"][-1]["and_or"] == ")":
                                        config_dict["condition"][-1]["and_or"] = ") AND "
                                    else:
                                        config_dict["condition"][-1]["and_or"] = "AND"
                                    config_dict["condition"].append(
                                        {
                                            "table_name": config_dict.get("join_table_names")[i],
                                            "column_name": "(is_active_flag",
                                            "condition": "Equal to",
                                            "input_value": "NULL",
                                            "and_or": "OR",
                                        }
                                    )
                                    config_dict["condition"].append(
                                        {
                                            "table_name": config_dict.get("join_table_names")[i],
                                            "column_name": "is_active_flag",
                                            "condition": "Not Equal to",
                                            "input_value": "No",
                                            "and_or": ")",
                                        }
                                    )
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
            else:
                pass
        else:
            if table not in sys_tables and not fetch_all_entries:
                if "is_active_flag" in field_list:
                    is_active_flag_bool = True
                    config_dict["condition"] = []
                    config_dict["condition"].append(
                        {
                            "column_name": "(is_active_flag",
                            "condition": "Equal to",
                            "input_value": "NULL",
                            "and_or": "OR",
                            "constraintName": "is_active_contraint",
                            "ruleSet": "is_active_rule_set1",
                        }
                    )
                    config_dict["condition"].append(
                        {
                            "column_name": "is_active_flag",
                            "condition": "Not Equal to",
                            "input_value": "No",
                            "and_or": ")",
                            "constraintName": "is_active_contraint",
                            "ruleSet": "is_active_rule_set",
                        }
                    )
                else:
                    pass
            else:
                pass
            if apply_joins:
                for i, join_table_name in enumerate(join_table_names):
                    if i == 0:
                        continue
                    if (
                        join_table_name
                        not in [
                            "information_schema.columns",
                            "information_schema.tables",
                            "auth_group",
                            "auditlog_logentry",
                            "django_apscheduler_djangojobexecution",
                            "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                            "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                            "master.dbo.sysdatabases",
                            "sys.default_constraints",
                        ]
                        and join_table_name not in admin_tables
                        and join_table_name not in sys_tables
                        and if_app_db
                    ):
                        modelName = get_model_class(
                            join_table_name, request, db_engine=engine2, db_type=db_type
                        )
                        field_list = {
                            field.name: field.verbose_name.title() for field in modelName.concrete_fields
                        }
                        if join_table_name not in sys_tables and not fetch_all_entries:
                            if "is_active_flag" in field_list:
                                if config_dict["condition"][-1]["and_or"] == ")":
                                    config_dict["condition"][-1]["and_or"] = ") AND "
                                config_dict["condition"].append(
                                    {
                                        "table_name": config_dict.get("join_table_names")[i],
                                        "column_name": "(is_active_flag",
                                        "condition": "Equal to",
                                        "input_value": "NULL",
                                        "and_or": "OR",
                                        "constraintName": "is_active_contraint" + str(i),
                                        "ruleSet": "is_active_rule_set" + str(i + 1),
                                    }
                                )
                                config_dict["condition"].append(
                                    {
                                        "table_name": config_dict.get("join_table_names")[i],
                                        "column_name": "is_active_flag",
                                        "condition": "Not Equal to",
                                        "input_value": "No",
                                        "and_or": ")",
                                        "constraintName": "is_active_contraint" + str(i),
                                        "ruleSet": "is_active_rule_set" + str(i + 2),
                                    }
                                )
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
            else:
                pass

        if config_dict.get("adv_condition"):
            if config_dict["adv_condition"] is not None:
                if config_dict["adv_condition"][0].get("constraintName"):
                    if config_dict["adv_condition"][0]["constraintName"] != "":
                        new_config_adv_cond = 1

        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if type(item["input_value"]) is str:
                        input_validation_check(item["input_value"])
                    else:
                        pass
                else:
                    pass

        if bool(config_dict.get("condition")) and not new_config_cond:
            if not skip:
                config_dict["condition"] = convert_format(config_dict["condition"], request, table, engine2)
            for i in range(0, len(config_dict["condition"])):
                query_tag = query_tag + adv_query_generator(
                    config_dict["condition"][i], config_dict["condition"][i].get("table_name", sql_table_name)
                )

            if bool(config_dict.get("adv_condition")) and not new_config_adv_cond:
                config_dict["adv_condition"] = convert_format(
                    config_dict["adv_condition"], request, table, engine2
                )
                for i in range(0, len(config_dict["adv_condition"])):
                    col_name = config_dict["adv_condition"][i]["column_name"]
                    agg_cond = config_dict["adv_condition"][i]["agg_condition"]
                    table_name = config_dict["adv_condition"][i].get("table_name", sql_table_name)

                    query_tag2 = query_tag2 + adv_query_generator(config_dict["adv_condition"][i], table_name)

                    if query_tag2 == "":
                        sql_query2 = f"{sql_query2} and {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name})"
                    else:
                        sql_query2 = f"{sql_query2} and {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name} where {query_tag2})"

                    query_tag2 = ""

            sql_query = f"select {agg_query} {column} from {sql_table_name} where {query_tag} {sql_query2} {order_query};"
            if apply_joins:

                sql_query = f"select {join_columns} from {sql_table_name} {join_query} where {query_tag};"
                if config_dict["join_table_data"].get("join_table_level_conditions"):
                    if config_dict["join_table_data"]["join_table_level_conditions"].get(sql_table_name):
                        condition_sub_query = condition_sub_query_generator(
                            config_dict["join_table_data"]["join_table_level_conditions"],
                            sql_table_name,
                            request,
                            engine2,
                            db_type="MSSQL",
                        )
                        sql_query = f"select {join_columns} from ({condition_sub_query}) AS {sql_table_name} {join_query} where {query_tag} {order_query}"

        else:
            if bool(config_dict.get("adv_condition")) and not new_config_adv_cond:

                config_dict["adv_condition"] = convert_format(
                    config_dict["adv_condition"], request, table, engine2
                )
                for i in range(0, len(config_dict["adv_condition"])):
                    col_name = config_dict["adv_condition"][i]["column_name"]
                    agg_cond = config_dict["adv_condition"][i]["agg_condition"]
                    table_name = config_dict["adv_condition"][i].get("table_name", sql_table_name)

                    query_tag2 = query_tag2 + adv_query_generator(config_dict["adv_condition"][i], table_name)

                    if i == 0:
                        if query_tag2 != "":
                            sql_query2 = f"{sql_query2} where {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name} where {query_tag2})"
                        else:
                            sql_query2 = f"{sql_query2} where {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name})"
                    else:
                        if query_tag2 != "":
                            sql_query2 = f"{sql_query2} and {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name} where {query_tag2})"
                        else:
                            sql_query2 = f"{sql_query2} and {table_name}.{col_name} = (select {agg_cond}({table_name}.{col_name}) from {table_name})"

                    query_tag2 = ""

            sql_query = f"select {agg_query} {column} from {sql_table_name} {sql_query2} {order_query};"
        if new_config_cond or new_config_adv_cond:
            if config_dict.get("adv_condition"):
                advance_conditions = config_dict["adv_condition"]
            else:
                advance_conditions = []
            if apply_joins:
                if config_dict["join_table_data"].get("join_table_level_conditions"):
                    join_table_level_cons = config_dict["join_table_data"].get(
                        "join_table_level_conditions", {}
                    )
                else:
                    join_table_level_cons = {}
            else:
                join_table_level_cons = {}
            sql_query = adv_query_generator2(
                advance_conditions,
                config_dict["condition"],
                request,
                table,
                engine2,
                sql_table_name,
                column,
                agg_query,
                order_query,
                is_active_flag_bool,
                apply_joins,
                join_columns,
                join_query,
                join_table_level_cons,
            )
        else:
            pass
        if group_by_string:
            sql_query = sql_query.split(";")[0] + f" {group_by_string} ;"
        else:
            pass
        if order_by_query_string:
            sql_query = sql_query.split(";")[0] + f" {order_by_query_string} ;"

        chunksize = config_dict.get("chunk_size",10 ** 5)
        table = execute_read_query(sql_query, engine2, db_type, chunksize=chunksize)
        return table
    elif db_type == "PostgreSQL":
        central_db_call = False
        instance_id = None
        if table in admin_tables:
            central_db_call = True
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
            if request != "" and not request.user.is_anonymous:
                instance_id = request.user.instance_id
            else:
                if instance:
                    instance_id = instance.id
                else:
                    pass
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]

        column_list = []
        if columnlist != ["*"]:
            if config_dict.get("aliases"):
                aliases = config_dict.get("aliases")
                alias_expresions = []
                for field in columnlist:
                    if aliases.get(field, "") != "":
                        alias_query = sql.SQL("{} AS {} ").format(
                            sql.Identifier(field.lower()), sql.Identifier(aliases.get(field))
                        )
                    else:
                        alias_query = sql.Identifier(field.lower())
                    alias_expresions.append(alias_query)

                column = sql.SQL(", ").join(alias_expresions)
            else:
                column = sql.SQL(", ").join([sql.Identifier(field.lower()) for field in columnlist])
        else:
            column = sql.SQL("*")
            cursor1 = sql_engine.cursor()
            if central_db_call:
                table_schema = "public"
            else:
                table_schema = schema
            cursor1.execute(
                f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = '{sql_table_name}' AND table_schema = '{table_schema}'"
            )
            columns_records = cursor1.fetchall()
            cursor1.close()
            column_list = [i[0] for i in np.array(columns_records)]

        join_columns = ""
        join_query = ""
        if apply_joins:
            join_columns, join_query = join_query_generator(config_dict, request, engine2, db_type)
            table_names = config_dict.get("join_table_names")
            if join_table_group_by_select_columns:
                join_columns = sql.SQL(join_table_group_by_select_columns)
            if config_dict["join_table_data"].get("join_conditions"):
                if not config_dict.get("condition"):
                    config_dict["condition"] = []
                else:
                    if config_dict["condition"][-1]["and_or"] == ")":
                        config_dict["condition"][-1]["and_or"] = ") AND "
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                for join_table in config_dict["join_table_data"]["join_conditions"]:
                    for condition in config_dict["join_table_data"]["join_conditions"][join_table]:
                        if "users_" + condition["table_name"] in table_names:
                            condition["table_name"] = "users_" + condition["table_name"]
                        config_dict["condition"].append(condition)
            else:
                pass

        if config_dict["inputs"].get("group_by_aggregation"):
            aggregation_cols_groupby = []
            group_by_agg_cols = []
            for agg_col, aggregation in config_dict["inputs"]["group_by_aggregation"].items():
                if type(aggregation) is list:
                    for item in aggregation:
                        aggregation_type = item.get("agg_type", aggregation)
                        aggregation_alias = item.get("agg_alias", agg_col)
                        if apply_joins:
                            if "." in agg_col:
                                agg_table_name, agg_column_name = agg_col.split(".")
                                agg_col_identifier = sql.SQL("{}").format(
                                    sql.Identifier(agg_table_name, agg_column_name.lower())
                                )
                            else:
                                agg_col_identifier = sql.Identifier(agg_col.lower())
                        else:
                            agg_col_identifier = sql.Identifier(agg_col.lower())
                        aggregation_cols_groupby.append(
                            get_aggregation_query(agg_col_identifier, aggregation_type, aggregation_alias)
                        )

                    group_by_agg_cols.append(agg_col)
                else:
                    if aggregation == "sum":
                        aggregation_cols_groupby.append(
                            sql.SQL("SUM({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "average":
                        aggregation_cols_groupby.append(
                            sql.SQL("AVG({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "variance":
                        aggregation_cols_groupby.append(
                            sql.SQL("var_pop({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "standard deviation":
                        aggregation_cols_groupby.append(
                            sql.SQL("stddev_pop({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "count":
                        aggregation_cols_groupby.append(
                            sql.SQL("COUNT({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "count distinct":
                        aggregation_cols_groupby.append(
                            sql.SQL("COUNT(DISTINCT {agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "maximum":
                        aggregation_cols_groupby.append(
                            sql.SQL("MAX({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "minimum":
                        aggregation_cols_groupby.append(
                            sql.SQL("MIN({agg_col}) AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    elif aggregation == "percentage of total":
                        aggregation_cols_groupby.append(
                            sql.SQL("SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS {as_name}").format(
                                agg_col=sql.Identifier(agg_col.lower()),
                                as_name=sql.SQL(agg_col),
                            )
                        )
                    else:
                        continue
                    group_by_agg_cols.append(agg_col)
            column = sql.SQL(", ").join([column, *aggregation_cols_groupby])
            column_list.extend(group_by_agg_cols)
            columnlist.extend(group_by_agg_cols)
            if apply_joins:
                group_by_columns = sql.SQL(", ").join([join_columns, *aggregation_cols_groupby])
                join_columns = group_by_columns
        else:
            pass

        group_by_query = sql.SQL("")
        if config_dict["inputs"].get("group_by"):
            group_by_cols = sql.SQL(", ").join(
                [sql.Identifier(field.lower()) for field in config_dict["inputs"]["group_by"]]
            )
            if apply_joins:
                join_table_group_by_query_list = []
                for field in config_dict["inputs"].get("group_by"):
                    if "." in field:
                        agg_table_name, agg_column_name = field.split(".")
                        join_table_group_by_query_list.append(
                            sql.SQL("{}").format(sql.Identifier(agg_table_name, agg_column_name.lower()))
                        )
                    else:
                        join_table_group_by_query_list.append(
                            sql.SQL("{}").format(sql.Identifier(agg_column_name.lower()))
                        )
                group_by_cols = sql.SQL(", ").join(join_table_group_by_query_list)
            group_by_query = sql.SQL("GROUP BY {group_by_cols}").format(group_by_cols=group_by_cols)
        else:
            pass

        if not central_db_call and sql_table_name.lower() not in [
            "information_schema.columns",
            "information_schema.tables",
            "information_schema.constraint_column_usage",
            "information_schema.table_constraints",
        ]:
            postgres_table_name = sql.Identifier(schema, sql_table_name)
        else:
            postgres_table_name = sql.Identifier(sql_table_name)
        if apply_joins:
            postgres_table_name = sql.Identifier(sql_table_name)

        agg_query = sql.SQL("")
        limit_query = sql.SQL("")
        order_query = sql.SQL("")
        offset_query = sql.SQL("")
        is_agg = False
        is_order = False
        is_offset = False
        new_config_cond = 0
        agg_column = ""
        if config_dict.get("order_by_configs"):
            config_dict["inputs"]["Order_Type"] = order_by_query_generator(config_dict, if_app_db)
        if "Agg_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Agg_Type"] != "":
                is_agg = True
                agg_type = config_dict["inputs"]["Agg_Type"]
                if agg_type.startswith("LIMIT"):
                    limit_query = sql.SQL(agg_type)
                elif agg_type.startswith("TOP"):
                    limit_query = sql.SQL(agg_type.replace("TOP(", "LIMIT ").replace(")", ""))
                else:
                    agg_query = sql.SQL(agg_type)
                    if "(" in agg_type:
                        agg_column = agg_type.split("(")[1].replace(")", "").strip(" ")
                    else:
                        pass
            else:
                pass
        else:
            pass
        if "Order_Type" in config_dict["inputs"]:
            if config_dict["inputs"]["Order_Type"] != "":
                is_order = True
                order_query = sql.SQL(config_dict["inputs"]["Order_Type"])
            else:
                pass
        else:
            pass
        if "Offset" in config_dict["inputs"]:
            offset_query += sql.SQL(" OFFSET {offset} ROWS ").format(
                offset=sql.Literal(config_dict["inputs"]["Offset"])
            )
            is_offset = True
            if "Fetch_next" in config_dict["inputs"]:
                offset_query += sql.SQL(" FETCH NEXT {fetch_next} ROWS ONLY ").format(
                    fetch_next=sql.Literal(config_dict["inputs"]["Fetch_next"])
                )
            else:
                pass
        else:
            pass
        query_tag = ""
        cond_date_list = []
        cond_datetime_list = []
        if (
            table
            not in admin_tables
            + [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "INFORMATION_SCHEMA.constraint_column_usage",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]
            and table not in sys_tables
        ):
            try:
                modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
                field_list = {field.name: field.verbose_name.title() for field in modelName.concrete_fields}
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
                if access_controller:
                    access_controls = modelName.get_access_controls()
                    if access_controls and request:
                        if config_dict.get("condition"):
                            if config_dict["condition"][0].get("constraintName"):
                                new_config_cond = 1
                            else:
                                pass
                        else:
                            pass
                        if access_controls["access_type"] == "created_by_user":
                            if config_dict.get("condition"):
                                if config_dict["condition"][-1]["and_or"] == ")":
                                    config_dict["condition"][-1]["and_or"] = ") AND "
                                else:
                                    config_dict["condition"][-1]["and_or"] = "AND"
                            else:
                                pass
                            access_control_condition = {
                                "column_name": "created_by",
                                "condition": "Equal to",
                                "input_value": request.user.username,
                                "and_or": "OR",
                            }
                            access_control_condition1 = {
                                "column_name": "modified_by",
                                "condition": "Equal to",
                                "input_value": request.user.username,
                                "and_or": ")",
                            }
                            if new_config_cond:
                                access_control_condition["constraintName"] = "access_control_constraint"
                                access_control_condition["ruleSet"] = "access_control_rule1"
                                access_control_condition1["constraintName"] = "access_control_constraint"
                                access_control_condition1["ruleSet"] = "access_control_rule2"
                                access_control_condition1["and_or"] = ""
                            else:
                                access_control_condition["column_name"] = (
                                    f"({access_control_condition['column_name']}"
                                )
                                access_control_condition["and_or"] = "OR"
                            config_dict["condition"].append(access_control_condition)
                            config_dict["condition"].append(access_control_condition1)
                        elif access_controls["access_type"] == "custom":
                            if config_dict.get("condition"):
                                if config_dict["condition"][-1]["and_or"] == ")":
                                    config_dict["condition"][-1]["and_or"] = ") AND "
                                else:
                                    config_dict["condition"][-1]["and_or"] = "AND"
                            else:
                                pass
                            additional_config = access_controls["additional_config"]
                            control_measure = additional_config["controlMeasure"]
                            access_control_condition_list = []
                            for cust_acc_col in additional_config["fields"]:
                                if cust_acc_col in ["created_by", "modified_by"]:
                                    access_control_condition_list.append(
                                        {
                                            "column_name": cust_acc_col,
                                            "condition": "Equal to",
                                            "input_value": request.user.username,
                                            "and_or": "",
                                        }
                                    )
                                else:
                                    if (
                                        modelName.get_field(cust_acc_col).get_internal_type()
                                        == "MultiselectField"
                                    ):
                                        multi_select_config = json.loads(
                                            modelName.get_field(cust_acc_col).mulsel_config
                                        )
                                        master_table = multi_select_config["value"][0]
                                        master_column = multi_select_config["masterColumn"][0]
                                        if control_measure in ["any_email", "all_email"]:
                                            input_value = request.user.email
                                        else:
                                            input_value = request.user.username

                                        corresponding_id = execute_read_query(
                                            f"Select id from users_{master_table.lower()} where {master_column} = '{input_value}'",
                                            engine2,
                                            db_type,
                                        )
                                        if not corresponding_id.empty:
                                            input_value = f'"{str(corresponding_id.iloc[0,0])}":'
                                        else:
                                            pass
                                        access_control_condition_list.append(
                                            {
                                                "column_name": cust_acc_col,
                                                "condition": "Contains",
                                                "input_value": input_value,
                                                "and_or": "",
                                            }
                                        )
                                    else:
                                        if control_measure in ["any_email", "all_email"]:
                                            input_value = request.user.email
                                        else:
                                            input_value = request.user.username
                                        access_control_condition_list.append(
                                            {
                                                "column_name": cust_acc_col,
                                                "condition": "Equal to",
                                                "input_value": input_value,
                                                "and_or": "",
                                            }
                                        )
                            if new_config_cond:
                                for i in range(len(access_control_condition_list)):
                                    access_control_condition_list[i][
                                        "constraintName"
                                    ] = "access_control_constraint"
                                    if control_measure in ["any", "any_email"]:
                                        access_control_condition_list[i][
                                            "ruleSet"
                                        ] = f"access_control_rule{i}"
                                    else:
                                        access_control_condition_list[i]["ruleSet"] = f"access_control_rule"
                            else:
                                access_control_condition_list[0][
                                    "column_name"
                                ] = f'({access_control_condition_list[0]["column_name"]}'
                                access_control_condition_list[-1]["and_or"] = ")"
                                for i in range(len(access_control_condition_list)):
                                    if i != len(access_control_condition_list) - 1:
                                        if control_measure in ["any", "any_email"]:
                                            access_control_condition_list[i]["and_or"] = "OR"
                                        else:
                                            access_control_condition_list[i]["and_or"] = "AND"
                                    else:
                                        continue
                            if access_control_condition_list:
                                config_dict["condition"] += access_control_condition_list
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
                is_new_config_call = False
                if config_dict.get("condition"):
                    if config_dict["condition"][0].get("constraintName"):
                        is_new_config_call = True
                    else:
                        pass
                else:
                    pass
                if not fetch_all_entries and "is_active_flag" in field_list:
                    if config_dict.get("condition"):
                        if "is_active_flag" in config_dict["condition"][-1]["column_name"]:
                            config_dict["condition"][-1]["and_or"] = ") AND "
                        elif config_dict["condition"][-1]["and_or"] == ")":
                            config_dict["condition"][-1]["and_or"] = ") AND "
                        else:
                            config_dict["condition"][-1]["and_or"] = "AND"
                        is_active_condition1 = {
                            "condition": "Equal to",
                            "input_value": "NULL",
                            "and_or": "",
                        }
                        if is_new_config_call:
                            is_active_condition1["column_name"] = "is_active_flag"
                        else:
                            is_active_condition1["column_name"] = "(is_active_flag"
                        is_active_condition = {
                            "column_name": "is_active_flag",
                            "condition": "Not Equal to",
                            "input_value": "No",
                            "and_or": ")",
                        }
                        if is_new_config_call:
                            is_active_condition1["constraintName"] = "is_active_contraint"
                            is_active_condition1["ruleSet"] = "is_active_rule_set1"
                            is_active_condition["constraintName"] = "is_active_contraint"
                            is_active_condition["ruleSet"] = "is_active_rule_set2"
                            is_active_condition["and_or"] = ""
                        else:
                            is_active_condition1["and_or"] = "OR"

                        config_dict["condition"].append(is_active_condition1)
                        config_dict["condition"].append(is_active_condition)

                        if apply_joins:
                            if is_new_config_call:
                                for i, join_table_name in enumerate(join_table_names):
                                    if i == 0:
                                        continue
                                    if (
                                        join_table_name
                                        not in admin_tables
                                        + [
                                            "information_schema.columns",
                                            "information_schema.tables",
                                            "auth_group",
                                            "auditlog_logentry",
                                            "django_apscheduler_djangojobexecution",
                                            "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                            "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                                            "INFORMATION_SCHEMA.constraint_column_usage",
                                            "master.dbo.sysdatabases",
                                            "sys.default_constraints",
                                        ]
                                        and join_table_name not in sys_tables
                                    ):
                                        try:
                                            modelName = get_model_class(
                                                join_table_name, request, db_engine=engine2, db_type=db_type
                                            )
                                            cond_date_list.extend(
                                                [
                                                    field.name
                                                    for field in modelName._meta.concrete_fields
                                                    if field.get_internal_type() in ["DateField"]
                                                ]
                                            )
                                            cond_datetime_list.extend(
                                                [
                                                    field.name
                                                    for field in modelName._meta.concrete_fields
                                                    if field.get_internal_type() in ["DateTimeField"]
                                                ]
                                            )
                                            field_list = {
                                                field.name: field.verbose_name.title()
                                                for field in modelName.concrete_fields
                                            }
                                            if not fetch_all_entries and "is_active_flag" in field_list:

                                                config_dict["condition"].append(
                                                    {
                                                        "table_name": config_dict.get("join_table_names")[i],
                                                        "column_name": "is_active_flag",
                                                        "condition": "Equal to",
                                                        "input_value": "NULL",
                                                        "and_or": "",
                                                        "constraintName": "is_active_contraint" + str(i),
                                                        "ruleSet": "is_active_rule_set" + str(i + 1),
                                                    }
                                                )
                                                config_dict["condition"].append(
                                                    {
                                                        "table_name": config_dict.get("join_table_names")[i],
                                                        "column_name": "is_active_flag",
                                                        "condition": "Not Equal to",
                                                        "input_value": "No",
                                                        "and_or": "",
                                                        "constraintName": "is_active_contraint" + str(i),
                                                        "ruleSet": "is_active_rule_set" + str(i),
                                                    }
                                                )
                                            else:
                                                pass
                                        except Exception as e:
                                            logging.warning(f"Following exception occured - {e}")
                                    else:
                                        pass

                            else:
                                for i, join_table_name in enumerate(join_table_names):
                                    if i == 0:
                                        continue
                                    if (
                                        join_table_name
                                        not in admin_tables
                                        + [
                                            "information_schema.columns",
                                            "information_schema.tables",
                                            "auth_group",
                                            "auditlog_logentry",
                                            "django_apscheduler_djangojobexecution",
                                            "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                            "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                                            "INFORMATION_SCHEMA.constraint_column_usage",
                                            "master.dbo.sysdatabases",
                                            "sys.default_constraints",
                                        ]
                                        and join_table_name not in sys_tables
                                    ):
                                        try:
                                            modelName = get_model_class(
                                                join_table_name, request, db_engine=engine2, db_type=db_type
                                            )
                                            cond_date_list.extend(
                                                [
                                                    field.name
                                                    for field in modelName._meta.concrete_fields
                                                    if field.get_internal_type() in ["DateField"]
                                                ]
                                            )
                                            cond_datetime_list.extend(
                                                [
                                                    field.name
                                                    for field in modelName._meta.concrete_fields
                                                    if field.get_internal_type() in ["DateTimeField"]
                                                ]
                                            )
                                            field_list = {
                                                field.name: field.verbose_name.title()
                                                for field in modelName.concrete_fields
                                            }
                                            if not fetch_all_entries and "is_active_flag" in field_list:
                                                if (
                                                    "is_active_flag"
                                                    in config_dict["condition"][-1]["column_name"]
                                                ):
                                                    config_dict["condition"][-1]["and_or"] = ") AND "
                                                elif config_dict["condition"][-1]["and_or"] == ")":
                                                    config_dict["condition"][-1]["and_or"] = ") AND "
                                                else:
                                                    config_dict["condition"][-1]["and_or"] = "AND"
                                                config_dict["condition"].append(
                                                    {
                                                        "table_name": config_dict.get("join_table_names")[i],
                                                        "column_name": "(is_active_flag",
                                                        "condition": "Equal to",
                                                        "input_value": "NULL",
                                                        "and_or": "OR",
                                                    }
                                                )
                                                config_dict["condition"].append(
                                                    {
                                                        "table_name": config_dict.get("join_table_names")[i],
                                                        "column_name": "is_active_flag",
                                                        "condition": "Not Equal to",
                                                        "input_value": "No",
                                                        "and_or": ")",
                                                    }
                                                )
                                            else:
                                                pass
                                        except Exception as e:
                                            logging.warning(f"Following exception occured - {e}")
                                    else:
                                        pass
                        else:
                            pass
                    else:
                        config_dict["condition"] = []
                        config_dict["condition"].append(
                            {
                                "column_name": "is_active_flag",
                                "condition": "Equal to",
                                "input_value": "NULL",
                                "and_or": "",
                                "constraintName": "is_active_contraint",
                                "ruleSet": "is_active_rule_set1",
                            }
                        )
                        config_dict["condition"].append(
                            {
                                "column_name": "is_active_flag",
                                "condition": "Not Equal to",
                                "input_value": "No",
                                "and_or": "",
                                "constraintName": "is_active_contraint",
                                "ruleSet": "is_active_rule_set",
                            }
                        )
                        if apply_joins:
                            for i, join_table_name in enumerate(join_table_names):
                                if i == 0:
                                    continue
                                if (
                                    join_table_name
                                    not in admin_tables
                                    + [
                                        "information_schema.columns",
                                        "information_schema.tables",
                                        "auth_group",
                                        "auditlog_logentry",
                                        "django_apscheduler_djangojobexecution",
                                        "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                        "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                                        "INFORMATION_SCHEMA.constraint_column_usage",
                                        "master.dbo.sysdatabases",
                                        "sys.default_constraints",
                                    ]
                                    and join_table_name not in sys_tables
                                ):
                                    try:
                                        modelName = get_model_class(
                                            join_table_name, request, db_engine=engine2, db_type=db_type
                                        )
                                        cond_date_list.extend(
                                            [
                                                field.name
                                                for field in modelName._meta.concrete_fields
                                                if field.get_internal_type() in ["DateField"]
                                            ]
                                        )
                                        cond_datetime_list.extend(
                                            [
                                                field.name
                                                for field in modelName._meta.concrete_fields
                                                if field.get_internal_type() in ["DateTimeField"]
                                            ]
                                        )

                                        field_list = {
                                            field.name: field.verbose_name.title()
                                            for field in modelName.concrete_fields
                                        }
                                        if not fetch_all_entries and "is_active_flag" in field_list:
                                            if config_dict["condition"][-1]["and_or"] == ")":
                                                config_dict["condition"][-1]["and_or"] = ") AND "
                                            config_dict["condition"].append(
                                                {
                                                    "table_name": config_dict.get("join_table_names")[i],
                                                    "column_name": "is_active_flag",
                                                    "condition": "Equal to",
                                                    "input_value": "NULL",
                                                    "and_or": "",
                                                    "constraintName": "is_active_contraint" + str(i),
                                                    "ruleSet": "is_active_rule_set" + str(i + 1),
                                                }
                                            )
                                            config_dict["condition"].append(
                                                {
                                                    "table_name": config_dict.get("join_table_names")[i],
                                                    "column_name": "is_active_flag",
                                                    "condition": "Not Equal to",
                                                    "input_value": "No",
                                                    "and_or": "",
                                                    "constraintName": "is_active_contraint" + str(i),
                                                    "ruleSet": "is_active_rule_set" + str(i + 2),
                                                }
                                            )
                                        else:
                                            pass
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                else:
                                    pass
                        else:
                            pass
                else:
                    pass
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
        elif table in admin_tables and table not in auth_tables and table != "Instance":
            if config_dict.get("condition"):
                is_instance_condition_present = any(
                    [True if i["column_name"] == "instance_id" else False for i in config_dict["condition"]]
                )
                if not is_instance_condition_present:
                    if config_dict["condition"][0].get("constraintName"):
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                                "constraintName": "tenant_constraint",
                                "ruleSet": "tenant",
                            }
                        )
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                            }
                        )
                else:
                    pass
            else:
                config_dict["condition"] = [
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance_id,
                        "and_or": "",
                    }
                ]
        else:
            pass
        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if type(item["input_value"]) is str:
                        input_validation_check(item["input_value"])
                    else:
                        pass
                else:
                    pass

        if bool(config_dict.get("condition")) or config_dict.get("adv_condition"):
            query_tag = postgres_condition_generator(
                config_dict, cond_date_list, cond_datetime_list, postgres_table_name
            )
            if table.lower() in [
                "information_schema.columns",
                "information_schema.tables",
                "information_schema.key_column_usage",
                "information_schema.table_constraints",
                "information_schema.constraint_column_usage",
            ]:
                sql_query = sql.SQL(
                    "select {fields} from {sql_table_name} where {condition_query} {group_by_query};"
                ).format(
                    fields=column,
                    sql_table_name=sql.SQL(sql_table_name.lower()),
                    condition_query=query_tag,
                    group_by_query=group_by_query,
                )
            else:
                if is_agg or is_order or is_offset:
                    sql_query = sql.SQL(
                        "select {agg_query} {fields} from {table} where {condition_query} {group_by_query} {order_query} {offset_query} {limit_query};"
                    ).format(
                        agg_query=agg_query,
                        fields=column,
                        table=postgres_table_name,
                        condition_query=query_tag,
                        group_by_query=group_by_query,
                        order_query=order_query,
                        offset_query=offset_query,
                        limit_query=limit_query,
                    )
                else:
                    sql_query = sql.SQL(
                        "select {fields} from {table} where {condition_query} {group_by_query};"
                    ).format(
                        fields=column,
                        table=postgres_table_name,
                        condition_query=query_tag,
                        group_by_query=group_by_query,
                    )
                if apply_joins:
                    sql_query = sql.SQL(
                        "select {fields} from {table} {join_query} where {condition_query} {group_by_query} {order_query};"
                    ).format(
                        fields=join_columns,
                        table=postgres_table_name,
                        join_query=join_query,
                        condition_query=query_tag,
                        group_by_query=group_by_query,
                        order_query=order_query,
                    )
                    if config_dict["join_table_data"].get("join_table_level_conditions"):
                        if config_dict["join_table_data"]["join_table_level_conditions"].get(sql_table_name):
                            condition_sub_query = condition_sub_query_generator(
                                config_dict["join_table_data"]["join_table_level_conditions"],
                                sql_table_name,
                                request,
                                engine2,
                                db_type=db_type,
                            )
                            sql_query = sql.SQL(
                                "select {fields} from ({condition_sub_query}) AS {table} {join_query} where {condition_query} {group_by_query} {order_query};"
                            ).format(
                                fields=join_columns,
                                condition_sub_query=condition_sub_query,
                                table=sql.SQL(sql_table_name),
                                join_query=join_query,
                                condition_query=query_tag,
                                group_by_query=group_by_query,
                                order_query=order_query,
                            )
                        else:
                            pass
                    else:
                        pass

        else:
            if sql_table_name.lower() in [
                "information_schema.columns",
                "information_schema.tables",
                "information_schema.key_column_usage",
                "information_schema.table_constraints",
                "information_schema.constraint_column_usage",
            ]:
                sql_query = sql.SQL("select {fields} from {sql_table_name} {group_by_query};").format(
                    fields=column,
                    sql_table_name=sql.SQL(sql_table_name.lower()),
                    group_by_query=group_by_query,
                )
            else:
                if is_agg or is_order or is_offset:
                    sql_query = sql.SQL(
                        "select {agg_query} {fields} from {table} {group_by_query} {order_query} {offset_query} {limit_query};"
                    ).format(
                        agg_query=agg_query,
                        fields=column,
                        table=postgres_table_name,
                        group_by_query=group_by_query,
                        order_query=order_query,
                        offset_query=offset_query,
                        limit_query=limit_query,
                    )
                else:
                    sql_query = sql.SQL("select {fields} from {table} {group_by_query};").format(
                        fields=column,
                        table=postgres_table_name,
                        group_by_query=group_by_query,
                    )
        if config_dict.get("chunk_size"):
            with sql_engine.cursor(name='custom_cursor') as cursor:
                cursor.itersize = config_dict.get("chunk_size")
                cursor.execute(sql_query)
                records = cursor.fetchall()
                columns_selected = [desc[0] for desc in cursor.description]
        else:
            cursor = sql_engine.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            columns_selected = [desc[0] for desc in cursor.description]
        if columnlist != ["*"]:
            if not columnlist and is_agg:
                columnlist.append(agg_column)
            table = pd.DataFrame(records, columns=columns_selected)
        else:
            table = pd.DataFrame(records, columns=column_list)
        cursor.close()
        sql_engine.close()
        return table
    elif db_type == "Oracle":
        if (
            table
            not in [
                "all_tables",
                "all_constraints",
                "all_tab_columns",
                "all_cons_columns",
                "user_constraints",
                "user_tables",
                "user_cons_columns",
            ]
            + admin_tables
            and if_app_db
        ):
            model_class = get_model_class(table, request, db_engine=engine2, db_type=db_type)
            blob_type_columns = [
                field.name
                for field in model_class.concrete_fields
                if field.get_internal_type() in ["BinaryField"]
            ]
            date_type_columns = [
                field.name
                for field in model_class.concrete_fields
                if field.get_internal_type() in ["DateField"]
            ]
            join_tables_model_classes = {}
            if config_dict.get("apply_join"):
                for join_table in join_table_names:
                    join_tables_model_classes[join_table] = get_model_class(
                        join_table, request, db_engine=engine2, db_type=db_type
                    )
            else:
                pass
            data_type = {}
        elif not if_app_db:
            data_type_query = f"SELECT column_name, data_type from all_tab_columns where table_name='{table}'"
            data_type = execute_read_query(data_type_query, engine2, db_type, chunksize=chunksize)
            data_type = data_type.set_index("column_name")["data_type"].to_dict()
            date_type_columns = [i for i, t in data_type.items() if t == "DATE"]
            blob_type_columns = []
            model_class = None
            join_tables_model_classes = {}
        else:
            date_type_columns = []
            blob_type_columns = []
            model_class = None
            data_type = {}
            join_tables_model_classes = {}
        chunksize = config_dict.get("chunk_size",10 ** 5)
        oracleQueryGenerator = OracleSQLQueryGenerator(
            request,
            config_dict,
            table,
            access_controller,
            fetch_all_entries,
            model_class=model_class,
            if_app_db_call=if_app_db,
            schema=schema,
            data_type=data_type,
            join_table_names=join_table_names,
            join_tables_model_classes=join_tables_model_classes,
        )
        sql_query = oracleQueryGenerator.read_query_generator()
        table = execute_read_query(sql_query, engine2, db_type, chunksize=chunksize)
        if not table.empty:
            for col in blob_type_columns:
                if col in table.columns:
                    table[col] = table[col].map(lambda x: x.decode("utf-8"), na_action="ignore")
                else:
                    continue
            for col in date_type_columns:
                if col in table.columns:
                    table[col] = table[col].dt.date
                else:
                    continue            
        else:
            pass
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
    instance = get_current_tenant()
    if schema == "":
        if instance:
            schema = instance.name
        else:
            schema = "public"
    else:
        pass

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
            else:
                pass
        else:
            pass
    else:
        pass
    if db_type == "MSSQL":
        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if item.get("input_value"):
                        if type(item["input_value"]) is str:
                            input_validation_check(item["input_value"])
                        else:
                            pass
                    else:
                        continue
                else:
                    pass
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []
            if table not in admin_tables:
                try:
                    if if_app_db:
                        modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
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
                if update_data_dict[i]["input_value"] != "NULL" and update_data_dict[i]["input_value"]:
                    if type(update_data_dict[i]["input_value"]) is str:
                        input_validation_check(update_data_dict[i]["input_value"])
                    if update_data_dict[i]["column_name"] in cond_date_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d")
                    if update_data_dict[i]["column_name"] in cond_datetime_list:
                        update_data_dict[i]["input_value"] = pd.to_datetime(
                            update_data_dict[i]["input_value"]
                        ).strftime("%Y-%m-%d %H:%M:%S")

                    update_data_dict[i]["input_value"] = (
                        update_data_dict[i]["input_value"].replace("'", "''").replace(":", r"\:")
                    )

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
                if config_dict["condition"][i]["condition"] != "IN":
                    config_dict["condition"][i]["input_value"] = config_dict["condition"][i][
                        "input_value"
                    ].replace("'", "''")
                else:
                    pass
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
            sql_query = f"update {sql_table_name} set {update_data} where {query_tag}"
        else:
            sql_query = f"update {sql_table_name} set {update_data}"
        sql_query = text(sql_query)
        with engine2[0].begin() as conn:
            conn.execute(sql_query)
            conn.commit()
            conn.close()
        return None
    elif db_type == "PostgreSQL":
        instance_id = None
        if table in admin_tables:
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
            if request != "" and not request.user.is_anonymous:
                instance_id = request.user.instance_id
            else:
                instance = get_current_tenant()
                if instance:
                    instance_id = instance.id
                else:
                    cursor1 = sql_engine.cursor()
                    cursor1.execute(f"SELECT id FROM users_instance WHERE name = '{schema}';")
                    columns_records = cursor1.fetchall()
                    cursor1.close()
                    instance_id = columns_records[0][0]
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]

        if table not in admin_tables:
            postgres_table_name = sql.Identifier(schema, sql_table_name)
        else:
            postgres_table_name = sql.Identifier(sql_table_name)

        if table in admin_tables and table not in auth_tables:
            if config_dict.get("condition"):
                is_instance_condition_present = any(
                    [True if i["column_name"] == "instance_id" else False for i in config_dict["condition"]]
                )
                if not is_instance_condition_present:
                    if config_dict["condition"][0].get("constraintName"):
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                                "constraintName": "tenant_constraint",
                                "ruleSet": "tenant",
                            }
                        )
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                            }
                        )
                else:
                    pass
            else:
                config_dict["condition"] = [
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance_id,
                        "and_or": "",
                    }
                ]
        else:
            pass

        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if type(item["input_value"]) is str:
                        input_validation_check(item["input_value"])
                    else:
                        pass
                else:
                    pass
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables:
                try:
                    if if_app_db:
                        modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
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
                field = update_data_dict[i]["column_name"].lower()
                if update_data_dict[i]["input_value"] != "NULL":
                    if type(update_data_dict[i]["input_value"]) is str:
                        input_validation_check(update_data_dict[i]["input_value"])
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
                            field=sql.Identifier(field),
                            value=sql.Literal(update_data_dict[i]["input_value"]),
                            separator=sql.SQL(update_data_dict[i]["separator"]),
                        )
                    )
                else:
                    update_string_list.append(
                        sql.SQL("{field} = {value} {separator}").format(
                            field=sql.Identifier(field),
                            value=sql.SQL("NULL"),
                            separator=sql.SQL(update_data_dict[i]["separator"]),
                        )
                    )
            update_col_string = sql.SQL(" ").join([i for i in update_string_list])
            query_tag = postgres_condition_generator(
                config_dict, cond_date_list, cond_datetime_list, postgres_table_name
            )
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
    elif db_type == "Oracle":
        if (
            table
            not in [
                "all_tables",
                "all_constraints",
                "all_tab_columns",
                "all_cons_columns",
                "user_constraints",
                "user_tables",
                "user_cons_columns",
            ]
            + admin_tables
            and if_app_db
        ):
            model_class = get_model_class(table, request, db_engine=engine2, db_type=db_type)
            data_type = {}
        elif not if_app_db:
            data_type_query = f"SELECT column_name, data_type from all_tab_columns where table_name='{table}'"
            data_type = execute_read_query(data_type_query, engine2, db_type)
            data_type = data_type.set_index("column_name")["data_type"].to_dict()
            model_class = None
        else:
            model_class = None
            data_type = {}

        oracleQueryGenerator = OracleSQLQueryGenerator(
            request,
            config_dict,
            table,
            model_class=model_class,
            operation="update",
            if_app_db_call=if_app_db,
            schema=schema,
            data_type=data_type,
        )
        sql_query, parameter_dict = oracleQueryGenerator.update_query_generator()
        sql_query = text(sql_query)
        with engine2[0].begin() as conn:
            conn.execute(sql_query, parameter_dict)
            conn.commit()
            conn.close()
        return None


############## DELETE QUERY ####################
def delete_data_func(
    request,
    config_dict,
    engine2=[engine, turbodbc_connection],
    db_type=database_type,
    engine_override=False,
    schema="",
    if_app_db=True,
):
    instance = get_current_tenant()
    if schema == "":
        if instance:
            schema = instance.name
        else:
            schema = "public"
    else:
        pass
    table = config_dict["inputs"]["Table"]
    sql_table_name = "users_" + table.lower()
    query_tag = ""
    if table not in admin_tables:
        if not engine_override:
            user_app_db_engine, db_type, schema = app_engine_generator(request)
            if user_app_db_engine != "":
                engine2 = user_app_db_engine
            else:
                pass
        else:
            pass
    else:
        pass
    if db_type == "MSSQL":
        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if type(item["input_value"]) is str:
                        input_validation_check(item["input_value"])
                    else:
                        pass
                else:
                    pass
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables and if_app_db:
                modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
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
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        config_dict["condition"][i]["input_value"] = str(
                            tuple(config_dict["condition"][i]["input_value"])
                        ).replace(",)", ")")
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
                    if type(config_dict["condition"][i]["input_value"]) == list:
                        config_dict["condition"][i]["input_value"] = str(
                            tuple(config_dict["condition"][i]["input_value"])
                        ).replace(",)", ")")
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
        sql_query = text(sql_query)
        with engine2[0].begin() as conn:
            conn.execute(sql_query)
            conn.commit()
            conn.close()
        return None

    elif db_type == "PostgreSQL":
        if table in admin_tables:
            sql_engine = psycopg2.connect(
                dbname=central_database_config["dbname"],
                user=central_database_config["user"],
                password=central_database_config["password"],
                host=central_database_config["host"],
                port=central_database_config["port"],
            )
            if request != "" and not request.user.is_anonymous:
                instance_id = request.user.instance_id
            else:
                instance = get_current_tenant()
                if instance:
                    instance_id = instance.id
                else:
                    cursor1 = sql_engine.cursor()
                    cursor1.execute(f"SELECT id FROM users_instance WHERE name = '{schema}';")
                    columns_records = cursor1.fetchall()
                    cursor1.close()
                    instance_id = columns_records[0][0]
        else:
            sql_engine = postgreSQL_engine_generator(engine2[0])
            schema = engine2[0]["schema"]

        if table in admin_tables:
            postgres_table_name = sql.Identifier(sql_table_name)
        else:
            postgres_table_name = sql.Identifier(schema, sql_table_name)

        if table in admin_tables and table not in auth_tables:
            if config_dict.get("condition"):
                is_instance_condition_present = any(
                    [True if i["column_name"] == "instance_id" else False for i in config_dict["condition"]]
                )
                if not is_instance_condition_present:
                    if config_dict["condition"][0].get("constraintName"):
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                                "constraintName": "tenant_constraint",
                                "ruleSet": "tenant",
                            }
                        )
                    else:
                        config_dict["condition"][-1]["and_or"] = "AND"
                        config_dict["condition"].append(
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": instance_id,
                                "and_or": "",
                            }
                        )
                else:
                    pass
            else:
                config_dict["condition"] = [
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance_id,
                        "and_or": "",
                    }
                ]
        else:
            pass
        if bool(config_dict.get("condition")):
            for item in config_dict["condition"]:
                if item["condition"] != "IN" and item["condition"] != "NOT IN":
                    if type(item["input_value"]) is str:
                        input_validation_check(item["input_value"])
                    else:
                        pass
                else:
                    pass
        if bool(config_dict.get("condition")):
            cond_date_list = []
            cond_datetime_list = []

            if table not in admin_tables:
                modelName = get_model_class(table, request, db_engine=engine2, db_type=db_type)
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

            query_tag = postgres_condition_generator(
                config_dict, cond_date_list, cond_datetime_list, postgres_table_name
            )
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
    elif db_type == "Oracle":
        if (
            table
            not in [
                "all_tables",
                "all_constraints",
                "all_tab_columns",
                "all_cons_columns",
                "user_constraints",
                "user_tables",
                "user_cons_columns",
            ]
            + admin_tables
            + sys_tables
            and if_app_db
        ):
            model_class = get_model_class(table, request, db_engine=engine2, db_type=db_type)
        else:
            model_class = None

        oracleQueryGenerator = OracleSQLQueryGenerator(
            request,
            config_dict,
            table,
            model_class=model_class,
            operation="delete",
            schema=schema,
            if_app_db_call=if_app_db,
        )
        sql_query = oracleQueryGenerator.delete_query_generator()
        sql_query = text(sql_query)
        with engine2[0].begin() as conn:
            conn.execute(sql_query)
            conn.commit()
            conn.close()
        return None


def update_data_func_multiple(
    request,
    config_dict,
    data,
    engine2=[engine, turbodbc_connection],
    db_type=database_type,
    if_app_db=True,
    engine_override=False,
    schema="",
    if_update_else_insert=False,
):
    table = config_dict["inputs"]["Table"]
    if if_app_db:
        sql_table_name = "users_" + table.lower()
    else:
        sql_table_name = table
    update_data_dict = config_dict["inputs"]["Columns"]
    if table not in admin_tables:
        if not engine_override:
            user_app_db_engine, db_type, schema = app_engine_generator(request)
            if user_app_db_engine != "":
                engine2 = user_app_db_engine
    if db_type == "MSSQL":
        if if_update_else_insert:
            data["sql_query"] = data.apply(
                lambda row: update_else_insert_query_generator_row(
                    row, sql_table_name, update_data_dict, config_dict["condition"]
                ),
                axis=1,
            )
        else:
            data["sql_query"] = data.apply(
                lambda row: update_query_generator_row(
                    row, sql_table_name, update_data_dict, config_dict["condition"]
                ),
                axis=1,
            )
        with engine2[0].begin() as conn:
            if len(data) > 1000:
                n = round(len(data) / 1000) + 1
                for batch in np.array_split(data["sql_query"].to_numpy(), n):
                    batch_update_query = "; ".join(batch)
                    batch_update_query = text(batch_update_query)
                    conn.execute(batch_update_query)
            else:
                batch_update_query = "; ".join(data["sql_query"])
                batch_update_query = text(batch_update_query)
                conn.execute(batch_update_query)
            conn.commit()
            conn.close()
    elif db_type == "Oracle":
        if (
            table
            not in [
                "all_tables",
                "all_constraints",
                "all_tab_columns",
                "all_cons_columns",
                "user_constraints",
                "user_tables",
                "user_cons_columns",
            ]
            + admin_tables
            and if_app_db
        ):
            model_class = get_model_class(table, request, db_engine=engine2, db_type=db_type)
            data_type = {}
        elif not if_app_db:
            data_type_query = f"SELECT column_name, data_type from all_tab_columns where table_name='{table}'"
            data_type = execute_read_query(data_type_query, engine2, db_type)
            data_type = data_type.set_index("column_name")["data_type"].to_dict()
            model_class = None
        else:
            model_class = None
            data_type = {}
        oracleQueryGenerator = OracleSQLQueryGenerator(
            request,
            config_dict,
            table,
            model_class=model_class,
            operation="update",
            if_app_db_call=if_app_db,
            schema=schema,
            data_type=data_type,
        )
        if if_update_else_insert:
            sql_query = oracleQueryGenerator.bulk_update_query_generator(upsert=True, data=data)
        else:
            sql_query = oracleQueryGenerator.bulk_update_query_generator()
        data.replace({np.nan: None, pd.NaT: None}, inplace=True)
        bind_parameters = data.to_dict("records")
        with engine2[0].begin() as conn:
            conn.execute(text(sql_query), bind_parameters)
            conn.commit()
            conn.close()
    else:
        if table in admin_tables:
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
        postgres_table_name = sql.Identifier(schema, sql_table_name)
        if if_update_else_insert:
            data["sql_query"] = data.apply(
                lambda row: update_else_insert_query_generator_row_postgres(
                    row, postgres_table_name, update_data_dict, config_dict["condition"]
                ),
                axis=1,
            )
        else:
            data["sql_query"] = data.apply(
                lambda row: update_query_generator_row_postgres(
                    row, postgres_table_name, update_data_dict, config_dict["condition"]
                ),
                axis=1,
            )
        cursor = sql_engine.cursor()
        if len(data) > 1000:
            n = round(len(data) / 1000) + 1
            for batch in np.array_split(data["sql_query"].to_numpy(), n):
                batch_update_query = sql.SQL("; ").join(batch)
                cursor.execute(batch_update_query)
            sql_engine.commit()
        else:
            batch_update_query = sql.SQL("; ").join(data["sql_query"])
            cursor.execute(batch_update_query)
            sql_engine.commit()
        cursor.close()
        sql_engine.close()
    return None


def update_query_generator_row(data_row, sql_table_name, row_update_dict, conditions_list):
    set_col_list = []
    for col_idx in range(0, len(row_update_dict)):
        set_column_dict = row_update_dict[col_idx].copy()
        if not set_column_dict.get("input_value"):
            set_column_dict["input_value"] = str(data_row[set_column_dict["column_name"]]).replace("'", "''")
        else:
            pass
        set_col_list.append(set_column_dict)
    update_set_query = update_query_set_generator(set_col_list)
    row_update_dict = None
    set_col_list = None
    del set_col_list
    if conditions_list:
        condition_query = ""
        for cond_idx in range(len(conditions_list)):
            condition_dict = conditions_list[cond_idx].copy()
            if not condition_dict.get("input_value"):
                condition_dict["input_value"] = str(data_row[condition_dict["column_name"]]).replace(
                    "'", "''"
                )
            else:
                pass
            condition_query += adv_query_generator(condition_dict, sql_table_name)
        conditions_list = None
        del conditions_list
        sql_query = f"UPDATE {sql_table_name} SET {update_set_query} WHERE {condition_query}"
    else:
        sql_query = f"UPDATE {sql_table_name} SET {update_set_query}"
    return sql_query


def update_query_generator_row_postgres(data_row, sql_table_name, row_update_dict, conditions_list):
    set_col_list = []
    for col_idx in range(0, len(row_update_dict)):
        set_column_dict = row_update_dict[col_idx].copy()
        if not set_column_dict.get("input_value"):
            set_column_dict["input_value"] = str(data_row[set_column_dict["column_name"]]).replace("'", "''")
        else:
            pass
        set_col_list.append(set_column_dict)
    update_set_query = update_query_set_generator_postgres(set_col_list)
    row_update_dict = None
    set_col_list = None
    del set_col_list
    if conditions_list:
        config_dict = {}
        condition_list = []
        for cond_idx in range(len(conditions_list)):
            condition_dict = conditions_list[cond_idx].copy()
            if not condition_dict.get("input_value"):
                condition_dict["input_value"] = str(data_row[condition_dict["column_name"]]).replace(
                    "'", "''"
                )
            else:
                pass
            condition_list.append(condition_dict)
        config_dict["condition"] = condition_list
        condition_query = postgres_condition_generator(config_dict, [], [], sql_table_name)
        conditions_list = None
        del conditions_list
        sql_query = sql.SQL("UPDATE {sql_table_name} SET {update_set_query} WHERE {condition_query}").format(
            sql_table_name=sql_table_name, update_set_query=update_set_query, condition_query=condition_query
        )
    else:
        sql_query = sql.SQL("UPDATE {sql_table_name} SET {update_set_query}").format(
            sql_table_name=sql_table_name, update_set_query=update_set_query
        )
    return sql_query


def update_else_insert_query_generator_row(data_row, sql_table_name, row_update_dict, conditions_list):
    set_col_list = []
    for col_idx in range(0, len(row_update_dict)):
        set_column_dict = row_update_dict[col_idx].copy()
        if not set_column_dict.get("input_value"):
            set_column_dict["input_value"] = str(data_row[set_column_dict["column_name"]]).replace("'", "''")
        else:
            pass
        set_col_list.append(set_column_dict)
    update_set_query = update_query_set_generator(set_col_list)
    row_update_dict = None
    set_col_list = None
    del set_col_list
    data_dict = data_row.fillna("NULL").to_dict()
    insert_cols = ", ".join(data_dict.keys())
    values_string = ""
    for val in data_dict.values():
        if val != "NULL":
            values_string += f"'{val}'"
        else:
            values_string += "NULL"
        values_string += ", "
    values_string = values_string.rstrip(", ")
    if conditions_list:
        condition_query = ""
        for cond_idx in range(len(conditions_list)):
            condition_dict = conditions_list[cond_idx].copy()
            if not condition_dict.get("input_value"):
                condition_dict["input_value"] = str(data_row[condition_dict["column_name"]]).replace(
                    "'", "''"
                )
            else:
                pass
            condition_query += adv_query_generator(condition_dict, sql_table_name)
        conditions_list = None
        del conditions_list
        sql_query = f"""
        UPDATE {sql_table_name} SET {update_set_query} WHERE {condition_query}
        if @@rowcount = 0
        INSERT into {sql_table_name} ({insert_cols}) values ({values_string})
        """
    else:
        sql_query = f"""UPDATE {sql_table_name} SET {update_set_query}"""
    return sql_query


def update_else_insert_query_generator_row_postgres(
    data_row, sql_table_name, row_update_dict, conditions_list
):
    set_col_list = []
    for col_idx in range(0, len(row_update_dict)):
        set_column_dict = row_update_dict[col_idx].copy()
        if not set_column_dict.get("input_value"):
            set_column_dict["input_value"] = str(data_row[set_column_dict["column_name"]]).replace("'", "''")
        else:
            pass
        set_col_list.append(set_column_dict)
    update_set_query = update_query_set_generator_postgres(set_col_list)
    row_update_dict = None
    set_col_list = None
    del set_col_list
    data_dict = data_row.fillna("NULL").to_dict()
    insert_cols = sql.SQL(", ").join(sql.Identifier(i) for i in data_dict.keys())
    values_string = sql.SQL(", ").join(
        sql.Literal(i) if i != "NULL" else sql.SQL("NULL") for i in data_dict.values()
    )
    if conditions_list:
        config_dict = {}
        condition_list = []
        for cond_idx in range(len(conditions_list)):
            condition_dict = conditions_list[cond_idx].copy()
            if not condition_dict.get("input_value"):
                condition_dict["input_value"] = str(data_row[condition_dict["column_name"]]).replace(
                    "'", "''"
                )
            else:
                pass
            condition_list.append(condition_dict)
        config_dict["condition"] = condition_list
        condition_query = postgres_condition_generator(config_dict, [], [])
        conditions_list = None
        del conditions_list
        sql_query = sql.SQL(
            "UPDATE {sql_table_name} SET {update_set_query} WHERE {condition_query}; INSERT INTO {sql_table_name} ({insert_cols}) SELECT {values_string} WHERE NOT EXISTS (SELECT 1 FROM {sql_table_name} WHERE {condition_query})"
        ).format(
            sql_table_name=sql_table_name,
            insert_cols=insert_cols,
            values_string=values_string,
            update_set_query=update_set_query,
            condition_query=condition_query,
        )
    else:
        sql_query = sql.SQL(
            "UPDATE {sql_table_name} SET {update_set_query}; INSERT INTO {sql_table_name} ({insert_cols}) SELECT {values_string} WHERE NOT EXISTS (SELECT 1 FROM {sql_table_name})"
        ).format(
            sql_table_name=sql_table_name,
            insert_cols=insert_cols,
            values_string=values_string,
            update_set_query=update_set_query,
        )
    return sql_query


def update_query_set_generator(update_data_list):
    update_set_query = ""
    for set_dic in update_data_list:
        if set_dic["input_value"] != "NULL":
            set_dic["input_value"] = set_dic["input_value"].replace("'", "''")
            update_set_query += (
                " " + set_dic["column_name"] + "=" + "'" + set_dic["input_value"] + "'" + set_dic["separator"]
            )
        else:
            update_set_query += " " + set_dic["column_name"] + "=" + "NULL" + set_dic["separator"]
    return update_set_query


def update_query_set_generator_postgres(update_data_list):
    update_set_query = []
    for set_dic in update_data_list:
        if set_dic["input_value"] != "NULL":
            set_dic["input_value"] = set_dic["input_value"].replace("'", "''")
            update_set_query.append(
                sql.SQL("{field} = {value} {separator}").format(
                    field=sql.Identifier(set_dic["column_name"].lower()),
                    value=sql.Literal(set_dic["input_value"]),
                    separator=sql.SQL(set_dic["separator"]),
                )
            )
        else:
            update_set_query.append(
                sql.SQL("{field} = {value} {separator}").format(
                    field=sql.Identifier(set_dic["column_name"].lower()),
                    value=sql.SQL("NULL"),
                    separator=sql.SQL(set_dic["separator"]),
                )
            )
    update_col_string = sql.SQL(" ").join([i for i in update_set_query])
    return update_col_string


def app_engine_generator(request, tenant=None):
    # request.username/ redis username -> combination
    user_db_engine = ["", None]
    db_type = ""
    if not tenant:
        instance = get_current_tenant()
        if instance:
            schema = instance.name
        else:
            schema = tenant_schema_from_request(request)
    else:
        schema = tenant
    app_code, db_connection_name = current_app_db_extractor_url(request.path, schema)
    if db_connection_name != "":
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        pass
    return user_db_engine, db_type, schema


def application_database_details_extractor(request, tenant=None):
    user_db_engine = ["", None]
    db_type = ""
    db_connection_name = ""
    app_code = ""
    if not tenant:
        instance = get_current_tenant()
        if instance:
            tenant = instance.name
        else:
            tenant = tenant_schema_from_request(request)
    else:
        pass
    app_code, db_connection_name = current_app_db_extractor_url(request.path, tenant)
    if db_connection_name != "":
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        pass
    return app_code, db_connection_name, user_db_engine, db_type, tenant


def current_app_db_extractor_url(url_string, tenant):
    app_code = ""
    db_connection_name = ""
    if (
        not any(
            url_match in url_string
            for url_match in [
                "/users/selectApplication/",
                "/users/adminPanel/",
                "/users/alertsSetup/",
                "/users/customizeTheme/",
                "/users/selectDashboard/",
                "/users/dashboard/",
                "/users/previewTheme/",
                "/users/planner/",
                "/users/forum/",
                "/users/profile/",
                "/users/changeprofilename/",
                "/users/ajax/profilephoto_upload/",
                "/users/ajax/coverphoto_upload/",
                "/accounts/login/",
                "/accounts/logout/",
                "/users/plannerAPI/",
                "forum",
                "/media/",
            ]
        )
        and "/create_new/dev/application" not in url_string.lower()
        and not url_string.startswith("/account")
        and not url_string.startswith("/static")
        and not url_string.startswith("/tenant_admin")
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


def current_app_db_extractor(request, tenant=None):
    app_code = ""
    db_connection_name = ""
    if not tenant:
        instance = get_current_tenant()
        if instance:
            tenant = instance.name
        else:
            tenant = tenant_schema_from_request(request)
    else:
        pass
    url_string = request.path
    app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
    return app_code, db_connection_name


def engine_geneartor(app_code, request, tenant=None):
    user_db_engine = ["", None]
    if not tenant:
        instance = get_current_tenant()
        if instance:
            tenant = instance.name
        else:
            tenant = tenant_schema_from_request(request)
    else:
        pass
    db_type = "MSSQL"
    if app_code:
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = tenant + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
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
    engine_temp, turbodbc_connection_details = "", None
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
                        + ";Encrypt=yes;TrustServerCertificate=yes;Connect Timeout=60;"
                    )
                    engine_temp = create_engine(
                        f"mssql+pyodbc:///?odbc_connect={quoted_temp}",
                        pool_pre_ping=True,
                        pool_size=30,
                        max_overflow=10,
                        pool_recycle=900,
                        fast_executemany=False,
                    )
                    conn = engine_temp.connect()
                    conn.close()
                    turbodbc_connection_details = {
                        "driver": "ODBC Driver 18 for SQL Server",
                        "server": db_data["HOST"] + "," + db_data["PORT"],
                        "database": db_data["NAME"],
                        "uid": db_data["USER"],
                        "pwd": db_data["PASSWORD"] + ";Encrypt=yes;TrustServerCertificate=yes;",
                        "turbodbc_options": make_options(
                            prefer_unicode=True,
                            use_async_io=True,
                            varchar_max_character_limit=10000000,
                            autocommit=True,
                        ),
                    }
                    turbodbc_connection = db_connection_generator(turbodbc_connection_details)
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_connection], db_type
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            elif db_data["db_type"] == "PostgreSQL":
                try:
                    engine_temp = {
                        "dbname": db_data["NAME"],
                        "user": db_data["USER"],
                        "password": db_data["PASSWORD"],
                        "host": db_data["HOST"],
                        "port": db_data["PORT"],
                        "schema": db_data["schema"],
                    }
                    turbodbc_connection_details = None
                    database_engine_dict[db_connection_name] = [
                        engine_temp,
                        turbodbc_connection_details,
                    ], db_type
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            elif db_data["db_type"] == "Oracle":
                try:
                    if db_data.get("db_connection_mode") == "thick":
                        oracledb.init_oracle_client()
                        thick_mode = True
                    else:
                        thick_mode = False
                    engine_temp = create_engine(
                        f'oracle+oracledb://{db_data["USER"]}:{db_data["PASSWORD"]}@',
                        thick_mode=thick_mode,
                        connect_args={
                            "host": db_data["HOST"],
                            "port": db_data["PORT"],
                            "service_name": db_data["service_name"],
                        },
                        pool_pre_ping=True,
                        pool_size=30,
                        max_overflow=10,
                        pool_recycle=900,
                    )
                    turbodbc_connection = None
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_connection], db_type
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            else:
                pass
            json_file.close()
    return [engine_temp, turbodbc_connection_details], db_type


def execute_read_query(sql_query, con_detail, db_type="MSSQL", chunksize=10**5, set_iter_size=False):
    sql_query = sql_query.split(";")[0]
    sql_engine, turb_connection = con_detail
    if db_type == "PostgreSQL":
        sql_engine = postgreSQL_engine_generator(sql_engine)
        if set_iter_size:
            with sql_engine.cursor(name='custom_cursor') as cursor:
                cursor.itersize = chunksize
                cursor.execute(sql_query)
                records = cursor.fetchall()
        else:
            cursor = sql_engine.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        table = pd.DataFrame(records, columns=col_names)
    else:
        table = pd.DataFrame()
        sql_query = text(sql_query)
        cursor = sql_engine.connect()
        for chunk in pd.read_sql_query(sql_query, cursor, chunksize=chunksize):
            table = pd.concat([table, chunk], ignore_index=True)
        cursor.close()
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


def pandas_push(table, db_table_name, con, if_exists="append", chunksize=2000):
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
        sql_table = bcpy.SqlTable(server_config, table=db_table_name)
        bdf.to_sql(sql_table, use_existing_sql_table=True)
        return True
    else:
        raise Exception("Server config not found!")


def non_standard_read_data_func(sql_query, engine2=[engine, turbodbc_connection], db_type="MSSQL",chunksize = 10 ** 5,set_iter_size=False):
    table = execute_read_query(sql_query, engine2,db_type,chunksize=chunksize,set_iter_size=set_iter_size)
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
    for col in data_table.select_dtypes(include=["int64", "int32"]).columns:
        data_table[col] = data_table[col].astype(int)
    if db_table_name not in ["users_profile"]:
        column = sql.SQL(", ").join([sql.Identifier(field.lower()) for field in data_table.columns])
    else:
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
    sql_query = sql.SQL("INSERT INTO {table} ({columnnames}) VALUES %s").format(
        table=postgres_table_name, columnnames=column
    )

    data = list(data_table.itertuples(index=False, name=None))
    row_count = data_table.shape[0]
    data_table = None
    page_size = max(10000, row_count)
    cursor = sql_engine.cursor()
    psycopg2.extras.execute_values(cursor, sql_query, data, template=None, page_size=page_size)
    sql_engine.commit()
    cursor.close()
    sql_engine.close()
    return True


def adv_query_generator(adv_condition, sql_table_name):
    query_tag2 = ""
    if adv_condition["condition"] == "Greater than":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + sql_table_name
                + "."
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
                    + sql_table_name
                    + "."
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
                    + sql_table_name
                    + "."
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
                + sql_table_name
                + "."
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
                    + sql_table_name
                    + "."
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
                    + sql_table_name
                    + "."
                    + (adv_condition["column_name"])
                    + " "
                    + "<"
                    + " "
                    + adv_condition["input_value"]
                    + " "
                    + adv_condition["and_or"]
                )
    elif adv_condition["condition"] == "Equal to":
        if adv_condition["column_name"][0] == "(":
            sql_table_name = "(" + sql_table_name
            column_name = adv_condition["column_name"][1:]
        else:
            column_name = adv_condition["column_name"]
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + sql_table_name
                + "."
                + (column_name)
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
                + sql_table_name
                + "."
                + (column_name)
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
            + sql_table_name
            + "."
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
            + sql_table_name
            + "."
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
                + sql_table_name
                + "."
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
                + sql_table_name
                + "."
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
    elif adv_condition["condition"] == "Smaller than equal to":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + sql_table_name
                + "."
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
                    + sql_table_name
                    + "."
                    + (adv_condition["column_name"])
                    + " "
                    + "<="
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
                    + sql_table_name
                    + "."
                    + (adv_condition["column_name"])
                    + " "
                    + "<="
                    + " "
                    + adv_condition["input_value"]
                    + " "
                    + adv_condition["and_or"]
                )
    elif adv_condition["condition"] == "Greater than equal to":
        if adv_condition["input_value"] == "NULL":
            query_tag2 = (
                query_tag2
                + " "
                + sql_table_name
                + "."
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
                    + sql_table_name
                    + "."
                    + (adv_condition["column_name"])
                    + " "
                    + ">="
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
                    + sql_table_name
                    + "."
                    + (adv_condition["column_name"])
                    + " "
                    + ">="
                    + " "
                    + adv_condition["input_value"]
                    + " "
                    + adv_condition["and_or"]
                )
    elif adv_condition["condition"] == "Between":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "BETWEEN"
            + " "
            + "'"
            + adv_condition["input_value_lower"]
            + "'"
            + " "
            + "AND"
            + " "
            + "'"
            + adv_condition["input_value_upper"]
            + "'"
            + " "
            + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Starts with":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "LIKE"
            + " "
            + "'"
            + adv_condition["input_value"]
            + "%"
            "'" + " " + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Ends with":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "LIKE"
            + " "
            + "'"
            "%" + adv_condition["input_value"] + "'" + " " + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Contains":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "LIKE"
            + " "
            + "'"
            "%" + adv_condition["input_value"] + "%"
            "'" + " " + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Not Starts with":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "NOT LIKE"
            + " "
            + "'"
            + adv_condition["input_value"]
            + "%"
            "'" + " " + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Not Ends with":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "NOT LIKE"
            + " "
            + "'"
            "%" + adv_condition["input_value"] + "'" + " " + adv_condition["and_or"]
        )
    elif adv_condition["condition"] == "Not Contains":
        query_tag2 = (
            query_tag2
            + " "
            + sql_table_name
            + "."
            + (adv_condition["column_name"])
            + " "
            + "NOT LIKE"
            + " "
            + "'"
            "%" + adv_condition["input_value"] + "%"
            "'" + " " + adv_condition["and_or"]
        )
    return query_tag2


def convert_format(config_dict, request, table, engine2):
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

        for i in range(0, len(config_dict)):
            if (
                config_dict[i]["condition"] != "Between"
                and config_dict[i]["condition"] != "IN"
                and config_dict[i]["condition"] != "NOT IN"
                and config_dict[i]["input_value"] != "NULL"
            ):
                try:
                    if config_dict[i]["column_name"] in cond_date_list:
                        if config_dict[i]["input_value"] != "":
                            config_dict[i]["input_value"] = pd.to_datetime(
                                config_dict[i]["input_value"]
                            ).strftime("%Y-%m-%d")

                    if config_dict[i]["column_name"] in cond_datetime_list:
                        if config_dict[i]["input_value"] != "":
                            config_dict[i]["input_value"] = pd.to_datetime(
                                config_dict[i]["input_value"]
                            ).strftime("%Y-%m-%d %H:%M:%S.%f")
                            config_dict[i]["input_value"] = config_dict[i]["input_value"][:-3]
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            else:
                if (
                    config_dict[i]["condition"] != "IN"
                    and config_dict[i]["condition"] != "NOT IN"
                    and config_dict[i].get("input_value") != "NULL"
                ):
                    try:
                        if config_dict[i]["column_name"] in cond_date_list:
                            if config_dict[i]["input_value_lower"] != "":
                                config_dict[i]["input_value_lower"] = pd.to_datetime(
                                    config_dict[i]["input_value_lower"]
                                ).strftime("%Y-%m-%d")
                                config_dict[i]["input_value_upper"] = pd.to_datetime(
                                    config_dict[i]["input_value_upper"]
                                ).strftime("%Y-%m-%d")
                        if config_dict[i]["column_name"] in cond_datetime_list:
                            if config_dict[i]["input_value_lower"] != "":
                                config_dict[i]["input_value_lower"] = pd.to_datetime(
                                    config_dict[i]["input_value_lower"]
                                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                                config_dict[i]["input_value_lower"] = config_dict[i]["input_value_lower"][:-3]
                                config_dict[i]["input_value_upper"] = pd.to_datetime(
                                    config_dict[i]["input_value_upper"]
                                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                                config_dict[i]["input_value_upper"] = config_dict[i]["input_value_upper"][:-3]
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
    return config_dict


def adv_query_generator2(
    adv_condition,
    condition,
    request,
    table,
    engine2,
    sql_table_name,
    column,
    agg_query="",
    order_query="",
    is_active_flag_bool=True,
    apply_joins=False,
    join_columns="",
    join_query="",
    join_table_level_cons={},
):
    adv_condition = convert_format(adv_condition, request, table, engine2)
    condition = convert_format(condition, request, table, engine2)
    condition2 = condition.copy()
    sql_query = ""
    query_tag = ""
    query_tag2 = ""

    for i in range(0, len(adv_condition)):
        query_tag2 = adv_query_generator(adv_condition[i], adv_condition[i].get("table_name", sql_table_name))
        table_name = adv_condition[i].get("table_name", sql_table_name)

        for j in range(0, len(condition)):
            if adv_condition[i]["constraintName"] == condition[j]["constraintName"]:
                if adv_condition[i]["ruleSet"] == condition[j]["ruleSet"]:
                    and_or = " and "
                else:
                    and_or = " or "
                if query_tag2:
                    query_tag2 = (
                        query_tag2
                        + and_or
                        + adv_query_generator(
                            condition[j], condition[j].get("table_name", sql_table_name)
                        ).removesuffix("AND")
                    )
                else:
                    query_tag2 = query_tag2 + adv_query_generator(
                        condition[j], condition[j].get("table_name", sql_table_name)
                    ).removesuffix("AND")
                condition2.remove(condition[j])

        if i == 0:
            query_tag = query_tag + table_name + "." + adv_condition[i]["column_name"] + " = "
            if is_active_flag_bool:
                if query_tag2:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where {query_tag2} and ({table_name}.is_active_flag IS NULL  or  {table_name}.is_active_flag != 'No' ))"
                else:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where ({table_name}.is_active_flag IS NULL  or  {table_name}.is_active_flag != 'No' ))"
            else:
                if query_tag2:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where {query_tag2})"
                else:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name})"
        else:
            query_tag = query_tag + " and " + table_name + "." + adv_condition[i]["column_name"] + " = "
            if is_active_flag_bool:
                if query_tag2:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where {query_tag2} and ({table_name}.is_active_flag IS NULL  or  {table_name}.is_active_flag != 'No' ))"
                else:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where ({table_name}.is_active_flag IS NULL  or  {table_name}.is_active_flag != 'No' ))"
            else:
                if query_tag2:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name} where {query_tag2})"
                else:
                    query_tag += f"(select {adv_condition[i]['agg_condition']}({table_name}.{adv_condition[i]['column_name']}) from {table_name})"

    cond_dic = {}
    for i in range(0, len(condition)):
        if condition[i]["constraintName"] in cond_dic:
            existing_val = cond_dic[condition[i]["constraintName"]]
            t_list = []
            for t in existing_val:
                t_list.append(t)
            t_list.append(condition[i])
            cond_dic[condition[i]["constraintName"]] = t_list
        else:
            cond_dic[condition[i]["constraintName"]] = [condition[i]]

    for key, value in cond_dic.items():
        if len(value) == 1:
            if query_tag:
                query_tag = (
                    query_tag
                    + " and "
                    + adv_query_generator(value[0], value[0].get("table_name", sql_table_name)).removesuffix(
                        "AND"
                    )
                )
            else:
                query_tag = query_tag + adv_query_generator(
                    value[0], value[0].get("table_name", sql_table_name)
                ).removesuffix("AND")
        else:
            rule_set_list = {i["ruleSet"] for i in value}
            cond_query = "("
            for r_idx, rule in enumerate(rule_set_list):
                rule_query = "("
                rule_conditions = [i for i in value if i["ruleSet"] == rule]
                for rule_idx, rule_cond in enumerate(rule_conditions):
                    rule_query += adv_query_generator(
                        rule_cond, rule_cond.get("table_name", sql_table_name)
                    ).removesuffix("AND")
                    if rule_query.endswith("OR"):
                        rule_query = rule_query.removesuffix("OR")
                    elif rule_query.endswith("or"):
                        rule_query = rule_query.removesuffix("or")
                    elif rule_query.endswith("AND"):
                        rule_query = rule_query.removesuffix("AND")
                    elif rule_query.endswith("and"):
                        rule_query = rule_query.removesuffix("and")
                    else:
                        pass
                    if rule_idx != len(rule_conditions) - 1:
                        rule_query += " AND "
                    else:
                        continue
                rule_query += ")"
                cond_query += rule_query
                if r_idx != len(rule_set_list) - 1:
                    cond_query += " OR "
                else:
                    continue
            cond_query += ")"
            if query_tag:
                query_tag += " AND "
                query_tag += cond_query
            else:
                query_tag += cond_query

    sql_query = f"select {agg_query} {column} from {sql_table_name} where {query_tag} {order_query};"
    if apply_joins:
        sql_query = (
            f"select {join_columns} from {sql_table_name} {join_query} where {query_tag} {order_query}"
        )
        if join_table_level_cons.get(sql_table_name):
            condition_sub_query = condition_sub_query_generator(
                join_table_level_cons, sql_table_name, request, engine2, db_type="MSSQL"
            )
            sql_query = f"select {join_columns} from ({condition_sub_query}) AS {sql_table_name} {join_query} where {query_tag} {order_query}"
    return sql_query


def db_name_extractor(request, app_code):
    tenant = tenant_schema_from_request(request)
    app_db_mapping = {}
    user_db_mapping = {}
    db_name = ""
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            user_db_mapping = json.load(json_file)
            json_file.close()
    if app_db_mapping and user_db_mapping:
        tenant_app_code = tenant + "_" + app_code
        db_connection_name = app_db_mapping[tenant_app_code]
        db_server, port, db_name, username, password = decrypt_existing_db_credentials(
            user_db_mapping[db_connection_name]["server"],
            user_db_mapping[db_connection_name]["port"],
            user_db_mapping[db_connection_name]["db_name"],
            user_db_mapping[db_connection_name]["username"],
            user_db_mapping[db_connection_name]["password"],
            user_db_mapping[db_connection_name]["connection_code"],
        )
    return db_name


def raw_query_executor(query, db_engine, db_type):
    if db_type in ["MSSQL", "Oracle"]:
        query = query.split(";")[0]
        query = text(query)
        with db_engine[0].begin() as conn:
            conn.execute(query)
            conn.commit()
            conn.close()
    else:
        sql_engine = postgreSQL_engine_generator(db_engine[0])
        cursor = sql_engine.cursor()
        cursor.execute(query)
        sql_engine.commit()
        cursor.close()
        sql_engine.close()
    return True


def extract_foreign_keys(table_name, db_engine, db_type):
    if db_type == "MSSQL":
        table = non_standard_read_data_func(f"EXEC sp_fkeys '{table_name}';", db_engine, db_type)
    elif db_type == "Oracle":
        table = non_standard_read_data_func(
            f"""
        SELECT a.table_name, a.column_name, a.constraint_name, c.owner,
            -- referenced pk
            c.r_owner, c_pk.table_name r_table_name, c_pk.constraint_name r_pk
        FROM all_cons_columns a
        JOIN all_constraints c ON a.owner = c.owner
                                AND a.constraint_name = c.constraint_name
        JOIN all_constraints c_pk ON c.r_owner = c_pk.owner
                                AND c.r_constraint_name = c_pk.constraint_name
        WHERE c.constraint_type = 'R'
        AND a.table_name = '{table_name.upper()}';
        """,
            db_engine,
            db_type,
        )
        table.rename(
            {"table_name": "FKTABLE_NAME", "column_name": "FKCOLUMN_NAME", "r_table_name": "PKTABLE_NAME"},
            axis=1,
            inplace=True,
        )
        table["PKCOLUMN_NAME"] = "id"
    else:
        table = non_standard_read_data_func(
            f"""
        SELECT
            r.table_name as child_table, r.column_name as child_column, u.table_name as parent_table, u.column_name as parent_column
        FROM information_schema.constraint_column_usage       u
        INNER JOIN information_schema.referential_constraints fk
                ON u.constraint_catalog = fk.unique_constraint_catalog
                    AND u.constraint_schema = fk.unique_constraint_schema
                    AND u.constraint_name = fk.unique_constraint_name
        INNER JOIN information_schema.key_column_usage        r
                ON r.constraint_catalog = fk.constraint_catalog
                    AND r.constraint_schema = fk.constraint_schema
                    AND r.constraint_name = fk.constraint_name
        WHERE
            u.table_schema = '{db_engine[0]['schema']}' AND
            u.table_name = '{table_name}';
        """,
            db_engine,
            db_type,
        )

        table.rename(
            {
                "child_table": "FKTABLE_NAME",
                "child_column": "FKCOLUMN_NAME",
                "parent_table": "PKTABLE_NAME",
                "parent_column": "PKCOLUMN_NAME",
            },
            axis=1,
            inplace=True,
        )
    return table


def input_validation_check(input_value_check):
    input_value_check.replace(" ", "")
    exclusion_list = ["'+", "'and", "'or", "'%", "'--", "';", "Waitfor", "delay", "lag", "getdate()"]
    count_single_quote = input_value_check.count("'")
    if count_single_quote > 1:
        if any(item.lower() in input_value_check.lower() for item in exclusion_list):
            raise Exception("Attempt for SQL Injection! Request cannot be completed")
        else:
            pass
    return None


def join_query_generator(config_dict, request, engine, db_type):
    join_table_data = config_dict.get("join_table_data")
    apply_join = config_dict.get("apply_join")
    aliases = config_dict.get("aliases")
    table_names = config_dict.get("join_table_names")

    common_columns = config_dict.get("common_columns")
    type_of_join = config_dict.get("type_of_join")

    join_table_level_conditions = config_dict.get("join_table_data").get("join_table_level_conditions", {})

    join_select_columns = ""
    columns_set = set()
    for table in join_table_data["tables"]:
        table_name = table
        if "users_" + table.lower() in table_names:
            table_name = "users_" + table_name.lower()
        else:
            pass
        columns_joins = join_table_data["tables"][table]
        for column in columns_joins:
            if aliases and aliases.get("join_table_aliases"):
                if aliases["join_table_aliases"].get(table):
                    alias = aliases["join_table_aliases"][table].get(column, "")
                else:
                    alias = ""
            else:
                alias = ""
            if column not in columns_set:
                if alias != "":
                    join_select_columns += f'{table_name}.{column} as "{alias}", '
                if alias == "":
                    join_select_columns += f"{table_name}.{column}, "
            else:
                if alias != "":
                    join_select_columns += f'{table_name}.{column} as "{alias}", '
                if alias == "":
                    join_select_columns += f'{table_name}.{column} as "{table}.{column}", '
            columns_set.add(column)
    join_select_columns = join_select_columns[:-2]
    join_query = ""
    if db_type == "MSSQL":
        for i, table in enumerate(table_names):
            if i == 0:
                continue
            join_statement = f"{table}.{common_columns[i]} = {table_names[0]}.{common_columns[0]}"
            if join_table_level_conditions.get(table):
                join_sub_query = condition_sub_query_generator(
                    join_table_level_conditions, table, request, engine, db_type
                )
                join_query += f" {type_of_join} ({join_sub_query}) AS {table} ON {join_statement} "
            else:
                join_query += f" {type_of_join} {table} ON {join_statement}"

    if db_type == "PostgreSQL":
        join_select_columns = sql.SQL(join_select_columns)
        join_query = sql.SQL("")
        for i, table in enumerate(table_names):
            if i == 0:
                continue
            join_statement = sql.SQL("{col_id1} = {col_id2}").format(
                col_id1=sql.Identifier(table, common_columns[i]),
                col_id2=sql.Identifier(table_names[0], common_columns[0]),
            )
            if join_table_level_conditions.get(table):
                join_sub_query = condition_sub_query_generator(
                    join_table_level_conditions, table, request, engine, db_type
                )
                join_query += sql.SQL(
                    " {type_of_join} ({join_sub_query}) AS {table} ON {join_statement}"
                ).format(
                    type_of_join=sql.SQL(type_of_join),
                    join_sub_query=join_sub_query,
                    table=sql.Identifier(table),
                    join_statement=join_statement,
                )
            else:
                join_query += sql.SQL(" {type_of_join} {table} ON {join_statement}").format(
                    type_of_join=sql.SQL(type_of_join),
                    table=sql.Identifier(table),
                    join_statement=join_statement,
                )

    return join_select_columns, join_query


def condition_sub_query_generator(conditions, sql_table_name, request, engine, db_type):
    if db_type == "MSSQL":
        table_name = conditions.get(sql_table_name)[0]["table"]
        sub_query = (
            adv_query_generator2(
                [], conditions.get(sql_table_name), request, table_name, engine, sql_table_name, "*"
            )
            .strip()
            .rstrip(";")
        )
        return sub_query
    if db_type == "PostgreSQL":
        table_name = conditions.get(sql_table_name)[0]["table"]
        modelName = get_model_class(table_name, request, db_engine=engine, db_type=db_type)
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
        conditions_query = postgres_condition_generator(
            {"condition": conditions.get(sql_table_name)}, cond_date_list, cond_datetime_list
        )
        sub_query = sql.SQL("SELECT * FROM {sql_table_name} WHERE {cond}").format(
            sql_table_name=sql.Identifier(sql_table_name), cond=conditions_query
        )
        return sub_query


def group_by_query_generator(config_dict, if_app_db):
    aliases = config_dict.get("aliases")
    group_by_select_columns = ""
    group_by_query = ""
    group_by_aggregations = {}

    columns_set = set()
    for table in config_dict["group_by_configs"]["group_by_tables"]:

        sql_table_name = get_sql_table_name(table, if_app_db)
        for column in config_dict["group_by_configs"]["group_by_columns"][table]:
            if aliases and aliases.get("join_table_aliases"):
                if aliases["join_table_aliases"].get(table):
                    alias = aliases["join_table_aliases"][table].get(column, "")
                else:
                    alias = ""
            else:
                alias = ""
            group_by_query += f"{sql_table_name}.{column}, "
            if column not in columns_set:
                if alias != "":
                    group_by_select_columns += f'{sql_table_name}.{column} AS "{alias}", '
                if alias == "":
                    group_by_select_columns += f"{sql_table_name}.{column}, "
            else:
                if alias != "":
                    group_by_select_columns += f'{sql_table_name}.{column} AS "{alias}", '
                if alias == "":
                    group_by_select_columns += f'{sql_table_name}.{column} AS "{sql_table_name}.{column}", '
            columns_set.add(column)
        if config_dict["group_by_configs"].get("aggregations"):
            aggregations = config_dict["group_by_configs"]["aggregations"].get(table)
            if aggregations:
                for key, aggregations_list in aggregations.items():
                    group_by_aggregations[f"{sql_table_name}.{key}"] = aggregations_list
            else:
                pass
        else:
            pass

    group_by_select_columns = group_by_select_columns[:-2]
    group_by_query = group_by_query[:-2]

    return group_by_select_columns, group_by_query, group_by_aggregations


def get_aggregation_query(agg_col_identifier, aggregation_type, aggregation_alias):
    if aggregation_type == "sum":
        return sql.SQL('SUM({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "average":
        return sql.SQL('AVG({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "variance":
        return sql.SQL('var_pop({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "standard deviation":
        return sql.SQL('stddev_pop({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "count":
        return sql.SQL('COUNT({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "count distinct":
        return sql.SQL('COUNT(DISTINCT {agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "maximum":
        return sql.SQL('MAX({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "minimum":
        return sql.SQL('MIN({agg_col}) AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    elif aggregation_type == "percentage of total":
        return sql.SQL('SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS "{as_name}"').format(
            agg_col=agg_col_identifier,
            as_name=sql.SQL(aggregation_alias),
        )
    else:
        return sql.SQL("")


def order_by_query_generator(config_dict, if_app_db):
    order_by_configs = config_dict.get("order_by_configs")
    order_by_query = "ORDER BY "

    for column in order_by_configs:
        if "." in column:
            group_by_table, group_by_column = column.split(".").copy()
            group_by_table = get_sql_table_name(group_by_table, if_app_db)
            order_by_query += f"{group_by_table}.{group_by_column} {order_by_configs[column]}, "
        else:
            order_by_query += f'"{column}" {order_by_configs[column]}, '
    order_by_query = order_by_query[:-2]

    return order_by_query


def get_sql_table_name(table_name, if_app_db):
    if if_app_db:
        if (
            table_name
            not in [
                "information_schema.columns",
                "information_schema.tables",
                "auth_group",
                "auditlog_logentry",
                "django_apscheduler_djangojobexecution",
                "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                "INFORMATION_SCHEMA.constraint_column_usage",
                "master.dbo.sysdatabases",
                "sys.default_constraints",
            ]
            and not table_name.startswith("information_schema")
            and not table_name.startswith("INFORMATION_SCHEMA")
        ):
            return "users_" + table_name.lower()
        else:
            return table_name
    else:
        return table_name
