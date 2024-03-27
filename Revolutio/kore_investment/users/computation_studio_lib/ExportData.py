from datetime import datetime
import json
import logging
import os
import pickle

import pandas as pd

from config.settings.base import PLATFORM_FILE_PATH
from kore_investment.users.computations import (
    Data_replica_utilities,
    dynamic_model_create,
    standardised_functions,
)
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    read_data_func,
    update_data_func,
    update_data_func_multiple,
)
from kore_investment.users.computations.db_connection_handlers import (
    mssql_engine_generator,
    oracle_engine_generator,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.computations.file_storage import computation_storage
import redis

from . import ApiIntegration


def exportMain(
    request, config_dict, data, exp_run_model, scenario_name, scenario_id, elementid, transaction_id, run_step
):
    if "output_type" in list(config_dict["inputs"].keys()):
        output_type_export = config_dict["inputs"]["output_type"]
    else:
        output_type_export = "individual_export"

    if output_type_export == "multi_export":
        parent_element = config_dict["inputs"]["data"]
        computation_storage(data, "exception", parent_element)
        output_msg = exportDataRunModel(
            request,
            config_dict,
            data,
            output_type_export,
            scenario_name,
            scenario_id,
            elementid,
            transaction_id,
            exp_run_model,
            run_step,
        )
        data = config_dict
    else:
        parent_element = config_dict["inputs"]["data"]
        if type(parent_element) == dict:
            parent_element = list(parent_element.values())[0]
        computation_storage(data, "dataframe", parent_element)
        output_msg = exportDataRunModel(
            request,
            config_dict,
            data,
            output_type_export,
            scenario_name,
            scenario_id,
            elementid,
            transaction_id,
            exp_run_model,
            run_step,
        )
    return data, output_type_export, [], output_msg


def exportDataRunModel(
    request,
    config_dict,
    data,
    output_type_export,
    scenario_name,
    scenario_id,
    element_id,
    transaction_id,
    exp_run_model,
    run_step,
):
    temp_dict = {}
    temp_dict["output_msg"] = ""
    temp_dict["total_data"] = ""
    if output_type_export == "multi_export":
        msg = []
        multi_export_config = config_dict["inputs"]["multi_export_config"]
        for key, export_dict in multi_export_config.items():
            if len(export_dict.keys()) > 0:
                if export_dict["exportTo"] == "Database" and scenario_name is None:
                    t_name = config_dict["inputs"]["tableName"]
                    actmodelName = dynamic_model_create.get_model_class(t_name, request)
                    fieldList = {
                        field.verbose_name.title(): field.name for field in actmodelName.concrete_fields
                    }
                    for field in actmodelName.concrete_fields:
                        fieldList[field.verbose_name] = field.name
                    fieldList["Approval Status"] = "approval_status"
                    fieldList["Approved By"] = "approved_by"
                    table_name = export_dict["tableName"]
                    req_data = data[0][key]
                    if isinstance(req_data, (dict, list)):
                        req_data = pd.DataFrame(req_data)
                    sql_data = req_data.copy()
                    if export_dict.get("exportType"):
                        export_type = export_dict["exportType"]
                    else:
                        export_type = "append"
                    sql_data.rename(columns=fieldList, inplace=True)
                    sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                    if export_type in ["append", "replace"]:
                        columnList = export_dict["columnList"]
                        if len(columnList) > 0:
                            sql_data = sql_data.loc[:, columnList]
                        try:
                            sql_data["created_date"] = datetime.now()
                            sql_data["modified_date"] = datetime.now()
                            sql_data["created_by"] = request.user.username
                            sql_data["modified_by"] = request.user.username
                            sql_data["active_from"] = datetime.now()
                            sql_data["active_to"] = datetime(2099, 7, 5)

                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="create",
                                export_type=export_type,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                msg.append(
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                                data_handling(
                                    request,
                                    sql_data,
                                    table_name,
                                    if_exists=export_type,
                                    if_app_db=True,
                                )
                                msg.append(f"Data exported to {table_name} table successfully")
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            msg.append(f"Failed to export data to {table_name} table")
                    elif export_type == "update":
                        identifier_column = export_dict["selectUpdateIdentifierCol"]
                        update_column = export_dict["selectUpdateCol"]
                        try:
                            update_config_dict = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": table_name,
                                    "Columns": [],
                                },
                                "condition": [],
                            }
                            for id_index, id_col in enumerate(identifier_column):
                                if id_col in fieldList:
                                    id_col = fieldList[id_col]
                                condition_dict = {
                                    "column_name": id_col,
                                    "condition": "Equal to",
                                    "and_or": "",
                                }
                                if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                    condition_dict["and_or"] = "AND"
                                update_config_dict["condition"].append(condition_dict)

                            for up_index, up_col in enumerate(update_column):
                                if up_col in fieldList:
                                    up_col = fieldList[up_col]
                                column_dict = {
                                    "column_name": up_col,
                                    "separator": ",",
                                }
                                update_config_dict["inputs"]["Columns"].append(column_dict)
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_date",
                                    "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "separator": ",",
                                }
                            )
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_by",
                                    "input_value": request.user.username,
                                    "separator": "",
                                }
                            )
                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="update",
                                export_data="yes",
                                export_type=export_type,
                                export_update_column=update_column,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                msg.append(
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                                update_data_func_multiple(
                                    request, update_config_dict, sql_data.fillna("NULL"), if_app_db=True
                                )
                                msg.append(f"Data in {table_name} table updated successfully")

                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            msg.append(f"Failed to update data in {table_name} table")

                    elif export_type == "update_else_insert":
                        identifier_column = export_dict["selectUpdateIdentifierCol"]
                        update_column = export_dict["selectUpdateCol"]
                        try:
                            update_config_dict = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": table_name,
                                    "Columns": [],
                                },
                                "condition": [],
                            }
                            for id_index, id_col in enumerate(identifier_column):
                                if id_col in fieldList:
                                    id_col = fieldList[id_col]
                                condition_dict = {
                                    "column_name": id_col,
                                    "condition": "Equal to",
                                    "and_or": "",
                                }
                                if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                    condition_dict["and_or"] = "AND"
                                update_config_dict["condition"].append(condition_dict)

                            for up_index, up_col in enumerate(update_column):
                                if up_col in fieldList:
                                    up_col = fieldList[up_col]
                                column_dict = {
                                    "column_name": up_col,
                                    "separator": ",",
                                }
                                update_config_dict["inputs"]["Columns"].append(column_dict)
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_date",
                                    "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "separator": ",",
                                }
                            )
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_by",
                                    "input_value": request.user.username,
                                    "separator": "",
                                }
                            )
                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="update",
                                export_data="yes",
                                export_type=export_type,
                                export_update_column=update_column,
                                upsert=True,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                msg.append(
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                                update_data_func_multiple(
                                    request,
                                    update_config_dict,
                                    sql_data.fillna("NULL"),
                                    if_app_db=True,
                                    if_update_else_insert=True,
                                )
                                msg.append(f"Data in {table_name} table updated successfully")

                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            msg.append(f"Failed to update data in {table_name} table")

                    else:
                        pass
                elif export_dict["exportTo"] == "Database" and scenario_name:
                    base_table_name = export_dict["tableName"]
                    actmodelName = dynamic_model_create.get_model_class(base_table_name, request)
                    field_list = {
                        field.verbose_name.title(): field.name for field in actmodelName.concrete_fields
                    }
                    for field in actmodelName.concrete_fields:
                        field_list[field.verbose_name] = field.name
                    field_list["Approval Status"] = "approval_status"
                    field_list["Approved By"] = "approved_by"
                    req_data = data[0][key]
                    if isinstance(req_data, (dict, list)):
                        req_data = pd.DataFrame(req_data)
                    sql_data = req_data.copy()
                    sc_output_table_name = base_table_name + "_scenario_output"
                    sql_data["scenario_id"] = scenario_id

                    sql_data.rename(columns=field_list, inplace=True)
                    sc_table_check = read_data_func(
                        request,
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
                        model_class = dynamic_model_create.get_model_class(sc_output_table_name, request)
                        if export_dict.get("exportType"):
                            export_type = export_dict["exportType"]
                        else:
                            export_type = "append"
                        table_name = sc_output_table_name
                        fieldList = {
                            field.verbose_name.title(): field.name for field in model_class.concrete_fields
                        }
                        if export_type in ["append", "replace"]:
                            columnList = export_dict["columnList"]
                            if len(columnList) > 0:
                                sql_data = sql_data.loc[:, columnList]
                            try:
                                sql_data["created_date"] = datetime.now()
                                sql_data["modified_date"] = datetime.now()
                                sql_data["created_by"] = request.user.username
                                sql_data["modified_by"] = request.user.username
                                sql_data["active_from"] = datetime.now()
                                sql_data["active_to"] = datetime(2099, 7, 5)

                                f_data = standardised_functions.data_preprocessing(
                                    sql_data,
                                    table_name,
                                    request,
                                    customvalidation={},
                                    message_show="no",
                                    user_operation="create",
                                    export_type=export_type,
                                )
                                sql_data = f_data.data_validation(message_out=False)

                                if isinstance(sql_data, list):
                                    msg.append(
                                        f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                    )
                                elif isinstance(sql_data, pd.DataFrame):
                                    sql_data = sql_data[
                                        [i for i in sql_data.columns if i in fieldList.values()]
                                    ]
                                    data_handling(
                                        request,
                                        sql_data,
                                        table_name,
                                        if_exists=export_type,
                                        if_app_db=True,
                                    )
                                    msg.append(f"Data exported to {table_name} table successfully")
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                msg.append(f"Failed to export data to {table_name} table")
                        elif export_type == "update":
                            identifier_column = export_dict["selectUpdateIdentifierCol"]
                            update_column = export_dict["selectUpdateCol"]
                            try:
                                update_config_dict = {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": [],
                                    },
                                    "condition": [],
                                }
                                for id_index, id_col in enumerate(identifier_column):
                                    if id_col in fieldList:
                                        id_col = fieldList[id_col]
                                    condition_dict = {
                                        "column_name": id_col,
                                        "condition": "Equal to",
                                        "and_or": "",
                                    }
                                    if len(identifier_column) > 0 and (
                                        id_index != (len(identifier_column) - 1)
                                    ):
                                        condition_dict["and_or"] = "AND"
                                    update_config_dict["condition"].append(condition_dict)

                                for up_index, up_col in enumerate(update_column):
                                    if up_col in fieldList:
                                        up_col = fieldList[up_col]
                                    column_dict = {
                                        "column_name": up_col,
                                        "separator": ",",
                                    }
                                    if up_index == len(update_column) - 1:
                                        column_dict["separator"] = ""
                                    else:
                                        pass
                                    update_config_dict["inputs"]["Columns"].append(column_dict)

                                f_data = standardised_functions.data_preprocessing(
                                    sql_data,
                                    table_name,
                                    request,
                                    customvalidation={},
                                    message_show="no",
                                    user_operation="update",
                                    export_data="yes",
                                    export_type=export_type,
                                    export_update_column=update_column,
                                )
                                sql_data = f_data.data_validation(message_out=False)

                                if isinstance(sql_data, list):
                                    msg.append(
                                        f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                    )
                                elif isinstance(sql_data, pd.DataFrame):
                                    sql_data = sql_data[
                                        [i for i in sql_data.columns if i in fieldList.values()]
                                    ]

                                    update_data_func_multiple(
                                        request,
                                        update_config_dict,
                                        sql_data.fillna("NULL"),
                                        if_app_db=True,
                                    )
                                    update_data_func(
                                        request=request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": table_name,
                                                "Columns": [
                                                    {
                                                        "column_name": "modified_date",
                                                        "input_value": datetime.now().strftime(
                                                            "%Y-%m-%d %H:%M:%S"
                                                        ),
                                                        "separator": ",",
                                                    },
                                                    {
                                                        "column_name": "modified_by",
                                                        "input_value": request.user.username,
                                                        "separator": "",
                                                    },
                                                ],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": id_col,
                                                    "condition": "IN",
                                                    "input_value": sql_data[id_col]
                                                    .fillna("NULL")
                                                    .unique()
                                                    .tolist(),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                    msg.append(f"Data in {table_name} table updated successfully")

                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                msg.append(f"Failed to update data in {table_name} table")
                        elif export_type == "update_else_insert":
                            identifier_column = export_dict["selectUpdateIdentifierCol"]
                            update_column = export_dict["selectUpdateCol"]
                            try:
                                update_config_dict = {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": [],
                                    },
                                    "condition": [],
                                }
                                for id_index, id_col in enumerate(identifier_column):
                                    if id_col in fieldList:
                                        id_col = fieldList[id_col]
                                    condition_dict = {
                                        "column_name": id_col,
                                        "condition": "Equal to",
                                        "and_or": "",
                                    }
                                    if len(identifier_column) > 0 and (
                                        id_index != (len(identifier_column) - 1)
                                    ):
                                        condition_dict["and_or"] = "AND"
                                    update_config_dict["condition"].append(condition_dict)

                                for up_index, up_col in enumerate(update_column):
                                    if up_col in fieldList:
                                        up_col = fieldList[up_col]
                                    column_dict = {
                                        "column_name": up_col,
                                        "separator": ",",
                                    }
                                    if up_index == len(update_column) - 1:
                                        column_dict["separator"] = ""
                                    else:
                                        pass
                                    update_config_dict["inputs"]["Columns"].append(column_dict)

                                f_data = standardised_functions.data_preprocessing(
                                    sql_data,
                                    table_name,
                                    request,
                                    customvalidation={},
                                    message_show="no",
                                    user_operation="update",
                                    export_data="yes",
                                    export_type=export_type,
                                    export_update_column=update_column,
                                    upsert=True,
                                )
                                sql_data = f_data.data_validation(message_out=False)

                                if isinstance(sql_data, list):
                                    msg.append(
                                        f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                    )
                                elif isinstance(sql_data, pd.DataFrame):
                                    sql_data = sql_data[
                                        [i for i in sql_data.columns if i in fieldList.values()]
                                    ]

                                    update_data_func_multiple(
                                        request,
                                        update_config_dict,
                                        sql_data,
                                        if_app_db=True,
                                        if_update_else_insert=True,
                                    )
                                    update_data_func(
                                        request=request,
                                        config_dict={
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": table_name,
                                                "Columns": [
                                                    {
                                                        "column_name": "modified_date",
                                                        "input_value": datetime.now().strftime(
                                                            "%Y-%m-%d %H:%M:%S"
                                                        ),
                                                        "separator": ",",
                                                    },
                                                    {
                                                        "column_name": "modified_by",
                                                        "input_value": request.user.username,
                                                        "separator": "",
                                                    },
                                                ],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": id_col,
                                                    "condition": "IN",
                                                    "input_value": sql_data[id_col]
                                                    .fillna("NULL")
                                                    .unique()
                                                    .tolist(),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                    msg.append(f"Data in {table_name} table updated successfully")

                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                msg.append(f"Failed to update data in {table_name} table")
                        else:
                            pass
                    else:
                        # Create scenario table
                        base_table_structure = read_data_func(
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
                            sc_table_fields = dynamic_model_create.create_table_dict_creator(
                                base_table_structure
                            )
                            dynamic_model_create.create_table_sql(
                                sc_output_table_name, sc_table_fields, request
                            )
                            model_class = dynamic_model_create.get_model_class(sc_output_table_name, request)
                            if export_dict.get("exportType"):
                                export_type = export_dict["exportType"]
                            else:
                                export_type = "append"
                            table_name = sc_output_table_name
                            fieldList = {
                                field.verbose_name.title(): field.name
                                for field in model_class.concrete_fields
                            }
                            if export_type in ["append", "replace"]:
                                columnList = export_dict["columnList"]
                                if len(columnList) > 0:
                                    sql_data = sql_data.loc[:, columnList]
                                try:
                                    sql_data["created_date"] = datetime.now()
                                    sql_data["modified_date"] = datetime.now()
                                    sql_data["created_by"] = request.user.username
                                    sql_data["modified_by"] = request.user.username
                                    sql_data["active_from"] = datetime.now()
                                    sql_data["active_to"] = datetime(2099, 7, 5)

                                    f_data = standardised_functions.data_preprocessing(
                                        sql_data,
                                        table_name,
                                        request,
                                        customvalidation={},
                                        message_show="no",
                                        user_operation="create",
                                        export_type=export_type,
                                    )
                                    sql_data = f_data.data_validation(message_out=False)

                                    if isinstance(sql_data, list):
                                        msg.append(
                                            f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                        )
                                    elif isinstance(sql_data, pd.DataFrame):
                                        sql_data = sql_data[
                                            [i for i in sql_data.columns if i in fieldList.values()]
                                        ]
                                        data_handling(
                                            request,
                                            sql_data,
                                            table_name,
                                            if_exists=export_type,
                                            if_app_db=True,
                                        )
                                        msg.append(f"Data exported to {table_name} table successfully")
                                except Exception as e:
                                    logging.warning(f"Following exception occured - {e}")
                                    msg.append(f"Failed to export data to {table_name} table")
                            elif export_type == "update":
                                identifier_column = export_dict["selectUpdateIdentifierCol"]
                                update_column = export_dict["selectUpdateCol"]
                                try:
                                    update_config_dict = {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": table_name,
                                            "Columns": [],
                                        },
                                        "condition": [],
                                    }
                                    for id_index, id_col in enumerate(identifier_column):
                                        if id_col in fieldList:
                                            id_col = fieldList[id_col]
                                        condition_dict = {
                                            "column_name": id_col,
                                            "condition": "Equal to",
                                            "and_or": "",
                                        }
                                        if len(identifier_column) > 0 and (
                                            id_index != (len(identifier_column) - 1)
                                        ):
                                            condition_dict["and_or"] = "AND"
                                        update_config_dict["condition"].append(condition_dict)

                                    for up_index, up_col in enumerate(update_column):
                                        if up_col in fieldList:
                                            up_col = fieldList[up_col]
                                        column_dict = {
                                            "column_name": up_col,
                                            "separator": ",",
                                        }
                                        update_config_dict["inputs"]["Columns"].append(column_dict)
                                    update_config_dict["inputs"]["Columns"].append(
                                        {
                                            "column_name": "modified_date",
                                            "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "separator": ",",
                                        }
                                    )
                                    update_config_dict["inputs"]["Columns"].append(
                                        {
                                            "column_name": "modified_by",
                                            "input_value": request.user.username,
                                            "separator": "",
                                        }
                                    )
                                    f_data = standardised_functions.data_preprocessing(
                                        sql_data,
                                        table_name,
                                        request,
                                        customvalidation={},
                                        message_show="no",
                                        user_operation="update",
                                        export_data="yes",
                                        export_type=export_type,
                                        export_update_column=update_column,
                                    )
                                    sql_data = f_data.data_validation(message_out=False)

                                    if isinstance(sql_data, list):
                                        msg.append(
                                            f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                        )
                                    elif isinstance(sql_data, pd.DataFrame):
                                        sql_data = sql_data[
                                            [i for i in sql_data.columns if i in fieldList.values()]
                                        ]
                                        update_data_func_multiple(
                                            request,
                                            update_config_dict,
                                            sql_data.fillna("NULL"),
                                            if_app_db=True,
                                        )
                                        msg.append(f"Data in {table_name} table updated successfully")

                                except Exception as e:
                                    logging.warning(f"Following exception occured - {e}")
                                    msg.append(f"Failed to update data in {table_name} table")
                            elif export_type == "update_else_insert":
                                identifier_column = export_dict["selectUpdateIdentifierCol"]
                                update_column = export_dict["selectUpdateCol"]
                                try:
                                    update_config_dict = {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": table_name,
                                            "Columns": [],
                                        },
                                        "condition": [],
                                    }
                                    for id_index, id_col in enumerate(identifier_column):
                                        if id_col in fieldList:
                                            id_col = fieldList[id_col]
                                        condition_dict = {
                                            "column_name": id_col,
                                            "condition": "Equal to",
                                            "and_or": "",
                                        }
                                        if len(identifier_column) > 0 and (
                                            id_index != (len(identifier_column) - 1)
                                        ):
                                            condition_dict["and_or"] = "AND"
                                        update_config_dict["condition"].append(condition_dict)

                                    for up_index, up_col in enumerate(update_column):
                                        if up_col in fieldList:
                                            up_col = fieldList[up_col]
                                        column_dict = {
                                            "column_name": up_col,
                                            "separator": ",",
                                        }
                                        update_config_dict["inputs"]["Columns"].append(column_dict)
                                    update_config_dict["inputs"]["Columns"].append(
                                        {
                                            "column_name": "modified_date",
                                            "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "separator": ",",
                                        }
                                    )
                                    update_config_dict["inputs"]["Columns"].append(
                                        {
                                            "column_name": "modified_by",
                                            "input_value": request.user.username,
                                            "separator": "",
                                        }
                                    )
                                    f_data = standardised_functions.data_preprocessing(
                                        sql_data,
                                        table_name,
                                        request,
                                        customvalidation={},
                                        message_show="no",
                                        user_operation="update",
                                        export_data="yes",
                                        export_type=export_type,
                                        export_update_column=update_column,
                                        upsert=True,
                                    )
                                    sql_data = f_data.data_validation(message_out=False)

                                    if isinstance(sql_data, list):
                                        msg.append(
                                            f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                        )
                                    elif isinstance(sql_data, pd.DataFrame):
                                        sql_data = sql_data[
                                            [i for i in sql_data.columns if i in fieldList.values()]
                                        ]
                                        update_data_func_multiple(
                                            request,
                                            update_config_dict,
                                            sql_data.fillna("NULL"),
                                            if_app_db=True,
                                            if_update_else_insert=True,
                                        )
                                        msg.append(f"Data in {table_name} table updated successfully")

                                except Exception as e:
                                    logging.warning(f"Following exception occured - {e}")
                                    msg.append(f"Failed to update data in {table_name} table")
                            else:
                                pass
                else:
                    pass

        op_str = ""
        for i in msg:
            op_str += i + ". "
        temp_dict["output_msg"] = op_str
    else:
        if config_dict["inputs"]["exportTo"] == "Database" and scenario_name is None:
            t_name = config_dict["inputs"]["tableName"]
            actmodelName = dynamic_model_create.get_model_class(t_name, request)
            fieldList = {field.verbose_name.title(): field.name for field in actmodelName.concrete_fields}
            chunk_size = config_dict["inputs"].get("chunk_size", 10**5)
            fast_executemany = config_dict["inputs"].get("fast_executemany", False)
            for field in actmodelName.concrete_fields:
                fieldList[field.verbose_name] = field.name
            fieldList["Approval Status"] = "approval_status"
            fieldList["Approved By"] = "approved_by"
            table_name = config_dict["inputs"]["tableName"]
            sql_data = data.copy()
            if config_dict["inputs"].get("exportType"):
                export_type = config_dict["inputs"]["exportType"]
            else:
                export_type = "append"
            sql_data.rename(columns=fieldList, inplace=True)
            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
            if export_type in ["append", "replace"]:
                columnList = config_dict["inputs"]["columnList"]
                if len(columnList) > 0:
                    sql_data = sql_data.loc[:, columnList]
                try:
                    sql_data["created_date"] = datetime.now()
                    sql_data["modified_date"] = datetime.now()
                    sql_data["created_by"] = request.user.username
                    sql_data["modified_by"] = request.user.username
                    sql_data["active_from"] = datetime.now()
                    sql_data["active_to"] = datetime(2099, 7, 5)
                    f_data = standardised_functions.data_preprocessing(
                        sql_data,
                        table_name,
                        request,
                        customvalidation={},
                        message_show="no",
                        user_operation="create",
                        export_type=export_type,
                    )
                    sql_data = f_data.data_validation(message_out=False)
                    if isinstance(sql_data, list):
                        temp_dict["output_msg"] = (
                            f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                        )
                    elif isinstance(sql_data, pd.DataFrame):
                        sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                        if exp_run_model:
                            FinalData_, len__, status__ = standardised_functions.decisionBox(
                                element_id,
                                t_name,
                                sql_data,
                                request,
                                transaction_id=transaction_id,
                                type="create",
                            )
                            if not FinalData_.empty and status__ == "pass":
                                data_handling(
                                    request,
                                    FinalData_,
                                    table_name,
                                    if_exists=export_type,
                                    if_app_db=True,
                                    chunksize=chunk_size,
                                    fast_executemany=fast_executemany,
                                )
                                multi_select_field_dict = {}
                                is_multi_select_field = False
                                for field in actmodelName.concrete_fields:
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
                                                        "input_value": table_name_replica + "_mul",
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )
                                        if len(mt) > 0:
                                            records = len(FinalData_)
                                            recent_record_ids = read_data_func(
                                                request,
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
                                            FinalData_["id"] = recent_record_ids

                                            Data_replica_utilities.insert_delimited_data(
                                                elementID="",
                                                request=request,
                                                table_name_replica=table_name_replica,
                                                multi_select_tables=multi_select_tables,
                                                mutli_select_cols=mutli_select_cols,
                                                mutli_select_attr=mutli_select_attr,
                                                existingData=FinalData_,
                                            )
                                        else:
                                            pass
                                else:
                                    pass
                            if status__ == "pass":
                                temp_dict["total_data"] = len(sql_data) - len(FinalData_)
                                if len(sql_data) == len(FinalData_):
                                    message = f"Data exported to {table_name} successfully"
                                elif len(FinalData_) == 0:
                                    message = "Data sent for approval successfully"
                                else:
                                    message = f"{len(FinalData_)} row(s) exported to {table_name} and {len(sql_data) - len(FinalData_)} row(s) has been sent for approval."
                                temp_dict["output_msg"] = message
                            else:
                                temp_dict["output_msg"] = f"Failed!"
                        else:
                            data_handling(
                                request,
                                sql_data,
                                table_name,
                                if_exists=export_type,
                                if_app_db=True,
                                chunksize=chunk_size,
                                fast_executemany=fast_executemany,
                            )

                            if run_step:
                                multi_select_field_dict = {}
                                is_multi_select_field = False
                                for field in actmodelName.concrete_fields:
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
                                                        "input_value": table_name_replica + "_mul",
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                        )
                                        if len(mt) > 0:
                                            records = len(sql_data)
                                            recent_record_ids = read_data_func(
                                                request,
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
                                            sql_data["id"] = recent_record_ids

                                            Data_replica_utilities.insert_delimited_data(
                                                elementID="",
                                                request=request,
                                                table_name_replica=table_name_replica,
                                                multi_select_tables=multi_select_tables,
                                                mutli_select_cols=mutli_select_cols,
                                                mutli_select_attr=mutli_select_attr,
                                                existingData=sql_data,
                                            )
                                        else:
                                            pass
                                else:
                                    pass
                            temp_dict["output_msg"] = f"Data exported to {table_name} table successfully"
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    temp_dict["output_msg"] = f"Failed to export data to {table_name} table"
            elif export_type == "update":
                identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                update_column = config_dict["inputs"]["selectUpdateCol"]

                if exp_run_model:
                    f_data = standardised_functions.data_preprocessing(
                        sql_data,
                        table_name,
                        request,
                        customvalidation={},
                        message_show="no",
                        user_operation="update",
                        export_data="yes",
                        export_type=export_type,
                        export_update_column=update_column,
                    )
                    sql_data = f_data.data_validation(message_out=False)

                    if isinstance(sql_data, list):
                        temp_dict["output_msg"] = (
                            f"Failed to update data on {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                        )
                    elif isinstance(sql_data, pd.DataFrame):
                        origData = sql_data

                        sql_data, len__, status__ = standardised_functions.decisionBox(
                            element_id,
                            table_name,
                            sql_data,
                            request,
                            transaction_id=transaction_id,
                            type="update",
                            identifier_column=identifier_column,
                            update_column=update_column,
                        )
                        FinalData_ = sql_data
                        if not FinalData_.empty and status__ == "pass":
                            try:
                                update_config_dict = {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": [],
                                    },
                                    "condition": [],
                                }
                                for id_index, id_col in enumerate(identifier_column):
                                    if id_col in fieldList:
                                        id_col = fieldList[id_col]
                                    condition_dict = {
                                        "column_name": id_col,
                                        "condition": "Equal to",
                                        "and_or": "",
                                    }
                                    if len(identifier_column) > 0 and (
                                        id_index != (len(identifier_column) - 1)
                                    ):
                                        condition_dict["and_or"] = "AND"
                                    update_config_dict["condition"].append(condition_dict)

                                for up_index, up_col in enumerate(update_column):
                                    if up_col in fieldList:
                                        up_col = fieldList[up_col]
                                    column_dict = {
                                        "column_name": up_col,
                                        "separator": ",",
                                    }
                                    update_config_dict["inputs"]["Columns"].append(column_dict)
                                update_config_dict["inputs"]["Columns"].append(
                                    {
                                        "column_name": "modified_date",
                                        "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "separator": ",",
                                    }
                                )
                                update_config_dict["inputs"]["Columns"].append(
                                    {
                                        "column_name": "modified_by",
                                        "input_value": request.user.username,
                                        "separator": "",
                                    }
                                )
                                update_data_func_multiple(
                                    request,
                                    update_config_dict,
                                    FinalData_.fillna("NULL"),
                                    if_app_db=True,
                                )

                                temp_dict["total_data"] = len(origData) - len(FinalData_)
                                temp_dict["output_msg"] = (
                                    f"{len(FinalData_)} number of row have been updated to {table_name} table, {len(origData) - len(FinalData_)} row of data has been sent for approval."
                                )
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                temp_dict["output_msg"] = f"Failed to update data in {table_name} table"

                        elif FinalData_.empty and status__ == "pass":
                            temp_dict["total_data"] = len(origData)
                            temp_dict["output_msg"] = (
                                f"{len(origData)} row of data has been sent for approval."
                            )
                        else:
                            # pass
                            temp_dict["output_msg"] = f"Failed!"
                    else:
                        temp_dict["output_msg"] = f"Failed!"
                else:
                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            if id_col in fieldList:
                                id_col = fieldList[id_col]
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            if up_col in fieldList:
                                up_col = fieldList[up_col]
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_date",
                                "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "separator": ",",
                            }
                        )
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_by",
                                "input_value": request.user.username,
                                "separator": "",
                            }
                        )
                        f_data = standardised_functions.data_preprocessing(
                            sql_data,
                            table_name,
                            request,
                            customvalidation={},
                            message_show="no",
                            user_operation="update",
                            export_data="yes",
                            export_type=export_type,
                            export_update_column=update_column,
                        )
                        sql_data = f_data.data_validation(message_out=False)

                        if isinstance(sql_data, list):
                            temp_dict["output_msg"] = (
                                f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                            )
                        elif isinstance(sql_data, pd.DataFrame):
                            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                            update_data_func_multiple(
                                request,
                                update_config_dict,
                                sql_data.fillna("NULL"),
                                if_app_db=True,
                            )
                            temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
            elif export_type == "update_else_insert":
                identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                update_column = config_dict["inputs"]["selectUpdateCol"]

                if exp_run_model:
                    f_data = standardised_functions.data_preprocessing(
                        sql_data,
                        table_name,
                        request,
                        customvalidation={},
                        message_show="no",
                        user_operation="update",
                        export_data="yes",
                        export_type=export_type,
                        export_update_column=update_column,
                    )
                    sql_data = f_data.data_validation(message_out=False)

                    if isinstance(sql_data, list):
                        temp_dict["output_msg"] = (
                            f"Failed to update data on {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                        )
                    elif isinstance(sql_data, pd.DataFrame):
                        sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                        origData = sql_data

                        sql_data, len__, status__ = standardised_functions.decisionBox(
                            element_id,
                            table_name,
                            sql_data,
                            request,
                            transaction_id=transaction_id,
                            type="update",
                            identifier_column=identifier_column,
                            update_column=update_column,
                        )
                        FinalData_ = sql_data
                        if not FinalData_.empty and status__ == "pass":
                            try:
                                update_config_dict = {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": [],
                                    },
                                    "condition": [],
                                }
                                for id_index, id_col in enumerate(identifier_column):
                                    if id_col in fieldList:
                                        id_col = fieldList[id_col]
                                    condition_dict = {
                                        "column_name": id_col,
                                        "condition": "Equal to",
                                        "and_or": "",
                                    }
                                    if len(identifier_column) > 0 and (
                                        id_index != (len(identifier_column) - 1)
                                    ):
                                        condition_dict["and_or"] = "AND"
                                    update_config_dict["condition"].append(condition_dict)

                                for up_index, up_col in enumerate(update_column):
                                    if up_col in fieldList:
                                        up_col = fieldList[up_col]
                                    column_dict = {
                                        "column_name": up_col,
                                        "separator": ",",
                                    }
                                    update_config_dict["inputs"]["Columns"].append(column_dict)
                                update_config_dict["inputs"]["Columns"].append(
                                    {
                                        "column_name": "modified_date",
                                        "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "separator": ",",
                                    }
                                )
                                update_config_dict["inputs"]["Columns"].append(
                                    {
                                        "column_name": "modified_by",
                                        "input_value": request.user.username,
                                        "separator": "",
                                    }
                                )
                                FinalData_["created_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                FinalData_["modified_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                FinalData_["created_by"] = request.user.username
                                FinalData_["modified_by"] = request.user.username
                                FinalData_["active_from"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                FinalData_["active_to"] = datetime(2099, 7, 5).strftime("%Y-%m-%d %H:%M:%S")
                                update_data_func_multiple(
                                    request,
                                    update_config_dict,
                                    FinalData_,
                                    if_app_db=True,
                                    if_update_else_insert=True,
                                )

                                temp_dict["total_data"] = len(origData) - len(FinalData_)
                                temp_dict["output_msg"] = (
                                    f"{len(FinalData_)} number of row have been updated to {table_name} table, {len(origData) - len(FinalData_)} row of data has been sent for approval."
                                )
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")
                                temp_dict["output_msg"] = f"Failed to update data in {table_name} table"

                        elif FinalData_.empty and status__ == "pass":
                            temp_dict["total_data"] = len(origData)
                            temp_dict["output_msg"] = (
                                f"{len(origData)} row of data has been sent for approval."
                            )
                        else:
                            # pass
                            temp_dict["output_msg"] = f"Failed!"
                    else:
                        temp_dict["output_msg"] = f"Failed!"
                else:
                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            if id_col in fieldList:
                                id_col = fieldList[id_col]
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            if up_col in fieldList:
                                up_col = fieldList[up_col]
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_date",
                                "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "separator": ",",
                            }
                        )
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_by",
                                "input_value": request.user.username,
                                "separator": "",
                            }
                        )

                        f_data = standardised_functions.data_preprocessing(
                            sql_data,
                            table_name,
                            request,
                            customvalidation={},
                            message_show="no",
                            user_operation="update",
                            export_data="yes",
                            export_type=export_type,
                            export_update_column=update_column,
                            upsert=True,
                        )
                        sql_data = f_data.data_validation(message_out=False)

                        if isinstance(sql_data, list):
                            temp_dict["output_msg"] = (
                                f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                            )
                        elif isinstance(sql_data, pd.DataFrame):
                            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]
                            sql_data["created_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sql_data["modified_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sql_data["created_by"] = request.user.username
                            sql_data["modified_by"] = request.user.username
                            sql_data["active_from"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            sql_data["active_to"] = datetime(2099, 7, 5).strftime("%Y-%m-%d %H:%M:%S")
                            update_data_func_multiple(
                                request,
                                update_config_dict,
                                sql_data,
                                if_app_db=True,
                                if_update_else_insert=True,
                            )
                            temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
            else:
                pass
        elif config_dict["inputs"]["exportTo"] == "Database" and scenario_name:
            base_table_name = config_dict["inputs"]["tableName"]
            actmodelName = dynamic_model_create.get_model_class(base_table_name, request)
            field_list = {field.verbose_name.title(): field.name for field in actmodelName.concrete_fields}
            chunk_size = config_dict["inputs"].get("chunk_size", 10**5)
            fast_executemany = config_dict["inputs"].get("fast_executemany", False)
            for field in actmodelName.concrete_fields:
                field_list[field.verbose_name] = field.name
            field_list["Approval Status"] = "approval_status"
            field_list["Approved By"] = "approved_by"
            sc_output_table_name = base_table_name + "_scenario_output"
            sql_data = data.copy()
            sql_data.rename(columns=field_list, inplace=True)
            sql_data = sql_data[[i for i in sql_data.columns if i in field_list.values()]]
            sql_data["scenario_id"] = scenario_id
            sc_table_check = read_data_func(
                request,
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
                model_class = dynamic_model_create.get_model_class(sc_output_table_name, request)
                if config_dict["inputs"].get("exportType"):
                    export_type = config_dict["inputs"]["exportType"]
                else:
                    export_type = "append"
                table_name = sc_output_table_name
                fieldList = {field.verbose_name.title(): field.name for field in model_class.concrete_fields}
                if export_type in ["append", "replace"]:
                    columnList = config_dict["inputs"]["columnList"]
                    if len(columnList) > 0:
                        sql_data = sql_data.loc[:, columnList]
                    try:
                        sql_data["created_date"] = datetime.now()
                        sql_data["modified_date"] = datetime.now()
                        sql_data["created_by"] = request.user.username
                        sql_data["modified_by"] = request.user.username
                        sql_data["active_from"] = datetime.now()
                        sql_data["active_to"] = datetime(2099, 7, 5)

                        f_data = standardised_functions.data_preprocessing(
                            sql_data,
                            table_name,
                            request,
                            customvalidation={},
                            message_show="no",
                            user_operation="create",
                            export_type=export_type,
                        )
                        sql_data = f_data.data_validation(message_out=False)

                        if isinstance(sql_data, list):
                            temp_dict["output_msg"] = (
                                f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                            )
                        elif isinstance(sql_data, pd.DataFrame):
                            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                            data_handling(
                                request,
                                sql_data,
                                table_name,
                                if_exists=export_type,
                                if_app_db=True,
                                chunksize=chunk_size,
                                fast_executemany=fast_executemany,
                            )

                            temp_dict["output_msg"] = f"Data exported to {table_name} table successfully"

                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = f"Failed to export data to {table_name} table"
                elif export_type == "update":
                    identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                    update_column = config_dict["inputs"]["selectUpdateCol"]

                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            if id_col in fieldList:
                                id_col = fieldList[id_col]
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            if up_col in fieldList:
                                up_col = fieldList[up_col]
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_date",
                                "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "separator": ",",
                            }
                        )
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_by",
                                "input_value": request.user.username,
                                "separator": "",
                            }
                        )

                        f_data = standardised_functions.data_preprocessing(
                            sql_data,
                            table_name,
                            request,
                            customvalidation={},
                            message_show="no",
                            user_operation="update",
                            export_data="yes",
                            export_type=export_type,
                            export_update_column=update_column,
                        )
                        sql_data = f_data.data_validation(message_out=False)

                        if isinstance(sql_data, list):
                            temp_dict["output_msg"] = (
                                f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                            )
                        elif isinstance(sql_data, pd.DataFrame):
                            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                            update_data_func_multiple(
                                request,
                                update_config_dict,
                                sql_data.fillna("NULL"),
                                if_app_db=True,
                            )
                            temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
                elif export_type == "update_else_insert":
                    identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                    update_column = config_dict["inputs"]["selectUpdateCol"]

                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            if id_col in fieldList:
                                id_col = fieldList[id_col]
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            if up_col in fieldList:
                                up_col = fieldList[up_col]
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_date",
                                "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "separator": ",",
                            }
                        )
                        update_config_dict["inputs"]["Columns"].append(
                            {
                                "column_name": "modified_by",
                                "input_value": request.user.username,
                                "separator": "",
                            }
                        )

                        f_data = standardised_functions.data_preprocessing(
                            sql_data,
                            table_name,
                            request,
                            customvalidation={},
                            message_show="no",
                            user_operation="update",
                            export_data="yes",
                            export_type=export_type,
                            export_update_column=update_column,
                            upsert=True,
                        )
                        sql_data = f_data.data_validation(message_out=False)

                        if isinstance(sql_data, list):
                            temp_dict["output_msg"] = (
                                f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                            )
                        elif isinstance(sql_data, pd.DataFrame):
                            sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                            update_data_func_multiple(
                                request,
                                update_config_dict,
                                sql_data.fillna("NULL"),
                                if_app_db=True,
                                if_update_else_insert=True,
                            )
                            temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
                else:
                    pass
            else:
                # Create scenario table
                base_table_structure = read_data_func(
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
                    sc_table_fields = dynamic_model_create.create_table_dict_creator(base_table_structure)
                    dynamic_model_create.create_table_sql(sc_output_table_name, sc_table_fields, request)
                    model_class = dynamic_model_create.get_model_class(sc_output_table_name, request)
                    if config_dict["inputs"].get("exportType"):
                        export_type = config_dict["inputs"]["exportType"]
                    else:
                        export_type = "append"
                    table_name = sc_output_table_name
                    fieldList = {
                        field.verbose_name.title(): field.name for field in model_class.concrete_fields
                    }
                    if export_type in ["append", "replace"]:
                        columnList = config_dict["inputs"]["columnList"]
                        if len(columnList) > 0:
                            sql_data = sql_data.loc[:, columnList]
                        try:
                            sql_data["created_date"] = datetime.now()
                            sql_data["modified_date"] = datetime.now()
                            sql_data["created_by"] = request.user.username
                            sql_data["modified_by"] = request.user.username
                            sql_data["active_from"] = datetime.now()
                            sql_data["active_to"] = datetime(2099, 7, 5)

                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="create",
                                export_type=export_type,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                temp_dict["output_msg"] = (
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                                data_handling(
                                    request,
                                    sql_data,
                                    table_name,
                                    if_exists=export_type,
                                    if_app_db=True,
                                    chunksize=chunk_size,
                                    fast_executemany=fast_executemany,
                                )

                                temp_dict["output_msg"] = f"Data exported to {table_name} table successfully"

                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            temp_dict["output_msg"] = f"Failed to export data to {table_name} table"
                    elif export_type == "update":
                        identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                        update_column = config_dict["inputs"]["selectUpdateCol"]

                        try:
                            update_config_dict = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": table_name,
                                    "Columns": [],
                                },
                                "condition": [],
                            }
                            for id_index, id_col in enumerate(identifier_column):
                                if id_col in fieldList:
                                    id_col = fieldList[id_col]
                                condition_dict = {
                                    "column_name": id_col,
                                    "condition": "Equal to",
                                    "and_or": "",
                                }
                                if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                    condition_dict["and_or"] = "AND"
                                update_config_dict["condition"].append(condition_dict)

                            for up_index, up_col in enumerate(update_column):
                                if up_col in fieldList:
                                    up_col = fieldList[up_col]
                                column_dict = {
                                    "column_name": up_col,
                                    "separator": ",",
                                }
                                update_config_dict["inputs"]["Columns"].append(column_dict)
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_date",
                                    "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "separator": ",",
                                }
                            )
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_by",
                                    "input_value": request.user.username,
                                    "separator": "",
                                }
                            )

                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="update",
                                export_data="yes",
                                export_type=export_type,
                                export_update_column=update_column,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                # pass
                                temp_dict["output_msg"] = (
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                                update_data_func_multiple(
                                    request,
                                    update_config_dict,
                                    sql_data.fillna("NULL"),
                                    if_app_db=True,
                                )
                                temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"

                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
                    elif export_type == "update_else_insert":
                        identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                        update_column = config_dict["inputs"]["selectUpdateCol"]

                        try:
                            update_config_dict = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": table_name,
                                    "Columns": [],
                                },
                                "condition": [],
                            }
                            for id_index, id_col in enumerate(identifier_column):
                                if id_col in fieldList:
                                    id_col = fieldList[id_col]
                                condition_dict = {
                                    "column_name": id_col,
                                    "condition": "Equal to",
                                    "and_or": "",
                                }
                                if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                    condition_dict["and_or"] = "AND"
                                update_config_dict["condition"].append(condition_dict)

                            for up_index, up_col in enumerate(update_column):
                                if up_col in fieldList:
                                    up_col = fieldList[up_col]
                                column_dict = {
                                    "column_name": up_col,
                                    "separator": ",",
                                }
                                update_config_dict["inputs"]["Columns"].append(column_dict)
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_date",
                                    "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "separator": ",",
                                }
                            )
                            update_config_dict["inputs"]["Columns"].append(
                                {
                                    "column_name": "modified_by",
                                    "input_value": request.user.username,
                                    "separator": "",
                                }
                            )

                            f_data = standardised_functions.data_preprocessing(
                                sql_data,
                                table_name,
                                request,
                                customvalidation={},
                                message_show="no",
                                user_operation="update",
                                export_data="yes",
                                export_type=export_type,
                                export_update_column=update_column,
                                upsert=True,
                            )
                            sql_data = f_data.data_validation(message_out=False)

                            if isinstance(sql_data, list):
                                # pass
                                temp_dict["output_msg"] = (
                                    f"Failed to export data to {table_name} table as following validations failed - {sql_data[0][0]['error_description'].replace('Error while uploading:','')}"
                                )
                            elif isinstance(sql_data, pd.DataFrame):
                                sql_data = sql_data[[i for i in sql_data.columns if i in fieldList.values()]]

                                update_data_func_multiple(
                                    request,
                                    update_config_dict,
                                    sql_data.fillna("NULL"),
                                    if_app_db=True,
                                    if_update_else_insert=True,
                                )
                                temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"

                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            temp_dict["output_msg"] = f"Failed to update data in {table_name} table"
                    else:
                        pass

        elif config_dict["inputs"]["exportTo"] == "external_database":
            table_name = config_dict["inputs"]["tableName"]
            connection_name = config_dict["inputs"]["connection_name"]
            filename = f"{PLATFORM_FILE_PATH}external_databases.json"
            external_databases_config = {}
            sql_data = data.copy()
            chunk_size = config_dict["inputs"].get("chunk_size", 10**5)
            fast_executemany = config_dict["inputs"].get("fast_executemany", False)
            if os.path.exists(filename):
                with open(filename) as fout:
                    external_databases_config = json.load(fout)
                    fout.close()
            else:
                pass
            if external_databases_config.get(connection_name):
                ext_db_config = external_databases_config[connection_name]
                db_type = ext_db_config["db_type"]
                schema = ""
                server = ext_db_config["server"]
                port = ext_db_config["port"]
                db_name = ext_db_config["db_name"]
                username = ext_db_config["username"]
                password = ext_db_config["password"]
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
                    logging.warning("5")
                    logging.warning(server)
                    logging.warning(port)
                    logging.warning(db_name)
                    logging.warning(username)
                    logging.warning(password)
                else:
                    (
                        encrypted_server,
                        encrypted_port,
                        encrypted_database,
                        encrypted_username,
                        encrypted_user_secret_key,
                        connection_code,
                    ) = encrypt_db_credentials(server, port, db_name, username, password)
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
                ext_db_config["dbname"] = db_name
                ext_db_config["user"] = username
                ext_db_config["host"] = server

                if db_type == "MSSQL":
                    db_engine = mssql_engine_generator(ext_db_config)
                elif db_type == "PostgreSQL":
                    db_engine = ext_db_config
                elif db_type == "Oracle":
                    schema = ext_db_config.get("schema", "")
                    db_engine = oracle_engine_generator(ext_db_config)
                else:
                    pass
                if config_dict["inputs"].get("exportType"):
                    export_type = config_dict["inputs"]["exportType"]
                else:
                    export_type = "append"
                user_engine = [db_engine, None]
                if export_type in ["append", "replace"]:
                    try:
                        data_handling(
                            "",
                            sql_data,
                            table_name,
                            if_exists=export_type,
                            if_app_db=False,
                            con=user_engine,
                            connection_name=connection_name,
                            engine_override=True,
                            schema=schema,
                            db_type=db_type,
                            chunksize=chunk_size,
                            fast_executemany=fast_executemany,
                        )
                        temp_dict["output_msg"] = f"Data exported to {table_name} table successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = (
                            f"Failed to export data to {table_name} table. Following exception occured - {e}"
                        )
                elif export_type == "update":
                    identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                    update_column = config_dict["inputs"]["selectUpdateCol"]
                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"][-1]["separator"] = ""
                        update_data_func_multiple(
                            "",
                            update_config_dict,
                            sql_data.fillna("NULL"),
                            if_app_db=False,
                            engine2=user_engine,
                            engine_override=True,
                            db_type=db_type,
                            schema=schema,
                        )
                        temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = (
                            f"Failed to update data in {table_name} table. Following exception occured - {e}"
                        )
                elif export_type == "update_else_insert":
                    identifier_column = config_dict["inputs"]["selectUpdateIdentifierCol"]
                    update_column = config_dict["inputs"]["selectUpdateCol"]
                    try:
                        update_config_dict = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": [],
                            },
                            "condition": [],
                        }
                        for id_index, id_col in enumerate(identifier_column):
                            condition_dict = {
                                "column_name": id_col,
                                "condition": "Equal to",
                                "and_or": "",
                            }
                            if len(identifier_column) > 0 and (id_index != (len(identifier_column) - 1)):
                                condition_dict["and_or"] = "AND"
                            update_config_dict["condition"].append(condition_dict)

                        for up_index, up_col in enumerate(update_column):
                            column_dict = {
                                "column_name": up_col,
                                "separator": ",",
                            }
                            update_config_dict["inputs"]["Columns"].append(column_dict)
                        update_config_dict["inputs"]["Columns"][-1]["separator"] = ""
                        update_data_func_multiple(
                            "",
                            update_config_dict,
                            sql_data,
                            if_app_db=False,
                            engine2=user_engine,
                            engine_override=True,
                            if_update_else_insert=True,
                            db_type=db_type,
                            schema=schema,
                        )
                        temp_dict["output_msg"] = f"Data in {table_name} table updated successfully"
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        temp_dict["output_msg"] = (
                            f"Failed to update data in {table_name} table. Following exception occured - {e}"
                        )
                else:
                    pass
            else:
                raise Exception
        elif config_dict["inputs"]["exportTo"] == "Redis":
            db_key = config_dict["inputs"]["db_key"]
            connection_name = config_dict["inputs"]["connection_name"]
            filename = f"{PLATFORM_FILE_PATH}external_databases.json"
            external_databases_config = {}
            if os.path.exists(filename):
                with open(filename) as fout:
                    external_databases_config = json.load(fout)
                    fout.close()
            user_secret_key = external_databases_config[connection_name]["password"]
            server = external_databases_config[connection_name]["server"]
            port = external_databases_config[connection_name]["port"]
            columnList = config_dict["inputs"]["columnList"]
            if "connection_code" in external_databases_config[connection_name]:
                connection_code = external_databases_config[connection_name]["connection_code"]
                db_name = ""
                server, port, db_name, username, user_secret_key = decrypt_existing_db_credentials(
                    server, port, db_name, username, password, connection_code
                )
                logging.warning("export_redis")
                logging.warning(server)
                logging.warning(port)
                logging.warning(db_name)
                logging.warning(username)
                logging.warning(password)
            else:
                database = ""
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
            try:
                if user_secret_key != "":
                    r = redis.StrictRedis(host=server, port=port, db=0, password=user_secret_key)
                else:
                    r = redis.StrictRedis(host=server, port=port, db=0)
                r.set(db_key, pickle.dumps(data))
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                temp_dict["output_msg"] = "Failed export data to Redis"
            else:
                temp_dict["output_msg"] = "Data exported to Redis successfully"
        elif config_dict["inputs"]["exportTo"] == "API":
            temp_context = ApiIntegration.send_data(config_dict, data)
            temp_dict["output_msg"] = temp_context["msg"]
        elif config_dict["inputs"]["exportTo"] == "CSV":
            columnList = config_dict["inputs"]["columnList"]
            if len(columnList) > 0:
                data = data.loc[:, columnList]

            file_name = config_dict["inputs"]["fileName"]
            file_name = file_name + ".csv"
            result = data.to_csv(index=False).encode()
            result_data = result.decode("utf8")
            temp_dict["file"] = result_data
            temp_dict["file_name"] = file_name

        elif config_dict["inputs"]["exportTo"] == "JSON":
            columnList = config_dict["inputs"]["columnList"]
            if len(columnList) > 0:
                data = data.loc[:, columnList]

            file_name = config_dict["inputs"]["fileName"]
            file_name = file_name + ".json"
            result = data.to_json(orient="records").encode()
            result_data = result.decode("utf8")
            temp_dict["file"] = result_data
            temp_dict["file_name"] = file_name

        elif config_dict["inputs"]["exportTo"] == "Parquet":
            columnList = config_dict["inputs"]["columnList"]
            if len(columnList) > 0:
                data = data.loc[:, columnList]

            file_name = config_dict["inputs"]["fileName"]
            file_name = file_name + ".parquet"
            result = data.to_parquet(index=False)
            result_data = result.decode("latin-1")
            temp_dict["file"] = result_data
            temp_dict["file_name"] = file_name

        return temp_dict
