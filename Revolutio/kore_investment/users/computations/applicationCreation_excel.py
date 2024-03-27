from datetime import datetime
import json
import logging
import pickle
import random
import string

import pandas as pd

## Cache
from config.settings.base import redis_instance
from kore_investment.users import views
from kore_investment.users.computations import standardised_functions
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    db_engine_extractor,
    read_data_func,
)

from . import dynamic_model_create

# Global Variables
main_engine_name = None
data_model_global_list = {}
business_model_global_list = {}


def application_creation_excel_init(app_data_file, app_file, db_connection_name, request):
    final_data_config = {}
    guidance_list = ["data_model", "process_flow", "business_model", "application_details"]
    try:
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        return {"Error": f"Error connecting to the database! {str(e)}"}
    else:
        global main_engine_name
        main_engine_name = user_db_engine
        if app_data_file:
            sheet_list = app_data_file.sheetnames
            for sheet_name in guidance_list:
                if sheet_name in sheet_list:
                    # Data Model
                    if sheet_name == "data_model":
                        data_model_status = data_model_configuration_init(
                            app_file, user_engine=user_db_engine
                        )
                        if "Error" in data_model_status:
                            return data_model_status
                        else:
                            final_data_config["Data_model"] = data_model_status["Data_model"]

                    # Process Flow
                    if sheet_name == "process_flow":
                        process_flow_status = process_flow_configuration_init(
                            app_file,
                            final_data_config,
                            db_connection_name=db_connection_name,
                            user_engine=user_db_engine,
                        )

                        if "Error" in process_flow_status:
                            return process_flow_status
                        else:
                            final_data_config["Process_flow"] = process_flow_status["Process_flow"]

                    # Business Model
                    if sheet_name == "business_model":
                        business_model_status = business_model_configuration_init(
                            app_file,
                            final_data_config,
                            db_connection_name=db_connection_name,
                            user_engine=user_db_engine,
                        )
                        if "Error" in business_model_status:
                            return business_model_status
                        else:
                            final_data_config["Business_model"] = business_model_status["Business_model"]

                    if sheet_name == "application_details":
                        application_status = application_configuration_init(
                            app_file,
                            final_data_config,
                            db_connection_name=db_connection_name,
                            user_engine=user_db_engine,
                        )
                        if "Error" in application_status:
                            return application_status
                        else:
                            final_data_config["Application_Details"] = application_status[
                                "Application_Details"
                            ]

            # Final iteration
            if len(final_data_config) > 0:
                for config_name, config_desc in final_data_config.items():
                    if config_name == "Data_model":
                        if len(config_desc) > 0:
                            for tab_no in range(len(config_desc)):
                                for tabname, fields in config_desc[tab_no].items():
                                    dynamic_model_create.create_table_sql(
                                        tabname,
                                        fields,
                                        request,
                                        db_connection_name=db_connection_name,
                                    )
                    if config_name == "Process_flow":
                        create_process_handling(
                            request, flow_context=final_data_config, user_engine=user_db_engine
                        )
                    if config_name == "Business_model":
                        create_business_model(request, bus_config=final_data_config["Business_model"])
                    if config_name == "Application_Details":
                        create_application_model(request, app_config=final_data_config["Application_Details"])
                return {"FinalSuccess": "Excel sheet Executed!"}
        else:
            return {"Error": "File not found!"}


# Create Data Model Config
def data_model_configuration_init(app_file, user_engine=""):
    data_context = {"Data_model": []}
    final_list = []
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
        ],
        "BooleanField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "columns",
            "divider",
        ],
        "FileField": [
            "field name",
            "field data type",
            "nullable?",
            "field header",
            "unique",
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
            "divider",
        ],
        "BigIntegerField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "default",
            "unique",
            "columns",
            "divider",
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
        ],
        "TimeField": [
            "field name",
            "field data type",
            "auto now?",
            "editable?",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
        ],
        "DateTimeField": [
            "field name",
            "field data type",
            "auto now?",
            "editable?",
            "nullable?",
            "field header",
            "unique",
            "columns",
            "divider",
        ],
        "TextField": [
            "field name",
            "field data type",
            "field header",
            "nullable?",
            "unique",
            "columns",
            "divider",
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
    }

    data_model_excel = pd.read_excel(app_file, sheet_name="data_model", engine="openpyxl")
    if not data_model_excel.empty:
        unique_table_names = data_model_excel.data_table_name.unique()
        for table_name in unique_table_names:
            table_df_og = read_data_func(
                "",
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Tables",
                        "Columns": ["tablename", "fields"],
                    },
                    "condition": [],
                },
                engine2=user_engine,
                db_type="MSSQL",
                engine_override=True,
            )
            table_df = table_df_og[table_df_og["tablename"].isin(unique_table_names)]
            if not table_df.empty:
                total_tables_list = table_df["tablename"].tolist()
                data_context = {"Error": ", ".join(total_tables_list) + " already exist in database"}
                return data_context
            else:
                # Global Data model make
                global data_model_global_list
                data_model_global_list[table_name] = []
                d2 = {}
                data_dict = {table_name: []}
                data_df = data_model_excel[data_model_excel["data_table_name"] == table_name].fillna("")
                for index, row in data_df.iterrows():
                    d1 = {}
                    d2[row["field_name"]] = {}
                    if row["field_data_type"] in valid_field_dict.keys():
                        # Global Change
                        data_model_global_list[table_name] = {}
                        if row["field_data_type"] == "ForeignKey":
                            if row["parent_table"] not in table_df_og.tablename.tolist():
                                return {
                                    "Error": f"Parent table: {row['parent_table']} doesnt exist in current database."
                                }
                            else:
                                col_df = read_data_func(
                                    "",
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": row["parent_table"],
                                            "Columns": ["*"],
                                        },
                                        "condition": [],
                                    },
                                    engine2=user_engine,
                                    db_type="MSSQL",
                                    engine_override=True,
                                )
                                if row["field_name"] not in col_df.columns:
                                    return {
                                        "Error": f"Parent table:{row['parent_table']} does not contain field {row['field_name']}."
                                    }

                        for field_config in valid_field_dict[row["field_data_type"]]:
                            data_col = field_config.replace(" ", "_")
                            field_config = field_config.replace("_", " ")
                            if data_col == "maximum_length*":
                                d1["maximum length*"] = row["maximum_length"]
                                d2[row["field_name"]]["maximum length*"] = row["maximum_length"]
                            else:
                                if row[data_col]:
                                    if data_col in ["nullable?", "unique", "auto_now?", "editable?"]:
                                        if row[data_col] not in ["Yes", "No"]:
                                            return {
                                                "Error": "Columns: ['nullable?','unique','auto_now?', 'editable?'] accepts value in Yes or No."
                                            }
                                    if data_col in ["choices", "columns"]:
                                        row[data_col] = row[data_col].split(",")
                                    d1[field_config] = row[data_col]
                                    d2[row["field_name"]][field_config] = row[data_col]
                                else:
                                    d1[field_config] = ""
                                    d2[row["field_name"]][field_config] = ""

                    else:
                        return {
                            "Error": f"{table_name}: {row['field_name']} with{row['field_data_type']} not a valid datatype"
                        }
                    data_dict[table_name].append(d1)
                    data_model_global_list[table_name] = d2
                final_list.append(data_dict)
        data_context["Data_model"] = final_list
        return data_context
    else:
        data_context = {"Error": "data_model sheet not found!"}
    return data_context


# Create Process & Subprocess Config
def process_flow_configuration_init(app_file, final_data_config, db_connection_name="", user_engine=""):
    flow_context = {"Process_flow": {}}
    data_model_excel = pd.read_excel(app_file, sheet_name="process_flow", engine="openpyxl")
    # Process
    final_process_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "NavigationSideBar",
                "Columns": ["item_name", "item_group_name"],
            },
            "condition": [],
        },
        engine2=user_engine,
        db_type="MSSQL",
        engine_override=True,
    )
    draft_process_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "DraftProcess",
                "Columns": ["item_name", "item_group_name"],
            },
            "condition": [],
        },
        engine2=user_engine,
        db_type="MSSQL",
        engine_override=True,
    )

    # Combine Draft and Final Process
    total_process_list = draft_process_df.item_name.tolist() + final_process_df.item_name.tolist()

    # Combine Excel and Existing Database tables
    overall_table_list = []

    table_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [],
        },
        engine2=main_engine_name,
        db_type="MSSQL",
        engine_override=True,
    ).tablename.tolist()

    overall_table_list = overall_table_list + table_df
    if "Data_model" in final_data_config:
        data_model_tables = [list(i.keys())[0] for i in final_data_config["Data_model"]]
        overall_table_list = overall_table_list + data_model_tables

    if not data_model_excel.empty:
        # Find unique process
        unique_process_names = data_model_excel.process_name.unique()
        process_checker = any(item in unique_process_names for item in total_process_list)
        if not process_checker:
            if len(unique_process_names) > 0:
                for process in unique_process_names:
                    process = process.strip()
                    process_model_df = data_model_excel[data_model_excel.process_name == process]
                    # Generate Process Code
                    Finalitemcode = "Prg" + str(standardised_functions.random_no_generator())
                    process_dict = {
                        "Process_code": Finalitemcode,
                        "Process_name": process,
                        "app_allocation_status": "unallocated",
                        "sub_process_list": [],
                    }
                    subprocesses_list = []
                    if not process_model_df.empty:
                        # Find unique subprocess
                        unique_subprocess_names = process_model_df.sub_process_name.unique()
                        if len(unique_subprocess_names) > 0:
                            for subprocess in unique_subprocess_names:
                                subprocess = subprocess.strip()
                                subprocess_df = process_model_df[
                                    process_model_df.sub_process_name == subprocess
                                ]
                                # Generate Subprocess Code
                                subprocess_code = "Pr" + str(standardised_functions.random_no_generator())
                                subprocess_dict = {
                                    "Subprocess_code": subprocess_code,
                                    "Subprocess_shortname": "",
                                    "Subprocess_name": subprocess,
                                    "Subprocess_item_code": process_dict["Process_code"],
                                    "Subprocess_item_name": process_dict["Process_name"],
                                    "hover": "no",
                                    "L3_config": [],
                                }
                                L3_config_list = []
                                if not subprocess_df.empty:
                                    for index2, row2 in subprocess_df.iterrows():
                                        no_table_list = ["Analysis", "Pivot Report"]
                                        subprocess_dict["Subprocess_shortname"] = row2[
                                            "screen_functionality_description"
                                        ].strip()
                                        if row2["sub_process_tab_type"] not in no_table_list:
                                            if "," in row2["related_table"]:
                                                related_table = row2["related_table"].split(",")
                                                related_table = [tabName.strip() for tabName in related_table]
                                            else:
                                                related_table = row2["related_table"].strip()

                                            if len(related_table) > 0:
                                                if type(related_table) == list:
                                                    table_checker = any(
                                                        item in overall_table_list for item in related_table
                                                    )
                                                else:
                                                    table_checker = related_table in overall_table_list
                                                if table_checker:
                                                    template_config = subprocess__template_type_config(
                                                        template_mode=row2["sub_process_tab_type"],
                                                        table_names=related_table,
                                                        related_data_fields=row2["required_data_fields"],
                                                        related_item_code=subprocess_code,
                                                        data_context=final_data_config,
                                                    )

                                                    if "Error" in template_config:
                                                        return {
                                                            "Error": f"Line {index2} : {template_config['Error']}"
                                                        }
                                                    else:
                                                        tabScreendf = read_data_func(
                                                            "",
                                                            {
                                                                "inputs": {
                                                                    "Data_source": "Database",
                                                                    "Table": "TabScreens",
                                                                    "Columns": [
                                                                        "tab_type",
                                                                        "tab_header_name",
                                                                    ],
                                                                },
                                                                "condition": [
                                                                    {
                                                                        "column_name": "tab_type",
                                                                        "condition": "Equal to",
                                                                        "input_value": template_config[
                                                                            "tab_type"
                                                                        ].strip(),
                                                                        "and_or": "",
                                                                    }
                                                                ],
                                                            },
                                                            engine2=main_engine_name,
                                                            db_type="MSSQL",
                                                            engine_override=True,
                                                        ).tab_header_name.tolist()
                                                        if row2["sub_process_tab_name"]:
                                                            if (
                                                                row2["sub_process_tab_name"].strip()
                                                                in tabScreendf
                                                            ):
                                                                return {
                                                                    "Error": "Tab Header should be unique"
                                                                }
                                                            else:
                                                                template_config["tab_header_name"] = row2[
                                                                    "sub_process_tab_name"
                                                                ].strip()
                                                                L3_config_list.append(template_config)
                                                        else:
                                                            return {"Error": "Tab Header is mandatory"}
                                                else:
                                                    if type(related_table) == list:
                                                        table_found = [
                                                            item
                                                            for item in related_table
                                                            if item in overall_table_list
                                                        ]
                                                        return {
                                                            "Error": ", ".join(table_found)
                                                            + " tables do not exist!"
                                                        }
                                                    else:
                                                        return {
                                                            "Error": f"{related_table} table do not exist!"
                                                        }

                                            else:
                                                return {
                                                    "Error": f"table_name is mandatory in Create View, List View, Upload and OCR and should be present in process_flow sheet."
                                                }
                                        else:
                                            template_config = subprocess__template_type_config(
                                                template_mode=row2["sub_process_tab_type"].strip(),
                                                related_data_fields=row2["required_data_fields"],
                                                related_item_code=subprocess_code,
                                                data_context=final_data_config,
                                            )
                                            if "Error" in template_config:
                                                return {
                                                    "Error": f"Line {index2} : {template_config['Error']}"
                                                }
                                            else:
                                                template_config["tab_header_name"] = row2[
                                                    "sub_process_tab_name"
                                                ].strip()
                                            L3_config_list.append(template_config)
                                    subprocess_dict["L3_config"] = L3_config_list
                                    subprocesses_list.append(subprocess_dict)

                            process_dict["sub_process_list"] = subprocesses_list
                        else:
                            return {"Error": f"Process requires subprocesses to be present."}
                    flow_context["Process_flow"][process] = process_dict
            else:
                return {"Error": "Process column empty!"}
            return flow_context
        else:
            process_found = data_model_excel[
                data_model_excel["process_name"].isin(total_process_list)
            ].process_name.unique()
            return {"Error": ", ".join(process_found) + " process(s) with the same name already exists!"}
    else:
        return {"Error": "process_flow sheet not found!"}


# Create Application Configuration
def application_configuration_init(app_file, final_data_config, db_connection_name="", user_engine=""):
    application_context = {}
    data_model_excel = pd.read_excel(app_file, sheet_name="application_details", engine="openpyxl")
    application_checker = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Application",
                "Columns": ["application_name"],
            },
            "condition": [],
        },
        engine2=user_engine,
        db_type="MSSQL",
        engine_override=True,
    )
    application_checker = application_checker["application_name"].tolist()
    if not data_model_excel.empty:
        unique_application_names = data_model_excel.application_name.unique()
        if len(unique_application_names) > 0:
            for appname in unique_application_names:
                appname = appname.strip()
                if appname not in application_checker:
                    application_df = data_model_excel[data_model_excel.application_name == appname]
                    application_context[appname] = {}
                    application_context[appname]["App_Description"] = (
                        application_df["application_description"].iloc[0].strip()
                    )
                    application_context[appname]["App_code"] = "App" + str(
                        standardised_functions.random_no_generator()
                    )
                    application_context[appname]["app_icon"] = "fas fa-globe"
                    application_context[appname]["app_icon_color"] = "#b8860b"
                    application_context[appname]["app_card_color"] = "#000000"
                    application_context[appname]["app_text_color"] = "#FFFFFF"
                    app_process_tagging = list(
                        set(
                            application_df[application_df["business_model"].notnull()][
                                "business_model"
                            ].tolist()
                        )
                    )

                    if len(app_process_tagging) > 0:
                        app_process_tagging = [appName.strip() for appName in app_process_tagging]
                        if all(
                            pr_code in business_model_global_list.keys() for pr_code in app_process_tagging
                        ):
                            application_context[appname]["business_model_names"] = {}
                            for pr_name in app_process_tagging:
                                pr_name = pr_name.strip()
                                application_context[appname]["business_model_names"][pr_name] = (
                                    business_model_global_list[pr_name]
                                )
                        else:
                            wrong_process = [
                                pr_code.strip()
                                for pr_code in app_process_tagging
                                if pr_code.strip() not in business_model_global_list.keys()
                            ]
                            return {
                                "Error": "Application details: "
                                + str(",".join(wrong_process))
                                + "business model doesnt not exist in the sheet"
                            }

                else:
                    return {"Error": "application_name should be unique"}
        else:
            return {"Error": "application_name and application_description are mandatory"}
    else:
        return {"Error": "application_details sheet not found!"}
    final_data_config["Application_Details"] = application_context

    return final_data_config


# Create Business Configuration
def business_model_configuration_init(app_file, final_data_config, db_connection_name="", user_engine=""):
    business_context = {}
    data_model_excel = pd.read_excel(app_file, sheet_name="business_model", engine="openpyxl")
    existing_table_list = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [],
        },
        engine2=main_engine_name,
        db_type="MSSQL",
        engine_override=True,
    ).tablename.tolist()
    if not data_model_excel.empty:
        if "Data_model" in final_data_config:
            excel_data_model_tables = [list(i.keys())[0] for i in final_data_config["Data_model"]]
            excel_data_model_tables = excel_data_model_tables + existing_table_list
            if len(excel_data_model_tables) > 0:
                if "Process_flow" in final_data_config:
                    excel_process_list = {
                        k: v["Process_code"] for k, v in final_data_config["Process_flow"].items()
                    }
                    unique_business_model = data_model_excel.business_model_name.unique()
                    if len(excel_process_list) > 0:
                        if len(unique_business_model) > 0:
                            for bus_name in unique_business_model:
                                bus_name = bus_name.strip()
                                business_df = data_model_excel[
                                    data_model_excel.business_model_name == bus_name
                                ]
                                business_inner_dict = {}
                                business_inner_dict["Business_name"] = bus_name.strip()
                                business_inner_dict["Business_description"] = (
                                    business_df["business_model_description"].iloc[0].strip()
                                )
                                business_inner_dict["Process_name"] = {}
                                business_inner_dict["DataTables"] = []
                                business_inner_dict["Business_code"] = "BM" + str(
                                    standardised_functions.random_no_generator()
                                )
                                process_tagging_list = list(
                                    set(
                                        business_df[business_df["process_tagging"].notnull()][
                                            "process_tagging"
                                        ].tolist()
                                    )
                                )
                                data_modal_tag_list = list(
                                    set(
                                        business_df[business_df["data_model_tagging"].notnull()][
                                            "data_model_tagging"
                                        ].tolist()
                                    )
                                )
                                if len(process_tagging_list) > 0:
                                    process_tagging_list = [pr_tag.strip() for pr_tag in process_tagging_list]
                                    if all(
                                        pr_code in excel_process_list.keys()
                                        for pr_code in process_tagging_list
                                    ):
                                        for pr_name in process_tagging_list:
                                            pr_name = pr_name.strip()
                                            business_inner_dict["Process_name"][pr_name] = excel_process_list[
                                                pr_name
                                            ]
                                    else:
                                        wrong_process = [
                                            pr_code.strip()
                                            for pr_code in process_tagging_list
                                            if pr_code.strip() not in excel_process_list.keys()
                                        ]
                                        return {
                                            "Error": "Business model:"
                                            + str(",".join(wrong_process))
                                            + "process doesnt not exist in the sheet"
                                        }

                                if len(data_modal_tag_list) > 0:
                                    data_modal_tag_list = [pr_tag.strip() for pr_tag in data_modal_tag_list]
                                    if all(
                                        dt_name in excel_data_model_tables for dt_name in data_modal_tag_list
                                    ):
                                        business_inner_dict["DataTables"] = []
                                        for dt_name in data_modal_tag_list:
                                            business_inner_dict["DataTables"].append(dt_name)
                                    else:
                                        wrong_data_modal = [
                                            dt_name.strip()
                                            for dt_name in data_modal_tag_list
                                            if dt_name.strip() not in excel_data_model_tables
                                        ]
                                        return {
                                            "Error": "Business model:"
                                            + str(",".join(wrong_data_modal))
                                            + "data model doesnt not exist in the sheet"
                                        }
                                business_context[bus_name] = business_inner_dict
                        else:
                            return {
                                "Error": "business_model_name and business_model_description is mandatory."
                            }
                    else:
                        return {"Error": "No process found in process_flow sheet!"}
                else:
                    return {"Error": "process_flow sheet not found!"}
            else:
                return {"Error": "No tables defined in data_model sheet."}

        else:
            return {"Error": "data_model sheet not found!"}
    else:
        return {"Error": "business_model sheet not found!"}

    final_data_config["Business_model"] = business_context
    global business_model_global_list
    business_model_global_list = business_context
    return final_data_config


# Subprocess Type Configuration Creation
def subprocess__template_type_config(
    template_mode="", table_names=None, related_data_fields=None, related_item_code="", data_context=""
):

    element_id = "".join(random.SystemRandom().choice(string.digits) for _ in range(10))
    overall_dict = {
        "tab_header_name": "",
        "tab_icon": "",
        "tab_type": "",
        "shape": "",
        "related_item_code": related_item_code,
        "level": "2",
    }
    if template_mode == "Create View":
        if type(table_names) == str:
            table_names = table_names.split(",")
        template_config = create_view_template_generator(
            table_names=table_names, related_data_fields=related_data_fields
        )
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["table_name"] = table_names
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "create_view"
            overall_dict["shape"] = "whiteSpace=wrap"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "whiteSpacewrap" + element_id
            overall_dict["fields"] = []

    if template_mode == "List View":
        template_config = list_view_template_generator(table_names=table_names, related_data_fields=None)
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["table_name"] = table_names
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "list_view"
            overall_dict["shape"] = "shape=process"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "process" + element_id

    if template_mode == "Analysis":
        template_config = analysis_template_generator(related_data_fields=related_data_fields)
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "analysis"
            overall_dict["shape"] = "ellipse"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "ellipse" + element_id

    if template_mode == "OCR":
        if type(table_names) == list:
            table_names = table_names[0]
        template_config = ocr_template_generator(
            table_names=table_names, related_data_fields=related_data_fields
        )
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["table_name"] = table_names
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "Ocr"
            overall_dict["shape"] = "shape=cube"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "cube" + element_id

    if template_mode == "Pivot Report":
        template_config = pivot_report_template_generator(related_data_fields=related_data_fields)
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "PivotReport"
            overall_dict["shape"] = "shape=hexagon"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "hexagon" + element_id

    if template_mode == "Upload":
        if type(table_names) == str:
            table_names = table_names.split(",")
        template_config = upload_template_generator(
            table_names=table_names, related_data_fields=related_data_fields
        )
        if "Error" in template_config:
            return template_config
        else:
            overall_dict["template_mode"] = template_mode
            overall_dict["table_name"] = table_names
            overall_dict["tab_icon"] = "fas fa-plus"
            overall_dict["tab_type"] = "data_connector"
            overall_dict["shape"] = "shape=document"
            overall_dict["tab_body_content"] = template_config
            overall_dict["element_id"] = "document" + element_id

    return overall_dict


# Subprocess Type Configuration Generation
def create_view_template_generator(table_names=None, related_data_fields=None):
    field_choice_dict = FieldChoiceMaker(table_names)
    shape_html = shape_html_generate(table_names)
    html = ""
    if shape_html:
        html = {"html": shape_html}
    template_layout = {
        "Category_attributes": {
            "Template": {
                "Template_choice": "Default",
                "Template_type": "System defined template",
                "html": json.dumps(html),
                "select": 0,
                "formLevelField": [],
            }
        },
        "Search_fields": {"search_fields": []},
        "Category_sub_elements": [
            {
                "Category_sub_element_name": "Form",
                "Category_sub_element_attributes": [
                    {"Category_attr": "Table_name", "value": table_names},
                    {"Category_attr": "Field_Choice", "value": field_choice_dict},
                    {
                        "Category_attr": "Comparable_Choice",
                        "value": {},
                        "char_column": [],
                        "period": {"period_col": "", "periodFrom": "", "periodTo": ""},
                    },
                    {
                        "Category_attr": "Action",
                        "value": ["Save", "Save as Draft"],
                        "Table_name": table_names[0],
                    },
                    {
                        "Category_attr": "MultiSelect_Choice",
                        "value": "",
                        "masterColumn": None,
                        "char_column": [],
                        "master": "",
                        "add": [],
                        "checkBox": 0,
                    },
                    {
                        "Category_attr": "Constraint_Choice",
                        "selected_tables": [],
                        "selectedConstraint_fields": [],
                        "remove_additional_column": [],
                        "constraint_holder": {"": ""},
                        "constraint_name": "",
                        "constraint_type": "",
                    },
                    {
                        "Category_attr": "Flow_Choice",
                        "flowcolumn": "isin",
                        "mastertableflow": "",
                        "masterColumnflow": None,
                    },
                    {
                        "Category_attr": "asset_grouping",
                        "selected_tables": [],
                        "selectedConstraint_fields": "",
                        "remove_additional_column": "",
                        "constraint_holder": "",
                        "usecase_name": "",
                        "constraint_name": "",
                        "constraint_type": [],
                    },
                ],
            }
        ],
    }
    return template_layout


def FieldChoiceMaker(table_name):
    field_construct = []
    fields_not_displayed = [
        "created_by",
        "modified_by",
        "created_date",
        "modified_date",
        "active_to",
        "active_from",
        "approved_by",
        "approval_status",
    ]

    table_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [],
        },
        engine2=main_engine_name,
        db_type="MSSQL",
        engine_override=True,
    ).tablename.tolist()

    # Extract All Field Header
    if table_name[0] in table_df:

        modelName = dynamic_model_create.get_model_class(
            table_name[0], request_user="", db_engine=main_engine_name
        )
        for field in modelName.concrete_fields:
            if field.name not in fields_not_displayed:
                field_name = field.name
                if field.get_internal_type() != "AutoField":
                    field_construct.append(
                        {
                            f"{field_name}": [
                                {
                                    "tableattr": [{"attr": "Tablename", "value": table_name[0]}],
                                    "cssattr": [
                                        {
                                            "attr": "Datatype",
                                            "value": field.get_internal_type(),
                                            "verbose": field.verbose_name.title(),
                                        }
                                    ],
                                }
                            ]
                        }
                    )

    elif table_name[0] in data_model_global_list.keys():
        for field_name, field_config in data_model_global_list[table_name[0]].items():
            if field_config["field data type"] != "AutoField":
                field_construct.append(
                    {
                        field_config["field name"]: [
                            {
                                "tableattr": [{"attr": "Tablename", "value": table_name[0]}],
                                "cssattr": [
                                    {
                                        "attr": "Datatype",
                                        "value": field_config["field data type"],
                                        "verbose": field_config["field header"],
                                    }
                                ],
                            }
                        ]
                    }
                )
    return field_construct


# Create HTML Template for Create View
def shape_html_generate(table_name):
    fields_not_displayed = [
        "created_by",
        "modified_by",
        "created_date",
        "modified_date",
        "active_to",
        "active_from",
        "approved_by",
        "approval_status",
    ]

    table_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [],
        },
        engine2=main_engine_name,
        db_type="MSSQL",
        engine_override=True,
    ).tablename.tolist()

    html = ""
    main_html = ""

    # Extract All Field Header
    if table_name[0] in table_df:
        modelName = dynamic_model_create.get_model_class(
            table_name[0], request_user="", db_engine=main_engine_name
        )
        for field in modelName.concrete_fields:
            if field.name not in fields_not_displayed:
                if field.get_internal_type() != "AutoField":
                    choice = ""
                    field_name = field.name
                    verb = field.verbose_name.title()
                    if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]:
                        choice = f"""<input type="number"  name="{field_name}" min="-2147483648" max="2147483647"  class="textinput textInput form-control {field_name}"/>"""
                    elif field.get_internal_type() == "CharField":
                        choice = f"""<input type="text" name="{field_name}" class="textinput textInput form-control {field_name}"/>"""
                    elif field.get_internal_type() in ["DateField", "DateTimeField"]:
                        choice = f"""<input type="date" name="{field_name}" placeholder="DD:MM:YYYY"  class="textinput textInput form-control {field_name}">"""
                    elif field.get_internal_type() == "TextField":
                        choice = f"""<textarea type="text" name="{field_name}" class="textinput textInput form-control {field_name}">Enter text</textarea>"""
                    elif field.get_internal_type() == "BooleanField":
                        choice = f"""<input type="checkbox" name="{field_name}" class="{field_name}"/>"""
                    elif field.get_internal_type() == "EmailField":
                        choice = f"""<input type="email" name="{field_name}" class="textinput textInput form-control {field_name}"/>"""
                    elif field.get_internal_type() == "ImageField":
                        choice = f"""<input type="image" name="{field_name}" class="custom-file-input {field_name}"/>"""
                    elif field.get_internal_type() == "FileField":
                        choice = f"""<input type="file" name="{field_name}" class="custom-file-input {field_name}"/>"""
                    elif field.get_internal_type() == "ForeignKey":
                        choice = f"""<select class="form-control select2 {field_name}" name="{field_name}" tabindex="-1" aria-hidden="true"><option>----</option></select>"""
                    else:
                        choice = f"""<select class="form-control select2 {field_name}" name="{field_name}" tabindex="-1" aria-hidden="true"><option>----</option></select>"""

                    asterisk = ""
                    if hasattr(field, "null"):
                        if not field.null:
                            asterisk = "*"

                    classFile = ""
                    divFile = ""
                    if field.get_internal_type() in ["FileField", "ImageField"]:
                        classFile = "custom-file"
                        divFile = """<label class="custom-file-label" for="">Choose file</label>"""

                    html = f"""<div class="form-group col-lg-3 box color" draggable="true" onclick="changeColor.call(this)">
                            <div id={field_name}  class="form-group">
                            <label  class="requiredField label" style="display:inline-block; font-size:12px;">{verb}<span class="asteriskField">{asterisk}</span><i class="fas fa-edit float-right editjs" onclick="editElement.call(this)" style="margin-left:8px;margin-top:2px"></i></label>
                            <div class="{classFile}"> {choice} {divFile}</div>
                            </div>
                            </div>"""

    elif table_name[0] in data_model_global_list.keys():
        for field_name, field_config in data_model_global_list[table_name[0]].items():
            if field_config["field data type"] != "AutoField":
                choice = ""
                field_db_name = field_config["field name"]
                field_type = field_config["field data type"]
                verb = field_config["field header"]
                if field_type in ["IntegerField", "BigIntegerField", "FloatField"]:
                    choice = f"""<input type="number"  name="{field_db_name}" min="-2147483648" max="2147483647"  class="textinput textInput form-control {field_db_name}"/>"""
                elif field_type == "CharField":
                    choice = f"""<input type="text" name="{field_db_name}" class="textinput textInput form-control {field_db_name}"/>"""
                elif field_type in ["DateField", "DateTimeField"]:
                    choice = f"""<input type="date" name="{field_db_name}" placeholder="DD:MM:YYYY"  class="textinput textInput form-control {field_db_name}"/>"""
                elif field_type == "TextField":
                    choice = f"""<textarea type="text" name="{field_db_name}" class="textinput textInput form-control {field_db_name}">Enter text</textarea>"""
                elif field_type == "BooleanField":
                    choice = f"""<input type="checkbox" name="{field_db_name}" class="{field_db_name}" />"""
                elif field_type == "EmailField":
                    choice = f"""<input type="email" name="{field_db_name}" class="textinput textInput form-control {field_db_name}"/>"""
                elif field_type == "ImageField":
                    choice = f"""<input type="image" name="{field_db_name}" class="custom-file-input {field_db_name}"/>"""
                elif field_type == "FileField":
                    choice = f"""<input type="file" name="{field_db_name}" class="custom-file-input {field_db_name}"/>"""
                elif field_type == "ForeignKey":
                    choice = f"""<select class="form-control select2 {field_db_name}" name="{field_db_name}" tabindex="-1" aria-hidden="true"><option>----</option></select>"""
                else:
                    choice = f"""<select class="form-control select2 {field_db_name}" name="{field_db_name}" tabindex="-1" aria-hidden="true"><option>----</option></select>"""

                asterisk = ""
                if "nullable?" in field_config:
                    if field_config["nullable?"]:
                        if field_config["nullable?"] == "No":
                            asterisk = "*"

                classFile = ""
                divFile = ""
                if field_type in ["FileField", "ImageField"]:
                    classFile = "custom-file"
                    divFile = """<label class="custom-file-label" for="">Choose file</label>"""

                html = f"""<div class="form-group col-lg-3 box color" draggable="true" onclick="changeColor.call(this)">
                        <div id={field_db_name}  class="form-group">
                        <label  class="requiredField label" style="display:inline-block; font-size:12px;">{verb}<span class="asteriskField">{asterisk}</span><i class="fas fa-edit float-right editjs" onclick="editElement.call(this)" style="margin-left:8px;margin-top:2px"></i></label>
                        <div class="{classFile}"> {choice} {divFile}</div>
                        </div>
                        </div>"""
    if html:
        main_html = f"""<div class="formTempContainer isActive ui-draggable ui-draggable-handle ui-resizable" data-class="formTempContainer" style="border: 1px solid black; position: absolute; left: 0px; top: 0px; width: 98%; height: 100%; padding: 3px; margin: 0px; background-color: rgb(255, 255, 255); min-width: 140px; min-height: 100px;"><div class="float-right text" style="display:block;right: 10px; top: 45%;position: absolute; left:10%;opacity:0.5; z-index:999">Template</div><div class="toolbar float-right" style="display: none; right: 10px; top: 1px; position: absolute; left: 100%;">
              <button onclick="deleteElement.call(this)" style="background-color:transparent; border:transparent; border-color:transparent; position:sticky;"><i class="far fa-trash-alt" style="color: var(--primary-color);"></i></button><br>
              <button onclick="editElement.call(this)" style="background-color:transparent; border:transparent; border-color:transparent; position:sticky"><i class="far fa-edit" style="color: var(--primary-color);"></i></button><br>
              </div>
              <div class="card-body" style="margin:1px;max-height: 20rem;overflow: hidden; overflow-y: scroll"><div class="form-row">
              {html}
            </div><div class="form-group formBtn" style="display: none;"> <div class="row"> <input type="hidden" name="tablename"> <input type="hidden" name="elementid">
                      <input type="button" name="save" value="Compare With Existing" class="btn btn-primary buttonstyling acies_btn acies_btn-primary compareWithExisting" style="margin-right:4px;display: none;">
                      <input disabled="" type="submit" name="submit" value="Save" class="btn btn-primary buttonstyling acies_btn acies_btn-primary button_standard_save formBtn" style="display: none;"><button disabled="" type="button" name="back" class="btn backbtn ml-2" id="button-id-back"> ? </button>
                      <input disabled="" type="submit" name="submit" value="Save as Draft" data-entry="New" class="btn btn-primary buttonstyling acies_btn acies_btn-primary ml-2 consBtn" id="saveDraftbutton_whiteSpacewrap06629967346369674" style="display: none;"><input disabled="" type="button" name="previewButton" value="View Draft Versions" data-table-name="Product_Master" class="btn btn-primary buttonstyling acies_btn acies_btn-primary ml-2 consBtn" id="previewDraft_whiteSpacewrap06629967346369674" style="display: none;">
                      <input disabled="" type="button" name="resetDraft" value="Reset Draft Status " data-table-name="Product_Master" class="btn btn-primary buttonstyling acies_btn acies_btn-primary ml-2 consBtn" id="resetDraft_whiteSpacewrap06629967346369674" style="display: none;">
                      <input disabled="" type="button" value="Custom Validation" name="customValidation" class="btn btn-primary buttonstyling acies_btn acies_btn-primary ml-2  custBtnn" data-table-name="" data-toggle="modal" data-target="#customValidation" data-elementid="">
                     </div> </div></div></div>"""
    return main_html


# List View Template
def list_view_template_generator(table_names=None, related_data_fields=None):
    if table_names:
        if type(table_names) == list:
            table_names = table_names.split(",")
            table_names = table_names[0]
        template_layout = {
            "Category_attributes": {
                "Mandatory": {"Table_name": table_names, "user_table_name": {}, "DroppedFields": []},
                "Optional": {"Template_choice": "list_view_template_1.html"},
                "Default": {"Template_choice": "list_view_template_1.html"},
            },
            "reportingView": {
                "reportingViewColumns": [],
                "Template_choice": "Default",
                "uniqueColumn": [],
                "trackingColumn": [],
                "reportingShowLatest": False,
                "basicfilter_config": "[]",
            },
            "customView": [],
            "customTemplateListView": False,
            "createViewName": ["null"],
            "Category_sub_elements": [
                {
                    "Category_sub_element_name": "Data_table",
                    "Required": "Yes",
                    "Category_sub_element_attributes": [
                        {"attr": "Table_name", "value": table_names},
                        {
                            "attr": "SelectAll",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {"attr": "Upload", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                        {
                            "attr": "Save template",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "Multi_edit",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {"attr": "Expand", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                        {
                            "attr": "Paste Tabular Data",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "Edit Mode",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "Delete all data",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {"attr": "MODE", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                    ],
                },
                {
                    "Category_sub_element_name": "Plot_chart",
                    "Category_sub_element_attributes": [
                        {"attr": "Table_name", "value": "DEPENDENT_VALUE"},
                        {
                            "attr": "Plot_chart",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                    ],
                },
                {
                    "Category_sub_element_name": "Set_alert",
                    "Category_sub_element_attributes": [
                        {"attr": "Table_name", "value": "DEPENDENT_VALUE"},
                        {
                            "attr": "Set_alert",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                    ],
                },
                {
                    "Category_sub_element_name": "Filter",
                    "Category_sub_element_attributes": [
                        {"attr": "Table_name", "value": "DEPENDENT_VALUE"},
                        {"attr": "Filter", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                    ],
                },
                {
                    "Category_sub_element_name": "Action",
                    "Category_sub_element_attributes": [
                        {"attr": "Table_name", "value": "DEPENDENT_VALUE"},
                        {
                            "attr": "SelectAll_Action",
                            "value": "No",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "Edit Record",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "Delete Record",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                        {
                            "attr": "View Record",
                            "value": "Yes",
                            "html_attributes": {"data-parent_group_no": "g2"},
                        },
                    ],
                },
            ],
        }
        return template_layout
    else:
        return {"Error": "table_name is mandatory in List View."}


# Analysis Template
def analysis_template_generator(related_data_fields=None):
    template_layout = {
        "PlotCharts": "Yes",
        "AddTabs": "Yes",
        "PDF": "Yes",
        "share_with_group": "Yes",
        "global_settings": "Yes",
        "SaveButton": "Yes",
        "Template": "System defined template",
        "TabList": [{"TabID": 1}, {"TabID": 2}],
        "Analysis_Package": "Analysis Pack - II (Advanced)",
        "Layout": "Landscape",
    }
    return template_layout


# Upload Template
def upload_template_generator(table_names=[], related_data_fields=None):
    template_layout = {
        "Category_attributes": {
            "Mandatory": {"Table_name": table_names, "Template_type": "System defined template"},
            "Connector": {"Template_choice": "Upload functionality"},
        },
        "Category_sub_elements": [
            {"Category_sub_element_name": "Upload"},
            {
                "Category_sub_element_attributes": [
                    {"attr": "Table_name", "value": table_names},
                    {"attr": "Date", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                    {"attr": "Upload", "value": "Yes", "html_attributes": {"data-parent_group_no": "g2"}},
                    {
                        "attr": "Last upload date",
                        "value": "Yes",
                        "html_attributes": {"data-parent_group_no": "g2"},
                    },
                    {
                        "attr": "Next upload date",
                        "value": "Yes",
                        "html_attributes": {"data-parent_group_no": "g2"},
                    },
                    {
                        "attr": "Preview with data confirmation",
                        "value": "No",
                        "html_attributes": {"data-parent_group_no": "g2"},
                    },
                ]
            },
        ],
    }
    return template_layout


# OCR Template
def ocr_template_generator(table_names, related_data_fields=None):
    table_names = table_names.strip()
    field_list = []
    table_df = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Tables",
                "Columns": ["tablename", "fields"],
            },
            "condition": [],
        },
        engine2=main_engine_name,
        db_type="MSSQL",
        engine_override=True,
    ).tablename.tolist()

    # Extract All Field Header
    if table_names in table_df:
        modelName = dynamic_model_create.get_model_class(
            table_names, request_user="", db_engine=main_engine_name
        )
        field_list = [field.verbose_name.title() for field in modelName.concrete_fields]
    elif table_names in data_model_global_list.keys():
        for field_name, field_config in data_model_global_list[table_names].items():
            field_list.append(field_config["field header"])

    template_layout = {
        "tablename": table_names,
        "columns": field_list,
        "percentval": 0,
        "operationtype": "single_image",
    }

    return template_layout


# Pivot Report Template
def pivot_report_template_generator(related_data_fields=None):
    template_layout = {"category_name": "Category1", "report_name": "Report1"}
    return template_layout


# Creating Processses and Subprocess
def create_process_handling(
    request,
    flow_context=None,
    user_engine="",
    db_connection_name="",
):

    flow_context = flow_context["Process_flow"]
    if len(flow_context) > 0:
        for pname, pconfig in flow_context.items():
            pr_code = pconfig["Process_code"]
            pro_item_name = pconfig["Process_name"].strip()
            pro_item_shortname = pconfig["Process_name"][:10].strip()
            PC = pd.DataFrame(
                columns=[
                    "item_name",
                    "item_code",
                    "item_shortname",
                    "item_group_code",
                    "item_group_name",
                    "item_level",
                    "item_popup_config",
                    "item_url",
                    "item_extra_details",
                    "related_entity",
                    "app_allocation_status",
                    "created_by",
                    "created_date",
                ]
            )
            PC_dict = {
                "item_code": pconfig["Process_code"],
                "item_name": pconfig["Process_name"],
                "item_shortname": pro_item_shortname,
                "item_level": 0,
                "item_url": "#",
                "app_allocation_status": pconfig["app_allocation_status"],
                "created_by": request.user.username,
                "created_date": datetime.now(),
            }
            PC_df1 = pd.DataFrame.from_dict([PC_dict])
            PC = pd.concat(
                [PC, PC_df1],
                ignore_index=True,
            )
            data_handling(
                "", PC, "NavigationSideBar", con=main_engine_name, db_type="MSSQL", engine_override=True
            )
            for subprocess in pconfig["sub_process_list"]:
                PC1 = pd.DataFrame(
                    columns=[
                        "item_name",
                        "item_code",
                        "item_shortname",
                        "item_group_code",
                        "item_group_name",
                        "item_level",
                        "item_popup_config",
                        "item_url",
                        "hover_option",
                        "item_extra_details",
                        "related_entity",
                        "app_allocation_status",
                        "created_by",
                        "created_date",
                    ]
                )
                PC1_dict = {
                    "item_code": subprocess["Subprocess_code"],
                    "item_name": subprocess["Subprocess_name"],
                    "item_extra_details": subprocess["Subprocess_shortname"],
                    "item_group_code": subprocess["Subprocess_item_code"],
                    "item_group_name": pro_item_name,
                    "item_group_shortname": pro_item_shortname,
                    "item_level": 1,
                    "item_url": "#",
                    "hover_option": "no",
                    "app_allocation_status": "unallocated",
                    "created_by": request.user.username,
                    "created_date": datetime.now(),
                }
                PC1_df1 = pd.DataFrame.from_dict([PC1_dict])
                PC1 = pd.concat(
                    [PC1, PC1_df1],
                    ignore_index=True,
                )
                data_handling(
                    "", PC1, "NavigationSideBar", con=main_engine_name, db_type="MSSQL", engine_override=True
                )
                if "L3_config" in subprocess:
                    sub_process_code = subprocess["Subprocess_code"]
                    subprocesName = subprocess["Subprocess_name"]
                    xml_flow = f"""<mxGraphModel dx="1202" dy="355" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100"><root><mxCell id="0" /><mxCell id="1" parent="0"/>"""
                    final_xml = """"""
                    x_axis = 50
                    y_axis = 100
                    count = 2
                    for ele in range(len(subprocess["L3_config"])):
                        element_data = subprocess["L3_config"][ele]
                        if x_axis > 550:
                            x_axis = 0
                            y_axis = y_axis + 200
                        if element_data["template_mode"] in ["Create View"]:
                            xml_element = f"""<mxCell id="{count}" value="{element_data['template_mode']}" style="whiteSpace=wrap;html=1;aspect=fixed;shapeUniqueID={element_data['element_id']}" vertex="1" parent="1"><mxGeometry x="{x_axis}" y="{y_axis}" width="80" height="80" as="geometry"/></mxCell>"""
                            xml_flow = xml_flow + xml_element
                            x_axis = x_axis + 150
                        else:
                            xml_element = f"""<mxCell id="{count}" value="{element_data['template_mode']}" style="{element_data['shape']};whiteSpace=wrap;html=1;aspect=fixed;shapeUniqueID={element_data['element_id']}" vertex="1" parent="1"><mxGeometry x="{x_axis}" y="{y_axis}" width="80" height="80" as="geometry"/></mxCell>"""
                            xml_flow = xml_flow + xml_element
                            x_axis = x_axis + 150
                        if ele == len(subprocess["L3_config"]) - 1:
                            xml_flow = xml_flow + "</root></mxGraphModel>"
                            final_xml = xml_flow
                        count = count + 1
                        generate_L3_screen(
                            request,
                            element_data=element_data,
                            related_item_code=sub_process_code,
                            subprocesName=subprocesName,
                            processCode=pr_code,
                            final_xml=final_xml,
                        )
    return "success"


# Generate XML Data
def generate_L3_screen(
    request, element_data, related_item_code, subprocesName, processCode, final_xml=""""""
):
    status = None
    L3_PC = pd.DataFrame(
        columns=[
            "tab_header_name",
            "tab_icon",
            "tab_type",
            "tab_body_content",
            "level",
            "related_item_code",
            "element_id",
            "shape",
            "user_name",
            "table_name",
            "computation_name",
            "fields",
            "tabs_multi_function",
        ]
    )
    if "table_name" in element_data:
        table_name = element_data["table_name"]
        if type(element_data["table_name"]) == list:
            table_name = json.dumps(element_data["table_name"])
        L3_PC_dict = {
            "tab_header_name": element_data["tab_header_name"].strip(),
            "tab_icon": element_data["tab_icon"],
            "tab_type": element_data["tab_type"],
            "tab_body_content": json.dumps(element_data["tab_body_content"]),
            "level": "2",
            "related_item_code": related_item_code,
            "element_id": element_data["element_id"],
            "shape": element_data["shape"],
            "table_name": table_name,
        }
        L3_PC_dict_df = pd.DataFrame.from_dict([L3_PC_dict])
        L3_PC = pd.concat(
            [L3_PC, L3_PC_dict_df],
            ignore_index=True,
        )
        data_handling("", L3_PC, "TabScreens", con=main_engine_name, db_type="MSSQL", engine_override=True)
    else:
        L3_PC_dict = {
            "tab_header_name": element_data["tab_header_name"].strip(),
            "tab_icon": element_data["tab_icon"],
            "tab_type": element_data["tab_type"],
            "tab_body_content": json.dumps(element_data["tab_body_content"]),
            "level": "2",
            "related_item_code": related_item_code,
            "element_id": element_data["element_id"],
            "shape": element_data["shape"],
        }
        L3_PC_dict_df = pd.DataFrame.from_dict([L3_PC_dict])
        L3_PC = pd.concat([L3_PC, L3_PC_dict_df], ignore_index=True)
        data_handling("", L3_PC, "TabScreens", con=main_engine_name, db_type="MSSQL", engine_override=True)
    if final_xml != """""":
        xml_request = {}
        xml_request["filename"] = "Drawing1.xml"
        xml_request["xml"] = final_xml
        xml_request["processCode"] = processCode
        xml_request["subprocessName"] = subprocesName
        if not request.POST._mutable:
            request.POST._mutable = True
        request.POST["App_Creation_Data"] = xml_request
        status = views.XmlFlowchart(request, db_engine=main_engine_name, skip_gen=True)
        status = "success"
    return status


# Create Business Models
def create_business_model(request, bus_config):
    bus_pro_status = "success"
    if len(bus_config) > 0:
        bus_pro_status = None
        for bus_name, bus_info in bus_config.items():
            if not request.POST._mutable:
                request.POST._mutable = True
            # Create Business Model
            request.POST["operation"] = "createBusinessModel"
            request.POST["user_business_code"] = bus_info["Business_code"]
            request.POST["businessModelName"] = bus_name
            request.POST["businessModelDesc"] = bus_info["Business_description"]
            request.POST["db_engine"] = main_engine_name
            request.POST["operation"] = "createBusinessModel"
            bus_pro_status = views.business_model(request)
            bus_pro_status = "success"

            # Add Process to Business Model
            if "Process_name" in bus_info.keys():
                process_name = None
                process_code = None
                if len(bus_info["Process_name"]) > 0:
                    process_name = json.dumps(list(bus_info["Process_name"].keys()))
                    process_code = json.dumps(list(bus_info["Process_name"].values()))
                    request.POST["operation"] = "addBMProcess"
                    request.POST["businessModelName"] = bus_name
                    request.POST["businessModelCode"] = bus_info["Business_code"]
                    request.POST["process_name"] = process_name
                    request.POST["process_code"] = process_code
                    bus_pro_status = views.business_model(request)
                    bus_pro_status = "success"

            # Add DataTables to Business Model
            if "DataTables" in bus_info.keys():
                data_tables = []
                if len(bus_info["DataTables"]) > 0:
                    data_tables = json.dumps(bus_info["DataTables"])
                    request.POST["operation"] = "addBMData"
                    request.POST["businessModelName"] = bus_name
                    request.POST["table_name"] = data_tables
                    bus_pro_status = views.business_model(request)
                    bus_pro_status = "success"

    return bus_pro_status


# Create Application Models
def create_application_model(request, app_config):
    if not request.POST._mutable:
        request.POST._mutable = True
    for app_name, appInfo in app_config.items():
        request.POST["operation"] = "createApplication"
        request.POST["applicationName"] = app_name
        request.POST["applicationDesc"] = appInfo["App_Description"]
        request.POST["appIcon"] = appInfo["app_icon"]
        request.POST["app_code"] = appInfo["App_code"]
        request.POST["iconColor"] = appInfo["app_icon_color"]
        request.POST["cardColor"] = appInfo["app_card_color"]
        request.POST["textColor"] = appInfo["app_text_color"]
        request.POST["business_model_name"] = ""
        request.POST["business_model_code"] = ""
        app_status = views.application(request)
        if "business_model_names" in appInfo:
            business_list = appInfo["business_model_names"]
            if len(business_list) > 0:
                for bm_name, bm_code in business_list.items():
                    request.POST["application_code"] = appInfo["App_code"]
                    request.POST["operation"] = "addAppBM"
                    request.POST["business_model_name"] = bm_name
                    request.POST["business_model_code"] = bm_code["Business_code"]
                    app_status = views.application(request)
        request.POST["user_application_code"] = appInfo["App_code"]
        user_info = {}
        user_info["current_application_code"] = appInfo["App_code"]
        user_info["current_developer_mode"] = "Build"
        user_info["build_app_code"] = appInfo["App_code"]
        user_info["build_process_type"] = "Final"
        redis_instance.set(request.user.username, pickle.dumps(user_info))
        app_status = views.htmlgeneratorall(request, skip_gen=False)
    app_status = "success"
    return app_status
