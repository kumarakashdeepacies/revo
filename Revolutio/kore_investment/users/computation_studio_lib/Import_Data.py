import json
import os

import pandas as pd
import psycopg2

from config.settings.base import MEDIA_ROOT, PLATFORM_FILE_PATH
from kore_investment.users.computations import dynamic_model_create, standardised_functions
from kore_investment.users.computations.db_centralised_function import db_name_extractor, read_data_func
from kore_investment.users.computations.db_connection_handlers import (
    mssql_engine_generator,
    oracle_engine_generator,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.computations.file_storage import (
    file_storage_checker,
    read_computation_from_storage,
)
from kore_investment.utils.utilities import tenant_schema_from_request


def import_run_step(config_dict, request, if_app_db=True):
    curr_app_code, db_connection_name = standardised_functions.current_app_db_extractor(request)
    table = config_dict["inputs"]["Table"]
    data_table_query = ""
    priv_field_list = []
    privacy_config = {}
    is_id_present = False
    if config_dict["inputs"].get("connection_name"):
        connection_name = config_dict["inputs"]["connection_name"]
    else:
        connection_name = "default"
    rtf_columns = []
    if if_app_db:
        modelName = dynamic_model_create.get_model_class(table, request)

        rtf_columns = [
            field.name for field in modelName.concrete_fields if field.get_internal_type() in ["RTFField"]
        ]

        is_rft_field_present = False
        for kk in rtf_columns:
            if kk in config_dict["inputs"]["Columns"]:
                is_rft_field_present = True
        if len(rtf_columns) > 0 and is_rft_field_present:
            if "id" in config_dict["inputs"]["Columns"]:
                is_id_present = True
            else:
                config_dict["inputs"]["Columns"].append("id")

        for field in modelName.concrete_fields:
            if field.get_internal_type() == "PrivacyField":
                priv_field_list.append(field.name)
                privacy_config[field.name] = json.loads(field.privacy_config)

    if connection_name == "default":
        access_controller = False
        if "disableAccessControls" in config_dict["inputs"].keys():
            access_controller = not config_dict["inputs"]["disableAccessControls"]
        data_mapper = config_dict["data_mapper"]
        if data_mapper.get("parentData"):
            if isinstance(data_mapper.get("data_source"), pd.DataFrame) or isinstance(
                data_mapper.get("data_source"), str
            ):
                parent_table_column = config_dict["inputs"]["parent_table_column"]
                current_table_column = config_dict["inputs"]["current_table_column"]
                if isinstance(data_mapper.get("data_source"), pd.DataFrame):
                    parent_data = data_mapper["data_source"]
                    if parent_data[parent_table_column].dtype == "datetime64[ns]":
                        parent_data = parent_data[parent_table_column].apply(str).unique().tolist()
                    else:
                        parent_data = parent_data[parent_table_column].unique().tolist()
                elif file_storage_checker(data_mapper.get("data_source")):
                    parent_data = read_computation_from_storage(
                        data_mapper.get("data_source"), columns=[parent_table_column]
                    )
                    if parent_data[parent_table_column].dtype == "datetime64[ns]":
                        parent_data = parent_data[parent_table_column].apply(str).unique().tolist()
                    else:
                        parent_data = parent_data[parent_table_column].unique().tolist()
                else:
                    parent_data = None
                if parent_data:
                    config_dict["condition"].append(
                        {
                            "column_name": current_table_column,
                            "condition": "IN",
                            "input_value": parent_data,
                            "and_or": "",
                            "constraintName": "parent_filter",
                            "ruleSet": "parent_filter",
                        }
                    )
                else:
                    pass
            else:
                pass
        else:
            pass
        if access_controller:
            if len(priv_field_list) > 0:
                new_config_cond = False
                new_config_adv_cond = False
                if config_dict.get("condition"):
                    if config_dict["condition"][0].get("constraintName"):
                        new_config_cond = True
                    else:
                        pass
                else:
                    pass
                if config_dict.get("adv_condition"):
                    if config_dict["adv_condition"][0].get("constraintName"):
                        new_config_adv_cond = True
                for priv_field, priv_conf in privacy_config.items():
                    if priv_conf["privacy_option"] == "groups":
                        uid = read_data_func(
                            request,
                            {
                                "inputs": {"Data_source": "Database", "Table": "Profile", "Columns": ["id"]},
                                "condition": [
                                    {
                                        "column_name": "username",
                                        "condition": "Equal to",
                                        "input_value": str(request.user.username),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )["id"].tolist()

                        group_ids = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "user_groups",
                                    "Columns": ["group_id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "user_id",
                                        "condition": "IN",
                                        "input_value": str(tuple(uid)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        ).group_id.tolist()

                        curr_user_group = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "auth_group",
                                    "Columns": ["name"],
                                },
                                "condition": [
                                    {
                                        "column_name": "id",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_ids)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        ).name.tolist()

                        if new_config_cond or new_config_adv_cond:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "constraintName": "p2",
                                    "ruleSet": "Blank",
                                    "and_or": "",
                                }
                            )
                            for ug in curr_user_group:
                                config_dict["condition"].append(
                                    {
                                        "column_name": f"{priv_field}",
                                        "condition": "Contains",
                                        "input_value": f"""["]{ug}["]""",
                                        "constraintName": "p2",
                                        "ruleSet": f"{ug}",
                                        "and_or": "",
                                    }
                                )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "constraintName": "p2",
                                    "ruleSet": "NULL",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Creator",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                        else:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"({priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "and_or": "or",
                                }
                            )
                            for ug in curr_user_group:
                                config_dict["condition"].append(
                                    {
                                        "column_name": f"{priv_field}",
                                        "condition": "Contains",
                                        "input_value": f"""["]{ug}["]""",
                                        "and_or": "or",
                                    }
                                )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "and_or": "and",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": ")",
                                }
                            )

                    elif priv_conf["privacy_option"] == "master":
                        curr_grp_from_user = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Agg_Type": "DISTINCT",
                                    "Table": priv_conf["master_table"],
                                    "Columns": [priv_conf["group_field"]],
                                },
                                "condition": [
                                    {
                                        "column_name": priv_conf["user_field"],
                                        "condition": "Equal to",
                                        "input_value": request.user.username,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                        curr_grp_from_user = curr_grp_from_user[priv_conf["group_field"]].tolist()
                        if new_config_cond or new_config_adv_cond:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "constraintName": "p2",
                                    "ruleSet": "Blank",
                                    "and_or": "",
                                }
                            )
                            for ug in curr_grp_from_user:
                                config_dict["condition"].append(
                                    {
                                        "column_name": f"{priv_field}",
                                        "condition": "Contains",
                                        "input_value": f"""["]{ug}["]""",
                                        "constraintName": "p2",
                                        "ruleSet": f"{ug}",
                                        "and_or": "",
                                    }
                                )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "constraintName": "p2",
                                    "ruleSet": "NULL",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Creator",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                        else:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"({priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "and_or": "or",
                                }
                            )
                            for ug in curr_grp_from_user:
                                config_dict["condition"].append(
                                    {
                                        "column_name": f"{priv_field}",
                                        "condition": "Contains",
                                        "input_value": f"""["]{ug}["]""",
                                        "and_or": "or",
                                    }
                                )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "and_or": "and",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": ")",
                                }
                            )
                    else:
                        if new_config_cond or new_config_adv_cond:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "constraintName": "p2",
                                    "ruleSet": "Blank",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Contains",
                                    "input_value": f"""["]{request.user.username}["]""",
                                    "constraintName": "p2",
                                    "ruleSet": f"{request.user.username}",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "constraintName": "p2",
                                    "ruleSet": "NULL",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Creator",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "constraintName": "p2",
                                    "ruleSet": "Restrict all",
                                    "and_or": "",
                                }
                            )
                        else:
                            config_dict["condition"].append(
                                {
                                    "column_name": f"({priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"[]",
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Contains",
                                    "input_value": f"""["]{request.user.username}["]""",
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"{priv_field}",
                                    "condition": "Equal to",
                                    "input_value": f"NULL",
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": f"created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": "or",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": priv_field,
                                    "condition": "Contains",
                                    "input_value": f"all",
                                    "and_or": "and",
                                }
                            )
                            config_dict["condition"].append(
                                {
                                    "column_name": "created_by",
                                    "condition": "Equal to",
                                    "input_value": request.user.username,
                                    "and_or": ")",
                                }
                            )
            else:
                pass
        else:
            pass
        data_table_query = read_data_func(
            request, config_dict, if_app_db=True, access_controller=access_controller
        )
    else:
        filename = f"{PLATFORM_FILE_PATH}external_databases.json"
        external_databases_config = {}
        if os.path.exists(filename):
            with open(filename, "r+") as fout:
                external_databases_config = json.load(fout)
                fout.close()
        else:
            pass
        if external_databases_config.get(connection_name):
            ext_db_config = external_databases_config[connection_name]
            server = ext_db_config["server"]
            db_name = ext_db_config["db_name"]
            username = ext_db_config["username"]
            password = ext_db_config["password"]
            port = ext_db_config["port"]
            db_type = ext_db_config["db_type"]
            schema = ext_db_config.get("schema", "")
            if "connection_code" in external_databases_config[connection_name]:
                connection_code = external_databases_config[connection_name]["connection_code"]
                server, port, db_name, username, password = decrypt_existing_db_credentials(
                    server, port, db_name, username, password, connection_code
                )
                ext_db_config["server"] = server
                ext_db_config["db_name"] = db_name
                ext_db_config["username"] = username
                ext_db_config["password"] = password
                ext_db_config["port"] = port
            else:
                (
                    encrypted_server,
                    encrypted_port,
                    encrypted_database,
                    encrypted_username,
                    encrypted_user_secret_key,
                    connection_code,
                ) = encrypt_db_credentials(server, port, database, username, user_secret_key)
                content_encrypted = external_databases_config
                content_encrypted[connection_name]["server"] = encrypted_server
                content_encrypted[connection_name]["port"] = encrypted_port
                content_encrypted[connection_name]["db_name"] = encrypted_database
                content_encrypted[connection_name]["username"] = encrypted_username
                content_encrypted[connection_name]["password"] = encrypted_user_secret_key
                content_encrypted[connection_name]["connection_code"] = connection_code
                with open(filename, "w") as f:
                    json.dump(content_encrypted, f, indent=4)
                    f.close()
            ext_db_config["port"] = port
            ext_db_config["dbname"] = db_name
            ext_db_config["user"] = username
            ext_db_config["host"] = server

            if db_type == "MSSQL":
                db_engine = mssql_engine_generator(ext_db_config)
            elif db_type == "PostgreSQL":
                db_engine = psycopg2.connect(
                    dbname=db_name,
                    user=username,
                    password=password,
                    host=server,
                    port=port,
                )
            elif db_type == "Oracle":
                db_engine = oracle_engine_generator(ext_db_config)
            else:
                raise Exception
            data_mapper = config_dict.get("data_mapper")
            if data_mapper:
                if data_mapper.get("parentData"):
                    if data_mapper.get("data_source"):
                        parent_table_column = config_dict["inputs"]["parent_table_column"]
                        current_table_column = config_dict["inputs"]["current_table_column"]
                        if file_storage_checker(data_mapper.get("data_source")):
                            parent_data = read_computation_from_storage(
                                data_mapper.get("data_source"), columns=[parent_table_column]
                            )
                            if parent_data[parent_table_column].dtype == "datetime64[ns]":
                                parent_data = parent_data[parent_table_column].apply(str).unique().tolist()
                            else:
                                parent_data = parent_data[parent_table_column].unique().tolist()
                            config_dict["condition"].append(
                                {
                                    "column_name": current_table_column,
                                    "condition": "IN",
                                    "input_value": parent_data,
                                    "and_or": "",
                                    "constraintName": "parent_filter",
                                    "ruleSet": "parent_filter",
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
            if db_type == "PostgreSQL":
                engine_to_send = ext_db_config
            else:
                engine_to_send = db_engine
            data_table_query = read_data_func(
                request,
                config_dict,
                engine2=[engine_to_send, None],
                if_app_db=False,
                db_type=db_type,
                chunksize=10**5,
                schema=schema,
            )
        else:
            data_table_query = pd.DataFrame()

    if if_app_db:
        dt_columns = [
            field.name
            for field in modelName.concrete_fields
            if field.get_internal_type() in ["DateTimeField"]
        ]
        dt_columns_date = [
            field.name for field in modelName.concrete_fields if field.get_internal_type() in ["DateField"]
        ]
        dt_columns2 = [
            field.name for field in data_table_query.dtypes.to_list() if field.name in ["datetime64[ns]"]
        ]
        dt_columns3 = [
            field.name for field in modelName.concrete_fields if field.get_internal_type() in ["TimeField"]
        ]
        int_columns = [
            field.name for field in modelName.concrete_fields if field.get_internal_type() in ["IntegerField"]
        ]
        bigint_columns = [
            field.name
            for field in modelName.concrete_fields
            if field.get_internal_type() in ["BigIntegerField"]
        ]
        float_columns = [
            field.name for field in modelName.concrete_fields if field.get_internal_type() in ["FloatField"]
        ]

        if len(rtf_columns) > 0 and is_rft_field_present:
            db_name = db_name_extractor(request, curr_app_code)
            tenant = tenant_schema_from_request(request)
            temp = {}
            if os.path.exists(f"{MEDIA_ROOT}/rtf_files_master/{db_name}/rtf_data.json"):
                with open(f"{MEDIA_ROOT}/rtf_files_master/{db_name}/rtf_data.json") as fp:
                    temp = json.load(fp)
                    fp.close()

            if os.path.exists(f"{MEDIA_ROOT}/{tenant}/{curr_app_code}/rtf_files/{db_name}/rtf_data.json"):
                with open(
                    f"{MEDIA_ROOT}/{tenant}/{curr_app_code}/rtf_files/{db_name}/rtf_data.json", "w"
                ) as f:
                    json.dump(temp, f, indent=4)
                    f.close()

            if table in temp:
                json_data = temp[table]
            else:
                json_data = {}

            if json_data:
                for i in range(len(data_table_query)):
                    for j in rtf_columns:
                        if str(data_table_query.loc[i, "id"]) in json_data:
                            data_table_query.loc[i, j] = json_data[str(data_table_query.loc[i, "id"])]

            if not is_id_present:
                config_dict["inputs"]["Columns"].remove("id")
                data_table_query.drop(["id"], axis=1, inplace=True)

        object_columns = [
            field.name
            for field in modelName.concrete_fields
            if field.get_internal_type()
            in [
                "CharField",
                "TextField",
                "FileField",
                "URLField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "RTFField",
                "PrivacyField",
            ]
        ]

        if "show_foreignKey_value" in config_dict["inputs"].keys():
            if config_dict["inputs"]["show_foreignKey_value"]:
                values_dict = {
                    field.name: field
                    for field in modelName.concrete_fields
                    if field.get_internal_type() == "ForeignKey" and field.name in data_table_query.columns
                }
                for i in values_dict:
                    field = values_dict[i]
                    (
                        parent_model_name,
                        data_table_query,
                        table_h,
                    ) = standardised_functions.nestedForeignKey(
                        field, request, db_connection_name, data_table_query, i
                    )
            else:
                pass
        else:
            pass

        if config_dict["inputs"].get("verbose_name_checkbox"):
            if config_dict["inputs"]["verbose_name_checkbox"]:
                field_list = {field.name: field.verbose_name for field in modelName.concrete_fields}
                field_list["approval_status"] = "Approval status"
                field_list["approved_by"] = "Approved by"
                data_table_query.rename(columns=field_list, inplace=True)
            else:
                pass
        else:
            pass
    else:
        pass
    return data_table_query
