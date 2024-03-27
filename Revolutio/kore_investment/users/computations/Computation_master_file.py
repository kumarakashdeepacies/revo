from ast import literal_eval
from datetime import datetime, timedelta
import json
import logging
import math
import os
import pickle
import sys
import traceback

import bcpy
from dateutil.relativedelta import relativedelta
import joblib
import matplotlib
import msoffcrypto
import numba
import numpy as np
import openpyxl
import pandas as pd
import paramiko
import pyodbc
import pyxirr
import reportlab
import requests
import scipy
import sklearn
import statsmodels
import turbodbc
import workdays
import xlrd
import xlsxwriter

from config.settings.base import redis_instance

## Cache
from kore_investment.users.computation_studio_lib import (
    TWRR,
    Apply_Math_Operations,
    Comp_Column_Mapping,
    Compatibility_Functions,
    Copula,
    Correlation_Functions,
    Curve_Data_Bootstrapping,
    Data_Pre_Processing,
    Data_Transformation,
    Decision_Tree,
    Elementary_Statistics,
    ExportData,
    Financial_Functions,
    FitDiscreteDistribution,
    Import_Data,
    Linear_Regression,
    Logistic_Regression,
    MonteCarlo,
    OIS_Bootstrapping,
    Optimisation,
    Options_Pricing,
    Portfolio_Allocation,
    Portfolio_Attribution,
    Portfolio_Valuation,
    PortfolioMetrics,
    Single_Curve_Bootstrapping,
    Swap_Curve,
    TextFunctions,
    Time_Periods,
    Time_Series,
    Validation_check,
    Valuation_Models,
    VaR_Backtesting,
)
from kore_investment.users.computation_studio_lib.Boosting_Algorithm import AdaBoost, CatBoost, XGBoost
from kore_investment.users.computation_studio_lib.GoodnessFitTest import ContinousCurve
from kore_investment.users.computations import Data_replica_utilities, standardised_functions
from kore_investment.users.computations.db_centralised_function import (
    app_engine_generator,
    data_handling,
    delete_data_func,
    read_data_func,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.computations.dynamic_model_create import (
    create_table_dict_creator,
    create_table_sql,
    get_model_class,
)
from kore_investment.users.computations.file_storage import (
    computation_storage,
    file_storage_checker,
    read_computation_from_storage,
    read_diskstorage,
)

system_config_tables = [
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
    "user_model",
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
    "alertslog",
    "static_page_config",
    "audit_operation",
    "ProcessScheduler",
    "smtp_configuration",
    "event_master",
]


def save_interim_model_outputs(
    source, table_name, data, request_user, scenario_name, scenario_id, chunksize=10**5
):
    table_name = table_name.replace(" ", "_")
    data = data_type_convertor(data)
    if not isinstance(data, str):
        if scenario_name is None:
            if source == "existing_table":
                modelName = get_model_class(table_name, request_user)

                table_field_names = {
                    field.name: field.get_internal_type()
                    for field in modelName.concrete_fields
                    if field.get_internal_type() not in ["AutoField"]
                    if not field.primary_key
                }
                nullable_field_names = [field.name for field in modelName.concrete_fields if field.null]
                flist = {field.verbose_name.title(): field.name for field in modelName.concrete_fields}
                data.rename(columns=flist, inplace=True)
                flist = {field.verbose_name: field.name for field in modelName.concrete_fields}
                data.rename(columns=flist, inplace=True)
                if not isinstance(data, str):
                    if "created_by" in table_field_names.keys():
                        data["created_by"] = request_user.user.username
                        data["created_date"] = datetime.now()
                        data["modified_by"] = request_user.user.username
                        data["modified_date"] = datetime.now()
                    if "active_from" in table_field_names.keys():
                        data["active_from"] = datetime.now()
                    if "active_to" in table_field_names.keys():
                        data["active_to"] = datetime.now() + relativedelta(years=100)

                    f_data = standardised_functions.data_preprocessing(
                        data,
                        table_name,
                        request_user,
                        customvalidation={},
                        message_show="no",
                        user_operation="create",
                    )
                    FinalData_val = f_data.data_validation(message_out=False)

                    if isinstance(FinalData_val, list):
                        return f"Failed to export data to {table_name} table as following validations failed - {FinalData_val[0][0]['error_description'].replace('Error while uploading:','')}"
                    elif isinstance(FinalData_val, pd.DataFrame):
                        FinalData_val = FinalData_val[
                            [i for i in FinalData_val.columns if i in table_field_names]
                        ]
                        data_handling(request_user, FinalData_val, table_name, chunksize=chunksize)
                        multi_select_field_dict = {}
                        is_multi_select_field = False
                        for field in modelName.concrete_fields:
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
                            table_name_replica = table_name.lower()
                            multi_select_tables = multi_select_field_dict["value"]
                            mutli_select_cols = multi_select_field_dict["masterColumn"]
                            mutli_select_attr = multi_select_field_dict["master"]

                            replica = read_data_func(
                                request_user,
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
                                    request_user,
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
                                                "input_value": table_name_replica + "_mul",
                                                "and_or": "",
                                            },
                                        ],
                                    },
                                )
                                if len(mt) > 0:
                                    records = len(FinalData_val)
                                    recent_record_ids = read_data_func(
                                        request_user,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": table_name_replica,
                                                "Agg_Type": f"TOP({records})",
                                                "Order_Type": "ORDER BY id DESC",
                                                "Columns": ["id"],
                                            },
                                            "condition": [],
                                        },
                                    )["id"].tolist()
                                    FinalData_val["id"] = recent_record_ids

                                    Data_replica_utilities.insert_delimited_data(
                                        elementID="",
                                        request=request_user,
                                        table_name_replica=table_name_replica,
                                        multi_select_tables=multi_select_tables,
                                        mutli_select_cols=mutli_select_cols,
                                        mutli_select_attr=mutli_select_attr,
                                        existingData=FinalData_val,
                                    )
                                else:
                                    pass
                        else:
                            pass
                        return f"Data exported to {table_name} table successfully"
                else:
                    return data
            elif source == "create_table":
                tables_df = read_data_func(
                    request_user,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Tables",
                            "Columns": ["tablename", "model_type"],
                        },
                        "condition": [],
                    },
                )
                if table_name in tables_df.tablename.tolist():
                    modelName = get_model_class(table_name, request_user)
                    table_field_names = {
                        field.name: field.get_internal_type()
                        for field in modelName.concrete_fields
                        if field.get_internal_type() not in ["AutoField"]
                        if not field.primary_key
                    }
                    nullable_field_names = [field.name for field in modelName.concrete_fields if field.null]
                    flist = {field.verbose_name.title(): field.name for field in modelName.concrete_fields}
                    data.rename(columns=flist, inplace=True)
                    flist = {field.verbose_name: field.name for field in modelName.concrete_fields}
                    data.rename(columns=flist, inplace=True)
                    final_data = table_format_validator(
                        data,
                        fields=table_field_names,
                        nullable_fields=nullable_field_names,
                        table_name=table_name,
                    )
                    if not isinstance(final_data, str):
                        if "created_by" in table_field_names.keys():
                            final_data["created_by"] = request_user.user.username
                            final_data["created_date"] = datetime.now()
                            final_data["modified_by"] = request_user.user.username
                            final_data["modified_date"] = datetime.now()
                        if "active_from" in table_field_names.keys():
                            final_data["active_from"] = datetime.now()
                        if "active_to" in table_field_names.keys():
                            final_data["active_to"] = datetime.now() + relativedelta(years=100)

                        data_val = final_data.copy()
                        f_data = standardised_functions.data_preprocessing(
                            data_val,
                            table_name,
                            request_user,
                            customvalidation={},
                            message_show="no",
                            user_operation="create",
                        )
                        FinalData_val = f_data.data_validation(message_out=False)

                        if isinstance(FinalData_val, list):
                            return f"Failed to export data to {table_name} table as following validations failed - {FinalData_val[0][0]['error_description'].replace('Error while uploading:','')}"
                        elif isinstance(FinalData_val, pd.DataFrame):
                            data_handling(request_user, final_data, table_name, chunksize=chunksize)
                            return f"Data exported to {table_name} table successfully"
                    else:
                        return final_data
                else:
                    data_field_type = data.dtypes.apply(lambda x: x.name).to_dict()
                    model_fields = [
                        {
                            "field name": "id",
                            "field header": "Id",
                            "field data type": "AutoField",
                            "nullable?": "No",
                            "unique": "Yes",
                            "validators": [],
                            "primary_key": 1,
                        }
                    ]
                    for col_name, col_type in data_field_type.items():
                        data.rename(
                            columns={col_name: col_name.replace(" ", "_").lower().strip(" ")}, inplace=True
                        )
                        col_name = col_name.replace(" ", "_").lower().strip(" ")
                        field_config = {
                            "field name": col_name,
                            "field header": col_name.replace("_", " ").title(),
                            "field data type": "TextField",
                            "nullable?": "Yes",
                            "unique": "No",
                            "validators": [],
                            "editable?": "Yes",
                        }
                        if col_type == "object":
                            field_config["field data type"] = "TextField"
                        elif col_type == "datetime64[ns]":
                            field_config["field data type"] = "DateTimeField"
                            field_config["auto now?"] = "No"
                        elif col_type == "int32":
                            field_config["field data type"] = "IntegerField"
                        elif col_type == "int64":
                            field_config["field data type"] = "BigIntegerField"
                        elif col_type == "float64":
                            field_config["field data type"] = "FloatField"
                        elif col_type == "bool":
                            field_config["field data type"] = "BooleanField"
                        else:
                            pass
                        model_fields.append(field_config)

                    create_table_sql(table_name, model_fields, request_user)
                    data["created_by"] = request_user.user.username
                    data["created_date"] = datetime.now()
                    data["modified_by"] = request_user.user.username
                    data["modified_date"] = datetime.now()
                    data["active_from"] = datetime.now()
                    data["active_to"] = datetime.now() + relativedelta(years=100)
                    data_handling(request_user, data, table_name, chunksize=chunksize)
                    return f"Data exported to {table_name} table successfully"
        else:
            base_table_name = table_name
            sql_data = data.copy()
            sc_output_table_name = base_table_name + "_scenario_output"
            sql_data["scenario_id"] = scenario_id
            sql_data["created_by"] = request_user.user.username
            sql_data["created_date"] = datetime.now()
            sql_data["modified_by"] = request_user.user.username
            sql_data["modified_date"] = datetime.now()
            sc_table_check = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Tables",
                        "Columns": ["id"],
                    },
                    "condition": [
                        {
                            "column_name": "tablename",
                            "condition": "Equal to",
                            "input_value": sc_output_table_name,
                            "and_or": "",
                        },
                    ],
                },
            )
            if not sc_table_check.empty:
                # push data to the scenario table
                if isinstance(sql_data, pd.DataFrame):
                    model_class = get_model_class(sc_output_table_name, request_user)
                    fk_columns = {
                        field.name: field
                        for field in model_class.concrete_fields
                        if field.internal_type == "ForeignKey"
                    }
                    flist = {field.verbose_name.title(): field.name for field in model_class.concrete_fields}
                    sql_data.rename(columns=flist, inplace=True)
                    flist = {field.verbose_name: field.name for field in model_class.concrete_fields}
                    sql_data.rename(columns=flist, inplace=True)
                    for f_col in fk_columns:
                        if f_col in sql_data.columns:
                            fk_parent_table = fk_columns[f_col].parent
                            model_class_parent = get_model_class(fk_parent_table, request_user)
                            raw_data = read_data_func(
                                request_user,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": fk_parent_table,
                                        "Columns": [model_class_parent.pk.name, f_col],
                                    },
                                    "condition": [],
                                },
                            )
                            fk_data_mapper = raw_data.set_index(f_col)[model_class_parent.pk.name].to_dict()
                            sql_data[f_col] = sql_data[f_col].replace(to_replace=fk_data_mapper)
                    data_handling(
                        request_user,
                        sql_data,
                        sc_output_table_name,
                        chunksize=chunksize,
                    )
            else:
                # Create scenario table
                base_table_structure = read_data_func(
                    request_user,
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
                                "input_value": base_table_name,
                                "and_or": "",
                            },
                        ],
                    },
                )
                if not base_table_structure.empty:
                    base_table_structure = json.loads(base_table_structure.fields.iloc[0])
                    base_table_structure = {
                        k: v
                        for k, v in base_table_structure.items()
                        if k
                        not in [
                            "created_by",
                            "created_date",
                            "modified_by",
                            "modified_date",
                            "active_to",
                            "active_from",
                            "approved_by",
                            "approval_status",
                            "transaction_id",
                            "is_active_flag",
                        ]
                    }
                    base_table_structure["scenario_id"] = {
                        "internal_type": "CharField",
                        "verbose_name": "Scenario id",
                        "null": True,
                        "unique": False,
                        "validators": [],
                        "max_length": 255,
                    }
                    sc_table_fields = create_table_dict_creator(base_table_structure)
                    create_table_sql(sc_output_table_name, sc_table_fields, request_user)
                    # push data to the scenario output table
                    if isinstance(sql_data, pd.DataFrame):
                        model_class = get_model_class(sc_output_table_name, request_user)
                        fk_columns = {
                            field.name: field
                            for field in model_class.concrete_fields
                            if field.internal_type == "ForeignKey"
                        }
                        flist = {
                            field.verbose_name.title(): field.name for field in model_class.concrete_fields
                        }
                        sql_data.rename(columns=flist, inplace=True)
                        flist = {field.verbose_name: field.name for field in modelName.concrete_fields}
                        sql_data.rename(columns=flist, inplace=True)
                        for f_col in fk_columns:
                            if f_col in sql_data.columns:
                                fk_parent_table = fk_columns[f_col].parent
                                model_class_parent = get_model_class(fk_parent_table, request_user)
                                raw_data = read_data_func(
                                    request_user,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": fk_parent_table,
                                            "Columns": [
                                                model_class_parent.pk.name,
                                                f_col,
                                            ],
                                        },
                                        "condition": [],
                                    },
                                )
                                fk_data_mapper = raw_data.set_index(f_col)[
                                    model_class_parent.pk.name
                                ].to_dict()
                                sql_data[f_col] = sql_data[f_col].replace(to_replace=fk_data_mapper)
                        data_handling(
                            request_user,
                            sql_data,
                            sc_output_table_name,
                            chunksize=chunksize,
                        )
    else:
        data += f"Error! Failed to export data to {table_name}"
        return data


def fillNa(data, object_fill="None", num_fill=0, date_fill="2000-01-01"):
    columns_list = data.columns.tolist()
    field_type = data.dtypes.apply(lambda x: x.name).to_dict()
    for col_name in columns_list:
        if field_type[col_name] == "object":
            data[col_name] = data[col_name].fillna(object_fill)
        elif field_type[col_name] in ["int64", "float64"]:
            data[col_name] = data[col_name].fillna(num_fill)
        elif field_type[col_name] in ["datetime64[ns]"]:
            data[col_name] = data[col_name].fillna(pd.to_datetime(date_fill))
        else:
            data[col_name] = data[col_name].fillna(object_fill)
    return data


def table_format_validator(
    data,
    fields,
    nullable_fields,
    table_name,
    auto_fields=[
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
        "approval_status",
        "approved_by",
        "active_to",
        "active_from",
    ],
):
    data_field_type = data.dtypes.apply(lambda x: x.name).to_dict()
    field_type_mapper = {
        "CharField": "object",
        "TextField": "object",
        "HierarchyField": "object",
        "EmailTypeField": "object",
        "ForeignKey": "object",
        "ConcatenationField": "object",
        "DateField": "datetime64[ns]",
        "DateTimeField": "datetime64[ns]",
        "TimeField": "datetime64[ns]",
        "IntegerField": "int32",
        "BigIntegerField": "int64",
        "FloatField": "float64",
        "BooleanField": "bool",
    }
    mandatory_fields = [field for field in fields.keys() if field not in nullable_fields]
    editable_fields = [field for field in fields.keys() if field not in auto_fields]

    for col in editable_fields:
        if col not in data.columns.tolist() and col in mandatory_fields:
            return f"{col} is a mandatory field. Cant push data to this table"
        else:
            if col in data.columns.tolist():
                field_type = fields[col]
                if field_type_mapper[field_type] != data_field_type[col]:
                    try:
                        data[col] = data[col].astype(field_type_mapper[field_type])
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        return f"{col} is a mandatory field. Failed to export data to {table_name}!"
    return data


def data_type_convertor(data):
    if isinstance(data, (dict, list)):
        new_data = pd.DataFrame(data)
        return new_data
    elif isinstance(data, pd.DataFrame):
        return data
    else:
        return "Data is of unknown type"


def data_formatter(data, round_conv=4):
    float_cols = data.select_dtypes(include=["float64"]).columns.tolist()
    date_cols = data.select_dtypes(include=["datetime64[ns]"]).columns.tolist()
    for i in float_cols:
        data[i] = round(data[i], round_conv)
    for j in date_cols:
        data[j] = pd.to_datetime(data[j]).dt.strftime("%Y-%m-%d %H:%M:%S")
    return data


# Central compute fucntion for different utilities
def master_run_process(
    config_dict={},
    request_user=None,
    data=None,
    pred_data=None,
    elementid=None,
    element_id="",
    scenario_name=None,
    scenario_id=None,
    scenario_config=None,
    run_model=True,
    previous_data=False,
    default="no",
    multi_import=False,
    multi_import_val={},
    transaction_id="NULL",
    run_step=False,
    upload_then_compute=False,
):
    if isinstance(request_user, dict):

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

        request_user["user"] = AttrDict(request_user["user"])
        request_user = AttrDict(request_user)

    data_error = ""

    func_name = config_dict["function"]
    result_save_list = []

    if bool(data):
        if isinstance(data, list):
            for idx, f_name in enumerate(data):
                if isinstance(f_name, str) and file_storage_checker(f_name):
                    data[idx] = read_computation_from_storage(f_name)
                else:
                    continue
        elif isinstance(data, dict):
            for f_key, f_name in data.items():
                if isinstance(f_name, str) and file_storage_checker(f_name):
                    data[f_key] = read_computation_from_storage(f_name)
                else:
                    continue
        if len(data) == 1 and not isinstance(data, dict):
            data = data[0]
        else:
            pass
    else:
        data = None

    saved_parent_val = read_data_func(
        request_user,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "computation_model_configuration",
                "Columns": ["element_config"],
            },
            "condition": [
                {
                    "column_name": "element_id",
                    "condition": "Equal to",
                    "input_value": elementid + "_multi_import_val",
                    "and_or": "",
                },
            ],
        },
    )

    if len(saved_parent_val) > 0:
        elecon_dict = saved_parent_val.iloc[0, 0]
        par_val = json.loads(elecon_dict)
        multi_import_val = par_val
    else:
        multi_import_val = {}

    if multi_import_val:
        if isinstance(data, list):
            vals = multi_import_val.values()
            data = [data[i] for i in vals]
            if len(data) == 1:
                data = data[0]

    data, data_error = data_validation_check(func_name, data)
    if len(data_error):
        if func_name == "Portfolio Valuation" and run_model:
            return "", "", "", "", data_error
        else:
            return "", "", "", data_error
    if config_dict["inputs"].get("current_table"):
        curr_table = config_dict["inputs"]["current_table"]
    else:
        curr_table = "No"
    if config_dict["inputs"].get("current_table_flow"):
        curr_table_flow = config_dict["inputs"]["current_table_flow"]
    else:
        curr_table_flow = "No"

    message = ""
    if func_name == "Import Data":
        data_source = config_dict["inputs"]["Data_source"]
        if data_source in ["CSV", "JSON", "Parquet", "Redis", "XML"]:
            output_data = data
        elif data_source in ["SFTP", "FTP", "AWS_S3", "AZURE", "LOCAL"]:
            output_data = data
        elif data_source == "Database" and curr_table == "Yes":
            output_data = data
        elif data_source == "Database" and default == "yes":
            output_data = data
        elif data_source == "Database" and upload_then_compute:
            output_data = data
        elif data_source == "Database" and curr_table_flow == "Yes" and not previous_data:
            output_data = data
        elif data_source == "Model_output":
            selected_model = config_dict["inputs"]["model_selected"]
            current_global_dict = config_dict["current_global_dict"]

            selected_model_flowchart_elements = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "computation_model_flowchart",
                        "Columns": ["flowchart_elements"],
                    },
                    "condition": [
                        {
                            "column_name": "model_name",
                            "condition": "Equal to",
                            "input_value": selected_model,
                            "and_or": "",
                        },
                    ],
                },
            )
            # scenario
            scenario_element_check = False
            if scenario_name:
                if scenario_config and scenario_id:
                    model_element_ids = [
                        i["element_id"] for i in json.loads(selected_model_flowchart_elements.iloc[0, 0])
                    ]
                    for scn_co in scenario_config:
                        if scn_co["element_id"] in model_element_ids:
                            scenario_element_check = True
                            break
                else:
                    scenario_element_check = True
            output_imported = True
            import_output = False
            if not scenario_element_check:
                if config_dict["inputs"].get("import_output"):
                    import_output = config_dict["inputs"]["import_output"]
                if import_output:
                    modelOutputTable = config_dict["inputs"]["modelOutputTable"]
                    modelOutputColumn = config_dict["inputs"]["modelOutputColumn"]
                    condition = config_dict["inputs"]["condition"]
                    model_import_config = {
                        "data_mapper": {},
                        "inputs": {
                            "Data_source": "Database",
                            "Table": modelOutputTable,
                            "Columns": modelOutputColumn,
                        },
                        "condition": condition,
                    }
                    for cond in condition:
                        if cond["globalVariable"] != "":
                            for cu_var in current_global_dict:
                                if cu_var["varName"] == cond["globalVariable"]:
                                    if "defaultValue" in cu_var.keys():
                                        cond["input_value"] = cu_var["defaultValue"]
                                    if "inputValue" in cu_var.keys():
                                        cond["input_value"] = cu_var["inputValue"]
                    model_import_config["condition"] = condition

                    output_data = Import_Data.import_run_step(
                        model_import_config, request_user
                    )
                    if output_data.empty:
                        output_imported = False
            if not import_output or (import_output and not output_imported):
                model_output_selected = config_dict["inputs"]["model_output_selected"]
                model_gvar_map = config_dict["inputs"]["model_gvar_map"]
                current_run = config_dict["current_run"]
                output_data = {}
                if selected_model and model_output_selected:
                    existing_model_outputs = read_data_func(
                        request_user,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_output_repository",
                                "Columns": ["model_outputs"],
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": selected_model,
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    if not existing_model_outputs.empty:
                        existing_outputs2 = existing_model_outputs.model_outputs.iloc[0]
                        if existing_outputs2:
                            existing_outputs2 = json.loads(existing_outputs2)
                            if existing_outputs2.get(model_output_selected):
                                selected_output_details = existing_outputs2.get(model_output_selected)
                                last_run_element_id = selected_output_details["element_id"]
                                if not selected_model_flowchart_elements.empty:
                                    selected_model_flowchart_elements = (
                                        selected_model_flowchart_elements.iloc[0, 0]
                                    )
                                    selected_model_flowchart_elements = json.loads(
                                        selected_model_flowchart_elements
                                    )
                                    selected_model_global_config = read_data_func(
                                        request_user,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "computation_model_configuration",
                                                "Columns": ["element_id", "element_config"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "model_name",
                                                    "condition": "Equal to",
                                                    "input_value": selected_model,
                                                    "and_or": "and",
                                                },
                                                {
                                                    "column_name": "element_id",
                                                    "condition": "Contains",
                                                    "input_value": "globalVariable",
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )

                                    if len(selected_model_global_config) > 0:
                                        global_element_id = selected_model_global_config.element_id.iloc[0]
                                        selected_model_global_dict = (
                                            selected_model_global_config.element_config.iloc[0]
                                        )
                                        selected_model_global_dict = json.loads(selected_model_global_dict)
                                        selected_moddel_variableList = selected_model_global_dict["inputs"][
                                            "variables"
                                        ]
                                        for i in selected_moddel_variableList:
                                            if i["varName"] in model_gvar_map:
                                                mapped_var = model_gvar_map[i["varName"]]
                                                for cu_var in current_global_dict:
                                                    if cu_var["varName"] == mapped_var:
                                                        if "defaultValue" in cu_var.keys():
                                                            i["defaultValue"] = cu_var["defaultValue"]
                                                        if "inputValue" in cu_var.keys():
                                                            i["defaultValue"] = cu_var["inputValue"]
                                        selected_model_global_dict["inputs"][
                                            "variables"
                                        ] = selected_moddel_variableList
                                    else:
                                        global_element_id = "#"
                                        selected_model_global_dict = {"inputs": {}}
                                    output_data = standardised_functions.run_process_model_run_handler(
                                        request_user,
                                        selected_model_flowchart_elements,
                                        selected_model,
                                        selected_model_global_dict,
                                        global_element_id,
                                        last_run_element=last_run_element_id,
                                        run=current_run,
                                        scenario_name=scenario_name,
                                        scenario_id=scenario_id,
                                        scenario_config=scenario_config,
                                    )
                                    if selected_output_details["element_output_type"] == "multiple":
                                        output_multi_key_name = selected_output_details["multi-name"]
                                        if isinstance(output_data, dict):
                                            if output_multi_key_name in output_data.keys():
                                                output_data = pd.DataFrame(output_data[output_multi_key_name])
                                    else:
                                        if isinstance(output_data, (dict, list)):
                                            output_data = pd.DataFrame(output_data)
                                        else:
                                            output_data = output_data.copy()
        elif data_source == "API":
            api_name = config_dict["inputs"]["api_name"]
            if os.path.exists("api.json"):
                f = open("api.json")
                f_code = f.read()
                convertedDict = json.loads(f_code)
                f.close()

                return_val = convertedDict[api_name]["value"]
                url = convertedDict[api_name]["url"]
                res = requests.get(url)
                response = res.json()
                response
                output_data = literal_eval(return_val)
                if isinstance(output_data, dict):
                    output_data = [output_data]
                elif isinstance(output_data, (str, float, int, bool)):
                    output_data = [{return_val.split("[")[-1].replace("]", "").strip("'"): output_data}]
                try:
                    output_data = pd.DataFrame(output_data)
                    if 0 in output_data.columns.tolist():
                        output_data.rename(
                            columns={0: return_val.split("[")[-1].replace("]", "").strip("'")}, inplace=True
                        )
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    df = pd.DataFrame(columns=[return_val.split("[")[-1].replace("]", "")])
                    df[return_val.split("[")[-1].replace("]", "")] = output_data
                    output_data = df.copy()
            else:
                output_data = []
        else:
            dic = config_dict.copy()

            if config_dict["inputs"].get("connection_type"):
                connection_type = config_dict["inputs"]["connection_type"]
            else:
                connection_type = "default_connection"

            if connection_type == "default_connection":
                if config_dict["inputs"]["Table"] not in system_config_tables:
                    if config_dict["inputs"].get("verbose_name_checkbox"):
                        if config_dict["inputs"]["verbose_name_checkbox"]:
                            trans_col = "Transaction_Id"
                        else:
                            trans_col = "transaction_id"
                    else:
                        trans_col = "transaction_id"
                    if trans_col not in dic["inputs"]["Columns"]:
                        dic["inputs"]["Columns"].append(trans_col)
                else:
                    pass
                redis_data1 = Import_Data.import_run_step(
                    config_dict=config_dict, request=request_user, if_app_db=True
                )
                table = config_dict["inputs"]["Table"]
                if config_dict["inputs"]["Table"] not in system_config_tables:
                    output_data = redis_data1.drop(columns=[trans_col], errors="ignore")
                    if run_model:
                        if not redis_instance.exists("data_present_intransac"):
                            redis_instance.set("data_present_intransac", pickle.dumps({}))
                        standardised_functions.checkLatestData(
                            redis_data1, element_id, table, request_user, element="computation"
                        )
                else:
                    output_data = redis_data1.copy()
                del redis_data1
            else:
                output_data = Import_Data.import_run_step(
                    config_dict=config_dict, request=request_user, if_app_db=False
                )

        if scenario_name:
            if scenario_config and scenario_id:
                for scn_config in scenario_config:
                    if scn_config["element_id"] == elementid:
                        scenario_table_name = scn_config["scenario_table_name"]
                        scenario_data_type = scn_config["scenario_data_type"]
                        scenario_type = scn_config["scenario_type"]
                        if scenario_data_type == "upload_data":
                            scenario_table_config = config_dict.copy()
                            if scenario_table_config["inputs"]["Data_source"] == "Model_output":
                                actual_model_name = get_model_class(scenario_table_name, request_user)
                                audit_fields = [
                                    "created_by",
                                    "modified_by",
                                    "created_date",
                                    "modified_date",
                                    "active_to",
                                    "active_from",
                                    "approved_by",
                                    "approval_status",
                                    "transaction_id",
                                    "is_active_flag",
                                    actual_model_name.pk.name,
                                ]
                                columns_list = [
                                    field.name
                                    for field in actual_model_name.concrete_fields
                                    if field.name not in audit_fields
                                ]
                                scenario_table_config["inputs"]["Columns"] = columns_list
                                scenario_table_config["data_mapper"] = {}
                            scenario_table_config["inputs"]["Table"] = scenario_table_name
                            scenario_table_config["condition"] = [
                                {
                                    "column_name": "scenario_id",
                                    "condition": "Equal to",
                                    "input_value": scenario_id + "_" + scn_config["element_id"],
                                    "and_or": "",
                                },
                            ]
                            element_scenario_data = Import_Data.import_run_step(
                                scenario_table_config, request_user
                            )
                        else:
                            if scn_config.get("base_model_name"):
                                b_model_name = scn_config["base_model_name"]
                            else:
                                b_model_name = ""
                            global_config = read_data_func(
                                request_user,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "computation_model_configuration",
                                        "Columns": ["element_config", "element_id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "model_name",
                                            "condition": "Equal to",
                                            "input_value": b_model_name,
                                            "and_or": "and",
                                        },
                                        {
                                            "column_name": "element_id",
                                            "condition": "Contains",
                                            "input_value": "globalVariable",
                                            "and_or": "",
                                        },
                                    ],
                                },
                            )
                            if len(global_config) > 0:
                                global_dict = global_config.element_config.iloc[-1]
                                global_dict = json.loads(global_dict)
                            else:
                                global_dict = {}
                            if config_dict.get("scenario_global_dict"):
                                variable_list = config_dict["scenario_global_dict"]
                            else:
                                variable_list = []
                            if len(global_dict) > 0:
                                condition_list = global_dict["inputs"]["variables"]
                            else:
                                condition_list = []

                            if (
                                config_dict["function"] == "Import Data"
                                and config_dict["condition"] != []
                                and config_dict["inputs"]["Data_source"] in ["Database", "Model_output"]
                            ):
                                for cond in condition_list:
                                    for g in variable_list:
                                        if cond["varName"] == g["varName"]:
                                            cond["defaultValue"] = g["inputValue"]

                            if global_dict.get("inputs") not in [None]:
                                global_dict["inputs"]["variables"] = condition_list

                            equation_editor_model = scn_config["equation_editor_model"]
                            scn_flowchart_elements = read_data_func(
                                request_user,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "computation_model_flowchart",
                                        "Columns": ["flowchart_elements"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "model_name",
                                            "condition": "Equal to",
                                            "input_value": equation_editor_model,
                                            "and_or": "",
                                        },
                                    ],
                                },
                            ).iloc[0, 0]
                            scn_flowchart_elements = json.loads(scn_flowchart_elements)
                            ind_run_output = standardised_functions.run_process_model_run_handler(
                                request_user,
                                scn_flowchart_elements,
                                equation_editor_model,
                                global_dict,
                                "",
                            )
                            element_scenario_data = pd.DataFrame(ind_run_output["content"])
                            del ind_run_output

                        actmodelName = get_model_class(scenario_table_name, request_user)
                        field_list = {
                            field.name: field.verbose_name.title() for field in actmodelName.concrete_fields
                        }
                        if scenario_type == "append":
                            try:
                                field_type = output_data.dtypes.apply(lambda x: x.name).to_dict()
                                if (
                                    len(
                                        list(
                                            set(output_data.columns.tolist()).intersection(
                                                element_scenario_data.columns.tolist()
                                            )
                                        )
                                    )
                                    == 0
                                ):
                                    element_scenario_data.rename(columns=field_list, inplace=True)
                                for col in element_scenario_data.columns.tolist():
                                    if col in field_type:
                                        element_scenario_data[col] = element_scenario_data[col].astype(
                                            field_type[col], errors="ignore"
                                        )
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                data_error = f"Data validation error! {str(e)}"
                            output_data = pd.concat([output_data, element_scenario_data], ignore_index=True)
                        else:
                            if "replace_identifier_list" in scn_config.keys():
                                replace_identifier_list = scn_config["replace_identifier_list"]
                                replace_column_list = scn_config["replace_column_list"]
                            else:
                                replace_identifier_list = []
                                replace_column_list = []
                            if len(replace_identifier_list) > 0 and len(replace_column_list) > 0:
                                output_data_types = output_data.dtypes.apply(lambda x: x.name).to_dict()
                                for i in range(0, len(element_scenario_data)):
                                    row_data = element_scenario_data.iloc[i]
                                    condition_string = ""
                                    for id_index, id_col in enumerate(replace_identifier_list):
                                        try:
                                            if output_data_types[id_col] in ["datetime64[ns]"]:
                                                row_data[id_col] = pd.to_datetime(
                                                    row_data[id_col]
                                                )
                                            elif output_data_types[id_col] in ["object"]:
                                                row_data[id_col] = str(row_data[id_col])
                                            condition_string += (
                                                f"(output_data['{id_col}'] == '{row_data[id_col]}')"
                                            )
                                        except Exception as e:
                                            logging.warning(f"Following exception occured - {e}")
                                            if output_data_types[field_list[id_col]] in ["datetime64[ns]"]:
                                                row_data[field_list[id_col]] = pd.to_datetime(
                                                    row_data[field_list[id_col]]
                                                )
                                            elif output_data_types[field_list[id_col]] in ["object"]:
                                                row_data[field_list[id_col]] = str(
                                                    row_data[field_list[id_col]]
                                                )
                                            condition_string += f"(output_data['{field_list[id_col]}'] == '{row_data[field_list[id_col]]}')"
                                        if len(replace_identifier_list) > 0 and (
                                            id_index != (len(replace_identifier_list) - 1)
                                        ):
                                            condition_string += " & "
                                    for up_col in replace_column_list:
                                        try:
                                            output_data.loc[pd.eval(condition_string), up_col] = row_data[
                                                up_col
                                            ]
                                        except Exception as e:
                                            logging.warning(f"Following exception occured - {e}")
                                            output_data.loc[pd.eval(condition_string), field_list[up_col]] = (
                                                row_data[field_list[up_col]]
                                            )
                            else:
                                output_data = element_scenario_data.copy()
                                output_data.rename(columns=field_list, inplace=True)
                        del element_scenario_data
            else:
                if redis_instance.exists(scenario_name + elementid) == 1:
                    element_scenario_data = pickle.loads(redis_instance.get(scenario_name + elementid))
                    scenario_type = pickle.loads(
                        redis_instance.get(scenario_name + elementid + "scenario_type")
                    )
                    if scenario_type == "append":
                        try:
                            field_type = output_data.dtypes.apply(lambda x: x.name).to_dict()
                            for col in element_scenario_data.columns.tolist():
                                element_scenario_data[col] = element_scenario_data[col].astype(
                                    field_type[col], errors="ignore"
                                )
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            data_error = f"Data validation error! {str(e)}"
                        output_data = pd.concat([output_data, element_scenario_data], ignore_index=True)
                    else:
                        if redis_instance.exists(scenario_name + elementid + "replace_identifier_list") == 1:
                            replace_identifier_list = pickle.loads(
                                redis_instance.get(scenario_name + elementid + "replace_identifier_list")
                            )
                            replace_column_list = pickle.loads(
                                redis_instance.get(scenario_name + elementid + "replace_column_list")
                            )
                        else:
                            replace_identifier_list = []
                            replace_column_list = []
                        if len(replace_identifier_list) > 0 and len(replace_column_list) > 0:
                            output_data_types = output_data.dtypes.apply(lambda x: x.name).to_dict()
                            for i in range(0, len(element_scenario_data)):
                                row_data = element_scenario_data.iloc[i]
                                condition_string = ""
                                for id_index, id_col in enumerate(replace_identifier_list):
                                    if output_data_types[id_col] in ["datetime64[ns]"]:
                                        row_data[id_col] = pd.to_datetime(row_data[id_col])
                                    elif output_data_types[id_col] in ["object"]:
                                        row_data[id_col] = str(row_data[id_col])
                                    condition_string += f"(output_data['{id_col}'] == '{row_data[id_col]}')"
                                    if len(replace_identifier_list) > 0 and (
                                        id_index != (len(replace_identifier_list) - 1)
                                    ):
                                        condition_string += " & "
                                for up_col in replace_column_list:
                                    output_data.loc[pd.eval(condition_string), up_col] = row_data[up_col]
                        else:
                            output_data = element_scenario_data.copy()
                    del element_scenario_data

    elif func_name == "Merge and Join":
        final_config = config_dict["inputs"]["final_config"]

        if final_config["merge_and_join"] != "":
            merge_and_join_config = final_config["merge_and_join"]
            output_data = Data_Transformation.merge_and_join(
                data_list=data,
                config_dict=merge_and_join_config,
                request_user=request_user,
            )
            merge_data_key = config_dict["element_id"] + "_merge"
            computation_storage(output_data, "dataframe", merge_data_key)

        if final_config["groupby"] != "":
            groupby_config = final_config["groupby"]
            if groupby_config["inputs"]["req_data"] == list(groupby_config["inputs"]["data"].values())[0]:
                if isinstance(data, pd.DataFrame):
                    req_group_by_data = data
                else:
                    req_group_by_data = data[0]
            else:
                req_group_by_data = read_computation_from_storage(groupby_config["inputs"]["req_data"])
            output_data = Data_Transformation.groupby_and_sortby(req_group_by_data, groupby_config)
            groupby_key = config_dict["element_id"] + "_group"
            computation_storage(output_data, "dataframe", groupby_key)

        if final_config["conditional_merge"] != "":
            cond_merge_config = final_config["conditional_merge"]
            cond_merge_config["inputs"]["parent_data"] = read_computation_from_storage(
                cond_merge_config["inputs"]["data_mapper"]["parent"]
            )
            cond_merge_config["inputs"]["child_data"] = read_computation_from_storage(
                cond_merge_config["inputs"]["data_mapper"]["child"]
            )
            output_data = Data_Transformation.merge_and_join(data_list=data, config_dict=cond_merge_config)
            condmerge_key = config_dict["element_id"] + "_condmerge"
            computation_storage(output_data, "dataframe", condmerge_key)

        if final_config["sortby"] != "":
            sortby_config = final_config["sortby"]
            if (
                final_config["merge_and_join"] != ""
                or final_config["groupby"] != ""
                or final_config["conditional_merge"] != ""
            ):
                output_data = Data_Transformation.groupby_and_sortby(output_data, sortby_config)
            else:
                output_data = Data_Transformation.groupby_and_sortby(data, sortby_config)

    elif func_name == "Pivot and Transpose":
        output_data = Data_Transformation.pivot_and_transpose(data, config_dict)

    elif func_name == "Elementary Statistics":
        output_data = Elementary_Statistics.Compute_Elementary_Statistics(
            dataframe=data, config_dict=config_dict
        )
        output_data = pd.DataFrame(output_data).reset_index()
        if "index" in list(output_data.columns):
            output_data.drop(columns=["index"], inplace=True)

    elif func_name == "Apply Math Operation":
        output_data = Apply_Math_Operations.Apply_Math_Operation_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Financial Functions":
        output_data = Financial_Functions.Financial_Functions(dataframe=data, configDict=config_dict)

    elif func_name == "Compatibility Functions":
        output_data = Compatibility_Functions.Compatibility_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Correlation":
        output_data = Correlation_Functions.Correlation_Functions(dataframe=data, configDict=config_dict)

    elif func_name == "Missing Values":
        output_data = Data_Pre_Processing.Missing_Values(dataframe=data, configDict=config_dict)

    elif func_name == "Feature Scaling":
        output_data = Data_Pre_Processing.Feature_Scaling(dataframe=data, configDict=config_dict)

    elif func_name == "Outlier Checks":
        if not config_dict.get("resultCheck"):
            output_data = Data_Pre_Processing.Outlier_Check(dataframe=data, configDict=config_dict)[0]
        else:
            output_data = Data_Pre_Processing.Outlier_Check(dataframe=data, configDict=config_dict)[1]

    elif func_name == "Differencing":
        output_data = Data_Pre_Processing.Differencing(dataframe=data, configDict=config_dict)

    elif func_name == "Splitting Datasets":
        output_data = Data_Pre_Processing.Splitting_Datasets(dataframe=data, configDict=config_dict)
        result_save_list = []
        if config_dict.get("outputs"):
            output_config = config_dict["outputs"]
            for outputOption in output_config.keys():
                if output_config[outputOption].get("save"):
                    save_output_config = output_config[outputOption]["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            if outputOption == "train":
                                output_data_save = output_data["train"]
                            elif outputOption == "test":
                                output_data_save = output_data["test"]
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
        return output_data, message, result_save_list, data_error

    elif func_name == "Binning":
        output_data = Data_Pre_Processing.Binning(dataframe=data, configDict=config_dict)

    elif func_name == "Export Data":
        data, output_type_export, [], data_error = ExportData.exportMain(
            request_user,
            config_dict,
            data,
            run_model,
            scenario_name,
            scenario_id,
            element_id,
            transaction_id,
            run_step,
        )
        return data, output_type_export, [], data_error

    elif func_name == "Portfolio Liquidity":
        output_data = Portfolio_Allocation.PFA_Base_JSON(config_dict, request_user)

    elif func_name == "Portfolio Limit Utilisation":
        output_data = Portfolio_Allocation.PFA_Base_JSON(config_dict, request_user)

    elif func_name == "Expected Return":
        output_data = Portfolio_Allocation.PFA_Base_JSON(config_dict, request_user)

    elif func_name == "Portfolio Allocation":
        output_data = Portfolio_Allocation.PFA_Base_JSON(config_dict, request_user)

    elif func_name == "Portfolio Attribution":
        username = config_dict["username"]
        output_data = Portfolio_Attribution.portfolio_attribution(config_dict, username)
        result_save_list = []
        if config_dict.get("outputs"):
            output_config = config_dict["outputs"]
            for outputOption in output_config.keys():
                if output_config[outputOption].get("save"):
                    save_output_config = output_config[outputOption]["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            if outputOption == "portfolio_attribution":
                                output_data_save = output_data["Portfolio_attribution"]
                            elif outputOption == "portfolio_attribution_positions":
                                output_data_save = output_data["Imtermediate_output"]
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
        return output_data, message, result_save_list

    elif func_name == "Mean Variance Optimisation":
        if len(config_dict["inputs"]["data_mapping"]) == 2:
            prices = data["prices"]
            market_benchmarks = data["constraints"]
            position_data = data["position_data"]
            cashflow_data = data["cashflow_data"]
            security_data = data["security_data"]
            measure_data = data["measure_data"]
            benchmark_cashflow_data = data["benchmark_cashflow_data"]
            security_liquidity_data = data["security_liquidity_data"]
            uploaded_constraints = data["uploaded_constraints"]
            (
                config_dict,
                market_benchmarks,
                common_constraints,
                uploaded_constraints_security_allocation,
            ) = Optimisation.data_cleaning(
                uploaded_constraints,
                market_benchmarks,
                position_data,
                cashflow_data,
                security_data,
                measure_data,
                benchmark_cashflow_data,
                config_dict,
                request_user,
            )
            output_data = Optimisation.Optimiser().mean_variance(
                prices, market_benchmarks, common_constraints, config_dict
            )
        else:
            uploaded_constraints = data["uploaded_constraints"]
            prices = data["prices"]
            market_benchmarks = data["constraints"]
            position_data = data["position_data"]
            cashflow_data = data["cashflow_data"]
            security_data = data["security_data"]
            measure_data = data["measure_data"]
            benchmark_cashflow_data = data["benchmark_cashflow_data"]
            security_liquidity_data = data["security_liquidity_data"]
            (
                config_dict,
                market_benchmarks,
                common_constraints,
                uploaded_constraints_security_allocation,
            ) = Optimisation.data_cleaning(
                uploaded_constraints,
                market_benchmarks,
                position_data,
                cashflow_data,
                security_data,
                measure_data,
                benchmark_cashflow_data,
                config_dict,
                request_user,
            )
            output_data = Optimisation.Optimiser().mean_variance(
                prices, market_benchmarks, common_constraints, config_dict
            )
        new_investment = float(config_dict["inputs"]["investment_amount"]["investment_amount_allocation"])
        pool_id = market_benchmarks["pool_id"].iloc[0]
        security_allocation_output, unallocated_investment = Optimisation.Optimiser().security_allocation(
            uploaded_constraints_security_allocation,
            security_data,
            position_data,
            security_liquidity_data,
            output_data["portfolio_allocation"],
            new_investment,
            pool_id,
        )
        date_cols = security_allocation_output.select_dtypes(include=["datetime64[ns]"]).columns.to_list()
        for i in date_cols:
            security_allocation_output[i] = security_allocation_output[i].dt.strftime("%d-%m-%Y")
        security_allocation_output.fillna("None", inplace=True)
        security_allocation_output.drop(columns=["percentage_allocated_decimals"], inplace=True)
        output_data["security_allocation_output"] = security_allocation_output.to_dict("list")
        output_data["security_allocation_output_headers"] = security_allocation_output.columns.tolist()
        output_data["investment_amount"] = new_investment
        output_data["unallocated_investment_amount"] = unallocated_investment
        if not run_model:
            computation_storage(output_data, "exception", elementid)
        result_save_list = []
        if config_dict.get("outputs"):
            output_config = config_dict["outputs"]
            for outputOption in output_config.keys():
                if output_config[outputOption].get("save"):
                    save_output_config = output_config[outputOption]["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            if outputOption == "PA":
                                output_data_save = output_data["portfolio_allocation"]
                            elif outputOption == "CR":
                                output_data_save = output_data["constraint_report"]
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
        return output_data, message, result_save_list, data_error

    elif func_name == "Portfolio Valuation":
        if config_dict["inputs"].get("col_mapping"):
            col_mapping = config_dict["inputs"]["col_mapping"]
        else:
            col_mapping = []

        if len(col_mapping) != 0:
            if len(col_mapping[0]["Position Data"]) > 0:
                data["positions_table"] = Comp_Column_Mapping.create_mapped_data(
                    data["positions_table"], col_mapping[0]["Position Data"]
                )

            if len(col_mapping[0]["NMD Data"]) > 0 and data["nmd_data"] is not None:
                data["nmd_data"] = Comp_Column_Mapping.create_mapped_data(
                    data["nmd_data"], col_mapping[0]["NMD Data"]
                )

            if len(col_mapping[0]["Product Data"]) > 0 and data["product_data"] is not None:
                data["product_data"] = Comp_Column_Mapping.create_mapped_data(
                    data["product_data"], col_mapping[0]["Product Data"]
                )

            if len(col_mapping[0]["Cashflow Data"]) > 0 and data["cashflow_data_uploaded"] is not None:
                data["cashflow_data_uploaded"] = Comp_Column_Mapping.create_mapped_data(
                    data["cashflow_data_uploaded"], col_mapping[0]["Cashflow Data"]
                )

            if len(col_mapping[0]["Market Data"]) > 0 and data["market_data"] is not None:
                data["market_data"] = Comp_Column_Mapping.create_mapped_data(
                    data["market_data"], col_mapping[0]["Market Data"]
                )

            if len(col_mapping[0]["Repayment Schedule Data"]) > 0 and data["repayment_data"] is not None:
                data["repayment_data"] = Comp_Column_Mapping.create_mapped_data(
                    data["repayment_data"], col_mapping[0]["Repayment Schedule Data"]
                )

            if (
                len(col_mapping[0]["Product to Model mapping Data"]) > 0
                and data["product_model_mapper_table"] is not None
            ):
                data["product_model_mapper_table"] = Comp_Column_Mapping.create_mapped_data(
                    data["product_model_mapper_table"], col_mapping[0]["Product to Model mapping Data"]
                )

        final_output, output_dict_model, var_plot = Portfolio_Valuation.final_valuation_fn(
            config_dict, request_user, data=data
        )
        output_dict = {
            "output": json.dumps(
                [final_output.head(100).to_dict("records")], cls=standardised_functions.NpEncoder
            ),
            "var_plot": var_plot,
        }
        result_save_list = []
        if config_dict.get("outputs"):
            output_config = config_dict["outputs"]
            for outputOption in output_config.keys():
                if output_config[outputOption].get("save"):
                    save_output_config = output_config[outputOption]["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            if outputOption == "cashflows":
                                output_data_save = output_dict_model["Cashflow_Output"]
                            elif outputOption == "measures":
                                output_data_save = output_dict_model["Measures_Output"]
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
        computation_storage(output_dict_model, "exception", elementid)
        if not run_model:
            return output_dict, message, result_save_list, data_error
        else:
            return final_output, output_dict_model, var_plot, result_save_list, data_error

    elif func_name == "Schedule Generation":
        output_data = Valuation_Models.schedule_generation_function(config_dict, request_user, data)

    elif func_name == "Cashflow Generation":
        output_data = Valuation_Models.cashflow_generation_function(config_dict, request_user, data)

    elif func_name == "TTM Calculation":
        output_data = Valuation_Models.TTM_calculation_function(config_dict, request_user, data)

    elif func_name == "Bootstrapping":
        output_data = Valuation_Models.bootstrapping_function(config_dict, request_user, data)

    elif func_name == "Interpolation":
        output_data = Valuation_Models.interpolation_function(config_dict, request_user, data)

    elif func_name == "Discount Factor Calculation":
        output_data = Valuation_Models.discount_factor_function(config_dict, request_user, data)

    elif func_name == "Logistic Regression":
        existing_element = read_data_func(
            request_user,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "ml_model_repository",
                    "Columns": ["model_output"],
                },
                "condition": [
                    {
                        "column_name": "element_id",
                        "condition": "Equal to",
                        "input_value": config_dict["element_id"],
                        "and_or": "",
                    },
                ],
            },
        )
        if len(existing_element) > 0 and run_model:
            return json.loads(existing_element.iloc[0, 0]), message, []
        else:
            output_dict, lr_model = Logistic_Regression.log_regression(data, config_dict)

            if not run_model:
                existing_element = read_data_func(
                    request_user,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "ml_model_repository",
                            "Columns": ["element_name"],
                        },
                        "condition": [
                            {
                                "column_name": "element_id",
                                "condition": "Equal to",
                                "input_value": config_dict["element_id"],
                                "and_or": "",
                            },
                        ],
                    },
                )
                if len(existing_element) > 0:
                    delete_data_func(
                        request_user,
                        {
                            "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": config_dict["element_id"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ml_model_output = pd.DataFrame(
                    columns=[
                        "model",
                        "model_type",
                        "element_id",
                        "model_output",
                        "element_name",
                        "created_by",
                        "created_date",
                        "modified_by",
                        "modified_date",
                    ]
                )
                ml_model_output_dict = {
                    "model_type": "Logistic Regression",
                    "element_id": elementid,
                    "model": lr_model,
                    "model_output": json.dumps(output_dict),
                    "element_name": config_dict["element_name"],
                    "created_by": request_user.user.username,
                    "created_date": datetime.now(),
                    "modified_by": request_user.user.username,
                    "modified_date": datetime.now(),
                }
                ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
                ml_model_output = pd.concat(
                    [ml_model_output, ml_model_output_dict_df],
                    ignore_index=True,
                )
                data_handling(request_user, ml_model_output, "ml_model_repository")

            result_save_list = []
            if config_dict.get("outputs"):
                output_config = config_dict["outputs"]
                for outputOption in output_config.keys():
                    if output_config[outputOption].get("save"):
                        save_output_config = output_config[outputOption]["save"]
                        if save_output_config:
                            source = save_output_config["source"]
                            table_name = save_output_config["table"]
                            if source and table_name:
                                if outputOption == "CR":
                                    output_data_save = output_dict["report"]
                                elif outputOption == "Acc":
                                    output_data_save = output_dict["accuracy"]
                                elif outputOption == "Pr":
                                    output_data_save = output_dict["precision"]
                                elif outputOption == "Re":
                                    output_data_save = output_dict["recall"]
                                elif outputOption == "F1":
                                    output_data_save = output_dict["f1_metric"]
                                elif outputOption == "CM":
                                    output_data_save = output_dict["conf_matrix"]
                                chunksize = save_output_config.get("chunksize", 10**5)
                                result_save = save_interim_model_outputs(
                                    source,
                                    table_name,
                                    data=output_data_save,
                                    request_user=request_user,
                                    scenario_name=scenario_name,
                                    scenario_id=scenario_id,
                                    chunksize=chunksize,
                                )
                                if result_save:
                                    result_save_list.append(result_save)
        computation_storage(output_dict, "exception", elementid)
        return output_dict, message, result_save_list, data_error

    elif func_name == "Linear Regression":
        existing_element = read_data_func(
            request_user,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "ml_model_repository",
                    "Columns": ["model_output"],
                },
                "condition": [
                    {
                        "column_name": "element_id",
                        "condition": "Equal to",
                        "input_value": config_dict["element_id"],
                        "and_or": "",
                    },
                ],
            },
        )
        if len(existing_element) > 0 and run_model:
            return json.loads(existing_element.iloc[0, 0]), message, [], data_error
        else:
            output_dict, lr_model = Linear_Regression.linear_regression(data, config_dict)

            if not run_model:
                existing_element = read_data_func(
                    request_user,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "ml_model_repository",
                            "Columns": ["element_name"],
                        },
                        "condition": [
                            {
                                "column_name": "element_id",
                                "condition": "Equal to",
                                "input_value": elementid,
                                "and_or": "",
                            },
                        ],
                    },
                )
                if len(existing_element) > 0:
                    delete_data_func(
                        request_user,
                        {
                            "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": elementid,
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ml_model_output = pd.DataFrame(
                    columns=[
                        "model",
                        "model_type",
                        "element_id",
                        "model_output",
                        "element_name",
                        "created_by",
                        "created_date",
                        "modified_by",
                        "modified_date",
                    ]
                )
                ml_model_output_dict = {
                    "model_type": "Linear Regression",
                    "element_id": elementid,
                    "model": lr_model,
                    "model_output": json.dumps(output_dict),
                    "element_name": config_dict["element_name"],
                    "created_by": request_user.user.username,
                    "created_date": datetime.now(),
                    "modified_by": request_user.user.username,
                    "modified_date": datetime.now(),
                }
                ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
                ml_model_output = pd.concat(
                    [ml_model_output, ml_model_output_dict_df],
                    ignore_index=True,
                )
                data_handling(request_user, ml_model_output, "ml_model_repository")
                computation_storage(output_dict, "exception", elementid)

            result_save_list = []
            if config_dict.get("outputs"):
                output_config = config_dict["outputs"]
                for outputOption in output_config.keys():
                    if output_config[outputOption].get("save"):
                        save_output_config = output_config[outputOption]["save"]
                        if save_output_config:
                            source = save_output_config["source"]
                            table_name = save_output_config["table"]
                            if source and table_name:
                                if outputOption == "PE":
                                    output_data_save = output_dict["parameter_estimates"]
                                elif outputOption == "IE":
                                    output_data_save = output_dict["intercept_estimate"]
                                elif outputOption == "COD":
                                    output_data_save = output_dict["coefficient_of_determination"]
                                elif outputOption == "MAE":
                                    output_data_save = output_dict["mean_abs_error"]
                                elif outputOption == "MSE":
                                    output_data_save = output_dict["mean_sq_error"]
                                chunksize = save_output_config.get("chunksize", 10**5)
                                result_save = save_interim_model_outputs(
                                    source,
                                    table_name,
                                    data=output_data_save,
                                    request_user=request_user,
                                    scenario_name=scenario_name,
                                    scenario_id=scenario_id,
                                    chunksize=chunksize,
                                )
                                if result_save:
                                    result_save_list.append(result_save)
        return output_dict, message, result_save_list, data_error

    elif func_name == "DecisionTree":
        result_save_list = []
        data_train = data["train"]
        data_test = data["test"]
        data_mapping = data.get("mapping")
        if data_mapping is not None:
            target_column_data_mapper = data_mapping.to_dict("list")
        else:
            target_column_data_mapper = {}
        exp_variables = config_dict["inputs"]["regressors"]
        dep_variable = config_dict["inputs"]["regressand"]
        output_data, cart_model = Decision_Tree.dec_tree_main(
            data_train, data_test, config_dict, data_mapping
        )
        context = {"content": output_data, "explanatory_vars": exp_variables, "dependent_var": dep_variable}
        computation_storage(context, "exception", elementid)
        if not run_model:
            element_name = config_dict["element_name"]
            existing_element = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ml_model_repository",
                        "Columns": ["element_name"],
                    },
                    "condition": [
                        {
                            "column_name": "element_id",
                            "condition": "Equal to",
                            "input_value": elementid,
                            "and_or": "",
                        },
                    ],
                },
            )
            if len(existing_element) > 0:
                delete_data_func(
                    request_user,
                    {
                        "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                        "condition": [
                            {
                                "column_name": "element_id",
                                "condition": "Equal to",
                                "input_value": elementid,
                                "and_or": "",
                            }
                        ],
                    },
                )
            ml_model_output = pd.DataFrame(
                columns=[
                    "model",
                    "model_type",
                    "element_id",
                    "model_output",
                    "element_name",
                    "target_column_data_mapper",
                    "created_by",
                    "created_date",
                    "modified_by",
                    "modified_date",
                ]
            )
            ml_model_output_dict = {
                "model_type": "CART Algorithm",
                "element_id": elementid,
                "model": cart_model,
                "model_output": json.dumps(context),
                "element_name": element_name,
                "target_column_data_mapper": json.dumps(target_column_data_mapper),
                "created_by": request_user.user.username,
                "created_date": datetime.now(),
                "modified_by": request_user.user.username,
                "modified_date": datetime.now(),
            }
            ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
            ml_model_output = pd.concat(
                [ml_model_output, ml_model_output_dict_df],
                ignore_index=True,
            )
            data_handling(request_user, ml_model_output, "ml_model_repository")
            return context, message, result_save_list, data_error
        return output_data, message, result_save_list, data_error

    elif func_name == "boostingAlgorithm":
        result_save_list = []
        data_train = data["train"]
        data_test = data["test"]
        method = config_dict["inputs"]["method"]
        data_mapping = data.get("mapping")
        if data_mapping is not None:
            target_column_data_mapper = data_mapping.to_dict("list")
        else:
            target_column_data_mapper = {}
        exp_variables = config_dict["inputs"]["regressors"]
        dep_variable = config_dict["inputs"]["regressand"]
        if method == "XGBoost":
            output_data, cart_model = XGBoost.xg_tree_main(data_train, data_test, config_dict, data_mapping)
        elif method == "AdaBoost":
            output_data, cart_model = AdaBoost.ada_tree_main(data_train, data_test, config_dict, data_mapping)
        elif method == "CatBoost":
            output_data, cart_model = CatBoost.cat_tree_main(data_train, data_test, config_dict, data_mapping)

        context = {
            "method": method,
            "content": output_data,
            "explanatory_vars": exp_variables,
            "dependent_var": dep_variable,
        }
        computation_storage(context, "exception", elementid)
        if not run_model:
            existing_element = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ml_model_repository",
                        "Columns": ["element_name"],
                    },
                    "condition": [
                        {
                            "column_name": "element_id",
                            "condition": "Equal to",
                            "input_value": elementid,
                            "and_or": "",
                        },
                    ],
                },
            )
            if len(existing_element) > 0:
                delete_data_func(
                    request_user,
                    {
                        "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                        "condition": [
                            {
                                "column_name": "element_id",
                                "condition": "Equal to",
                                "input_value": elementid,
                                "and_or": "",
                            }
                        ],
                    },
                )
            ml_model_output = pd.DataFrame(
                columns=[
                    "model",
                    "model_type",
                    "element_id",
                    "model_output",
                    "element_name",
                    "target_column_data_mapper",
                    "created_by",
                    "created_date",
                    "modified_by",
                    "modified_date",
                ]
            )
            ml_model_output_dict = {
                "model_type": "Boosting Algorithm",
                "element_id": elementid,
                "model": cart_model,
                "model_output": json.dumps(context),
                "element_name": config_dict["element_name"],
                "target_column_data_mapper": json.dumps(target_column_data_mapper),
                "created_by": request_user.user.username,
                "created_date": datetime.now(),
                "modified_by": request_user.user.username,
                "modified_date": datetime.now(),
            }
            ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
            ml_model_output = pd.concat(
                [ml_model_output, ml_model_output_dict_df],
                ignore_index=True,
            )
            data_handling(request_user, ml_model_output, "ml_model_repository")
            return context, message, result_save_list, data_error
        return output_data, message, result_save_list, data_error

    elif func_name == "Data Mapping":
        base_data = data["base_data"]
        mapping_ruleset = data["mapping_ruleset"]
        if config_dict["inputs"].get("col_mapping"):
            col_mapping = config_dict["inputs"]["col_mapping"]
        else:
            col_mapping = []

        if len(col_mapping) == 0:
            mapping_ruleset = mapping_ruleset
        else:
            new_mapping_data = Comp_Column_Mapping.create_mapped_data(
                mapping_ruleset, col_mapping[0]["Mapping Data"]
            )
            mapping_ruleset = new_mapping_data

        output_data, data_error = Data_Pre_Processing.Data_Mapping(config_dict, base_data, mapping_ruleset)

    # Time Series
    elif func_name == "Analyse Time Series Data":
        output_data = {}
        result_save_list = []
        if len(config_dict) > 0:
            parent_element_id = config_dict["inputs"]["Data"]
            if len(data) > 0:
                output_data["existing_configuration"] = "Yes"
                (
                    data_set,
                    stationarity_test_result,
                    p_value,
                    acf_plot,
                    pacf_plot,
                ) = Time_Series.TS_Master_Function(config_dict, data)
                output_data["element_data"] = data_set.reset_index()
                output_data["acf_plot"] = acf_plot
                output_data["pacf_plot"] = pacf_plot
                output_data["p_value"] = p_value
                output_data["test_result"] = stationarity_test_result
            else:
                output_data["existing_configuration"] = "No"
        else:
            output_data["existing_configuration"] = "No"
        computation_storage(output_data, "exception", elementid)
        return output_data, message, result_save_list, data_error

    elif func_name == "Train an ARIMA Model":
        output_data = {}
        result_save_list = []
        if len(config_dict) > 0:
            parent_element_id = config_dict["inputs"]["Data"]
            if len(data) > 0:
                output_data["existing_configuration"] = "Yes"
                (
                    results_arima_model,
                    summary,
                    data_set_train,
                    data_set_test,
                    residuals_plot,
                    acf_result,
                    adf_p_value,
                    adf_test_result,
                    mean,
                    std,
                    jb_p_value,
                    jb_test_result,
                    mse,
                    predicted_vs_actual_table,
                    predicted_vs_actual_plot,
                    arima_order,
                    frequency,
                    model_results_all_data,
                    ts_column_name,
                    last_date,
                    index_column_name,
                ) = Time_Series.TS_Master_Function(config_dict, data)
                output_data["summary"] = summary
                output_data["residuals_plot"] = residuals_plot
                output_data["acf_result"] = acf_result
                try:
                    output_data["adf_p_value"] = adf_p_value.round(4)
                    output_data["jb_p_value"] = jb_p_value.round(4)
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    output_data["adf_p_value"] = adf_p_value
                    output_data["jb_p_value"] = jb_p_value
                output_data["adf_test_result"] = adf_test_result
                output_data["mean"] = mean.round(4)
                output_data["std"] = std.round(4)
                output_data["jb_test_result"] = jb_test_result
                output_data["mse"] = mse
                output_data["table"] = predicted_vs_actual_table
                output_data["table_headers"] = list(predicted_vs_actual_table.keys())
                output_data["plot"] = predicted_vs_actual_plot
                output_data["arima_order"] = arima_order
                output_data["frequency"] = frequency
                output_data["last_date"] = last_date
                computation_storage(output_data, "exception", elementid)
                if not run_model:
                    computation_storage(data_set_train, "dataframe", elementid + "train")
                    computation_storage(data_set_test, "dataframe", elementid + "test")
                    output_data["last_date"] = output_data["last_date"].strftime("%Y-%m-%d %H:%M:%S")
                    content = {
                        "content": output_data,
                        "explanatory_vars": [index_column_name],
                        "dependent_var": ts_column_name,
                    }
                    existing_element = read_data_func(
                        request_user,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ml_model_repository",
                                "Columns": ["element_name"],
                            },
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": element_id,
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    if len(existing_element) > 0:
                        delete_data_func(
                            request_user,
                            {
                                "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": element_id,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ml_model_output = pd.DataFrame(
                        columns=[
                            "model",
                            "model_type",
                            "element_id",
                            "model_output",
                            "element_name",
                            "created_by",
                            "created_date",
                            "modified_by",
                            "modified_date",
                        ]
                    )
                    ml_model_output_dict = {
                        "model_type": "Time Series",
                        "element_id": element_id,
                        "model": model_results_all_data,
                        "model_output": json.dumps(content),
                        "element_name": config_dict["element_name"],
                        "created_by": request_user.user.username,
                        "created_date": datetime.now(),
                        "modified_by": request_user.user.username,
                        "modified_date": datetime.now(),
                    }
                    ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
                    ml_model_output = pd.concat(
                        [ml_model_output, ml_model_output_dict_df],
                        ignore_index=True,
                    )
                    data_handling(request_user, ml_model_output, "ml_model_repository")
            else:
                output_data["existing_configuration"] = "No"
        else:
            output_data["existing_configuration"] = "No"
        return output_data, message, result_save_list, data_error

    elif func_name == "Train a GARCH Model":
        output_data = {}
        result_save_list = []
        if len(config_dict) > 0:
            parent_element_id = config_dict["inputs"]["Data"]
            if len(data) > 0:
                output_data["existing_configuration"] = "Yes"
                (
                    summary,
                    time_series_data,
                    data_set_test,
                    residuals_plot,
                    conditional_volatility_plot,
                    acf_result,
                    adf_p_value,
                    adf_test_result,
                    mean,
                    std,
                    jb_p_value,
                    jb_test_result,
                    predicted_vs_actual_table,
                    predicted_vs_actual_plot,
                    frequency,
                    model_results_all_data,
                    ts_column_name,
                    last_date,
                    index_column_name,
                ) = Time_Series.TS_Master_Function(config_dict, data)
                output_data["summary"] = summary
                output_data["residuals_plot"] = residuals_plot
                output_data["conditional_volatility_plot"] = conditional_volatility_plot
                output_data["acf_result"] = acf_result
                try:
                    output_data["adf_p_value"] = adf_p_value.round(4)
                    output_data["jb_p_value"] = jb_p_value.round(4)
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    output_data["adf_p_value"] = adf_p_value
                    output_data["jb_p_value"] = jb_p_value
                output_data["adf_test_result"] = adf_test_result
                output_data["mean"] = mean.round(4)
                output_data["std"] = std.round(4)
                output_data["jb_test_result"] = jb_test_result
                predicted_vs_actual_table = predicted_vs_actual_table.reset_index()
                predicted_vs_actual_table.iloc[:, 0] = predicted_vs_actual_table.iloc[:, 0].dt.strftime(
                    "%Y-%m-%d"
                )
                predicted_vs_actual_table = predicted_vs_actual_table.to_dict("list")
                output_data["table"] = predicted_vs_actual_table
                output_data["table_headers"] = list(predicted_vs_actual_table.keys())
                output_data["plot"] = predicted_vs_actual_plot
                output_data["frequency"] = frequency
                output_data["last_date"] = last_date
                computation_storage(output_data, "exception", elementid)
                if not run_model:
                    computation_storage(time_series_data, "dataframe", elementid + "train")
                    computation_storage(data_set_test, "dataframe", elementid + "test")
                    output_data["last_date"] = last_date.strftime("%Y-%m-%d %H:%M:%S")
                    content = {
                        "content": output_data,
                        "explanatory_vars": [index_column_name],
                        "dependent_var": ts_column_name,
                    }
                    existing_element = read_data_func(
                        request_user,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ml_model_repository",
                                "Columns": ["element_name"],
                            },
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": element_id,
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    if len(existing_element) > 0:
                        delete_data_func(
                            request_user,
                            {
                                "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": element_id,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ml_model_output = pd.DataFrame(
                        columns=[
                            "model",
                            "model_type",
                            "element_id",
                            "model_output",
                            "element_name",
                            "created_by",
                            "created_date",
                            "modified_by",
                            "modified_date",
                        ]
                    )

                    ml_model_output = ml_model_output.append(
                        {
                            "model_type": "GARCH Volatility Model",
                            "element_id": element_id,
                            "model": model_results_all_data,
                            "model_output": json.dumps(content),
                            "element_name": config_dict["element_name"],
                            "created_by": request_user.user.username,
                            "created_date": datetime.now(),
                            "modified_by": request_user.user.username,
                            "modified_date": datetime.now(),
                        },
                        ignore_index=True,
                    )
                    data_handling(request_user, ml_model_output, "ml_model_repository")
            else:
                output_data["existing_configuration"] = "No"
        else:
            output_data["existing_configuration"] = "No"
        return output_data, message, result_save_list, data_error

    elif func_name in ["Interest Rate Products", "Equities", "Mutual Fund"]:
        rounding_view = 4
        if config_dict["inputs"]["Data_Choice"] == "Custom_input":
            output_dict = {}
            curve_repo_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ir_curve_repository",
                        "Columns": ["curve_name", "curve_components", "interpolation_algorithm"],
                    },
                    "condition": [],
                },
            )
            curve_components_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ir_curve_components",
                        "Columns": ["id", "curve_component", "tenor_value", "tenor_unit"],
                    },
                    "condition": [],
                },
            )
            cs_curve_repo_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "cs_curve_repository",
                        "Columns": ["curve_name", "curve_components", "interpolation_algorithm"],
                    },
                    "condition": [],
                },
            )
            cs_curve_components_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "cs_curve_components",
                        "Columns": ["id", "curve_component", "tenor_value", "tenor_unit"],
                    },
                    "condition": [],
                },
            )
            mtm_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Quoted_Security_Data",
                        "Columns": [
                            "extract_date",
                            "security_identifier",
                            "quoted_price",
                            "yield",
                            "modified_duration",
                            "volume_traded",
                        ],
                    },
                    "condition": [],
                },
            )
            custom_daycount_conventions = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "custom_daycount_conventions",
                        "Columns": [
                            "convention_name",
                            "numerator",
                            "denominator",
                            "numerator_adjustment",
                            "denominator_adjustment",
                        ],
                    },
                    "condition": [],
                },
            )
            (
                cashflow_model_results,
                valuation_results,
                sensitivity_analysis,
            ) = Valuation_Models.Value_extraction(
                config_dict,
                curve_repo_data,
                curve_components_data,
                cs_curve_repo_data,
                cs_curve_components_data,
                mtm_data=mtm_data,
                custom_daycount_conventions=custom_daycount_conventions,
            )
            result_save_list = []
            if config_dict.get("output_options"):
                output_config = config_dict["output_options"]
                for outputOption in output_config.keys():
                    if output_config[outputOption].get("save"):
                        save_output_config = output_config[outputOption]["save"]
                        if save_output_config:
                            source = save_output_config["source"]
                            table_name = save_output_config["table"]
                            if source and table_name:
                                if outputOption == "cashflow":
                                    output_data_save = cashflow_model_results.copy()
                                elif outputOption == "valuation":
                                    output_data_save = valuation_results.copy()
                                elif outputOption == "sensitivity":
                                    output_data_save = sensitivity_analysis.copy()
                                chunksize = save_output_config.get("chunksize", 10**5)
                                result_save = save_interim_model_outputs(
                                    source,
                                    table_name,
                                    data=output_data_save,
                                    request_user=request_user,
                                    scenario_name=scenario_name,
                                    scenario_id=scenario_id,
                                    chunksize=chunksize,
                                )
                                if result_save:
                                    result_save_list.append(result_save)
            cashflow_model_results_headers = list(cashflow_model_results.columns)
            if len(valuation_results) > 0:
                valuation_headers = list(valuation_results[0].keys())
            else:
                valuation_headers = []
            if len(sensitivity_analysis) > 0:
                sensitivity_analysis_headers = list(sensitivity_analysis[0].keys())
            else:
                sensitivity_analysis_headers = []
            num_cols = cashflow_model_results.select_dtypes(include=["int64", "float64"]).columns.tolist()
            for i in num_cols:
                cashflow_model_results = round(cashflow_model_results, rounding_view)
            if len(valuation_results) > 0:
                for k, v in valuation_results[0].items():
                    if isinstance(v, float):
                        valuation_results[0][k] = round(v, rounding_view)
            if len(sensitivity_analysis) > 0:
                for k, v in sensitivity_analysis[0].items():
                    if isinstance(v, float):
                        sensitivity_analysis[0][k] = round(v, rounding_view)
            output_dict["cashflow_model_results"] = cashflow_model_results.loc[
                cashflow_model_results["Cashflow Dates"].notnull(), :
            ].to_dict("list")
            output_dict["cashflow_model_results_headers"] = cashflow_model_results_headers
            output_dict["valuation_results"] = valuation_results
            output_dict["valuation_headers"] = valuation_headers
            output_dict["sensitivity_analysis"] = sensitivity_analysis
            output_dict["sensitivity_analysis_headers"] = sensitivity_analysis_headers
        return output_dict, message, result_save_list, data_error

    elif func_name == "TWRR":
        rounding_view = 4
        position_data = data["position"]
        cashflow_data = data["cashflow"]
        transaction_data = data["transaction"]

        if config_dict["inputs"].get("col_mapping"):
            col_mapping = config_dict["inputs"]["col_mapping"]
        else:
            col_mapping = []

        if len(col_mapping) == 0:
            position_data = position_data
            cashflow_data = cashflow_data
            transaction_data = transaction_data
        else:
            if len(col_mapping[0]["Position Data"]) > 0:
                position_data = Comp_Column_Mapping.create_mapped_data(
                    position_data, col_mapping[0]["Position Data"]
                )
            else:
                position_data = position_data

            if len(col_mapping[0]["Cashflow Data"]) > 0:
                cashflow_data = Comp_Column_Mapping.create_mapped_data(
                    cashflow_data, col_mapping[0]["Cashflow Data"]
                )
            else:
                cashflow_data = cashflow_data

            if len(col_mapping[0]["Transaction cashflow Data"]) > 0:
                transaction_data = Comp_Column_Mapping.create_mapped_data(
                    transaction_data, col_mapping[0]["Transaction cashflow Data"]
                )
            else:
                transaction_data = transaction_data

        output_data, message = TWRR.twrr(position_data, cashflow_data, config_dict, transaction_data)
    elif func_name == "Rename Column":
        data_trnsf = Data_Transformation.DataTransformation()
        output_data = data_trnsf.rename_column(
            data=data,
            rename_dict=config_dict["inputs"]["rename_config"],
            drop_column=config_dict["inputs"]["drop_column"],
        )

    elif func_name == "Find and Replace":
        data_trnsf = Data_Transformation.DataTransformation()
        output_data = data_trnsf.find_replace(
            data=data,
            fdict=config_dict["inputs"]["fdict"],
        )
    elif func_name == "Code Editor":
        list_code = json.loads(config_dict["inputs"]["list_code"])[0]

        global_str = config_dict["inputs"].get("global_str")
        data_str = ""
        del_data_str = ""
        if isinstance(data, list):
            for index, ele in enumerate(data):
                data_str += f"Data{str(index+1)} = data[{index}]\n"
                del_data_str += f"del Data{str(index+1)}\n"
        else:
            data_str += "Data1 = data\n"
            del_data_str += "del Data1\n"

        if global_str:
            list_code = "import datetime\n" + global_str + list_code

        code = list_code

        code_editor_output = "run_process_codeeditor" + standardised_functions.random_no_generator()
        editor_output_dict = {"data": data, "request_user": request_user}
        try:
            exec(data_str + code + "\n" + del_data_str, globals(), editor_output_dict)
            output_data = editor_output_dict["output_data"]
            editor_output_dict = None
            del editor_output_dict
            message = "success"
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
            error_class = e.__class__.__name__
            detail = e.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1] - 1
            message = f"{error_class} at line {line_number} of the source code: {detail}."
            data_error = f"{error_class} at line {line_number} of the source code: {detail}."
            output_data = pd.DataFrame()
        else:
            pass

    elif func_name == "Portfolio Metrics":
        portfolio_data = data["portfolio_data"]
        riskfree_data = data["riskfree_data"]
        market_data = data["market_data"]

        PM = PortfolioMetrics.PortfolioMetrics()
        output_data = PM.unwrap_config(portfolio_data, config_dict, riskfree_data, market_data)

    elif func_name == "GSEC Bond Curve Bootstrapping":
        output_dict, backend_data = Single_Curve_Bootstrapping.singlecurve(data, config_dict)
        if not run_model:
            computation_storage(backend_data, "exception", elementid)
            return output_dict, message, result_save_list, data_error
        else:
            return backend_data, output_dict, message, [], data_error

    elif func_name == "Curve Data Bootstrapping":
        output_dict, backend_data = Curve_Data_Bootstrapping.curve_data_preprocessing(
            data, config_dict, request_user
        )
        if not run_model:
            computation_storage(backend_data, "exception", elementid)
            return output_dict, message, result_save_list, data_error
        else:
            return backend_data, output_dict, message, [], data_error

    elif func_name == "Options":
        pos_data = data["pos_data"]
        vix_data = data["vix_data"]

        output_data = Options_Pricing.master_val(pos_data, vix_data, config_dict)

    elif func_name == "OIS Curve Bootstrapping":
        output_dict, backend_data = OIS_Bootstrapping.ois(data, config_dict)
        if not run_model:
            computation_storage(backend_data, "exception", element_id)
            return output_dict, message, result_save_list, data_error
        else:
            return backend_data, output_dict, message, [], data_error

    elif func_name == "Predict":
        prediction_data = data
        result_save_list = []
        message = "Success"
        parent_element_id = config_dict["inputs"]["data"]
        if parent_element_id.get("Model"):
            model_element_id = parent_element_id["Model"]
        else:
            model_element_id = config_dict["inputs"]["mlModel"]
        model_output = read_data_func(
            request_user,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "ml_model_repository",
                    "Columns": ["model", "model_type", "model_output", "target_column_data_mapper"],
                },
                "condition": [
                    {
                        "column_name": "element_id",
                        "condition": "Equal to",
                        "input_value": model_element_id,
                        "and_or": "",
                    },
                ],
            },
        )
        if len(model_output) > 0:
            model_type = model_output.model_type.iloc[0]
            explanatory_vars = json.loads(model_output.model_output.iloc[0])["explanatory_vars"]
            dependent_var = json.loads(model_output.model_output.iloc[0])["dependent_var"]
            target_column_data_mapper = model_output.target_column_data_mapper.iloc[0]
            if target_column_data_mapper is not None:
                target_column_data_mapper = json.loads(target_column_data_mapper)
            else:
                target_column_data_mapper = {}
            model = pickle.loads(model_output.model.iloc[0])
            if model_type not in [
                "Time Series",
                "GARCH Volatility Model",
                "Holt-Winters Exponential Smoothing",
            ]:
                if prediction_data is None or len(prediction_data) == 0:
                    message = "Error! Data for prediction could not be found. Please reconfigure the model."
                    return {}, message, result_save_list
            if model_type == "Linear Regression":
                output_data = Linear_Regression.lin_reg_predict(
                    prediction_data, explanatory_vars, dependent_var, model
                )
            elif model_type == "Logistic Regression":
                output_data = Logistic_Regression.log_reg_predict(
                    prediction_data, explanatory_vars, dependent_var, model
                )
            elif model_type == "CART Algorithm":
                output_data = Decision_Tree.cart_predict(
                    prediction_data, explanatory_vars, dependent_var, model, target_column_data_mapper
                )
            elif model_type == "Boosting Algorithm":
                output_data = AdaBoost.cart_predict(
                    prediction_data, explanatory_vars, dependent_var, model, target_column_data_mapper
                )
            elif model_type == "Time Series":
                no_of_steps = int(config_dict["inputs"]["no_of_steps"])
                output_data = Time_Series.arima_predict(
                    explanatory_vars,
                    dependent_var,
                    model,
                    no_of_steps,
                    json.loads(model_output.model_output.iloc[0])["content"],
                )
            elif model_type == "GARCH Volatility Model":
                no_of_steps = int(config_dict["inputs"]["no_of_steps"])
                output_data = Time_Series.garch_predict(
                    explanatory_vars,
                    dependent_var,
                    model,
                    no_of_steps,
                    json.loads(model_output.model_output.iloc[0])["content"],
                )
            elif model_type == "Holt-Winters Exponential Smoothing":
                no_of_steps = int(config_dict["inputs"]["no_of_steps"])
                output_data = Time_Series.EWMA_predict(
                    explanatory_vars,
                    dependent_var,
                    model,
                    no_of_steps,
                    json.loads(model_output.model_output.iloc[0])["content"],
                )

            if config_dict.get("outputs"):
                output_config = config_dict["outputs"]
                if output_config.get("save"):
                    save_output_config = output_config["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            output_data_save = output_data.copy()
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
        else:
            message = "Error! Model config could not be found. Please re-run the model."
        return output_data, message, result_save_list, data_error

    elif func_name == "Swap Curve Bootstrapping":
        parent_elements_id = config_dict["inputs"]["data"]
        data = {}
        c = 1
        for dt_key, element_id in list(parent_elements_id.items()):
            data["d" + str(c)] = read_computation_from_storage(element_id)
            c += 1
        output_dict, backend_data = Swap_Curve.swap(data, config_dict)
        if not run_model:
            computation_storage(backend_data, "exception", elementid)
            return output_dict, message, result_save_list, data_error
        else:
            return backend_data, output_dict, message, [], data_error

    elif func_name == "Goodness Fit Test":
        df, best_fit_parameters, var_plot, info_dict = ContinousCurve.best_fit(
            config_dict, data, request_user
        )
        output_data = {
            "content": json.dumps(df),
            "best_fit": json.dumps(best_fit_parameters),
            "var_plot": var_plot,
            "info_dict": json.dumps(info_dict),
        }
        computation_storage(output_data, "exception", elementid)
        return output_data, message, result_save_list, data_error

    elif func_name == "Fit Discrete":
        best_fit_parameter, var_plot, info_dict = FitDiscreteDistribution.fit_discrete(
            config_dict, data, request_user
        )
        output_data = {
            "content": json.dumps(best_fit_parameter),
            "var_plot": var_plot,
            "info_dict": json.dumps(info_dict),
        }
        computation_storage(output_data, "exception", elementid)
        return output_data, message, result_save_list, data_error

    elif func_name == "Copula Function":
        scenerio_dict = {}
        loss_amt_df = data["loss_amt_df"]
        scenerio_df = data["scenerio_mapping"]
        val_number_percentile = json.loads(config_dict["inputs"]["percentile_input"])
        val_text_scenerio = json.loads(config_dict["inputs"]["scenerio_input"])
        scenerio_percentile_var = config_dict["inputs"]["scenerio_percentile_id"]
        if scenerio_percentile_var:
            scenerio_col = config_dict["inputs"]["scenerio_column"]
            percentile_col = config_dict["inputs"]["percentile_column"]
            scene = []
            percentile = []
            if scenerio_col in scenerio_df.columns:
                scene = scenerio_df[scenerio_col].tolist()
            if percentile_col in scenerio_df.columns:
                percentile = scenerio_df[percentile_col].tolist()
            scenerio_dict = {"Scenerio": scene, "Percentile": percentile}
        else:
            scene = val_text_scenerio["val_text"]
            percentile = val_number_percentile["val_number"]
            scenerio_dict = {"Scenerio": [scene], "Percentile": [int(percentile)]}

        resultant_dict = Copula.copula_result(loss_amt_df, scenerio_dict, config_dict, request=request_user)
        output_data = {"content": json.dumps(resultant_dict)}
        computation_storage(output_data, "exception", elementid)
        return output_data, message, result_save_list, data_error

    elif func_name == "Monte Carlo":
        output_data = MonteCarlo.monte_carlo_simulation(config_dict, request_user)

    elif func_name == "Data Summary":
        output_data = Data_Pre_Processing.Data_Summary(dataframe=data, configDict=config_dict)

    elif func_name == "VaR Backtesting":
        output_data = VaR_Backtesting.backrun(data, config_dict)

    elif func_name == "One Hot Encoding":
        output_data = Data_Pre_Processing.one_hot_encoder(data, config_dict)

    elif func_name == "Train an EWMA Model":
        output_data = {}
        result_save_list = []
        if len(config_dict) > 0:
            parent_element_id = config_dict["inputs"]["Data"]
            if len(data) > 0:
                output_data["existing_configuration"] = "Yes"
                (
                    results_ewma_model,
                    summary,
                    data_set_train,
                    data_set_test,
                    residuals_plot,
                    acf_result,
                    adf_p_value,
                    adf_test_result,
                    mean,
                    std,
                    jb_p_value,
                    jb_test_result,
                    mse,
                    predicted_vs_actual_table,
                    predicted_vs_actual_plot,
                    frequency,
                    model_results_all_data,
                    ts_column_name,
                    last_date,
                    index_column_name,
                ) = Time_Series.TS_Master_Function(config_dict, data)
                output_data["summary"] = summary
                output_data["residuals_plot"] = residuals_plot
                output_data["acf_result"] = acf_result
                try:
                    output_data["adf_p_value"] = adf_p_value.round(4)
                    output_data["jb_p_value"] = jb_p_value.round(4)
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    output_data["adf_p_value"] = adf_p_value
                    output_data["jb_p_value"] = jb_p_value
                output_data["adf_test_result"] = adf_test_result
                output_data["mean"] = mean.round(4)
                output_data["std"] = std.round(4)
                output_data["jb_test_result"] = jb_test_result
                output_data["mse"] = mse
                output_data["table"] = predicted_vs_actual_table
                output_data["table_headers"] = list(predicted_vs_actual_table.keys())
                output_data["plot"] = predicted_vs_actual_plot
                output_data["frequency"] = frequency
                output_data["last_date"] = last_date
                computation_storage(output_data, "exception", element_id)
                if not run_model:
                    computation_storage(data_set_train, "dataframe", element_id + "train")
                    computation_storage(data_set_test, "dataframe", element_id + "test")
                    output_data["last_date"] = output_data["last_date"].strftime("%Y-%m-%d %H:%M:%S")
                    content = {
                        "content": output_data,
                        "explanatory_vars": [index_column_name],
                        "dependent_var": ts_column_name,
                    }
                    existing_element = read_data_func(
                        request_user,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ml_model_repository",
                                "Columns": ["element_name"],
                            },
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": element_id,
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    if len(existing_element) > 0:
                        delete_data_func(
                            request_user,
                            {
                                "inputs": {"Data_source": "Database", "Table": "ml_model_repository"},
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": element_id,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ml_model_output = pd.DataFrame(
                        columns=[
                            "model",
                            "model_type",
                            "element_id",
                            "model_output",
                            "element_name",
                            "created_by",
                            "created_date",
                            "modified_by",
                            "modified_date",
                        ]
                    )
                    ml_model_output_dict = {
                        "model_type": "Holt-Winters Exponential Smoothing",
                        "element_id": element_id,
                        "model": model_results_all_data,
                        "model_output": json.dumps(content),
                        "element_name": config_dict["element_name"],
                        "created_by": request_user.user.username,
                        "created_date": datetime.now(),
                        "modified_by": request_user.user.username,
                        "modified_date": datetime.now(),
                    }
                    ml_model_output_dict_df = pd.DataFrame.from_dict([ml_model_output_dict])
                    ml_model_output = pd.concat(
                        [ml_model_output, ml_model_output_dict_df],
                        ignore_index=True,
                    )
                    data_handling(request_user, ml_model_output, "ml_model_repository")
                else:
                    output_data["last_date"] = output_data["last_date"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                output_data["existing_configuration"] = "No"
        else:
            output_data["existing_configuration"] = "No"
        return output_data, message, result_save_list, data_error

    elif func_name == "Add Time Periods":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Data Utilities":
        if config_dict["inputs"]["reset_checked"]:
            if config_dict["inputs"]["drop_checked"]:
                output_data = data.reset_index(drop=True)
            else:
                output_data = data.reset_index()
        elif config_dict["inputs"]["drop_checked"]:
            output_data = data.reset_index(drop=True)

        if config_dict["inputs"].get("cols"):
            if len(config_dict["inputs"]["cols"]) > 0:
                output_data = data.set_index(config_dict["inputs"]["cols"])

    elif func_name == "Drop Duplicate":
        if config_dict["inputs"]["Sub_Op"]:
            if config_dict["inputs"]["Other_Inputs"]["Data"]:
                column = config_dict["inputs"]["Other_Inputs"]["Data"]
                operation = config_dict["inputs"]["Sub_Op"]
                if operation in ["first", "last"]:
                    output_data = data.drop_duplicates(subset=column, keep=operation)
                else:
                    output_data = data.drop_duplicates(subset=column, keep=False)
        else:
            output_data = data.drop_duplicates()

    elif func_name == "Concat Columns":
        column_name = config_dict["inputs"]["Column_name"]
        column_1 = config_dict["inputs"]["Column_1"]
        separator = config_dict["inputs"]["Separator"]
        data[column_name] = (
            data[column_1].fillna("").apply(lambda row: separator.join(row.values.astype(str)), axis=1)
        )
        output_data = data

    elif func_name == "Add Fix Column":
        col_name = config_dict["inputs"]["input_name"]
        col_val = config_dict["inputs"]["input_value"]
        data[col_name] = col_val
        output_data = data

    elif func_name == "Compare Column":
        if config_dict["inputs"]["columnName"]:
            if config_dict["inputs"]["data_col"]:
                new_name = config_dict["inputs"]["columnName"]
                column = config_dict["inputs"]["data_col"]
                a = column[0]
                x = True
                data1 = data.to_dict("records")
                x = True
                for i in data1:
                    x = True
                    for [key, value] in i.items():
                        if key != a:
                            if key in column:
                                if i[a] == value:
                                    x = x & True
                                else:
                                    x = x & False
                    i[new_name] = x
                    data = pd.DataFrame.from_records(data1)
        output_data = data

    elif func_name == "Delimit Column":
        column_name = config_dict["inputs"]["columnName"]
        delimiter = config_dict["inputs"]["delimiter"]
        first_row = data[column_name].loc[~data[column_name].isnull()].iloc[0]
        if data[column_name].dtype == "datetime64[ns]":
            if delimiter != ":":
                first_row = first_row.strftime("%Y-%m-%d")
                data[column_name] = data[column_name].dt.strftime("%Y-%m-%d")
            elif delimiter == ":":
                first_row = first_row.strftime("%H:%M:%S")
                data[column_name] = data[column_name].dt.strftime("%H:%M:%S")
        cols_n = first_row.split(delimiter)
        rename_dict = {}
        for i in range(len(cols_n)):
            rename_dict[i] = column_name + "_" + str(i)
        output_data = data.join(
            data[column_name].astype(str).str.split(delimiter, expand=True).rename(columns=rename_dict)
        )

    elif func_name == "Date":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Days":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Day":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Time":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Second":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Now":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Eomonth":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Days360":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Edate":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Weeknum":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Weekday":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Today":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Hour":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Isoweeknum":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Year":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Minute":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Month":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Networkdays.Intl":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Networkdays":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Yearfrac":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Workdays.Intl":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "Workdays":
        output_data = Time_Periods.Time_Periods_Func(dataframe=data, config_dict=config_dict)

    elif func_name == "textjoinfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textafterfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textbeforefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "bahttextfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "lowerfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "properfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "upperfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "lenfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "charfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "unicodefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "leftfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "rightfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "midfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "exactfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "unicharfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "reptfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "findfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "searchfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "replacefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "trimfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "codefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "cleanfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "valuetotextfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "substitutefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "tfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "numbervaluefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "valuefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textjoinfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textafterfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textbeforefunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "fixedfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "dollarfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "arraytotextfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "textsplitfunc":
        output_data = TextFunctions.Apply_Text_Functions(dataframe=data, config_dict=config_dict)

    elif func_name == "Delimit values":
        output_data = Data_Pre_Processing.Delimit_values(data, config_dict)

    elif func_name == "Portfolio Validation":

        output_data = Validation_check.products_model_validation_check(
            request_user,
            data=data,
        )

    else:
        pass
    exception_list = []
    result_save_list = []
    if len(data_error) == 0:
        if not run_model and not multi_import:
            computation_storage(output_data, "dataframe", elementid)
        else:
            pass
        if func_name not in exception_list:
            if config_dict.get("outputs"):
                output_config = config_dict["outputs"]
                if output_config.get("save"):
                    save_output_config = output_config["save"]
                    if save_output_config:
                        source = save_output_config["source"]
                        table_name = save_output_config["table"]
                        if source and table_name:
                            output_data_save = output_data.copy()
                            chunksize = save_output_config.get("chunksize", 10**5)
                            result_save = save_interim_model_outputs(
                                source,
                                table_name,
                                data=output_data_save,
                                request_user=request_user,
                                scenario_name=scenario_name,
                                scenario_id=scenario_id,
                                chunksize=chunksize,
                            )
                            if result_save:
                                result_save_list.append(result_save)
    if run_model:
        return output_data, message, result_save_list, data_error
    else:
        return elementid, message, result_save_list, data_error


def data_validation_check(function, input_data):
    if function in [
        "Import Data",
        "Export Data",
        "Merge and Join",
        "Pivot and Transpose",
        "Rename Column",
        "Find and Replace",
        "Code Editor",
        "Data Mapping",
        "Apply Math Operation",
        "Financial Functions",
        "Correlation",
        "Elementary Statistics",
        "Interest Rate Products",
        "Equities",
        "Mutual Fund",
        "Analyse Time Series Data",
        "Train an ARIMA Model",
        "Train a GARCH Model",
        "Train an EWMA Model",
        "Goodness Fit Tes",
        "Fit Discrete",
        "Copula Function",
        "Monte Carlo",
    ]:
        return input_data, ""
    elif function == "Portfolio Valuation":
        data_validation_errors = []
        try:
            ideal_position_dtype = {
                "id": "int64",
                "unique_reference_id": "object",
                "position_id": "object",
                "underlying_position_id": "object",
                "issuer": "object",
                "position_direction": "object",
                "issue_date": "datetime64[ns]",
                "maturity_date": "datetime64[ns]",
                "reporting_date": "datetime64[ns]",
                "next_reset_date": "datetime64[ns]",
                "reset_frequency": "float64",
                "reset_frequency_unit": "object",
                "credit_spread_rate": "object",
                "credit_spread_curve": "object",
                "discount_daycount_convention": "object",
                "accrual_daycount_convention": "object",
                "primary_currency": "object",
                "discounting_curve": "object",
                "forward_benchmark_curve": "object",
                "fixed_spread": "object",
                "base_rate": "object",
                "face_value": "object",
                "redemption_amount": "object",
                "business_convention": "object",
                "holiday_calendar": "object",
                "payment_frequency": "float64",
                "payment_frequency_units": "object",
                "last_payment_date": "datetime64[ns]",
                "last_principal_payment_date": "datetime64[ns]",
                "emi_amount": "object",
                "internal_rating": "object",
                "quantity": "float64",
                "outstanding_amount": "object",
                "next_payment_date": "datetime64[ns]",
                "unutilized_limit_amount": "object",
                "put_call_type": "object",
                "option_style": "object",
                "asset_liability_type": "object",
                "fund_code": "object",
                "pool_id": "object",
                "product_variant_name": "object",
                "asset_class": "object",
                "legal_entity": "object",
                "business": "object",
            }

            for col in input_data["positions_table"].columns.tolist():
                if col in ideal_position_dtype:
                    if ideal_position_dtype[col] in ["int64", "float64"]:
                        input_data["positions_table"][col] = pd.to_numeric(
                            input_data["positions_table"][col], errors="coerce"
                        )
                    else:
                        input_data["positions_table"][col] = input_data["positions_table"][col].astype(
                            ideal_position_dtype[col]
                        )
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
            data_validation_errors.append(f"Data validation error in Position data in {col} column! {str(e)}")
        if len(input_data["nmd_data"]) > 0:
            try:
                ideal_nmd_dtype = {
                    "id": "int64",
                    "product_variant_name": "object",
                    "product_variant_code": "object",
                    "scenario_analysis_id": "object",
                    "reporting_date": "datetime64[ns]",
                    "percentage": "int64",
                    "end_tenor_unit": "object",
                    "end_tenor": "int64",
                    "start_tenor_unit": "object",
                    "start_tenor": "int64",
                }

                for col in input_data["nmd_data"].columns.tolist():
                    if col in ideal_nmd_dtype:
                        if ideal_nmd_dtype[col] in ["int64", "float64"]:
                            input_data["nmd_data"][col] = pd.to_numeric(
                                input_data["nmd_data"][col], errors="coerce"
                            )
                        else:
                            input_data["nmd_data"][col] = input_data["nmd_data"][col].astype(
                                ideal_nmd_dtype[col]
                            )
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in Behavioural NMD data in {col} column! {str(e)}"
                )

        if len(input_data["dpd_schedule"]) > 0:
            try:
                ideal_dpd_schedule_type = {
                    "id": "int64",
                    "extract_date": "datetime64[ns]",
                    "position_id": "object",
                    "cashflow_due_date": "datetime64[ns]",
                    "cashflow_type": "object",
                    "cashflow": "float64",
                    "dpd": "float64",
                }

                for col in input_data["dpd_schedule"].columns.tolist():
                    if col in ideal_dpd_schedule_type:
                        if ideal_dpd_schedule_type[col] in ["int64", "float64"]:
                            input_data["dpd_schedule"][col] = pd.to_numeric(
                                input_data["dpd_schedule"][col], errors="coerce"
                            )
                        else:
                            input_data["dpd_schedule"][col] = input_data["dpd_schedule"][col].astype(
                                ideal_dpd_schedule_type[col]
                            )
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in DPD Schedule data in {col} column! {str(e)}"
                )
        if len(input_data["dpd_data"]) > 0:
            try:
                ideal_dpd_ruleset_type = {
                    "id": "int64",
                    "scenario_analysis_id": "object",
                    "overdue_type": "object",
                    "dpd_start": "float64",
                    "dpd_end": "float64",
                    "dpd_start_unit": "object",
                    "dpd_end_unit": "object",
                    "ttm": "float64",
                }

                for col in input_data["dpd_data"].columns.tolist():
                    if col in ideal_dpd_ruleset_type:
                        if ideal_dpd_ruleset_type[col] in ["int64", "float64"]:
                            input_data["dpd_data"][col] = pd.to_numeric(
                                input_data["dpd_data"][col], errors="coerce"
                            )
                        else:
                            input_data["dpd_data"][col] = input_data["dpd_data"][col].astype(
                                ideal_dpd_ruleset_type[col]
                            )
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in DPD Ruleset in {col} column! {str(e)}"
                )

        if len(input_data["overdue_data"]) > 0:
            try:
                ideal_overdue_data_type = {
                    "id": "int64",
                    "scenario_analysis_id": "object",
                    "overdue_type": "object",
                    "product_variant_name": "object",
                    "ttm": "float64",
                }

                for col in input_data["overdue_data"].columns.tolist():
                    if col in ideal_overdue_data_type:
                        if ideal_overdue_data_type[col] in ["int64", "float64"]:
                            input_data["overdue_data"][col] = pd.to_numeric(
                                input_data["overdue_data"][col], errors="coerce"
                            )
                        else:
                            input_data["overdue_data"][col] = input_data["overdue_data"][col].astype(
                                ideal_overdue_data_type[col]
                            )
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in Overdue Bucketing Ruleset in {col} column! {str(e)}"
                )

        if len(input_data["cashflow_data_uploaded"]) > 0:
            try:
                ideal_cf_dtype = {
                    "extract_date": "datetime64[ns]",
                    "transaction_date": "datetime64[ns]",
                    "unique_reference_id": "object",
                    "reference_dimension": "object",
                    "cashflow_type": "object",
                    "cashflow_status": "object",
                    "cashflow": "float64",
                    "time_to_maturity": "float64",
                    "discount_factor": "float64",
                    "present_value": "float64",
                    "currency": "object",
                    "asset_liability_type": "object",
                    "product_variant_name": "object",
                    "fund": "object",
                    "portfolio": "object",
                    "entity": "object",
                    "cohort": "object",
                    "cf_analysis_id": "object",
                    "position_id": "object",
                }

                for col in input_data["cashflow_data_uploaded"].columns.tolist():
                    if col in ideal_cf_dtype:
                        if ideal_cf_dtype[col] in ["int64", "float64"]:
                            input_data["cashflow_data_uploaded"][col] = pd.to_numeric(
                                input_data["cashflow_data_uploaded"][col], errors="coerce"
                            )
                        else:
                            input_data["cashflow_data_uploaded"][col] = input_data["cashflow_data_uploaded"][
                                col
                            ].astype(ideal_cf_dtype[col])
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in Uploaded Cashflows data in {col} column! {str(e)}"
                )
        if len(input_data["repayment_data"]) > 0:
            try:
                ideal_repayment_dtype = {
                    "position_id": "object",
                    "version_no": "object",
                    "payment_date": "datetime64[ns]",
                    "payment_amount": "int64",
                    "scenario_analysis_id": "object",
                    "currency_code": "object",
                }

                for col in input_data["repayment_data"].columns.tolist():
                    if col in ideal_repayment_dtype:
                        if ideal_repayment_dtype[col] in ["int64", "float64"]:
                            input_data["repayment_data"][col] = pd.to_numeric(
                                input_data["repayment_data"][col], errors="coerce"
                            )
                        else:
                            input_data["repayment_data"][col] = input_data["repayment_data"][col].astype(
                                ideal_repayment_dtype[col]
                            )
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in Repayment schedule data in {col} column! {str(e)}"
                )
        if len(input_data["product_model_mapper_table"]) > 0:
            try:
                ideal_pr_to_model_dtype = {"product_variant_name": "object", "model_code": "object"}

                for col in input_data["product_model_mapper_table"].columns.tolist():
                    if col in ideal_pr_to_model_dtype:
                        if ideal_pr_to_model_dtype[col] in ["int64", "float64"]:
                            input_data["product_model_mapper_table"][col] = pd.to_numeric(
                                input_data["product_model_mapper_table"][col], errors="coerce"
                            )
                        else:
                            input_data["product_model_mapper_table"][col] = input_data[
                                "product_model_mapper_table"
                            ][col].astype(ideal_pr_to_model_dtype[col])
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data_validation_errors.append(
                    f"Data validation error in Product to model mapping data in {col} column! {str(e)}"
                )
        return input_data, data_validation_errors
    else:
        return input_data, ""
