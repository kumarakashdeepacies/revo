import base64
import datetime
import json
import logging
import os
import re

from django.apps import apps
from django_multitenant.utils import get_current_tenant
import openpyxl
import pandas as pd
from sqlalchemy import text

from config.settings.base import PLATFORM_DATA_PATH, PLATFORM_FILE_PATH, redis_instance
from kore_investment.users.computations.db_centralised_function import (
    app_engine_generator,
    data_handling,
    db_engine_extractor,
    delete_data_func,
    extract_foreign_keys,
    non_standard_read_data_func,
    raw_query_executor,
    read_data_func,
    sys_tables,
    update_data_func,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.computations.model_field_info import ModelInfo
from kore_investment.users.fields import (
    CardCvvField,
    CardExpiryField,
    CardField,
    CardTypeField,
    ConcatenationField,
    DateRangeField,
    DateTimeRangeField,
    EmailTypeField,
    HierarchyField,
    MultiselectField,
    PrivacyField,
    RTFField,
    TableField,
    TimeRangeField,
    UniqueIDField,
    UserField,
)

admin_tables = [
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
    "failed_login_alerts",
    "notification_management" "Instance",
    "applicationAccess",
]


def get_model_class(model_name, request, db_connection_name="", db_engine=["", None], db_type="MSSQL"):
    if model_name in admin_tables:
        model = apps.get_model("users", model_name)
        model = model._meta
    else:
        if db_engine != ["", None]:
            user_db_engine = db_engine
        else:
            instance = get_current_tenant()
            if instance:
                tenant = instance.name
            else:
                tenant = None
            if db_connection_name != "":
                user_db_engine, db_type = db_engine_extractor(db_connection_name)
            else:
                user_db_engine, db_type, schema = app_engine_generator(request, tenant=tenant)
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


def create_table_sql(
    tablename,
    fields,
    request,
    model_type="user defined",
    db_connection_name="",
    initial_migration=False,
    restore=False,
    sys_model_version="1.0.0",
    linked_table=None,
):
    if db_connection_name != "":
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        user_db_engine, db_type, schema = app_engine_generator(request)
    model_name = tablename
    tablename = "users_" + tablename.lower().replace(" ", "_")
    if db_type == "PostgreSQL":
        create_query = f"CREATE TABLE {user_db_engine[0]['schema']}.{tablename} ("
    else:
        create_query = f"CREATE TABLE {tablename} ("
    for field_attr in fields:
        field_attr["field name"] = field_attr["field name"].lower()
        fieldname = field_attr["field name"]
        if "ForeignKey" in field_attr["field data type"]:
            parent_table = "users_" + field_attr["parent table"].lower()
            if db_type == "MSSQL":
                column_query = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                            "Columns": ["COLUMN_NAME"],
                        },
                        "condition": [
                            {
                                "column_name": "TABLE_NAME",
                                "condition": "Contains",
                                "input_value": parent_table,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "CONSTRAINT_NAME",
                                "condition": "Contains",
                                "input_value": "PK",
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            elif db_type == "Oracle":
                contstraint_name = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "all_constraints",
                            "Columns": ["constraint_name"],
                        },
                        "condition": [
                            {
                                "column_name": "table_name",
                                "condition": "Contains",
                                "input_value": parent_table.upper(),
                                "and_or": "AND",
                            },
                            {
                                "column_name": "constraint_type",
                                "condition": "Equal to",
                                "input_value": "P",
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                ).iloc[0, 0]
                column_query = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "all_cons_columns",
                            "Columns": ["column_name"],
                        },
                        "condition": [
                            {
                                "column_name": "constraint_name",
                                "condition": "Equal to",
                                "input_value": contstraint_name,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            else:
                column_query = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "INFORMATION_SCHEMA.constraint_column_usage",
                            "Columns": ["column_name"],
                        },
                        "condition": [
                            {
                                "column_name": "table_name",
                                "condition": "Equal to",
                                "input_value": parent_table,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "table_schema",
                                "condition": "Equal to",
                                "input_value": user_db_engine[0]["schema"],
                                "and_or": "AND",
                            },
                            {
                                "column_name": "constraint_name",
                                "condition": "Contains",
                                "input_value": "pkey",
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            ref_column = column_query.iloc[0, -1]
            fieldFKTable = "users_" + field_attr["parent table"].lower().replace(" ", "_")
            field_attr["fieldFKTable"] = fieldFKTable
            field_attr["ref_column"] = ref_column
            if db_type == "PostgreSQL":
                field_attr["schema"] = user_db_engine[0]["schema"]
            else:
                pass
            add_string = create_table_query_generator(
                fieldname, "ForeignKey", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "AutoField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "AutoField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "CharField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 526
            add_string = create_table_query_generator(
                fieldname, "CharField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "ConcatenationField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 526
            add_string = create_table_query_generator(
                fieldname, "ConcatenationField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "TextField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "TextField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "URLField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "TextField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "BooleanField" in field_attr["field data type"]:
            if db_type == "Oracle":
                version = non_standard_read_data_func(
                    "select banner from v$version", engine2=user_db_engine, db_type=db_type
                ).iloc[0, 0]
            else:
                version = ""
            add_string = create_table_query_generator(
                fieldname,
                "BooleanField",
                field_attr,
                tablename,
                db_type=db_type,
                model_type=model_type,
                db_version=version,
            )

        elif "BigIntegerField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "BigIntegerField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "IntegerField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "IntegerField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "FloatField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "FloatField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "DateField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "DateField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "FileField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "FileField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "VideoField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "VideoField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "ImageField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "ImageField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "DateTimeField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "DateTimeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "TimeField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "TimeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "BinaryField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "BinaryField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "HierarchyField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 526
            add_string = create_table_query_generator(
                fieldname, "HierarchyField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "UniqueIDField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 526
            add_string = create_table_query_generator(
                fieldname, "UniqueIDField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "DateRangeField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "DateRangeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "DateTimeRangeField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "DateTimeRangeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "TimeRangeField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "TimeRangeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "UserField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "UserField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "PrivacyField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "PrivacyField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "CardField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 19
            add_string = create_table_query_generator(
                fieldname, "CardField", field_attr, tablename, db_type=db_type, model_type=model_type
            )
            if field_attr.get("secure_with") == "encrypt":
                if field_attr.get("datakey"):
                    passcode = field_attr["datakey"].encode("ascii")
                    base64_bytes = base64.b64encode(passcode)
                    base64_passcode = base64_bytes.decode("ascii")
                    field_attr["datakey"] = base64_passcode

        elif "TableField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "TableField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "CardCvvField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 5
            add_string = create_table_query_generator(
                fieldname, "CardCvvField", field_attr, tablename, db_type=db_type, model_type=model_type
            )
            if field_attr.get("secure_with") == "encrypt":
                if field_attr.get("datakey"):
                    passcode = field_attr["datakey"].encode("ascii")
                    base64_bytes = base64.b64encode(passcode)
                    base64_passcode = base64_bytes.decode("ascii")
                    field_attr["datakey"] = base64_passcode

        elif "CardExpiryField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 10
            add_string = create_table_query_generator(
                fieldname, "CardExpiryField", field_attr, tablename, db_type=db_type, model_type=model_type
            )
            if field_attr.get("secure_with") == "encrypt":
                if field_attr.get("datakey"):
                    passcode = field_attr["datakey"].encode("ascii")
                    base64_bytes = base64.b64encode(passcode)
                    base64_passcode = base64_bytes.decode("ascii")
                    field_attr["datakey"] = base64_passcode

        elif "CardTypeField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 50
            add_string = create_table_query_generator(
                fieldname, "CardTypeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )
            if field_attr.get("secure_with") == "encrypt":
                if field_attr.get("datakey"):
                    passcode = field_attr["datakey"].encode("ascii")
                    base64_bytes = base64.b64encode(passcode)
                    base64_passcode = base64_bytes.decode("ascii")
                    field_attr["datakey"] = base64_passcode

        elif "EmailTypeField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 255
            add_string = create_table_query_generator(
                fieldname, "EmailTypeField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "RTFField" in field_attr["field data type"]:
            if not field_attr.get("maximum length*"):
                field_attr["maximum length*"] = 255
            add_string = create_table_query_generator(
                fieldname, "RTFField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        elif "MultiselectField" in field_attr["field data type"]:
            add_string = create_table_query_generator(
                fieldname, "MultiselectField", field_attr, tablename, db_type=db_type, model_type=model_type
            )

        else:
            pass

        create_query = create_query + add_string
    if model_type == "user defined" and restore is False:
        if db_type == "MSSQL":
            create_query = create_query + "created_by VARCHAR(100) NOT NULL,"
            create_query = create_query + "created_date DATETIME,"
            create_query = create_query + "modified_by VARCHAR(100) NOT NULL,"
            create_query = create_query + "modified_date DATETIME,"
            create_query = create_query + "active_from DATETIME,"
            create_query = create_query + "active_to DATETIME,"
            create_query = create_query + "transaction_id VARCHAR(100),"
            create_query = create_query + "is_active_flag VARCHAR(100)"
        elif db_type == "Oracle":
            create_query = create_query + "created_by VARCHAR2(100) NOT NULL,"
            create_query = create_query + "created_date TIMESTAMP,"
            create_query = create_query + "modified_by VARCHAR2(100) NOT NULL,"
            create_query = create_query + "modified_date TIMESTAMP,"
            create_query = create_query + "active_from TIMESTAMP,"
            create_query = create_query + "active_to TIMESTAMP,"
            create_query = create_query + "transaction_id VARCHAR2(100),"
            create_query = create_query + "is_active_flag VARCHAR2(100)"
        else:
            create_query = create_query + "created_by varchar(100) NOT NULL,"
            create_query = create_query + "created_date timestamp,"
            create_query = create_query + "modified_by varchar(100) NOT NULL,"
            create_query = create_query + "modified_date timestamp,"
            create_query = create_query + "active_from timestamp,"
            create_query = create_query + "active_to timestamp,"
            create_query = create_query + "transaction_id varchar(100),"
            create_query = create_query + "is_active_flag varchar(100)"
    else:
        if create_query.endswith(", "):
            create_query = create_query.rstrip(", ")
        else:
            pass
    create_query = create_query + ");"
    raw_query_executor(create_query, user_db_engine, db_type)
    error = "Success"

    if not initial_migration:
        attribute_dict = {
            "field header": "verbose_name",
            "nullable?": "null",
            "unique": "unique",
            "divider": "divider",
            "columns": "columns",
            "maximum length*": "max_length",
            "choices": "choices",
            "upload path": "upload_to",
            "default": "default",
            "auto now?": "auto_now",
            "Seconds precision?": "use_seconds",
            "editable?": "editable",
            "secure_with": "secure_with",
            "datakey": "datakey",
            "validators": "validators",
            "primary_key": "primary_key",
            "computed value": "computed value",
            "uuid_config": "uuid_config",
            "file_extension": "file_extension",
            "video_type": "video_type",
            "timerange_type": "timerange_type",
            "datetimerange_type": "datetimerange_type",
            "daterange_type": "daterange_type",
            "card_config": "card_config",
            "table_config": "table_config",
            "blacklist characters": "blacklist characters",
            "mulsel_config": "mulsel_config",
            "privacy_config": "privacy_config",
            "file_size": "file_size",
            "use_seconds": "use_seconds",
            "computed input": "computed input",
        }
        model_fields = {}
        for field in fields:
            field["field data type"] = field["field data type"].split(
                " ",
            )[0]
            if field["field data type"] != "ForeignKey":
                if field["field data type"] == "AutoField":
                    field_config = {
                        "internal_type": field["field data type"],
                        "primary_key": True,
                    }
                else:
                    field_config = {
                        "internal_type": field["field data type"],
                    }

                for key, value in field.items():
                    if key in attribute_dict:
                        attr_name = attribute_dict[key]
                    elif key in attribute_dict.values():
                        attr_name = key
                    else:
                        attr_name = key
                    if key not in ["field name", "field data type", "parent table"]:
                        if key != "default":
                            value = True if value == "Yes" else value
                            value = False if value == "No" else value
                            value = True if value is None else value
                        if field["field data type"] == "AutoField":
                            value = False if (value == "Select") else value
                            value = True if (value == "select") else value
                        else:
                            if key == "computed value":
                                value = False if (value == "Select") else value
                                value = True if (value == "select") else value
                            else:
                                value = True if (value == "Select") else value
                                value = False if (value == "select") else value
                        if key not in [
                            "field header",
                            "validators",
                            "choices",
                            "blacklist characters",
                            "computed input",
                        ]:
                            if value not in ["Yes", ""]:
                                try:
                                    value = int(value)
                                except Exception as e:
                                    logging.warning(f"Following exception occured - {e}")

                        if value in [True, False]:
                            field_config[attr_name] = value
                        else:
                            if type(value) in [int, float]:
                                field_config[attr_name] = value
                            elif type(value) == list:
                                if (
                                    attr_name == "choices"
                                    or attr_name == "blacklist characters"
                                    or attr_name == "computed input"
                                ):
                                    choices_list = []
                                    for val in value:
                                        choices_list.append((val, val))
                                    if value == "" or value == []:
                                        field_config[attr_name] = ""
                                    else:
                                        field_config[attr_name] = choices_list
                                elif attr_name == "columns":
                                    value = str(value).replace("'", '"')
                                    if value == "":
                                        field_config[attr_name] = f"{value}"
                                    else:
                                        field_config[attr_name] = value
                                else:
                                    field_config[attr_name] = value

                            else:
                                field_config[attr_name] = value

            elif field["field data type"] == "ForeignKey":
                field_config = {
                    "internal_type": field["field data type"],
                    "parent": field["parent table"],
                    "db_column": field["field name"],
                    "verbose_name": field["field header"],
                }
                for key, value in field.items():
                    if key in attribute_dict:
                        attr_name = attribute_dict[key]
                    elif key in attribute_dict.values():
                        attr_name = key
                    else:
                        attr_name = key
                    if key not in ["field name", "field data type", "computed value", "parent table"]:
                        value = True if value == "Yes" else value
                        value = False if value == "No" else value
                        if key not in ["field header"]:
                            if value not in ["Yes", ""]:
                                try:
                                    value = int(value)
                                except Exception as e:
                                    logging.warning(f"Following exception occured - {e}")

                        if value in [True, False]:
                            field_config[attr_name] = value

            model_fields[field["field name"]] = field_config
        if model_type == "user defined" and restore is False:
            model_fields["created_by"] = {
                "internal_type": "CharField",
                "verbose_name": "Created by",
                "null": 0,
                "unique": 0,
                "max_length": 100,
                "choices": "",
            }
            model_fields["modified_by"] = {
                "internal_type": "CharField",
                "verbose_name": "Modified by",
                "null": 0,
                "unique": 0,
                "max_length": 100,
                "choices": "",
            }
            model_fields["created_date"] = {
                "internal_type": "DateTimeField",
                "verbose_name": "Created date",
                "null": 0,
                "unique": 0,
                "auto_now": 1,
                "editable": 0,
            }
            model_fields["modified_date"] = {
                "internal_type": "DateTimeField",
                "verbose_name": "Modified date",
                "null": 0,
                "unique": 0,
                "auto_now": 1,
                "editable": 0,
            }
            model_fields["active_from"] = {
                "internal_type": "DateTimeField",
                "verbose_name": "Active From",
                "null": 1,
                "unique": 0,
                "auto_now": 1,
                "editable": 0,
            }
            model_fields["active_to"] = {
                "internal_type": "DateTimeField",
                "verbose_name": "Active To",
                "null": 1,
                "unique": 0,
                "auto_now": 1,
                "editable": 0,
            }
            model_fields["transaction_id"] = {
                "internal_type": "CharField",
                "verbose_name": "transaction_id",
                "null": 1,
                "unique": 0,
                "editable": 0,
                "max_length": 100,
                "choices": "",
            }
            model_fields["is_active_flag"] = {
                "internal_type": "CharField",
                "verbose_name": "is_active_flag",
                "null": 1,
                "unique": 0,
                "editable": 0,
                "max_length": 100,
                "choices": "",
                "default": "Yes",
            }
        model_fields = json.dumps(model_fields)

        delete_data_func(
            request,
            {
                "inputs": {"Data_source": "Database", "Table": "Tables"},
                "condition": [
                    {
                        "column_name": "tablename",
                        "condition": "Equal to",
                        "input_value": tablename,
                        "and_or": "",
                    }
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        final_details = {
            "tablename": model_name,
            "fields": model_fields,
            "version": sys_model_version,
            "model_type": model_type,
        }
        if linked_table:
            final_details["linked_table"] = linked_table
        else:
            final_details["linked_table"] = None
        df = pd.DataFrame(final_details, index=[0])
        data_handling(request, df, "Tables", con=user_db_engine, db_type=db_type, engine_override=True)
    return error


def create_relation_sql(tablename, fields, request):
    user_db_engine, db_type, schema = app_engine_generator(request)
    model_name = tablename
    tablename = "users_" + tablename.lower().replace(" ", "_")
    model_fields = json.loads(
        (
            read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields"]},
                    "condition": [
                        {
                            "column_name": "tablename",
                            "condition": "Equal to",
                            "input_value": model_name,
                            "and_or": "",
                        }
                    ],
                },
            )
        )
        .iloc[0]
        .fields
    )

    create_query = f"ALTER TABLE {tablename} "

    for field_attr in fields:
        if "field_mapper_data" in field_attr:
            field_data = json.loads(field_attr["field_mapper_data"])
            if field_data:
                for kv in field_data:
                    if kv["ref_id"] == "Null":
                        update_query = f"""UPDATE {tablename} SET {field_attr["field name"]} = {kv['new_id']} where {field_attr["field name"]} IS NULL"""
                        with user_db_engine[0].begin() as conn:
                            conn.execute(text(update_query))
                    else:
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": model_name,
                                    "Columns": [
                                        {
                                            "column_name": field_attr["field name"],
                                            "input_value": str(kv["new_id"]),
                                            "separator": "",
                                        },
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": field_attr["field name"],
                                        "condition": "Equal to",
                                        "input_value": str(kv["ref_id"]),
                                        "and_or": "",
                                    }
                                ],
                            },
                            db_type=db_type,
                        )

        default_constraint = f"DF" + f"_" + tablename + f"_" + field_attr["field name"]
        existing_default_exists = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "sys.default_constraints",
                    "Columns": ["name"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "Equal to",
                        "input_value": str(default_constraint),
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        if not existing_default_exists.empty:
            add_query2_def = f"ALTER TABLE {tablename} DROP CONSTRAINT {default_constraint}"
            with user_db_engine[0].begin() as conn:
                conn.execute(text(add_query2_def))
        type_change_query = f"ALTER TABLE {tablename} " + f"ALTER COLUMN {field_attr['field name']} INT;"
        with user_db_engine[0].begin() as conn:
            conn.execute(text(type_change_query))
        error = "Success"

        parent_table = "users_" + field_attr["fieldFKTable"]
        child_table = "users_" + field_attr["child_table"]

        column_query = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "Columns": ["COLUMN_NAME"],
                },
                "condition": [
                    {
                        "column_name": "TABLE_NAME",
                        "condition": "Contains",
                        "input_value": parent_table,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "CONSTRAINT_NAME",
                        "condition": "Contains",
                        "input_value": "PK",
                        "and_or": "",
                    },
                ],
            },
            db_type=db_type,
        )
        ref_column = column_query.iloc[0, 0]

        if "ForeignKey" in field_attr["field data type"]:
            fieldFKTable = "users_" + field_attr["fieldFKTable"].lower().replace(" ", "_")
            fieldFKconstraint = f"{parent_table}" + f"_" + f"{child_table}" + f"_" + field_attr["field name"]
            add_string = (
                "ADD CONSTRAINT FK_"
                + fieldFKconstraint
                + " "
                + f"FOREIGN KEY"
                + "("
                + field_attr["field name"]
                + ")"
                + " "
                + f"REFERENCES {fieldFKTable}({ref_column})"
            )

        create_query = create_query + add_string

    create_query = create_query + ";"
    if fields[0]["nullable?"] == "Yes":
        fields[0]["nullable?"] = 1
    else:
        fields[0]["nullable?"] = 0
    field_config = {
        "internal_type": fields[0]["field data type"],
        "parent": fields[0]["fieldFKTable"],
        "db_column": fields[0]["field name"],
        "verbose_name": fields[0]["field name"],
        "null": fields[0]["nullable?"],
    }
    model_fields[fields[0]["field name"]] = field_config
    model_fields = json.dumps(model_fields)

    update_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": [
                    {
                        "column_name": "fields",
                        "input_value": model_fields,
                        "separator": "",
                    }
                ],
            },
            "condition": [
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": model_name,
                    "and_or": "",
                },
            ],
        },
        db_type=db_type,
    )

    error = "Relation Successfully Created"
    try:
        with user_db_engine[0].begin() as conn:
            conn.execute(text(create_query))
    except Exception as e:
        logging.warning(
            f"Following exception occured - {e}",
        )
        error = e
    return error


def configure_data_foreign_mapper(parent_tablename, child_tablename, fields, sys_tables="", request=""):
    model_status = False

    final_dict = {}
    field_name = fields["fieldRelatedColumn"]
    # Child  Table
    model = get_model_class(child_tablename, request)

    # Old Parent  Table
    model2 = get_model_class(fields["fieldFKTable"], request)

    # New Parent Table
    model3 = get_model_class(parent_tablename, request)

    # Unique Checker
    unique_checker = [
        field.unique for field in model.concrete_fields if field.name == fields["fieldRelatedColumn"]
    ][0]
    if unique_checker in [True, 1]:
        unique_checker = True
    else:
        unique_checker = False

    # Create a Dataframe For Comparison

    save_data_df1 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": child_tablename,
                "Columns": [field_name, model.pk.name],
            },
            "condition": [],
        },
    )

    save_data_df2 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": fields["fieldFKTable"],
                "Columns": [field_name, model2.pk.name],
            },
            "condition": [],
        },
    )

    save_data_df3 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": parent_tablename,
                "Columns": [field_name, model3.pk.name],
            },
            "condition": [],
        },
    )
    filter_child_from_old_parent = pd.DataFrame(columns=[field_name])
    filter_value_not_present = pd.DataFrame(columns=[field_name])
    save_data_df1 = save_data_df1.drop_duplicates(subset=[field_name])

    # Retrieve the ID Number from the Old Parent Table
    if not save_data_df1[field_name].isnull().all():
        filter_child_from_old_parent = save_data_df2[
            save_data_df2[model2.pk.name].isin(save_data_df1[field_name])
        ]
    if not filter_child_from_old_parent[field_name].isnull().all():
        filter_value_not_present = filter_child_from_old_parent[
            ~filter_child_from_old_parent[field_name].isin(save_data_df3[field_name])
        ]

    if not filter_value_not_present[field_name].isnull().all():
        if not unique_checker:
            old_val_df = save_data_df2[save_data_df2[field_name].isin(filter_value_not_present[field_name])]
            old_val_df = old_val_df[[model2.pk.name, field_name]].to_dict(orient="records")
            change_val_df = save_data_df3[[model3.pk.name, field_name]].to_dict(orient="records")

            final_dict["old_value"] = json.dumps(old_val_df)
            final_dict["change_value"] = json.dumps(change_val_df)
            model_status = True
        else:
            old_val_df = save_data_df2[save_data_df2[field_name].isin(filter_value_not_present[field_name])]

            old_val_df = old_val_df[[model2.pk.name, field_name]].to_dict(orient="records")
            save_data_df3 = save_data_df3.drop_duplicates(subset=[field_name])
            change_val_df = save_data_df3[[model3.pk.name, field_name]].to_dict(orient="records")

            final_dict["old_value"] = json.dumps(old_val_df)
            final_dict["change_value"] = json.dumps(change_val_df)
            model_status = True

    return [final_dict, model_status]


# For Data Discovery Check
def check_relation_sql(parent_tablename, child_tablename, fields, request):
    model_status = False
    # Child/Current  Table
    model = get_model_class(child_tablename, request)

    # Parent  Table
    model2 = get_model_class(parent_tablename, request)

    # Create a Dataframe For Comparison
    save_data_df1 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": child_tablename,
                "Columns": [fields[0]["field name"], model.pk.name],
            },
            "condition": [],
        },
    )

    save_data_df2 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": parent_tablename,
                "Columns": [fields[0]["field name"], model2.pk.name],
            },
            "condition": [],
        },
    )
    field_name = fields[0]["field name"]
    final_dict = {}
    model_status = False

    if not save_data_df1[field_name].isnull().all():

        save_data_df1 = save_data_df1.drop_duplicates(subset=[field_name])
        save_data_df1.fillna("Null", inplace=True)
        save_data_df2.fillna("Null", inplace=True)
        old_val_df = save_data_df1[[model.pk.name, field_name]].astype(str).to_dict(orient="records")
        change_val_df = save_data_df2[[model2.pk.name, field_name]].astype(str).to_dict(orient="records")
        model_status = True
        final_dict["old_value"] = json.dumps(old_val_df)
        final_dict["change_value"] = json.dumps(change_val_df)

    return [final_dict, model_status]


def configure_relation_sql(tablename, fields, request):
    model_name = tablename
    tablename = "users_" + tablename.lower().replace(" ", "_")

    model_fields = json.loads(
        (
            read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields"]},
                    "condition": [
                        {
                            "column_name": "tablename",
                            "condition": "Equal to",
                            "input_value": model_name,
                            "and_or": "",
                        }
                    ],
                },
            )
        )
        .iloc[0]
        .fields
    )

    # Current  Table
    model = get_model_class(model_name, request)

    # Current Parent Table
    model2 = get_model_class(fields[0]["fieldFKTable"], request)

    # New Parent Table\
    model3 = get_model_class(fields[0]["fieldParentFKTable"], request)

    # Create a Dataframe For Comparison
    field_name_fk = fields[0]["fieldName"]
    save_data_df1 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": model_name,
                "Columns": [model.pk.name, field_name_fk],
            },
            "condition": [],
        },
    )

    save_data_df2 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": fields[0]["fieldFKTable"],
                "Columns": [model2.pk.name, field_name_fk],
            },
            "condition": [],
        },
    )

    save_data_df3 = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": fields[0]["fieldParentFKTable"],
                "Columns": [model3.pk.name, field_name_fk],
            },
            "condition": [],
        },
    )

    overall_unique_check = False

    current_table = save_data_df1[field_name_fk].tolist()
    if fields[0]["fieldUnique"] == "Yes":
        len_check = len(set(current_table)) == len(current_table)
        if not len_check:
            overall_unique_check = True

    db_engine, db_type, schema = app_engine_generator(request)
    if not overall_unique_check:

        query_check_foreign = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "Columns": ["CONSTRAINT_NAME"],
                },
                "condition": [
                    {
                        "column_name": "TABLE_NAME",
                        "condition": "Equal to",
                        "input_value": str(tablename),
                        "and_or": "and",
                    },
                    {
                        "column_name": "COLUMN_NAME",
                        "condition": "Equal to",
                        "input_value": str(field_name_fk),
                        "and_or": "",
                    },
                ],
            },
            db_type=db_type,
        )
        if not query_check_foreign.empty:
            fk_name = query_check_foreign["CONSTRAINT_NAME"].values[0]
            add_query1 = f"ALTER TABLE {tablename} " + f" DROP CONSTRAINT " + fk_name + ";"
            with db_engine[0].begin() as conn:
                conn.execute(text(add_query1))

        # Apply Mapper Operation
        if "fieldChangedValue" in fields[0]:
            if len(fields[0]["fieldChangedValue"]) > 0:
                for key in fields[0]["fieldChangedValue"]:
                    update_data_func(
                        request,
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": model_name,
                                "Columns": [
                                    {
                                        "column_name": fields[0]["fieldName"],
                                        "input_value": str(key["new_id"]),
                                        "separator": "",
                                    },
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": fields[0]["fieldName"],
                                    "condition": "Equal to",
                                    "input_value": str(key["ref_id"]),
                                    "and_or": "",
                                }
                            ],
                        },
                        db_type=db_type,
                    )

        # Data Processing For Replacing the Old Value to New Parent Values

        if not save_data_df1.empty:
            # Compress Datat which match and Drop duplicate entries
            update_data_dict = {}
            comp_save_data_2 = save_data_df2[
                save_data_df2[model2.pk.name].isin(save_data_df1[fields[0]["fieldName"]])
            ]
            if not comp_save_data_2.empty:
                comp_save_data_2 = comp_save_data_2.drop_duplicates(subset=[fields[0]["fieldName"]])
                comp_save_data_2.rename(columns={"country_id": "id"}, inplace=True)
                save_data_df3.rename(columns={"country_id": "id"}, inplace=True)
                merger = pd.merge(
                    comp_save_data_2.astype(str),
                    save_data_df3.astype(str),
                    on=fields[0]["fieldName"],
                    how="inner",
                    suffixes=["_1", "_2"],
                )
                merger = merger.drop_duplicates(subset=[fields[0]["fieldName"]])

                update_data_dict = merger.to_dict(orient="records")

                if len(update_data_dict) > 0:
                    for val in update_data_dict:
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": model_name,
                                    "Columns": [
                                        {
                                            "column_name": fields[0]["fieldName"],
                                            "input_value": str(val["id_2"]),
                                            "separator": "",
                                        },
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": fields[0]["fieldName"],
                                        "condition": "Equal to",
                                        "input_value": str(val["id_1"]),
                                        "and_or": "",
                                    }
                                ],
                            },
                            db_type=db_type,
                        )

        # End Data Processing

        create_query = f"ALTER TABLE {tablename} "
        for field_attr in fields:
            type_change_query = f"ALTER TABLE {tablename} " + f"ALTER COLUMN {field_attr['fieldName']} INT;"
            with db_engine[0].begin() as conn:
                conn.execute(text(type_change_query))

            parent_table = "users_" + field_attr["fieldParentFKTable"]

            column_query = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                        "Columns": ["COLUMN_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Contains",
                            "input_value": parent_table,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "CONSTRAINT_NAME",
                            "condition": "Contains",
                            "input_value": "PK",
                            "and_or": "",
                        },
                    ],
                },
                db_type=db_type,
            )
            ref_column = column_query.iloc[0, 0]

            if "ForeignKey" in field_attr["fieldDatatype"]:
                fieldFKTable = "users_" + field_attr["fieldParentFKTable"].lower().replace(" ", "_")
                fieldFKconstraint = f"users_" + f"{parent_table}" + f"_" + field_attr["fieldName"]
                add_string = (
                    "ADD CONSTRAINT FK_"
                    + fieldFKconstraint
                    + " "
                    + f"FOREIGN KEY"
                    + "("
                    + field_attr["fieldName"]
                    + ")"
                    + " "
                    + f"REFERENCES {fieldFKTable}({ref_column})"
                )

            create_query = create_query + add_string

        create_query = create_query + ";"

        if fields[0]["fieldNull"] == "Yes":
            fields[0]["fieldNull"] = True
        else:
            fields[0]["fieldNull"] = False

        if field_attr["fieldUnique"] == "Yes":
            start_query = f"ALTER TABLE {tablename} "
            unique_constraint = f"UQ" + f"_" + tablename + f"_" + fields[0]["fieldName"] + " "
            add_query1 = (
                start_query
                + " ADD CONSTRAINT "
                + unique_constraint
                + " UNIQUE ("
                + fields[0]["fieldName"]
                + ");"
            )
            with db_engine[0].begin() as conn:
                conn.execute(text(add_query1))
                fields[0]["fieldUnique"] = True
        else:
            start_query = f"ALTER TABLE {tablename}"
            unique_constraint = f"UQ" + f"_" + tablename + f"_" + fields[0]["fieldName"] + " "

            query_check_unique = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                        "Columns": ["CONSTRAINT_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Equal to",
                            "input_value": tablename,
                            "and_or": "",
                        },
                    ],
                },
                db_type=db_type,
            )

            if unique_constraint in query_check_unique["CONSTRAINT_NAME"].values:
                add_query1 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
                with db_engine[0].begin() as conn:
                    conn.execute(text(add_query1))
                fields[0]["fieldUnique"] = False
        field_config = {
            "internal_type": fields[0]["fieldDatatype"],
            "parent": fields[0]["fieldParentFKTable"],
            "db_column": fields[0]["fieldName"],
            "verbose_name": fields[0]["fieldVerboseName"],
            "null": fields[0]["fieldNull"],
        }
        model_fields[fields[0]["fieldName"]] = field_config
        model_fields = json.dumps(model_fields)

        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Tables",
                    "Columns": [
                        {
                            "column_name": "fields",
                            "input_value": model_fields,
                            "separator": "",
                        }
                    ],
                },
                "condition": [
                    {
                        "column_name": "tablename",
                        "condition": "Equal to",
                        "input_value": model_name,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "model_type",
                        "condition": "Equal to",
                        "input_value": "user defined",
                        "and_or": "",
                    },
                ],
            },
            db_type=db_type,
        )
        try:
            with db_engine[0].begin() as conn:
                conn.execute(text(create_query))
        except Exception as e:
            logging.warning(
                f"Following exception occured - {e}",
            )
    field_dict = {}
    field_dict["Field_name"] = fields[0]["fieldName"]
    field_dict["Front End Name"] = fields[0]["fieldVerboseName"]
    field_dict["Data Type"] = fields[0]["fieldDatatype"]
    field_dict["Primary Key"] = False
    field_dict["Unique"] = fields[0]["fieldUnique"]
    field_dict["Nullable"] = fields[0]["fieldNull"]
    field_dict["Editable"] = False
    field_dict["Max Length"] = None
    field_dict["Default"] = None
    field_dict["Validations"] = []
    field_dict["fieldParentFKTable"] = fields[0]["fieldParentFKTable"]
    field_dict["unique_check"] = overall_unique_check

    return field_dict


def add_element(tablename, fields, request, db_connection_name="", sys_model_version="1.0.0"):
    """
    tablename = Table Name

    fields = Fields

    """
    db_type = ""
    if db_connection_name != "":
        db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        db_engine, db_type, schema = app_engine_generator(request)
    model_fields = read_data_func(
        request,
        {
            "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields", "model_type"]},
            "condition": [
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": tablename,
                    "and_or": "",
                }
            ],
        },
        engine2=db_engine,
        db_type=db_type,
        engine_override=True,
    )
    model_type = model_fields.iloc[0].model_type
    model_fields = json.loads(model_fields.iloc[0].fields)
    table_name = "users_" + tablename.lower().replace(" ", "_")
    if db_type == "PostgreSQL":
        add_query = f"ALTER TABLE {db_engine[0]['schema']}.{table_name} ADD "
    else:
        add_query = f"ALTER TABLE {table_name} ADD "
    fields["fieldName"] = fields["fieldName"].lower()
    fieldname = fields["fieldName"]
    field_data_type = fields["fieldDatatype"]
    if fields["fieldDatatype"] == "ForeignKey":
        fieldFKTable = "users_" + fields["fieldFKTable"].lower().replace(" ", "_")

        if db_type == "MSSQL":
            column_query_add = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                        "Columns": ["COLUMN_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Contains",
                            "input_value": fieldFKTable,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "CONSTRAINT_NAME",
                            "condition": "Contains",
                            "input_value": "PK",
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
        elif db_type == "Oracle":
            contstraint_name = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "all_constraints",
                        "Columns": ["constraint_name"],
                    },
                    "condition": [
                        {
                            "column_name": "table_name",
                            "condition": "Contains",
                            "input_value": fieldFKTable.upper(),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "constraint_type",
                            "condition": "Equal to",
                            "input_value": "P",
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            ).iloc[0, 0]
            column_query_add = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "all_cons_columns",
                        "Columns": ["column_name"],
                    },
                    "condition": [
                        {
                            "column_name": "constraint_name",
                            "condition": "Equal to",
                            "input_value": contstraint_name,
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
        else:
            column_query_add = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.constraint_column_usage",
                        "Columns": ["column_name"],
                    },
                    "condition": [
                        {
                            "column_name": "table_name",
                            "condition": "Equal to",
                            "input_value": fieldFKTable,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "table_schema",
                            "condition": "Equal to",
                            "input_value": db_engine[0]["schema"],
                            "and_or": "AND",
                        },
                        {
                            "column_name": "constraint_name",
                            "condition": "Contains",
                            "input_value": "pkey",
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
        ref_column_add = column_query_add.iloc[0, -1]
        fields["fieldParentTable"] = fieldFKTable
        fields["ref_column"] = ref_column_add
        if db_type == "PostgreSQL":
            fields["schema"] = db_engine[0]["schema"]
        else:
            pass
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type
        )
        field_config = {
            "internal_type": "ForeignKey",
            "parent": fields["fieldFKTable"],
            "db_column": fields["fieldName"],
        }
    elif fields["fieldDatatype"] == "CharField":
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type
        )
        if fields.get("secure_with") == "encrypt":
            if fields.get("datakey"):
                passcode = fields["datakey"].encode("ascii")
                base64_bytes = base64.b64encode(passcode)
                base64_passcode = base64_bytes.decode("ascii")
                fields["datakey"] = base64_passcode
    elif fields["fieldDatatype"] in [
        "ConcatenationField",
        "DateField",
        "DateTimeField",
        "TextField",
        "URLField",
        "BooleanField",
        "TimeField",
        "FileField",
        "VideoField",
        "ImageField",
        "IntegerField",
        "BigIntegerField",
        "FloatField",
        "HierarchyField",
        "UniqueIDField",
        "PrivacyField",
        "TableField",
        "EmailTypeField",
        "MultiselectField",
        "RTFField",
        "BinaryField",
    ]:
        if db_type == "Oracle":
            version = non_standard_read_data_func(
                "select banner from v$version", engine2=db_engine, db_type=db_type
            ).iloc[0, 0]
        else:
            version = ""
        add_string = add_field_query_generator(
            fieldname,
            field_data_type,
            fields,
            table_name,
            db_type=db_type,
            model_type=model_type,
            db_version=version,
        )

    elif fields["fieldDatatype"] in ["DateTimeRangeField", "DateRangeField", "TimeRangeField", "UserField"]:
        fields["fieldMaxLength"] = 100
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type
        )

    elif fields["fieldDatatype"] in ["CardField", "CardCvvField"]:
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type
        )
        if fields.get("secure_with") == "encrypt":
            if fields.get("datakey"):
                passcode = fields["datakey"].encode("ascii")
                base64_bytes = base64.b64encode(passcode)
                base64_passcode = base64_bytes.decode("ascii")
                fields["datakey"] = base64_passcode

    elif fields["fieldDatatype"] in ["CardExpiryField", "CardTypeField"]:
        fields["fieldMaxLength"] = 255
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type
        )
        if fields.get("secure_with") == "encrypt":
            if fields.get("datakey"):
                passcode = fields["datakey"].encode("ascii")
                base64_bytes = base64.b64encode(passcode)
                base64_passcode = base64_bytes.decode("ascii")
                fields["datakey"] = base64_passcode
    else:
        add_string = ""

    add_query += add_string

    raw_query_executor(add_query, db_engine, db_type)

    error = "Success"

    attribute_dict = {
        "fieldVerboseName": "verbose_name",
        "fieldNull": "null",
        "fieldUnique": "unique",
        "fieldMaxLength": "max_length",
        "fieldChoices": "choices",
        "fieldUploadTo": "upload_to",
        "fieldDefault": "default",
        "fieldAutoNow": "auto_now",
        "fieldUseSeconds": "use_seconds",
        "fieldEditable": "editable",
        "secure_with": "secure_with",
        "datakey": "datakey",
        "hierarchy_group": "hierarchy_group",
        "divider": "divider",
        "columns": "columns",
        "validators": "validators",
        "computedValue": "computed value",
        "uuid_config": "uuid_config",
        "file_extension": "file_extension",
        "video_type": "video_type",
        "timerange_type": "timerange_type",
        "datetimerange_type": "datetimerange_type",
        "daterange_type": "daterange_type",
        "card_config": "card_config",
        "table_config": "table_config",
        "blacklist_chars": "blacklist characters",
        "mulsel_config": "mulsel_config",
        "privacy_config": "privacy_config",
        "file_size": "file_size",
        "computed_input": "computed input",
    }

    if fields["fieldDatatype"] == "ForeignKey":
        field_config = {
            "internal_type": "ForeignKey",
            "parent": fields["fieldFKTable"],
            "db_column": fields["fieldName"],
            "verbose_name": fields["fieldVerboseName"],
        }
    elif fields["fieldDatatype"] == "MultiselectField" and "_mul" in table_name:
        field_config = {
            "internal_type": "CharField",
            "verbose_name": fields["fieldVerboseName"],
        }
    else:
        field_config = {
            "internal_type": fields["fieldDatatype"],
            "verbose_name": fields["fieldVerboseName"],
        }

    for key, value in fields.items():
        if key in attribute_dict:
            attr_name = attribute_dict[key]
        elif key in attribute_dict.values():
            attr_name = key
        else:
            attr_name = key
        if key not in ["fieldName", "fieldDatatype", "fieldVerboseName"]:
            if key != "fieldDefault":
                value = True if value == "Yes" else value
                value = False if value == "No" else value
                value = True if value is None else value
                value = True if ((value == "Yes") or (value == "Select")) else value
            if value not in ["Yes", ""]:
                try:
                    value = int(value)
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")

            if value in [True, False]:
                field_config[attr_name] = value
            else:
                if fields["fieldDatatype"] != "ForeignKey":
                    if type(value) in [int, float]:
                        field_config[attr_name] = value
                    else:
                        if key == "fieldChoices" or key == "blacklist_chars" or key == "computed_input":
                            choices_list = []
                            for val in value:
                                choices_list.append((val, val))
                            if value == "" or value == []:
                                field_config[attr_name] = ""
                            else:
                                field_config[attr_name] = choices_list
                        else:
                            field_config[attr_name] = value

    model_fields[fields["fieldName"]] = field_config
    model_fields = json.dumps(model_fields)
    update_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": [
                    {"column_name": "fields", "input_value": model_fields, "separator": ","},
                    {
                        "column_name": "version",
                        "input_value": sys_model_version,
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {"column_name": "tablename", "condition": "Equal to", "input_value": tablename, "and_or": ""}
            ],
        },
        engine2=db_engine,
        db_type=db_type,
        engine_override=True,
    )
    return error


def attr_details(model_name, field_name, request):
    model = get_model_class(model_name, request)

    data_dict = {
        "Field_name": "name",
        "Front End Name": "verbose_name",
        "Data Type": "get_internal_type()",
        "Primary Key": "primary_key",
        "Unique": "unique",
        "Nullable": "null",
        "Editable": "editable",
        "Auto Now": "auto_now",
        "Seconds precision": "use_seconds",
        "Choices": "choices",
        "secure_with": "secure_with",
        "datakey": "datakey",
        "Max Length": "max_length",
        "Default": "get_default()",
        "Validations": "validators",
        "columns": "columns",
        "divider": "divider",
        "Computed Value": "computed_field",
        "uuid_config": "uuid_config",
        "File extension": "file_extension",
        "video_type": "video_type",
        "card_config": "card_config",
        "table_config": "table_config",
        "Blacklist Characters": "blacklist_chars",
        "mulsel_config": "mulsel_config",
        "privacy_config": "privacy_config",
        "Computed Input": "computed_input",
    }
    details = {}
    data_type_list = [
        "AutoField",
        "ForeignKey",
        "CharField",
        "ConcatenationField",
        "BooleanField",
        "FileField",
        "VideoField",
        "IntegerField",
        "BigIntegerField",
        "DateField",
        "TimeField",
        "ImageField",
        "DateTimeField",
        "TextField",
        "FloatField",
        "UniqueIDField",
        "URLField",
        "TimeRangeField",
        "DateTimeRangeField",
        "DateRangeField",
        "CardField",
        "CardCvvField",
        "CardExpiryField",
        "CardTypeField",
        "UserField",
        "EmailTypeField",
        "TableField",
        "MultiselectField",
        "RTFField",
        "PrivacyField",
    ]
    for key, value in data_dict.items():
        field_details = model.get_field(field_name)
        try:
            if key == "Data Type":
                if field_details.get_internal_type() == "CharField":
                    model_fields = json.loads(
                        (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "Tables",
                                        "Columns": ["fields"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "tablename",
                                            "condition": "Equal to",
                                            "input_value": model_name,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        )
                        .iloc[0]
                        .fields
                    )
                    if not model_fields[field_name]["internal_type"].startswith("ConcatenationField"):
                        details[key] = [x for x in data_type_list if field_details.get_internal_type() == x][
                            0
                        ]
                    else:
                        details[key] = "ConcatenationField"
                else:
                    details[key] = [x for x in data_type_list if field_details.get_internal_type() == x][0]
            elif key == "Default":
                field_default = field_details.get_default()
                if field_default:
                    if type(field_default) is datetime.datetime:
                        field_default = field_default.strftime("%Y-%m-%d %H:%M:%S")
                details[key] = field_default
            elif key == "Validations":
                details[key] = list({type(x).__name__ for x in field_details.validators})
            elif key in ["Unique", "Nullable"]:
                value = getattr(field_details, value)
                if value == 1:
                    details[key] = True
                elif value == 0:
                    details[key] = False
                else:
                    details[key] = False
            else:
                if key == "Choices" or key == "Blacklist Characters" or key == "Computed Input":
                    if value == "":
                        choices_list = getattr(field_details, value)
                        details[key] = choices_list

                    else:
                        choices_list = getattr(field_details, value)
                        choice_edit_list = []
                        for choice in choices_list:
                            choice_edit_list.append(choice[0])
                        details[key] = choice_edit_list
                else:
                    if key == "Computed Value":
                        value = getattr(field_details, value)
                        if value == 1:
                            details[key] = True
                        elif value == 0:
                            details[key] = False
                    else:
                        details[key] = getattr(field_details, value)
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")

    return details


def edit_element(
    tablename, fields, request, db_connection_name="", drop_n_create="no", sys_model_version="1.0.0"
):
    if db_connection_name != "":
        db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        db_engine, db_type, schema = app_engine_generator(request)
    model_fields = json.loads(
        (
            read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields"]},
                    "condition": [
                        {
                            "column_name": "tablename",
                            "condition": "Equal to",
                            "input_value": tablename,
                            "and_or": "",
                        }
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
        )
        .iloc[0]
        .fields
    )

    table_name = "users_" + tablename.lower().replace(" ", "_")
    model = ModelInfo(tablename, model_fields, {})
    create_df_flag = 0
    if db_type == "PostgreSQL":
        start_query = f"ALTER TABLE {db_engine[0]['schema']}.{table_name} "
    else:
        start_query = f"ALTER TABLE {table_name} "
    if db_type == "Oracle":
        alter_query = "MODIFY "
    else:
        alter_query = "ALTER COLUMN "
    add_query = start_query + alter_query
    fieldname = fields["fieldName"]
    field_data_type = fields["fieldDatatype"]
    if not fields.get("fieldUnique"):
        fields["fieldUnique"] = "No"
    add_string = ""
    if fields["fieldDatatype"] in ["DateRangeField", "DateTimeRangeField", "TimeRangeField", "UserField"]:
        fields["fieldMaxLength"] = 100
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type, edit=True
        )
    elif fields["fieldDatatype"] in ["CardExpiryField", "CardTypeField"]:
        fields["fieldMaxLength"] = 255
        add_string = add_field_query_generator(
            fieldname, field_data_type, fields, table_name, db_type=db_type, edit=True
        )
    else:
        if db_type == "Oracle":
            version = non_standard_read_data_func(
                "select banner from v$version", engine2=db_engine, db_type=db_type
            ).iloc[0, 0]
        else:
            version = ""
        current_field_config = model.get_field(fieldname)
        add_string = add_field_query_generator(
            fieldname,
            field_data_type,
            fields,
            table_name,
            db_type=db_type,
            edit=True,
            db_version=version,
            current_field_config=current_field_config,
        )
    add_query += add_string

    if "fieldParentFKTable" in fields:
        del fields["fieldParentFKTable"]
        if "fieldRelatedColumn" in fields:
            del fields["fieldRelatedColumn"]
        if "fieldChangedValue" in fields:
            del fields["fieldChangedValue"]

    field_name_fk = fields["fieldName"]
    if db_type == "MSSQL":
        if fields["fieldUnique"] == "Yes":
            unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
            existing_query_check_unique = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                        "Columns": ["CONSTRAINT_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Equal to",
                            "input_value": str(table_name),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "CONSTRAINT_NAME",
                            "condition": "Equal to",
                            "input_value": str(unique_constraint),
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if existing_query_check_unique.empty:
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)
            else:
                add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint
                with db_engine[0].begin() as conn:
                    conn.execute(text(add_query2))
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)
        else:
            try:
                unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
                query_check_unique = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                            "Columns": ["CONSTRAINT_NAME"],
                        },
                        "condition": [
                            {
                                "column_name": "TABLE_NAME",
                                "condition": "Equal to",
                                "input_value": str(table_name),
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

                if unique_constraint in query_check_unique["CONSTRAINT_NAME"].values:
                    add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
                    raw_query_executor(add_query2, db_engine, db_type)

                current_field_type = model.get_field(field_name_fk).internal_type
                if current_field_type == "ForeignKey" and fields["fieldDatatype"] != "ForeignKey":
                    query_check_foreign = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                                "Columns": ["CONSTRAINT_NAME"],
                            },
                            "condition": [
                                {
                                    "column_name": "TABLE_NAME",
                                    "condition": "Equal to",
                                    "input_value": str(table_name),
                                    "and_or": "and",
                                },
                                {
                                    "column_name": "COLUMN_NAME",
                                    "condition": "Equal to",
                                    "input_value": str(field_name_fk),
                                    "and_or": "",
                                },
                            ],
                        },
                        engine2=db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

                    if not query_check_foreign.empty:
                        fk_name = query_check_foreign["CONSTRAINT_NAME"].values[0]
                        add_query2 = start_query + f" DROP CONSTRAINT " + fk_name + ";"
                        raw_query_executor(add_query2, db_engine, db_type)

            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
    else:
        pass
    if db_type == "PostgreSQL":
        current_field_type = model.get_field(field_name_fk).internal_type
        if current_field_type == "ForeignKey" and fields["fieldDatatype"] != "ForeignKey":
            query_check_foreign = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                        "Columns": ["constraint_name"],
                    },
                    "condition": [
                        {
                            "column_name": "table_name",
                            "condition": "Equal to",
                            "input_value": str(table_name),
                            "and_or": "and",
                        },
                        {
                            "column_name": "table_schema",
                            "condition": "Equal to",
                            "input_value": str(db_engine[0]["schema"]),
                            "and_or": "and",
                        },
                        {
                            "column_name": "COLUMN_NAME",
                            "condition": "Equal to",
                            "input_value": str(field_name_fk),
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )

            if not query_check_foreign.empty:
                fk_name = query_check_foreign["constraint_name"].values[0]
                add_query2 = start_query + " DROP CONSTRAINT " + fk_name + ";"
                raw_query_executor(add_query2, db_engine, db_type)
        else:
            pass
        if fields["fieldUnique"] == "Yes":
            unique_constraint = f"uq" + f"_" + table_name + f"_" + fields["fieldName"]
            existing_query_check_unique = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                        "Columns": ["constraint_name"],
                    },
                    "condition": [
                        {
                            "column_name": "table_name",
                            "condition": "Equal to",
                            "input_value": str(table_name),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "constraint_name",
                            "condition": "Equal to",
                            "input_value": str(unique_constraint),
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if existing_query_check_unique.empty:
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)
            else:
                add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint
                with db_engine[0].begin() as conn:
                    conn.execute(text(add_query2))
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)
        else:
            try:
                unique_constraint = f"uq" + f"_" + table_name + f"_" + fields["fieldName"]
                query_check_unique = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                            "Columns": ["constraint_name"],
                        },
                        "condition": [
                            {
                                "column_name": "TABLE_NAME",
                                "condition": "Equal to",
                                "input_value": str(table_name),
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

                if unique_constraint in query_check_unique["constraint_name"].values:
                    add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
                    raw_query_executor(add_query2, db_engine, db_type)
            except Exception as e:
                logging.warning(f"Following exception occured xoxoxo - {e}")
    if db_type == "Oracle":
        if fields["fieldUnique"] != "Yes":
            try:
                query_check_cons = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user_cons_columns",
                            "Columns": ["CONSTRAINT_NAME"],
                        },
                        "condition": [
                            {
                                "column_name": "TABLE_NAME",
                                "condition": "Equal to",
                                "input_value": str(table_name).upper(),
                                "and_or": "AND",
                            },
                            {
                                "column_name": "COLUMN_NAME",
                                "condition": "Equal to",
                                "input_value": str(field_name_fk).upper(),
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if not query_check_cons.empty:
                    query_check_cons = query_check_cons.constraint_name.tolist()
                    query_check_cons = str(tuple(query_check_cons)).replace(",)", ")")
                    query_check_unique = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "user_constraints",
                                "Columns": ["CONSTRAINT_NAME"],
                            },
                            "condition": [
                                {
                                    "column_name": "TABLE_NAME",
                                    "condition": "Equal to",
                                    "input_value": str(table_name).upper(),
                                    "and_or": "AND",
                                },
                                {
                                    "column_name": "CONSTRAINT_TYPE",
                                    "condition": "Equal to",
                                    "input_value": "U",
                                    "and_or": "AND",
                                },
                                {
                                    "column_name": "CONSTRAINT_NAME",
                                    "condition": "IN",
                                    "input_value": query_check_cons,
                                    "and_or": "",
                                },
                            ],
                        },
                        engine2=db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                    if not query_check_unique.empty:
                        unique_constraint = query_check_unique.constraint_name.iloc[0]
                        add_query2 = start_query + " DROP CONSTRAINT " + unique_constraint + ";"
                        raw_query_executor(add_query2, db_engine, db_type)
                    else:
                        pass
                else:
                    pass
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
        else:
            pass
    else:
        pass
    if fields.get("fieldDefault") and db_type == "MSSQL":
        if fields["fieldDefault"]:
            default_constraint = f"DF" + f"_" + table_name + f"_" + fields["fieldName"]
            if fields["fieldDatatype"] in ["CharField", "TextField", "URLField"]:
                def_val = f"'{fields['fieldDefault']}' "
            else:
                def_val = f"{fields['fieldDefault']} "
            existing_default_exists = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "sys.default_constraints",
                        "Columns": ["name"],
                    },
                    "condition": [
                        {
                            "column_name": "name",
                            "condition": "Equal to",
                            "input_value": str(default_constraint),
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )

            if existing_default_exists.empty:
                if drop_n_create == "no":
                    create_df_flag = 1
                    add_query1_def = (
                        start_query
                        + " ADD CONSTRAINT "
                        + default_constraint
                        + " DEFAULT "
                        + def_val
                        + " FOR "
                        + fields["fieldName"]
                        + " ;"
                    )
                    raw_query_executor(add_query1_def, db_engine, db_type)
            else:
                add_query2_def = start_query + f" DROP CONSTRAINT " + default_constraint + ";"
                raw_query_executor(add_query2_def, db_engine, db_type)
                add_query1_def = (
                    start_query
                    + " ADD CONSTRAINT "
                    + default_constraint
                    + " DEFAULT "
                    + def_val
                    + " FOR "
                    + fields["fieldName"]
                    + " ;"
                )
                create_df_flag = 1
                raw_query_executor(add_query1_def, db_engine, db_type)
    elif db_type == "MSSQL":
        default_constraint = f"DF" + f"_" + table_name + f"_" + fields["fieldName"]
        query_check_default = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "sys.default_constraints",
                    "Columns": ["name"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "Equal to",
                        "input_value": str(default_constraint),
                        "and_or": "",
                    }
                ],
            },
            engine2=db_engine,
            db_type=db_type,
            engine_override=True,
        )

        if default_constraint in query_check_default["name"].values:
            add_query3 = start_query + f" DROP CONSTRAINT " + default_constraint + ";"
            raw_query_executor(add_query3, db_engine, db_type)
    else:
        pass

    if drop_n_create == "yes":
        create_unq_flag = 0
        unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
        default_constraint = f"DF" + f"_" + table_name + f"_" + fields["fieldName"]
        if fields.get("fieldDefault"):
            if fields["fieldDatatype"] in ["CharField", "TextField", "URLField"]:
                def_val = f"'{fields['fieldDefault']}' "
            else:
                def_val = f"{fields['fieldDefault']} "
        else:
            def_val = "NULL"
        query_check_unique = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                    "Columns": ["CONSTRAINT_NAME"],
                },
                "condition": [
                    {
                        "column_name": "TABLE_NAME",
                        "condition": "Equal to",
                        "input_value": str(table_name),
                        "and_or": "",
                    }
                ],
            },
            engine2=db_engine,
            db_type=db_type,
            engine_override=True,
        )

        if unique_constraint in query_check_unique["CONSTRAINT_NAME"].values:
            create_unq_flag = 1
            add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
            raw_query_executor(add_query2, db_engine, db_type)

        drop_query = f"{start_query} DROP COLUMN {fields['fieldName']} ;"
        raw_query_executor(drop_query, db_engine, db_type)

        add_string_create = ""
        if fields["fieldDatatype"] == "IntegerField":
            add_string_create = fields["fieldName"] + " " + f"INT"

        elif fields["fieldDatatype"] == "BigIntegerField":
            add_string_create = fields["fieldName"] + " " + f"BIGINT"

        elif fields["fieldDatatype"] == "FloatField":
            add_string_create = fields["fieldName"] + " " + f"FLOAT"

        elif fields["fieldDatatype"] == "DateTimeField":
            add_string_create = fields["fieldName"] + " " + f"DATETIME"

        elif fields["fieldDatatype"] == "TimeField":
            add_string_create = fields["fieldName"] + " " + f"TIME"

        elif fields["fieldDatatype"] == "DateField":
            add_string_create = fields["fieldName"] + " " + f"DATE"

        elif fields["fieldDatatype"] == "BooleanField":
            add_string_create = fields["fieldName"] + " " + f"BIT"

        create_query = f"{start_query} ADD {add_string_create}  ;"

        raw_query_executor(create_query, db_engine, db_type)

        if create_unq_flag:
            add_query1 = (
                start_query
                + " ADD CONSTRAINT "
                + unique_constraint
                + " UNIQUE ("
                + fields["fieldName"]
                + ");"
            )
            raw_query_executor(add_query1, db_engine, db_type)

        if create_df_flag:
            add_query1_def = (
                start_query
                + " ADD CONSTRAINT "
                + default_constraint
                + " DEFAULT "
                + def_val
                + " FOR "
                + fields["fieldName"]
                + " ;"
            )
            raw_query_executor(add_query1_def, db_engine, db_type)
    else:
        if db_type == "MSSQL":
            create_unq_flag = 0
            default_constraint = f"DF" + f"_" + table_name + f"_" + fields["fieldName"]
            unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
            if fields.get("fieldDefault"):
                if fields["fieldDatatype"] in ["CharField", "TextField", "URLField"]:
                    def_val = f"'{fields['fieldDefault']}' "
                else:
                    def_val = f"{fields['fieldDefault']} "
            else:
                def_val = "NULL"

            query_check_unique = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
                        "Columns": ["CONSTRAINT_NAME"],
                    },
                    "condition": [
                        {
                            "column_name": "TABLE_NAME",
                            "condition": "Equal to",
                            "input_value": str(table_name),
                            "and_or": "",
                        }
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )

            if unique_constraint in query_check_unique["CONSTRAINT_NAME"].values:
                create_unq_flag = 1
                add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
                raw_query_executor(add_query2, db_engine, db_type)

            if create_df_flag:
                add_query2_def = start_query + f" DROP CONSTRAINT " + default_constraint + ";"
                raw_query_executor(add_query2_def, db_engine, db_type)
        elif db_type == "PostgreSQL":
            create_unq_flag = 0
            unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
            query_check_unique = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "INFORMATION_SCHEMA.key_column_usage",
                        "Columns": ["constraint_name"],
                    },
                    "condition": [
                        {
                            "column_name": "table_name",
                            "condition": "Equal to",
                            "input_value": str(table_name),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "table_schema",
                            "condition": "Equal to",
                            "input_value": db_engine[0]["schema"],
                            "and_or": "",
                        },
                    ],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )

            if unique_constraint in query_check_unique["constraint_name"].values:
                create_unq_flag = 1
                add_query2 = start_query + f" DROP CONSTRAINT " + unique_constraint + ";"
                raw_query_executor(add_query2, db_engine, db_type)
        else:
            pass
        raw_query_executor(add_query, db_engine, db_type)

        if db_type == "MSSQL":
            if create_unq_flag:
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)

            if create_df_flag:
                add_query1_def = (
                    start_query
                    + " ADD CONSTRAINT "
                    + default_constraint
                    + " DEFAULT "
                    + def_val
                    + " FOR "
                    + fields["fieldName"]
                    + " ;"
                )
                raw_query_executor(add_query1_def, db_engine, db_type)
        elif db_type == "PostgreSQL":
            unique_constraint = f"UQ" + f"_" + table_name + f"_" + fields["fieldName"]
            if create_unq_flag:
                add_query1 = (
                    start_query
                    + " ADD CONSTRAINT "
                    + unique_constraint
                    + " UNIQUE ("
                    + fields["fieldName"]
                    + ");"
                )
                raw_query_executor(add_query1, db_engine, db_type)
            else:
                pass
        else:
            pass
    error = "Success"

    # Create a Dataframe For Moving Old Value To New , When Changing From Foreign To Another Datatype

    fk_detect = [
        field
        for field in model.concrete_fields
        if field.get_internal_type() == "ForeignKey" and field.name == field_name_fk
    ]
    if len(fk_detect) > 0 and fields["fieldDatatype"] != "ForeignKey":
        fk_name = fk_detect[0]
        if fk_name.parent:
            model2 = get_model_class(fk_name.parent, request, db_engine=db_engine, db_type=db_type)
            save_data_current = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": tablename,
                        "Columns": [model.pk.name, field_name_fk],
                    },
                    "condition": [],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
            save_data_current = save_data_current.drop_duplicates(subset=[field_name_fk])
            save_data_remote = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": fk_name.parent,
                        "Columns": [model2.pk.name, field_name_fk],
                    },
                    "condition": [],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            )
            save_data_remote = save_data_remote.drop_duplicates(subset=[field_name_fk])
            save_data_final = save_data_remote[
                save_data_remote[model2.pk.name]
                .astype(str)
                .isin(save_data_current[field_name_fk].astype(str))
            ]
            save_data_final_dict = save_data_final.to_dict(orient="records")
            if len(save_data_final_dict) > 0:
                if save_data_remote.dtypes[field_name_fk] in ["float64", "int64"] and fields[
                    "fieldDatatype"
                ] in ["IntegerField", "BigIntegerField", "FloatField"]:
                    for val in save_data_final_dict:
                        if (
                            fields["fieldDatatype"] == "IntegerField"
                            or fields["fieldDatatype"] == "BigIntegerField"
                        ):
                            val[field_name_fk] = int(val[field_name_fk])
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": tablename,
                                    "Columns": [
                                        {
                                            "column_name": field_name_fk,
                                            "input_value": str(val[field_name_fk]),
                                            "separator": "",
                                        }
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": field_name_fk,
                                        "condition": "Equal to",
                                        "input_value": str(val[model2.pk.name]),
                                        "and_or": "",
                                    }
                                ],
                            },
                            engine2=db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )
                if save_data_remote.dtypes[field_name_fk] in ["object"] and fields["fieldDatatype"] in [
                    "CharField",
                    "TextField",
                    "FileField",
                    "VideoField",
                    "ImageField",
                ]:
                    for val in save_data_final_dict:
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": tablename,
                                    "Columns": [
                                        {
                                            "column_name": field_name_fk,
                                            "input_value": str(val[field_name_fk]),
                                            "separator": "",
                                        }
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": field_name_fk,
                                        "condition": "Equal to",
                                        "input_value": str(val[model2.pk.name]),
                                        "and_or": "",
                                    }
                                ],
                            },
                            engine2=db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )
                else:
                    if fields["fieldDatatype"] in [
                        "CharField",
                        "TextField",
                        "FileField",
                        "VideoField",
                        "ImageField",
                    ]:
                        for val in save_data_final_dict:
                            update_data_func(
                                request,
                                config_dict={
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": tablename,
                                        "Columns": [
                                            {
                                                "column_name": field_name_fk,
                                                "input_value": str(val[field_name_fk]),
                                                "separator": "",
                                            }
                                        ],
                                    },
                                    "condition": [
                                        {
                                            "column_name": field_name_fk,
                                            "condition": "Equal to",
                                            "input_value": str(val[model2.pk.name]),
                                            "and_or": "",
                                        }
                                    ],
                                },
                                engine2=db_engine,
                                db_type=db_type,
                                engine_override=True,
                            )

                if save_data_remote.dtypes[field_name_fk] in ["datetime64[ns]"] and fields[
                    "fieldDatatype"
                ] in ["DateTimeField", "DateField", "TimeField"]:
                    for val in save_data_final_dict:
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": tablename,
                                    "Columns": [
                                        {
                                            "column_name": field_name_fk,
                                            "input_value": str(val[field_name_fk]),
                                            "separator": "",
                                        }
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": field_name_fk,
                                        "condition": "Equal to",
                                        "input_value": str(val[model2.pk.name]),
                                        "and_or": "",
                                    }
                                ],
                            },
                            engine2=db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )

    attribute_dict = {
        "fieldVerboseName": "verbose_name",
        "fieldNull": "null",
        "fieldUnique": "unique",
        "fieldMaxLength": "max_length",
        "fieldChoices": "choices",
        "fieldUploadTo": "upload_to",
        "fieldDefault": "default",
        "fieldAutoNow": "auto_now",
        "fieldUseSeconds": "use_seconds",
        "fieldEditable": "editable",
        "columns": "columns",
        "secure_with": "secure_with",
        "datakey": "datakey",
        "divider": "divider",
        "validators": "validators",
        "hierarchy_group": "hierarchy_group",
        "hierarchy_level_name": "hierarchy_level_name",
        "computedValue": "computed value",
        "uuid_config": "uuid_config",
        "file_extension": "file_extension",
        "video_type": "video_type",
        "timerange_type": "timerange_type",
        "datetimerange_type": "datetimerange_type",
        "daterange_type": "daterange_type",
        "card_config": "card_config",
        "table_config": "table_config",
        "blacklist_chars": "blacklist characters",
        "mulsel_config": "mulsel_config",
        "privacy_config": "privacy_config",
        "file_size": "file_size",
        "computed_input": "computed input",
    }

    if fields["fieldDatatype"] == "ForeignKey":
        field_config = {
            "internal_type": "ForeignKey",
            "parent": fields["fieldFKTable"],
            "db_column": fields["fieldName"],
        }
    elif fields["fieldDatatype"] == "MultiselectField" and "_mul" in tablename:
        field_config = {
            "internal_type": "CharField",
            "verbose_name": fields["fieldVerboseName"],
        }
    else:
        field_config = {
            "internal_type": fields["fieldDatatype"],
        }

    for key, value in fields.items():
        if key in attribute_dict:
            attr_name = attribute_dict[key]
        elif key in attribute_dict.values():
            attr_name = key
        else:
            attr_name = key

        if key not in ["fieldName", "fieldDatatype", "fieldFKTable"]:
            if key != "fieldDefault":
                value = True if value == "Yes" else value
                value = False if value == "No" else value
                value = True if value is None else value
            if value not in ["Yes", ""]:
                try:
                    value = int(value)
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            if value in [True, False]:
                field_config[attr_name] = value
            else:
                if type(value) in [int, float]:
                    field_config[attr_name] = value
                else:

                    if key == "fieldChoices" or key == "blacklist_chars" or key == "computed_input":
                        choices_list = []
                        for val in value:
                            choices_list.append((val, val))
                        if value == "" or value == []:
                            field_config[attr_name] = ""
                        else:
                            field_config[attr_name] = choices_list
                    else:
                        field_config[attr_name] = value

    model_fields[fields["fieldName"]] = field_config
    model_fields = json.dumps(model_fields)

    update_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": [
                    {"column_name": "fields", "input_value": model_fields, "separator": ","},
                    {
                        "column_name": "version",
                        "input_value": sys_model_version,
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {"column_name": "tablename", "condition": "Equal to", "input_value": tablename, "and_or": ""}
            ],
        },
        engine2=db_engine,
        db_type=db_type,
        engine_override=True,
    )
    return error


def relationships(
    tablename, field_name, request, model, db_connection_name="", model_dict={}, table_fk_data=None
):
    db_type = ""
    if db_connection_name != "":
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        user_db_engine, db_type, schema = app_engine_generator(request)
    table1 = []
    if not table_fk_data.empty:
        table1 = table_fk_data.loc[table_fk_data["FKCOLUMN_NAME"] == field_name, "FKTABLE_NAME"].tolist()

    table2 = model.get_field(field_name).parent
    model_list = []
    all_models = model_dict
    for value in table1:
        if all_models.get(value):
            model_list.append(all_models.get(value))
    if table2:
        model_list.append(table2)

    column_dict = {}
    for model_name in model_list:
        column_list = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "Columns": ["COLUMN_NAME"],
                },
                "condition": [
                    {
                        "column_name": "TABLE_NAME",
                        "condition": "Contains",
                        "input_value": model_name,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "CONSTRAINT_NAME",
                        "condition": "Contains",
                        "input_value": "FK",
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            engine_override=True,
            db_type=db_type,
        )
        if db_type == "MSSQL":
            column_list = column_list.COLUMN_NAME.tolist()
        else:
            column_list = column_list.column_name.tolist()
        column_dict[model_name] = column_list

    r = re.compile(field_name)
    final_dict = {}
    for key, val in column_dict.items():
        final_list = list(filter(r.fullmatch, val))
        if final_list:
            if key == table2:
                final_dict[key] = [final_list, "Parent"]
            else:
                final_dict[key] = [final_list, "Child"]
        else:
            if key == table2:
                final_dict[key] = [["id"], "Parent"]
    return final_dict


data_validators = {
    "MaxValueValidator": {
        "name": "Max value",
        "arguments": ["limit_value", "message"],
        "field_str": """
                                     <div class="row">
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Limit value</label>
                                             <input type="number" name="limit_value" class="form-control numberinput" />
                                         </div>
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Error Message</label>
                                             <input type="text" name="message" class="form-control textInput" />
                                         </div>
                                     </div>
                                     """,
        "desc": "Raises a ValidationError with a code of 'max_value' if value is greater than limit_value.",
    },
    "AdvancedValidator": {
        "name": "Advanced Validator",
        "arguments": ["start_value", "end_value", "validationid", "pattern_value"],
        "field_str": """
                                <div class="validationbody" style="margin-left:-6px">
                                     <div class="col-12 form-group" >
                                             <label class="acies_label col-md-3">Error Message</label>
                                             <input id="error_message" type="text" name="message" class="form-control textInput" />
                                         </div>
                                    <div class="acies-float-right">
                                        <div class="col-3 form-group" >
                                        <button id="addRow" class="btn btn-primary btn-xs rounded" style="width:25px" type="button" name="post">+</button>
                                     </div>
                                     </div>
                                     <div class="row">
                                         <div class="col-3 form-group" >
                                             <label class="acies_label col-md-12">Index start</label>
                                             <input min="0" type="number" name="start_value" id="start_value0" class="form-control numberinput"/>
                                         </div>
                                         <div class="col-3 form-group" >
                                             <label class="acies_label col-md-12">Index end</label>
                                             <input min="1" type="number" name="end_value" id="end_value0" class="form-control numberinput" />
                                         </div>
                                         <div class="col-3 form-group" >
                                             <label class="acies_label col-md-12">Validation type</label>
                                                <select id="validationid0" name="validationlist" form="validationform" class="form-control select2 validclass">
                                                <option value="Alphabet">Alphabet</option>
                                                <option value="Numeric">Numeric</option>
                                                <option value="Alphanumeric">Alphanumeric</option>
                                                <option value="Special Character">Special Character</option>
                                                <option value="Whitespace">Whitespace</option>
                                                <option value="Equal to">Equal to</option>
                                                </select>
                                         </div>
                                         <div class="col-3 form-group patternid" style='display:none;' id="pattern_div0">
                                             <label class="acies_label col-md-12">Value</label>
                                             <select name="pattern_value" class="form-control select2" id="pattern_value0" data-tags="true"> </select>
                                         </div>
                                         </div>
                                        <div id="newRow" style="margin-right:1.5rem"></div>
                                    </div>
                                    <span class="note">Index start from 0.</span>
                                    <script>
                                    $("#start_value0, #end_value0").on("input", function () {
                                        var inputValue = $(this).val();
                                        var sanitizedValue = inputValue.replace(/[^0-9]/g, '');
                                        $(this).val(sanitizedValue);
                                        if (sanitizedValue !== "") {
                                            var numericValue = parseInt(sanitizedValue);
                                            if (numericValue < 0) {
                                                $(this).val("");
                                            }
                                        }
                                    });


                                    $("#validationid0").select2()
                                    $("#pattern_value0").select2({tags:true})
                                    </script>
                                     """,
        "desc": "Raises AdvancedValidationError if given value does not match with the pattern defined.",
    },
    "MinValueValidator": {
        "name": "Min value",
        "arguments": ["limit_value", "message"],
        "field_str": """
                                     <div class="row">
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Limit value2</label>
                                             <input type="number" name="limit_value" class="form-control numberinput" />
                                         </div>
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Error Message</label>
                                             <input type="text" name="message" class="form-control textInput" />
                                         </div>
                                     </div>
                                     """,
        "desc": "Raises a ValidationError with a code of 'min_value' if value is less than limit_value.",
    },
    "MaxLengthValidator": {
        "name": "Max length",
        "arguments": ["limit_value", "message"],
        "field_str": """
                                <div class="validationbody">
                                     <div class="row">
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Limit value</label>
                                             <input type="number" name="limit_value" class="form-control numberinput" />
                                         </div>
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Error Message</label>
                                             <input type="text" name="message" class="form-control textInput" />
                                         </div>
                                     </div>
                                </div>
                                     """,
        "desc": "Raises a ValidationError with a code of 'max_length' if the length of value is greater than limit_value.",
    },
    "MinLengthValidator": {
        "name": "Min length",
        "arguments": ["limit_value", "message"],
        "field_str": """
                                <div class="validationbody">
                                     <div class="row">
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Limit value</label>
                                             <input type="number" name="limit_value" class="form-control numberinput" />
                                         </div>
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Error Message</label>
                                             <input type="text" name="message" class="form-control textInput" />
                                         </div>
                                     </div>
                                </div>
                                     """,
        "desc": "Raises a ValidationError with a code of 'min_length' if the length of value is less than limit_value.",
    },
    "DecimalValidator": {
        "name": "Rounding off",
        "arguments": ["max_digits", "decimal_places"],
        "field_str": """
                                    <div class="validationbody">
                                     <div class="row">
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Max digits</label>
                                             <input type="number" name="max_digits" class="form-control" />
                                         </div>
                                         <div class="col-6 form-group" >
                                             <label class="acies_label col-md-12">Decimal places</label>
                                             <input type="number" name="decimal_places" class="form-control" />
                                         </div>
                                     </div>
                                    </div>
                                     """,
        "desc": """
        Raises ValidationError with the following codes:
        - 'max_digits' if the number of digits is larger than max_digits.
        - 'max_decimal_places' if the number of decimals is larger than decimal_places.
        - 'max_whole_digits' if the number of whole digits is larger than the difference between max_digits and decimal_places."
        """,
    },
    "ColumnValidator": {
        "name": "Column based validation",
        "arguments": ["colV_col1_val", "colV_cond_val", "colV_col2_val", "error_message_colV"],
        "field_str": """
                                <div class="validationbody">
                                     <div class="col-12 form-group p-0">
                                             <label class="acies_label col-md-3">Error Message1</label>
                                             <input id="error_message_colV" type="text" name="error_message_colV" class="form-control textInput" />
                                         </div>
                                     <div class="row">
                                         <div class="col-4 form-group" >
                                             <label class="acies_label col-md-12">Column 1</label>
                                             <select id="colV_col1_val" name="colV_col1_val" class="form-control select2">
                                             </select>
                                         </div>
                                         <div class="col-4 form-group" >
                                             <label class="acies_label col-md-12">Condition</label>
                                             <select id="colV_cond_val" name="colV_cond_val" class="form-control select2">
                                             <option value="Equal to">Equal to</option>
                                             <option value="Not Equal to">Not Equal to</option>
                                             <option value="Greater than">Greater than</option>
                                             <option value="Smaller than">Smaller than</option>
                                             <option value="Greater than equal to">Greater than equal to</option>
                                             <option value="Smaller than equal to">Smaller than equal to</option>
                                             </select>
                                         </div>
                                         <div class="col-4 form-group" >
                                             <label class="acies_label col-md-12">Column 2</label>
                                                <select id="colV_col2_val" name="colV_col2_val" class="form-control select2">
                                             </select>
                                         </div>
                                         </div>
                                    </div>
                                     <script>$("#colV_col1_val").select2()
                                     $("#colV_cond_val").select2()
                                     $("#colV_col2_val").select2()
                                     </script>
                                     """,
        "desc": "Raises ColumnValidationError if given condition doesn't satisfy.",
    },
    "AdvanceDateValidation": {
        "name": "Advance date validation",
        "arguments": ["colV_cond_val", "colV_cond_val2", "error_message_colV"],
        "field_str": """
                                <div class="validationbody">
                                     <div class="col-12 form-group p-0">
                                             <label class="acies_label col-md-3">Error Message1</label>
                                             <input id="error_message_colV" type="text" name="error_message_colV" class="form-control textInput" />
                                      </div>
                                     <div class="row">
                                         <div class="col-4 form-group" >
                                             <label class="acies_label col-md-12">Condition</label>
                                             <select id="colV_cond_val" name="colV_cond_val" class="form-control select2">
                                             <option value="Equal to">Equal to</option>
                                             <option value="Not Equal to">Not Equal to</option>
                                             <option value="Greater than">Greater than</option>
                                             <option value="Smaller than">Smaller than</option>
                                             <option value="Greater than equal to">Greater than equal to</option>
                                             <option value="Smaller than equal to">Smaller than equal to</option>
                                             </select>
                                         </div>

                                        <div class="col-4 form-group" >
                                            <label class="acies_label col-md-12">Select Period</label>
                                            <select id="colV_cond_val2" name="colV_cond_val2" class="form-control select2">
                                                <option value="Today">Today</option>
                                                <option value="Yesterday">Yesterday</option>
                                                <option value="Tomorrow">Tomorrow</option>
                                                <option value="Last week">Last week</option>
                                                <option value="This week">This week</option>
                                                <option value="This month">This month</option>
                                                <option value="Last month">Last month</option>
                                                <option value="This year">This year</option>
                                                <option value="Last year">Last year</option>
                                                <option value="Custom date">Custom date</option>
                                            </select>
                                         </div>
                                        <div class="col-4 form-group" id="date_validation-input" style="display:none;">
                                            <label>Custom Date</label>
                                            <div class="input-group date">
                                                <input name="colV_cond_val2" type="date" placeholder="YYYY-MM-DD" class="form-control datepickerinput" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}">
                                                <div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv">
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                    <script>
                                        $("#colV_cond_val").select2()
                                        $('#colV_cond_val2').select2();

                                        $('#colV_cond_val2').on('select2:select', function() {
                                            var selectedOption = $(this).val();

                                            if (selectedOption === 'Custom date') {
                                                $('#date_validation-input').css("display", '');
                                            } else {
                                                $('#date_validation-input').css("display", 'none');
                                            }
                                        });
                                    </script>
                                     """,
        "desc": "Raises AdvanceDateValidationError if given condition doesn't satisfy.",
    },
    "EmailValidator": {
        "name": "Email validation",
        "arguments": ["error_message_emailV"],
        "field_str": """
                                    <div class="validationbody">
                                        <div class="col-12 form-group p-0">
                                             <label class="acies_label col-md-3">Error Message</label>
                                             <input id="error_message_emailV" type="text" name="error_message_emailV" class="form-control textInput" />
                                        </div>
                                    </div>
                                     <script>$("#colV_col1_val").select2()
                                     $("#colV_cond_val").select2()
                                     $("#colV_col2_val").select2()
                                     </script>
                                     """,
        "desc": "Raises EmailValidationError if input is not in valid email format.",
    },
}


def validation_details(selected_validation):
    return data_validators[selected_validation]


def add_validations(tablename, field_name, val_name, ValDict, request):

    model_fields = json.loads(
        (
            read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields"]},
                    "condition": [
                        {
                            "column_name": "tablename",
                            "condition": "Equal to",
                            "input_value": tablename,
                            "and_or": "",
                        }
                    ],
                },
            )
        )
        .iloc[0]
        .fields
    )

    validation_dict = {}
    for key, value in ValDict.items():
        try:
            ValDict[key] = int(value)
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        if value == "":
            ValDict[key] = None

    validation_dict[val_name] = ValDict
    if val_name == "AdvancedValidator":
        validation_dict[val_name]["regex"] = regex_validation(ValDict)

    if "validators" not in model_fields[field_name]:
        model_str = model_fields[field_name]
        model_str["validators"] = validation_dict
    else:
        model_str = model_fields[field_name]
        if isinstance(model_str["validators"], dict):
            model_str["validators"][val_name] = ValDict
        else:
            model_str["validators"] = validation_dict

    model_fields[field_name] = model_str
    model_fields = json.dumps(model_fields)

    error = "Success"
    try:
        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Tables",
                    "Columns": [
                        {
                            "column_name": "fields",
                            "input_value": model_fields,
                            "separator": "",
                        }
                    ],
                },
                "condition": [
                    {
                        "column_name": "tablename",
                        "condition": "Equal to",
                        "input_value": tablename,
                        "and_or": "",
                    },
                ],
            },
        )

    except Exception as e:
        logging.warning(
            f"Following exception occured - {e}",
            ConcatenationField,
            HierarchyField,
            UniqueIDField,
            DateRangeField,
            DateTimeRangeField,
            TimeRangeField,
            CardField,
            CardCvvField,
            CardExpiryField,
            CardTypeField,
            UserField,
            EmailTypeField,
            TableField,
            MultiselectField,
            RTFField,
            PrivacyField,
        )
        error = e

    return error


def delete_element(model_name, field_name, request, db_connection_name, sys_model_version="1.0.0"):
    user_db_engine, db_type = db_engine_extractor(db_connection_name)
    sql_table_name = "users_" + model_name.lower()
    model_fields = read_data_func(
        request,
        {
            "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["fields"]},
            "condition": [
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": model_name,
                    "and_or": "",
                }
            ],
        },
        engine2=user_db_engine,
        engine_override=True,
        db_type=db_type,
    ).fields.iloc[0]
    model_fields = json.loads(model_fields)

    if db_type == "MSSQL":
        default_constraint = f"DF_{sql_table_name}_{field_name}"
        existing_default_exists = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "sys.default_constraints",
                    "Columns": ["name"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "Equal to",
                        "input_value": default_constraint,
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
        if not existing_default_exists.empty:
            add_query2_def = f"ALTER TABLE {sql_table_name} DROP CONSTRAINT {default_constraint}"
            with user_db_engine[0].begin() as conn:
                conn.execute(text(add_query2_def))

        check_fk_status = extract_foreign_keys(sql_table_name, user_db_engine, db_type)
        check_fk_status = check_fk_status[check_fk_status["FKCOLUMN_NAME"] == field_name]
        if not check_fk_status.empty:
            modelName = get_model_class(
                model_name,
                request=request,
                db_connection_name=db_connection_name,
                db_engine=user_db_engine,
                db_type=db_type,
            )
            current_field = modelName.get_field(field_name)
            parent_model_config = {}
            if current_field.get_internal_type() in ["IntegerField", "FloatField", "BigIntegerField"]:
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldDefault": current_field.default,
                    "fieldName": current_field.name,
                }
            if current_field.get_internal_type() == "CharField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_field.max_length,
                    "fieldDefault": current_field.default,
                    "fieldName": current_field.name,
                }
            if current_field.get_internal_type() == "ConcatenationField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }
            if current_field.get_internal_type() == "UniqueIDField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "uuid_config": "uuid_config",
                }
            if current_field.get_internal_type() == "FileField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "file_extension": "file_extension",
                }
            if current_field.get_internal_type() == "VideoField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "video_type": "video_type",
                }

            if current_field.get_internal_type() in ["TextField", "BooleanField", "URLField"]:
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": current_field.null,
                    "fieldUnique": current_field.unique,
                    "computedValue": False,
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() in ["DateTimeField", "DateField", "TimeField"]:
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldAutoNow": "No",
                    "fieldEditable": "Yes",
                    "fieldName": current_field.name,
                    "fieldUseSeconds": "true",
                }

            if current_field.get_internal_type() == "DateRangeField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "TimeRangeField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "DateTimeRangeField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "UserField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "PrivacyField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "privacy_config": "privacy_config",
                }

            if current_field.get_internal_type() == "CardField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "card_config": "card_config",
                }

            if current_field.get_internal_type() == "TableField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "table_config": "table_config",
                }

            if current_field.get_internal_type() == "CardCvvField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "CardExpiryField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "CardTypeField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "EmailTypeField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_field.max_length,
                    "fieldDefault": current_field.default,
                    "fieldName": current_field.name,
                }

            if current_field.get_internal_type() == "MultiselectField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_field.name,
                    "mulsel_config": "mulsel_config",
                }

            if current_field.get_internal_type() == "RTFField":
                parent_model_config = {
                    "fieldDatatype": current_field.get_internal_type(),
                    "fieldVerboseName": current_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_field.max_length,
                    "fieldDefault": current_field.default,
                    "fieldName": current_field.name,
                }

            fk_table_list = check_fk_status["FKTABLE_NAME"].values
            fk_col_list = check_fk_status["FKCOLUMN_NAME"].values
            model_df = read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["tablename"]},
                    "condition": [],
                },
                engine2=user_db_engine,
                engine_override=True,
                db_type=db_type,
            ).tablename.tolist()
            model_dict_data = {"users_" + model_df[i].lower(): model_df[i] for i in range(len(model_df))}
            if len(fk_table_list) > 0 and parent_model_config:
                for i in range(len(fk_table_list)):
                    child_org_name = model_dict_data[fk_table_list[i]]
                    child_model_field = get_model_class(
                        child_org_name, request=request, db_connection_name=db_connection_name
                    )
                    parent_model_config["fieldName"] = fk_col_list[i]
                    parent_model_config["fieldVerboseName"] = child_model_field.get_field(
                        fk_col_list[i]
                    ).verbose_name
                    edit_element(child_org_name, parent_model_config, request, db_connection_name)
                    redis_instance.delete(db_connection_name + fk_table_list[i])

    db_type = ""
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            db_type = db_data[db_connection_name].get("db_type")
            json_file.close()
    if db_type == "PostgreSQL":
        start_query = f"ALTER TABLE {user_db_engine[0]['schema']}.users_{model_name.lower()} "
    else:
        start_query = f"ALTER TABLE users_{model_name.lower()} "
    if db_type == "MSSQL":
        constraint_check = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                    "Columns": ["CONSTRAINT_NAME"],
                },
                "condition": [
                    {
                        "column_name": "TABLE_NAME",
                        "condition": "Equal to",
                        "input_value": str(sql_table_name),
                        "and_or": "and",
                    },
                    {
                        "column_name": "COLUMN_NAME",
                        "condition": "Equal to",
                        "input_value": str(field_name),
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
    elif db_type == "Oracle":
        constraint_check = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "all_cons_columns",
                    "Columns": ["constraint_name"],
                },
                "condition": [
                    {
                        "column_name": "column_name",
                        "condition": "Equal to",
                        "input_value": field_name.upper(),
                        "and_or": "AND",
                    },
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": sql_table_name.upper(),
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
    else:
        constraint_check = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "information_schema.key_column_usage",
                    "Columns": ["constraint_name"],
                },
                "condition": [
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": str(sql_table_name),
                        "and_or": "and",
                    },
                    {
                        "column_name": "table_schema",
                        "condition": "Equal to",
                        "input_value": str(user_db_engine[0]["schema"]),
                        "and_or": "and",
                    },
                    {
                        "column_name": "column_name",
                        "condition": "Equal to",
                        "input_value": str(field_name),
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
    if not constraint_check.empty:
        for c_name in constraint_check.values:
            drop_query = f"{start_query} DROP CONSTRAINT {c_name[0]} ;"
            raw_query_executor(drop_query, user_db_engine, db_type)
    exec_query = f"{start_query} DROP COLUMN {field_name} ;"
    raw_query_executor(exec_query, user_db_engine, db_type)
    if model_fields.get(field_name):
        del model_fields[field_name]
    model_fields = json.dumps(model_fields)
    update_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": [
                    {
                        "column_name": "fields",
                        "input_value": model_fields,
                        "separator": ",",
                    },
                    {
                        "column_name": "version",
                        "input_value": sys_model_version,
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": model_name,
                    "and_or": "",
                },
            ],
        },
        engine2=user_db_engine,
        db_type=db_type,
        engine_override=True,
    )
    return "success"


def delete_model(model_name, request, db_connection_name):
    sql_table_name = "users_" + model_name.lower()
    if db_connection_name != "":
        db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        db_engine, db_type, schema = app_engine_generator(request)

    if db_type in ["MSSQL", "Oracle"]:
        del_query = f"DROP TABLE users_{model_name.lower()}"
        alter_query = f"ALTER TABLE users_{model_name.lower()}"
    else:
        del_query = f"DROP TABLE {db_engine[0]['schema']}.users_{model_name.lower()}"
        alter_query = f"ALTER TABLE {db_engine[0]['schema']}.users_{model_name.lower()}"

    modelName = get_model_class(model_name, request=request, db_connection_name=db_connection_name)

    check_fk_status = extract_foreign_keys(sql_table_name, db_engine, db_type)

    if not check_fk_status.empty:
        db_foreign_dict = check_fk_status.to_dict(orient="records")
        for i in range(len(db_foreign_dict)):
            current_parent_field = modelName.get_field(db_foreign_dict[i]["FKCOLUMN_NAME"])
            parent_model_config = {}
            if current_parent_field.get_internal_type() in ["IntegerField", "FloatField", "BigIntegerField"]:
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldDefault": current_parent_field.default,
                    "fieldName": current_parent_field.name,
                }
            if current_parent_field.get_internal_type() in ["CharField", "URLField"]:
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_parent_field.max_length,
                    "fieldDefault": current_parent_field.default,
                    "fieldName": current_parent_field.name,
                }
            if current_parent_field.get_internal_type() == "ConcatenationField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }
            if current_parent_field.get_internal_type() == "UniqueIDField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "uuid_config": "uuid_config",
                }

            if current_parent_field.get_internal_type() == "FileField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "file_extension": "file_extension",
                }

            if current_parent_field.get_internal_type() == "VideoField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "video_type": "video_type",
                }

            if current_parent_field.get_internal_type() in ["TextField", "BooleanField"]:
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": current_parent_field.null,
                    "fieldUnique": current_parent_field.unique,
                    "computedValue": False,
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() in ["DateTimeField", "DateField", "TimeField"]:
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldAutoNow": "No",
                    "fieldEditable": "Yes",
                    "fieldName": current_parent_field.name,
                    "fieldUseSeconds": "true",
                }

            if current_parent_field.get_internal_type() == "DateRangeField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "TimeRangeField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "DateTimeRangeField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "UserField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "PrivacyField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "privacy_config": "privacy_config",
                }

            if current_parent_field.get_internal_type() == "CardField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "card_config": "card_config",
                }

            if current_parent_field.get_internal_type() == "TableField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "table_config": "table_config",
                }

            if current_parent_field.get_internal_type() == "CardCvvField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "CardExpiryField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "CardTypeField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "fieldMaxLength": current_parent_field.max_length,
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "EmailTypeField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_parent_field.max_length,
                    "fieldDefault": current_parent_field.default,
                    "fieldName": current_parent_field.name,
                }

            if current_parent_field.get_internal_type() == "MultiselectField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "columns": [],
                    "divider": "select",
                    "fieldEditable": "No",
                    "fieldName": current_parent_field.name,
                    "mulsel_config": "mulsel_config",
                }

            if current_parent_field.get_internal_type() == "RTFField":
                parent_model_config = {
                    "fieldDatatype": current_parent_field.get_internal_type(),
                    "fieldVerboseName": current_parent_field.verbose_name,
                    "fieldNull": "Yes",
                    "fieldUnique": "No",
                    "computedValue": False,
                    "fieldMaxLength": current_parent_field.max_length,
                    "fieldDefault": current_parent_field.default,
                    "fieldName": current_parent_field.name,
                }

            model_df = read_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["tablename"]},
                    "condition": [],
                },
                engine2=db_engine,
                engine_override=True,
                db_type=db_type,
            ).tablename.tolist()

            model_dict_data = {"users_" + model_df[i].lower(): model_df[i] for i in range(len(model_df))}

            if parent_model_config:
                child_org_name = model_dict_data[db_foreign_dict[i]["FKTABLE_NAME"]]
                child_model_field = get_model_class(
                    child_org_name, request=request, db_connection_name=db_connection_name
                )
                parent_model_config["fieldVerboseName"] = child_model_field.get_field(
                    current_parent_field.name
                ).verbose_name
                edit_element(child_org_name, parent_model_config, request, db_connection_name)
                redis_instance.delete(db_connection_name + db_foreign_dict[i]["FKTABLE_NAME"])
    else:
        pass
    for field in modelName.concrete_fields:
        if field.get_internal_type() == "ForeignKey":
            if db_type == "MSSQL":
                constraint_check = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
                            "Columns": ["CONSTRAINT_NAME"],
                        },
                        "condition": [
                            {
                                "column_name": "TABLE_NAME",
                                "condition": "Equal to",
                                "input_value": str(sql_table_name),
                                "and_or": "and",
                            },
                            {
                                "column_name": "COLUMN_NAME",
                                "condition": "Equal to",
                                "input_value": str(field.name),
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
            elif db_type == "Oracle":
                constraint_check = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "all_cons_columns",
                            "Columns": ["constraint_name"],
                        },
                        "condition": [
                            {
                                "column_name": "table_name",
                                "condition": "Equal to",
                                "input_value": sql_table_name.upper(),
                                "and_or": "and",
                            },
                            {
                                "column_name": "column_name",
                                "condition": "Equal to",
                                "input_value": field.name.upper(),
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            else:
                constraint_check = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "information_schema.key_column_usage",
                            "Columns": ["constraint_name"],
                        },
                        "condition": [
                            {
                                "column_name": "table_name",
                                "condition": "Equal to",
                                "input_value": str(sql_table_name),
                                "and_or": "and",
                            },
                            {
                                "column_name": "table_schema",
                                "condition": "Equal to",
                                "input_value": str(db_engine[0]["schema"]),
                                "and_or": "and",
                            },
                            {
                                "column_name": "column_name",
                                "condition": "Equal to",
                                "input_value": str(field.name),
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            if not constraint_check.empty:
                for c_name in constraint_check.values:
                    drop_query = f"{alter_query} DROP CONSTRAINT {c_name[0]} ;"
                    raw_query_executor(drop_query, db_engine, db_type)

    raw_query_executor(del_query, db_engine, db_type)

    delete_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
            },
            "condition": [
                {
                    "column_name": "tablename",
                    "condition": "Equal to",
                    "input_value": model_name,
                    "and_or": "",
                },
            ],
        },
        engine2=db_engine,
        engine_override=True,
        db_type=db_type,
    )
    return True


def migration_handler(sys_table_repo, model_json, request, db_connection_name):
    existing_tables = sys_table_repo["tablename"].tolist()
    model_tables = model_json.keys()
    deleted_models = [i for i in existing_tables if i not in model_tables]
    user_db_engine, db_type = db_engine_extractor(db_connection_name)
    app_config_version_check = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["*"],
            },
            "condition": [
                {
                    "column_name": "model_type",
                    "condition": "Equal to",
                    "input_value": "system defined",
                    "and_or": "",
                }
            ],
        },
        engine2=user_db_engine,
        db_type=db_type,
        engine_override=True,
    )
    if "version" not in app_config_version_check:
        field_config_version = {
            "fieldName": "version",
            "fieldDatatype": "CharField",
            "fieldVerboseName": "Version",
            "fieldNull": "No",
            "fieldUnique": "No",
            "validators": [],
            "fieldMaxLength": 10,
            "fieldDefault": "1.0.0",
        }
        add_element("Tables", field_config_version, request, db_connection_name)

    for table in model_json:
        sys_model_dict = model_json[table]["field_config"]
        sys_table_data = sys_table_repo[sys_table_repo["tablename"] == table]

        sys_model_version = model_json[table]["version"]

        if not sys_table_data.empty:
            sys_table_dict = json.loads(sys_table_data.fields.values[0])
            if table == "CountryMaster" or table == "CurrencyMaster":
                if table == "CountryMaster":
                    field = "country_name"
                else:
                    field = "currency_code"
                field_config = sys_table_dict[field]
                val = field_config["choices"]
                if val:
                    if type(val) == list and type(val[0]) == list and type(val[0][0]) == list:
                        sys_table_dict[field]["choices"] = [i[0] for i in val]
                    elif type(val) == list and type(val[0]) == str:
                        sys_table_dict[field]["choices"] = [[i, i] for i in val]
                    else:
                        sys_table_dict[field]["choices"] = val
                    update_data_func(
                        request,
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Tables",
                                "Columns": [
                                    {
                                        "column_name": "fields",
                                        "input_value": json.dumps(sys_table_dict),
                                        "separator": "",
                                    }
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": "tablename",
                                    "condition": "Equal to",
                                    "input_value": table,
                                    "and_or": "",
                                },
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                else:
                    pass
                continue
            else:
                pass
            if sys_model_dict != sys_table_dict:
                collated_fields = {i for i in list(sys_model_dict.keys()) + list(sys_table_dict.keys())}
                for field in collated_fields:
                    if not sys_model_dict.get(field) and sys_table_dict.get(field):
                        delete_element(table, field, request, db_connection_name, sys_model_version)
                for field in collated_fields:
                    if sys_model_dict.get(field) and sys_table_dict.get(field):
                        if (sys_model_dict[field] != sys_table_dict[field]) and table not in [
                            "CountryMaster",
                            "CurrencyMaster",
                        ]:
                            # Update field attribute
                            field_config = {"fieldName": field}
                            for attr, val in sys_model_dict[field].items():
                                if attr == "internal_type":
                                    field_config["fieldDatatype"] = val
                                elif attr == "verbose_name":
                                    field_config["fieldVerboseName"] = sys_table_dict[field]["verbose_name"]
                                elif attr == "null":
                                    if val:
                                        field_config["fieldNull"] = "Yes"
                                    else:
                                        field_config["fieldNull"] = "No"
                                elif attr == "unique":
                                    if val:
                                        field_config["fieldUnique"] = "Yes"
                                    else:
                                        field_config["fieldUnique"] = "No"
                                elif attr == "default":
                                    field_config["default"] = val
                                elif attr == "choices":
                                    field_config["fieldChoices"] = val
                                elif attr == "max_length":
                                    field_config["fieldMaxLength"] = val
                                elif attr == "parent":
                                    field_config["fieldParentFKTable"] = val
                                elif attr == "related_column":
                                    field_config["fieldRelatedColumn"] = val
                                elif sys_table_dict[field].get("parent"):
                                    field_config["fieldFKTable"] = sys_table_dict[field]["parent"]
                                elif attr == "validators":
                                    field_config["validators"] = val
                                elif attr == "blacklist characters":
                                    field_config["blacklist characters"] = val
                                elif attr == "computed input":
                                    field_config["computed input"] = val
                            edit_element(
                                table,
                                field_config,
                                request,
                                db_connection_name,
                                sys_model_version=sys_model_version,
                            )
                        else:
                            pass
                    elif sys_model_dict.get(field) and not sys_table_dict.get(field):
                        # Add new field
                        field_config = {"fieldName": field}
                        for attr, val in sys_model_dict[field].items():
                            if attr == "internal_type":
                                field_config["fieldDatatype"] = val
                            elif attr == "verbose_name":
                                field_config["fieldVerboseName"] = val
                            elif attr == "null":
                                if val:
                                    field_config["fieldNull"] = "Yes"
                                else:
                                    field_config["fieldNull"] = "No"
                            elif attr == "unique":
                                if val:
                                    field_config["fieldUnique"] = "Yes"
                                else:
                                    field_config["fieldUnique"] = "No"
                            elif attr == "default":
                                field_config["fieldDefault"] = val
                            elif attr == "choices":
                                field_config["fieldChoices"] = val
                            elif attr == "max_length":
                                field_config["fieldMaxLength"] = val
                            elif attr == "parent":
                                field_config["fieldFKTable"] = val
                            elif attr == "related_name":
                                field_config["fieldRelatedName"] = val
                            elif attr == "editable":
                                field_config["fieldEditable"] = val
                            elif attr == "auto_now":
                                field_config["fieldAutoNow"] = val
                            elif attr == "use_seconds":
                                field_config["fieldUseSeconds"] = val
                            elif attr == "secure_with":
                                field_config["secure_with"] = val
                            elif attr == "datakey":
                                field_config["datakey"] = val
                            elif attr == "validators":
                                field_config["validators"] = val
                            elif attr == "blacklist characters":
                                field_config["blacklist characters"] = val
                            elif attr == "computed input":
                                field_config["computed input"] = val
                        add_element(table, field_config, request, db_connection_name, sys_model_version)
            elif sys_table_data.version.values[0] != sys_model_version:
                update_data_func(
                    request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Tables",
                            "Columns": [
                                {
                                    "column_name": "version",
                                    "input_value": sys_model_version,
                                    "separator": "",
                                }
                            ],
                        },
                        "condition": [
                            {
                                "column_name": "tablename",
                                "condition": "Equal to",
                                "input_value": table,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
            else:
                pass
        else:
            # Create new model
            new_model_name = table
            fields = []
            for f_name, f_attr in sys_model_dict.items():
                field_config = {}
                field_config["field name"] = f_name
                for attr, val in f_attr.items():
                    if attr == "internal_type":
                        field_config["field data type"] = val
                    elif attr == "verbose_name":
                        field_config["field header"] = val
                    elif attr == "null":
                        if val:
                            field_config["nullable?"] = "Yes"
                        else:
                            field_config["nullable?"] = "No"
                    elif attr == "unique":
                        if val:
                            field_config["unique"] = "Yes"
                        else:
                            field_config["unique"] = "No"
                    elif attr == "default":
                        field_config["default"] = val
                    elif attr == "choices":
                        field_config["choices"] = val
                    elif attr == "max_length":
                        field_config["maximum length*"] = val
                    elif attr == "parent":
                        field_config["parent table"] = val
                    elif attr == "auto_now":
                        field_config["auto now?"] = val
                    elif attr == "use_seconds":
                        field_config["Seconds precision?"] = val
                    elif attr == "editable":
                        field_config["editable?"] = val
                    elif attr == "validators":
                        field_config["validators"] = val
                    elif attr == "secure_with":
                        field_config["secure_with"] = val
                    elif attr == "datakey":
                        field_config["datakey"] = val
                    elif attr == "blacklist characters":
                        field_config["blacklist characters"] = val
                    elif attr == "computed input":
                        field_config["computed input"] = val
                fields.append(field_config)
            create_table_sql(
                new_model_name,
                fields,
                request,
                model_type="system defined",
                db_connection_name=db_connection_name,
                sys_model_version=sys_model_version,
            )
    for delt in deleted_models:
        delete_model(delt, request, db_connection_name)
    return True


def fresh_migration(request, db_connection_name):
    if os.path.exists(f"{PLATFORM_DATA_PATH}app_config_tables.json"):
        with open(f"{PLATFORM_DATA_PATH}app_config_tables.json") as json_file:
            model_json = json.load(json_file)
            models_list = []
            for table in model_json:
                sys_model_dict = model_json[table]["field_config"]
                sys_model_version = model_json[table]["version"]
                new_model_name = table
                fields = []
                for f_name, f_attr in sys_model_dict.items():
                    field_config = {}
                    field_config["field name"] = f_name
                    for attr, val in f_attr.items():
                        if attr == "internal_type":
                            field_config["field data type"] = val
                        elif attr == "verbose_name":
                            field_config["field header"] = val
                        elif attr == "null":
                            if val:
                                field_config["nullable?"] = "Yes"
                            else:
                                field_config["nullable?"] = "No"
                        elif attr == "unique":
                            if val:
                                field_config["unique"] = "Yes"
                            else:
                                field_config["unique"] = "No"
                        elif attr == "default":
                            field_config["default"] = val
                        elif attr == "choices":
                            field_config["choices"] = val
                        elif attr == "max_length":
                            field_config["maximum length*"] = val
                        elif attr == "parent":
                            field_config["parent table"] = val
                        elif attr == "auto_now":
                            field_config["auto now?"] = val
                        elif attr == "use_seconds":
                            field_config["Seconds precision?"] = val
                        elif attr == "editable":
                            field_config["editable?"] = val
                        elif attr == "secure_with":
                            field_config["secure_with"] = val
                        elif attr == "datakey":
                            field_config["datakey"] = val
                        elif attr == "blacklist characters":
                            field_config["blacklist characters"] = val
                        elif attr == "computed input":
                            field_config["computed input"] = val
                        else:
                            field_config[attr] = val
                    fields.append(field_config)
                create_table_sql(
                    new_model_name,
                    fields,
                    request,
                    model_type="system defined",
                    db_connection_name=db_connection_name,
                    initial_migration=True,
                )
                models_list.append(
                    {
                        "tablename": new_model_name,
                        "fields": json.dumps(sys_model_dict),
                        "model_type": "system defined",
                        "version": sys_model_version,
                    }
                )
            data = pd.DataFrame(models_list)
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            data_handling(request, data, "Tables", con=user_db_engine, db_type=db_type, engine_override=True)
        return "Success"
    return "Config is missing"


def get_models(request, db_connection_name=""):
    if db_connection_name != "":
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    else:
        user_db_engine, db_type, schema = app_engine_generator(request)
    db_tables = read_data_func(
        request,
        {
            "inputs": {"Data_source": "Database", "Table": "Tables", "Columns": ["tablename", "fields"]},
            "condition": [],
        },
        engine2=user_db_engine,
        engine_override=True,
        db_type=db_type,
    )
    model_list = []
    for i in db_tables.index:
        tb_detail = db_tables.iloc[i]
        if tb_detail["tablename"] not in admin_tables:
            model = ModelInfo(tb_detail["tablename"], json.loads(tb_detail["fields"]))
        model_list.append(model)

    return model_list


def create_table_dict_creator(raw_fields):
    fields = []
    for f_name, f_attr in raw_fields.items():
        field_config = {}
        field_config["field name"] = f_name
        for attr, val in f_attr.items():
            if attr == "internal_type":
                field_config["field data type"] = val
            elif attr == "verbose_name":
                field_config["field header"] = val
            elif attr == "null":
                if val:
                    field_config["nullable?"] = "Yes"
                else:
                    field_config["nullable?"] = "No"
            elif attr == "unique":
                if val:
                    field_config["unique"] = "Yes"
                else:
                    field_config["unique"] = "No"
            elif attr == "default":
                field_config["default"] = val
            elif attr == "choices":
                field_config["choices"] = val
            elif attr == "max_length":
                field_config["maximum length*"] = val
            elif attr == "parent":
                field_config["parent table"] = val
            elif attr == "auto_now":
                field_config["auto now?"] = val
            elif attr == "use_seconds":
                field_config["Seconds precision?"] = val
            elif attr == "editable":
                field_config["editable?"] = val
            elif attr == "validators":
                field_config["validators"] = val
            elif attr == "secure_with":
                field_config["secure_with"] = val
            elif attr == "datakey":
                field_config["datakey"] = val
            elif attr == "blacklist characters":
                field_config["blacklist characters"] = val
            elif attr == "computed input":
                field_config["computed input"] = val
        fields.append(field_config)
    return fields


def regex_validation(idict):
    if "regex" in idict:
        return idict["regex"]


def data_model_creation_file(request, file_predata, filename_extension):
    data_context = {"Data_model": []}
    final_list = []
    unique_table_names = []
    card_config_dict = {}
    card_dict = {}
    is_cardf_present = False
    is_otherCard_flag = False
    # Field Data Info
    valid_field_dict = {
        "AutoField": ["field name", "field data_type", "field header", "nullable?", "unique"],
        "CharField": [
            "field name",
            "field data type",
            "maximum length*",
            "field header",
            "choices",
            "nullable?",
            "unique",
            "secure_with",
            "datakey",
            "blacklist characters",
            "computed input",
        ],
        "ConcatenationField": [
            "field name",
            "field data type",
            "maximum length*",
            "field header",
            "choices",
            "editable?",
            "nullable?",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "BooleanField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "FileField": [
            "field name",
            "field data type",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "VideoField": [
            "field name",
            "field data type",
            "nullable?",
            "field header",
            "columns",
            "divider",
        ],
        "ImageField": [
            "field name",
            "field data type",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
        ],
        "IntegerField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "default",
            "unique",
            "columns",
            "computed value",
            "divider",
            "computed input",
        ],
        "BigIntegerField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "default",
            "unique",
            "columns",
            "computed value",
            "divider",
            "computed input",
        ],
        "DateField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "auto now?",
            "editable?",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "TimeField": [
            "field name",
            "field data type",
            "auto now?",
            "Seconds precision?",
            "editable?",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "DateTimeField": [
            "field name",
            "field data type",
            "auto now?",
            "Seconds precision?",
            "editable?",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
            "computed input",
        ],
        "TextField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "columns",
            "divider",
            "blacklist characters",
            "computed input",
        ],
        "FloatField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "default",
            "unique",
            "columns",
            "divider",
            "computed value",
            "computed input",
        ],
        "ForeignKey": [
            "field name",
            "field data type",
            "field header",
            "parent table",
            "nullable?",
            "default",
            "unique",
            "columns",
            "divider",
        ],
        "PrivacyField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "CardField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "CardCvvField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "CardExpiryField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "CardTypeField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "MultiselectField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "UniqueIDField": [
            "field name",
            "field data type",
            "field header",
            "maximum length*",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "URLField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "DateRangeField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "DateTimeRangeField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "TimeRangeField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "UserField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "EmailTypeField": [
            "field name",
            "field data type",
            "field header",
            "maximum length*",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "TableField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
        "RTFField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "computed value",
            "computed input",
        ],
    }
    data_model_excel = pd.DataFrame()
    if filename_extension == "xlsx":
        excel_data = openpyxl.load_workbook(file_predata, read_only=True)
        data_model_excel = pd.read_excel(excel_data, sheet_name=0, engine="openpyxl")
    elif filename_extension == ".csv":
        data_model_excel = pd.read_csv(file_predata, encoding="unicode_escape")
    if not data_model_excel.empty:
        unique_table_names = data_model_excel.data_table_name.unique()
        for table_name in unique_table_names:
            table_df_og = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Tables",
                        "Columns": ["tablename", "fields"],
                    },
                    "condition": [],
                },
            )
            table_df = table_df_og[table_df_og["tablename"].isin(unique_table_names)]
            if not table_df.empty:
                total_tables_list = table_df["tablename"].tolist()
                data_context = {"Error": ", ".join(total_tables_list) + " already exist in database"}
                return data_context
            else:
                d2 = {}
                data_dict = {table_name: []}
                data_df = data_model_excel[data_model_excel["data_table_name"] == table_name].fillna("")
                for index, row in data_df.iterrows():
                    d1 = {}
                    d2[row["field_name"]] = {}
                    if row["field_data_type"] in valid_field_dict.keys():
                        if row["field_data_type"] == "ForeignKey":
                            if row["parent_table"] not in table_df_og.tablename.tolist():
                                return {
                                    "Error": f"Parent table: {row['parent_table']} is mandatory in ForeignKey"
                                }
                            else:
                                col_df = read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": row["parent_table"],
                                            "Columns": ["*"],
                                        },
                                        "condition": [],
                                    },
                                )
                                if row["field_name"] not in col_df.columns:
                                    return {
                                        "Error": f"Parent table:{row['parent_table']} does not contain field {row['field_name']}."
                                    }
                        else:
                            if row["parent_table"] in table_df_og.tablename.tolist():
                                return {
                                    "Error": f"Field data type is not 'ForeignKey', but parent table: {row['parent_table']} exists in the current database."
                                }

                        for field_config in valid_field_dict[row["field_data_type"]]:
                            data_col = field_config.replace(" ", "_")
                            field_config = field_config.replace("_", " ")
                            if data_col == "maximum_length*":
                                d1["maximum length*"] = row["maximum_length"]
                                d2[row["field_name"]]["maximum length*"] = row["maximum_length"]
                            elif data_col == "computed_value" and row["field_data_type"] in [
                                "IntegerField",
                                "BigIntegerField",
                                "FloatField",
                            ]:
                                d1["computed value"] = "No"
                                d2[row["field_name"]]["computed value"] = "No"
                            elif data_col == "secure_with" and row["field_data_type"] in ["CharField"]:
                                d1["secure_with"] = "No"
                                d2[row["field_name"]]["secure_with"] = "No"
                            elif data_col == "datakey" and row["field_data_type"] in ["CharField"]:
                                d1["datakey"] = ""
                                d2[row["field_name"]]["datakey"] = ""
                            elif data_col == "blacklist_characters" and row["field_data_type"] in [
                                "CharField",
                                "TextField",
                            ]:
                                d1["blacklist characters"] = []
                                d2[row["field_name"]]["blacklist characters"] = []
                            elif data_col == "computed input":
                                d1["computed input"] = []
                                d2[row["field_name"]]["computed input"] = []
                            elif row["field_data_type"] == "ConcatenationField":
                                required_columns = ["columns", "divider"]
                                for col in required_columns:
                                    if not row[col]:
                                        return {
                                            "Error": f"{table_name}: {row['field_name']} - '{col}' is a required field for ConcatenationField."
                                        }
                            else:
                                if row[data_col]:
                                    if data_col in ["nullable?", "unique", "auto_now?", "editable?"]:
                                        if row[data_col] not in ["Yes", "No"]:
                                            return {
                                                "Error": "Columns: ['nullable?','unique','auto_now?', 'editable?'] accepts value in Yes or No."
                                            }
                                    if data_col in [
                                        "choices",
                                        "columns",
                                        "blacklist characters",
                                        "computed input",
                                    ]:
                                        row[data_col] = row[data_col].split(",")
                                    d1[field_config] = row[data_col]
                                    d2[row["field_name"]][field_config] = row[data_col]
                                else:
                                    d1[field_config] = ""
                                    d2[row["field_name"]][field_config] = ""

                        if row["field_data_type"] == "CardField":
                            if "CardField" in card_dict:
                                card_dict["CardField"] += 1
                            else:
                                card_dict["CardField"] = 0
                            is_cardf_present = True

                        if row["field_data_type"] == "CardCvvField":
                            if "CardCvvField" in card_dict:
                                card_dict["CardCvvField"] += 1
                            else:
                                card_dict["CardCvvField"] = 0
                            is_otherCard_flag = True
                            card_config_dict["cvv_field_create"] = True
                            card_config_dict["cvv_field_create_fname"] = row["field_name"]
                            card_config_dict["cvv_field_create_vname"] = row["field_header"]
                            if row["nullable?"] == "" or row["nullable?"] == "No":
                                card_config_dict["cvv_field_create_null"] = "2"
                            else:
                                card_config_dict["cvv_field_create_null"] = "1"
                            card_config_dict["cvv_field_create_enclass"] = "None"
                            card_config_dict["cvv_field_create_kclass"] = ""

                        if row["field_data_type"] == "CardTypeField":
                            if "CardTypeField" in card_dict:
                                card_dict["CardTypeField"] += 1
                            else:
                                card_dict["CardTypeField"] = 0
                            is_otherCard_flag = True
                            card_config_dict["cardtype_field_create"] = True
                            card_config_dict["cardtype_field_create_fname"] = row["field_name"]
                            card_config_dict["cardtype_field_create_vname"] = row["field_header"]
                            if row["nullable?"] == "" or row["nullable?"] == "No":
                                card_config_dict["cardtype_field_create_null"] = "2"
                            else:
                                card_config_dict["cardtype_field_create_null"] = "1"
                            card_config_dict["cardtype_field_create_enclass"] = "None"
                            card_config_dict["cardtype_field_create_kclass"] = ""

                        if row["field_data_type"] == "CardExpiryField":
                            if "CardExpiryField" in card_dict:
                                card_dict["CardExpiryField"] += 1
                            else:
                                card_dict["CardExpiryField"] = 0
                            is_otherCard_flag = True
                            card_config_dict["expiryDate_field_create"] = True
                            card_config_dict["expiryDate_field_create_fname"] = row["field_name"]
                            card_config_dict["expiryDate_field_create_vname"] = row["field_header"]
                            if row["nullable?"] == "" or row["nullable?"] == "No":
                                card_config_dict["expiryDate_field_create_null"] = "2"
                            else:
                                card_config_dict["expiryDate_field_create_null"] = "1"
                            card_config_dict["expiryDate_field_create_enclass"] = "None"
                            card_config_dict["expiryDate_field_create_kclass"] = ""

                    else:
                        return {
                            "Error": f"{table_name}: {row['field_name']} with{row['field_data_type']} not a valid datatype"
                        }
                    data_dict[table_name].append(d1)
                final_list.append(data_dict)
        if is_cardf_present:
            cardf_count = card_dict["CardField"]
            if "CardCvvField" in card_dict:
                if card_dict["CardCvvField"] > cardf_count:
                    return {
                        "Error": "Each CardField can have atmost one CardCvvField. Please check the input and try again."
                    }
            if "CardExpiryField" in card_dict:
                if card_dict["CardExpiryField"] > cardf_count:
                    return {
                        "Error": "Each CardField can have atmost one CardExpiryField. Please check the input and try again."
                    }
            if "CardTypeField" in card_dict:
                if card_dict["CardTypeField"] > cardf_count:
                    return {
                        "Error": "Each CardField can have atmost one CardTypeField. Please check the input and try again."
                    }
            for t in final_list:
                for k, v in t.items():
                    for config in v:
                        if config["field data type"] == "CardField":
                            config["card_config"] = json.dumps(card_config_dict)
                            break
        if is_otherCard_flag and not is_cardf_present:
            return {"Error": "Cannot create CardCvvField, CardExpiryField or CardTypeField without CardField"}
        data_context["Data_model"] = final_list
        return data_context
    else:
        data_context = {"Error": "Uploaded file empty."}
    return data_context


def create_table_query_generator(
    field_name, field_type, field_attr, table_name, db_type="MSSQL", model_type="user defined", db_version=""
):
    field_query_string = ""
    if db_type == "MSSQL":
        if field_attr["nullable?"] == "Yes":
            nullable_string = " NULL "
        else:
            nullable_string = " NOT NULL "
        if field_attr.get("default"):
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
                "DateField",
                "DateTimeField",
                "TimeField",
                "BooleanField",
            ]:
                default_string = (
                    f""" CONSTRAINT DF_{table_name}_{field_name} DEFAULT '{field_attr["default"]}' """
                )
            else:
                default_string = (
                    f""" CONSTRAINT DF_{table_name}_{field_name} DEFAULT {field_attr["default"]} """
                )
        else:
            default_string = ""
        if field_attr.get("unique") == "Yes":
            unique_string = f" CONSTRAINT UQ_{table_name}_{field_name} UNIQUE ({field_name}), "
        else:
            unique_string = ", "
        if field_type == "ForeignKey":
            field_query_string += f"{field_name} INT FOREIGN KEY REFERENCES {field_attr['fieldFKTable']}({field_attr['ref_column']}){nullable_string}{default_string}{unique_string}"
        elif field_type == "AutoField":
            field_query_string += f"{field_name} INT IDENTITY PRIMARY KEY {nullable_string}{default_string}, "
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["maximum length*"])
            field_query_string += (
                f"{field_name} VARCHAR({max_length}) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type in [
            "TextField",
            "URLField",
            "FileField",
            "VideoField",
            "ImageField",
            "PrivacyField",
            "TableField",
            "MultiselectField",
            "BinaryField",
        ]:
            field_query_string += (
                f"{field_name} NVARCHAR(max) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "BooleanField":
            field_query_string += f"{field_name} BIT {nullable_string}{default_string}{unique_string}"
        elif field_type == "IntegerField":
            field_query_string += f"{field_name} INT {nullable_string}{default_string}{unique_string}"
        elif field_type == "BigIntegerField":
            field_query_string += f"{field_name} BIGINT {nullable_string}{default_string}{unique_string}"
        elif field_type == "FloatField":
            field_query_string += f"{field_name} FLOAT {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateField":
            field_query_string += f"{field_name} DATE {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateTimeField":
            field_query_string += f"{field_name} DATETIME {nullable_string}{default_string}{unique_string}"
        elif field_type == "TimeField":
            field_query_string += f"{field_name} TIME {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "DateTimeRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "TimeRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "UserField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        else:
            pass
    elif db_type == "PostgreSQL":
        if field_attr["nullable?"] == "Yes":
            nullable_string = " NULL "
        else:
            nullable_string = " NOT NULL "
        if field_attr.get("default"):
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
            ]:
                default_string = f""" DEFAULT '{field_attr["default"]}' """
            else:
                default_string = f""" DEFAULT {field_attr["default"]} """
        else:
            default_string = ""
        if field_attr.get("unique") == "Yes":
            unique_string = f" CONSTRAINT UQ_{table_name}_{field_name} UNIQUE, "
        else:
            unique_string = ", "
        if field_type == "ForeignKey":
            field_query_string += f"{field_name} INT REFERENCES {field_attr['schema']}.{field_attr['fieldFKTable']}({field_attr['ref_column']}) ON DELETE CASCADE {nullable_string}{default_string}{unique_string}"
        elif field_type == "AutoField":
            if field_attr.get("unique") == "Yes":
                unique_string = " UNIQUE, "
            else:
                pass
            field_query_string += (
                f"{field_name} serial PRIMARY KEY {nullable_string}{default_string}{unique_string}"
            )
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["maximum length*"])
            field_query_string += (
                f"{field_name} varchar({max_length}) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type in [
            "TextField",
            "URLField",
            "FileField",
            "VideoField",
            "ImageField",
            "PrivacyField",
            "TableField",
            "MultiselectField",
            "BinaryField",
        ]:
            field_query_string += f"{field_name} text {nullable_string}{default_string}{unique_string}"
        elif field_type == "BooleanField":
            field_query_string += f"{field_name} bool {nullable_string}{default_string}{unique_string}"
        elif field_type == "IntegerField":
            field_query_string += f"{field_name} integer {nullable_string}{default_string}{unique_string}"
        elif field_type == "BigIntegerField":
            field_query_string += f"{field_name} bigint {nullable_string}{default_string}{unique_string}"
        elif field_type == "FloatField":
            field_query_string += (
                f"{field_name} double precision {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "DateField":
            field_query_string += f"{field_name} date {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateTimeField":
            field_query_string += f"{field_name} timestamp {nullable_string}{default_string}{unique_string}"
        elif field_type == "TimeField":
            field_query_string += f"{field_name} time {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateRangeField":
            field_query_string += (
                f"{field_name} varchar(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "DateTimeRangeField":
            field_query_string += (
                f"{field_name} varchar(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "TimeRangeField":
            field_query_string += (
                f"{field_name} varchar(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "UserField":
            field_query_string += (
                f"{field_name} varchar(100) {nullable_string}{default_string}{unique_string}"
            )
        else:
            pass
    elif db_type == "Oracle":
        if field_attr["nullable?"] == "Yes":
            nullable_string = " NULL "
        else:
            nullable_string = " NOT NULL"
        if field_attr.get("default"):
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
                "DateField",
                "DateTimeField",
                "TimeField",
            ]:
                default_string = f"""DEFAULT '{field_attr["default"]}'"""
            elif field_type == "BooleanField":
                if db_version and db_version.startswith("Oracle Database 23c"):
                    default_string = f""" DEFAULT '{field_attr["default"]}' """
                else:
                    if field_attr["default"]:
                        default_string = f""" DEFAULT 1 """
                    else:
                        default_string = f""" DEFAULT 0 """
            else:
                default_string = f"""DEFAULT {field_attr["default"]}"""
        else:
            default_string = ""
        if field_attr.get("unique") == "Yes":
            unique_string = " UNIQUE,"
        else:
            unique_string = ", "
        if field_type == "ForeignKey":
            field_query_string += f"""{field_name} NUMBER(38) {default_string} REFERENCES {field_attr['fieldFKTable']}({field_attr['ref_column']}) {nullable_string}{unique_string}"""
        elif field_type == "AutoField":
            field_query_string += f"""{field_name} NUMBER(38) GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1) PRIMARY KEY {default_string}{nullable_string}, """
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["maximum length*"])
            field_query_string += (
                f"""{field_name} VARCHAR2({max_length}) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type in ["BinaryField"]:
            field_query_string += f"""{field_name} BLOB {nullable_string}{unique_string}"""
        elif field_type in [
            "TextField",
            "TableField",
            "MultiselectField",
            "URLField",
            "PrivacyField",
            "FileField",
            "VideoField",
            "ImageField",
        ]:
            field_query_string += (
                f"""{field_name} VARCHAR2(4000) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "BooleanField":
            if db_version and db_version.startswith("Oracle Database 23c"):
                field_query_string += (
                    f"""{field_name} BOOLEAN {default_string}{nullable_string}{unique_string}"""
                )
            else:
                field_query_string += (
                    f"""{field_name} NUMBER(1) {default_string}{nullable_string}{unique_string}"""
                )
        elif field_type == "IntegerField":
            field_query_string += (
                f"""{field_name} SMALLINT {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "BigIntegerField":
            field_query_string += f"""{field_name} INTEGER {default_string}{nullable_string}{unique_string}"""
        elif field_type == "FloatField":
            field_query_string += f"""{field_name} FLOAT {default_string}{nullable_string}{unique_string}"""
        elif field_type == "DateField":
            field_query_string += f"""{field_name} DATE {default_string}{nullable_string}{unique_string}"""
        elif field_type == "DateTimeField":
            field_query_string += (
                f"""{field_name} TIMESTAMP(0) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "TimeField":
            if db_version and db_version.startswith("Oracle Database 23c"):
                field_query_string += (
                    f"""{field_name} TIME {default_string}{nullable_string}{unique_string}"""
                )
            else:
                field_query_string += (
                    f"""{field_name} VARCHAR2(20) {default_string}{nullable_string}{unique_string}"""
                )
        elif field_type == "DateRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "DateTimeRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "TimeRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "UserField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        else:
            pass
    else:
        pass
    return field_query_string


def add_field_query_generator(
    field_name,
    field_type,
    field_attr,
    table_name,
    db_type="MSSQL",
    edit=False,
    model_type="user defined",
    db_version="",
    current_field_config={},
):
    field_query_string = ""
    if db_type == "MSSQL":
        if field_attr["fieldNull"] == "Yes":
            nullable_string = " NULL "
        else:
            nullable_string = " NOT NULL "
        if field_attr.get("fieldDefault") and not edit:
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
                "BooleanField",
            ]:
                default_string = f""" DEFAULT '{field_attr["fieldDefault"]}' """
            else:
                default_string = f""" DEFAULT {field_attr["fieldDefault"]} """
        else:
            default_string = ""
        if field_attr.get("fieldUnique") == "Yes" and not edit:
            unique_string = f" CONSTRAINT UQ_{table_name}_{field_name} UNIQUE ({field_name}) "
        else:
            unique_string = " "
        if field_type == "ForeignKey":
            if edit:
                field_query_string += f"{field_name} INT {nullable_string}{default_string}{unique_string}"
            else:
                field_query_string += f"{field_name} INT FOREIGN KEY REFERENCES {field_attr['fieldParentTable']}({field_attr['ref_column']}){nullable_string}{default_string}{unique_string}"
        elif field_type == "AutoField":
            field_query_string += f"{field_name} INT IDENTITY PRIMARY KEY {nullable_string}{default_string}, "
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["fieldMaxLength"])
            field_query_string += (
                f"{field_name} VARCHAR({max_length}) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type in [
            "TextField",
            "URLField",
            "FileField",
            "VideoField",
            "ImageField",
            "PrivacyField",
            "TableField",
            "MultiselectField",
            "BinaryField",
        ]:
            field_query_string += (
                f"{field_name} NVARCHAR(max) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "BooleanField":
            field_query_string += f"{field_name} BIT {nullable_string}{default_string}{unique_string}"
        elif field_type == "IntegerField":
            field_query_string += f"{field_name} INT {nullable_string}{default_string}{unique_string}"
        elif field_type == "BigIntegerField":
            field_query_string += f"{field_name} BIGINT {nullable_string}{default_string}{unique_string}"
        elif field_type == "FloatField":
            field_query_string += f"{field_name} FLOAT {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateField":
            field_query_string += f"{field_name} DATE {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateTimeField":
            field_query_string += f"{field_name} DATETIME {nullable_string}{default_string}{unique_string}"
        elif field_type == "TimeField":
            field_query_string += f"{field_name} TIME {nullable_string}{default_string}{unique_string}"
        elif field_type == "DateRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "DateTimeRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "TimeRangeField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        elif field_type == "UserField":
            field_query_string += (
                f"{field_name} VARCHAR(100) {nullable_string}{default_string}{unique_string}"
            )
        else:
            pass
    elif db_type == "PostgreSQL":
        if field_attr["fieldNull"] == "Yes":
            nullable_string = "NULL "
        else:
            nullable_string = "NOT NULL "
        if field_attr.get("fieldDefault"):
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
            ]:
                default_string = f""" DEFAULT '{field_attr["fieldDefault"]}' """
            else:
                default_string = f""" DEFAULT {field_attr["fieldDefault"]} """
        else:
            default_string = ""
        if field_attr.get("fieldUnique") == "Yes" and not edit:
            unique_string = f" UNIQUE "
        else:
            unique_string = " "
        if edit:
            additional_string = " TYPE "
        else:
            additional_string = ""
        if field_type == "ForeignKey":
            if edit:
                field_query_string += f"{field_name} {additional_string} INT"
            else:
                field_query_string += f"{field_name} INT REFERENCES {field_attr['schema']}.{field_attr['fieldParentTable']}({field_attr['ref_column']}) ON DELETE CASCADE {nullable_string}{default_string}{unique_string}"
        elif field_type == "AutoField":
            if field_attr.get("fieldUnique") == "Yes":
                unique_string = " UNIQUE, "
            else:
                pass
            field_query_string += f"{field_name} serial PRIMARY KEY"
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["fieldMaxLength"])
            field_query_string += f"{field_name} {additional_string} varchar({max_length})"

        elif field_type in [
            "TextField",
            "URLField",
            "FileField",
            "VideoField",
            "ImageField",
            "PrivacyField",
            "TableField",
            "MultiselectField",
            "BinaryField",
        ]:
            field_query_string += f"{field_name} {additional_string} text"
        elif field_type == "BooleanField":
            field_query_string += f"{field_name} {additional_string} bool"
        elif field_type == "IntegerField":
            field_query_string += f"{field_name} {additional_string} integer"
        elif field_type == "BigIntegerField":
            field_query_string += f"{field_name} {additional_string} bigint"
        elif field_type == "FloatField":
            field_query_string += f"{field_name} {additional_string} double precision"
        elif field_type == "DateField":
            field_query_string += f"{field_name} {additional_string} date"
        elif field_type == "DateTimeField":
            field_query_string += f"{field_name} {additional_string} timestamp without time zone"
        elif field_type == "TimeField":
            field_query_string += f"{field_name} {additional_string} time"
        elif field_type == "DateRangeField":
            field_query_string += f"{field_name} {additional_string} varchar(100)"
        elif field_type == "DateTimeRangeField":
            field_query_string += f"{field_name} {additional_string} varchar(100)"
        elif field_type == "TimeRangeField":
            field_query_string += f"{field_name} {additional_string} varchar(100)"
        elif field_type == "UserField":
            field_query_string += f"{field_name} {additional_string} varchar(100)"
        else:
            pass
        if field_type not in ["AutoField"]:
            if edit:
                if nullable_string:
                    if nullable_string == "NOT NULL ":
                        nullable_string = "SET NOT NULL "
                    else:
                        nullable_string = "DROP NOT NULL "
                    field_query_string += f", ALTER COLUMN {field_name} {nullable_string}"
                if default_string:
                    field_query_string += f", ALTER COLUMN {field_name} SET {default_string}"
                if unique_string and unique_string != " ":
                    field_query_string += f", ALTER COLUMN {field_name} {unique_string}"
            else:
                field_query_string += f" {nullable_string}{default_string}{unique_string}"
        else:
            pass
    elif db_type == "Oracle":
        if not edit:
            if field_attr["fieldNull"] == "Yes":
                nullable_string = " NULL "
            else:
                nullable_string = " NOT NULL "
        else:
            if (current_field_config.null and field_attr["fieldNull"] == "Yes") or (
                not current_field_config.null and field_attr["fieldNull"] != "Yes"
            ):
                nullable_string = " "
            elif not current_field_config.null and field_attr["fieldNull"] == "Yes":
                nullable_string = " NULL "
            else:
                nullable_string = " NOT NULL "

        if field_attr.get("fieldDefault") and not edit:
            if field_type in [
                "CharField",
                "TextField",
                "ConcatenationField",
                "HierarchyField",
                "UniqueIDField",
                "URLField",
                "CardField",
                "CardCvvField",
                "CardExpiryField",
                "CardTypeField",
                "EmailTypeField",
                "RTFField",
                "BooleanField",
            ]:
                default_string = f""" DEFAULT '{field_attr["fieldDefault"]}' """
            elif field_type == "BooleanField":
                if db_version and db_version.startswith("Oracle Database 23c"):
                    default_string = f""" DEFAULT {field_attr["fieldDefault"]} """
                else:
                    if field_attr["fieldDefault"]:
                        default_string = f""" DEFAULT 1 """
                    else:
                        default_string = f""" DEFAULT 0 """
            else:
                default_string = f""" DEFAULT {field_attr["fieldDefault"]} """
        else:
            default_string = ""

        if not edit:
            if field_attr.get("fieldUnique") == "Yes":
                unique_string = " UNIQUE "
            else:
                unique_string = " "
        else:
            if not current_field_config.unique and field_attr["fieldUnique"] == "Yes":
                unique_string = " UNIQUE "
            else:
                unique_string = " "

        if field_type == "ForeignKey":
            if edit:
                field_query_string += (
                    f"""{field_name} NUMBER(38) {nullable_string}{default_string}{unique_string}"""
                )
            else:
                field_query_string += f"""{field_name} NUMBER(38) {default_string} REFERENCES USERS_{field_attr['fieldFKTable'].upper()}({field_attr['ref_column']}){nullable_string}{unique_string}"""
        elif field_type == "AutoField":
            field_query_string += f"""{field_name} NUMBER(38) GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1) PRIMARY KEY {nullable_string} """
        elif field_type in [
            "CharField",
            "ConcatenationField",
            "HierarchyField",
            "UniqueIDField",
            "CardField",
            "CardCvvField",
            "CardExpiryField",
            "CardTypeField",
            "EmailTypeField",
            "RTFField",
        ]:
            max_length = int(field_attr["fieldMaxLength"])
            field_query_string += (
                f"""{field_name} VARCHAR2({max_length}) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type in ["BinaryField"]:
            field_query_string += f"""{field_name} BLOB {nullable_string}{unique_string}"""
        elif field_type in [
            "TextField",
            "URLField",
            "PrivacyField",
            "FileField",
            "VideoField",
            "ImageField",
            "TableField",
            "MultiselectField",
        ]:
            field_query_string += (
                f"""{field_name} VARCHAR2(4000) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "BooleanField":
            if db_version and db_version.startswith("Oracle Database 23c"):
                field_query_string += (
                    f"""{field_name} BOOLEAN {default_string}{nullable_string}{unique_string}"""
                )
            else:
                field_query_string += (
                    f"""{field_name} NUMBER(1) {default_string}{nullable_string}{unique_string}"""
                )
        elif field_type == "IntegerField":
            field_query_string += (
                f"""{field_name} SMALLINT {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "BigIntegerField":
            field_query_string += f"""{field_name} INTEGER {default_string}{nullable_string}{unique_string}"""
        elif field_type == "FloatField":
            field_query_string += f"""{field_name} FLOAT {default_string}{nullable_string}{unique_string}"""
        elif field_type == "DateField":
            field_query_string += f"""{field_name} DATE {default_string}{nullable_string}{unique_string}"""
        elif field_type == "DateTimeField":
            field_query_string += (
                f"""{field_name} TIMESTAMP(0) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "TimeField":
            if db_version and db_version.startswith("Oracle Database 23c"):
                field_query_string += (
                    f"""{field_name} TIME {default_string}{nullable_string}{unique_string}"""
                )
            else:
                field_query_string += (
                    f"""{field_name} VARCHAR2(20) {default_string}{nullable_string}{unique_string}"""
                )
        elif field_type == "DateRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "DateTimeRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "TimeRangeField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        elif field_type == "UserField":
            field_query_string += (
                f"""{field_name} VARCHAR2(100) {default_string}{nullable_string}{unique_string}"""
            )
        else:
            pass
    else:
        pass
    return field_query_string
