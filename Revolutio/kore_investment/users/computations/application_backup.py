from datetime import datetime
import json
import logging
import os
from ast import literal_eval

from django_multitenant.utils import get_current_tenant
import pandas as pd

## Cache
from config.settings.base import PLATFORM_FILE_PATH
from kore_investment.users import scheduler as schedulerfunc
from kore_investment.users.computations import emailBox_functions, standardised_functions
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    db_engine_extractor,
    delete_data_func,
    read_data_func,
    update_data_func,
)
from kore_investment.users.computations.model_field_info import ModelInfo
from kore_investment.users.computations.standardised_functions import nestedForeignKey

from . import Data_replica_utilities, dynamic_model_create
from .process_scheduler_handler import schedule_block, schedule_flow
from django.contrib.auth.models import Group


def backup_application(app_code, data_backup, request, permissions_backup=False, permissions_migration_option="append"):
    context = {}
    app_db_mapping = {}
    app_config_json = {}
    app_data_backup = {}
    instance = get_current_tenant()
    tenant = instance.name
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()
    if app_db_mapping:
        tenant_app_code = tenant + "_" + app_code
        db_connection_name = app_db_mapping[tenant_app_code]
        db_type = "MSSQL"
        try:
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
            context["response"] = f"Error connecting to the database! {str(e)}"
        else:
            app_config_json = {
                "version": "1.0.0",
            }
            app_config = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Application",
                        "Columns": ["*"],
                    },
                    "condition": [
                        {
                            "column_name": "application_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "",
                        }
                    ],
                },
                engine2=user_db_engine,
                engine_override=True,
                db_type=db_type,
            )
            app_config.drop(columns=["id"], inplace=True)
            app_config_json["application_config"] = app_config.to_dict("records")

            # Business Model config
            tagged_bm = app_config.business_model_codes.iloc[0]
            if tagged_bm:
                tagged_bm = tagged_bm.replace('"', "'").replace("[", "(").replace("]", ")")
                bm_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Business_Models",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "business_model_code",
                                "condition": "IN",
                                "input_value": tagged_bm,
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                bm_config.drop(columns=["id"], inplace=True)
            else:
                bm_config = pd.DataFrame()
            app_config_json["business_model_config"] = bm_config.to_dict("records")

            # Process config
            tagged_process = app_config.process_group_codes.iloc[0]
            if tagged_process and tagged_process != "[]":
                tagged_process = tagged_process.replace('"', "'").replace("[", "(").replace("]", ")")
                nav_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "NavigationSideBar",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "item_code",
                                "condition": "IN",
                                "input_value": tagged_process,
                                "and_or": "or",
                            },
                            {
                                "column_name": "item_group_code",
                                "condition": "IN",
                                "input_value": tagged_process,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                nav_config.drop(columns=["id"], inplace=True)
            else:
                nav_config = pd.DataFrame()

            app_config_json["navigationSidebar_config"] = nav_config.to_dict("records")

            if app_config.process_group_codes.iloc[0] and app_config.process_group_codes.iloc[0] != "[]":
                tagged_subprocess = [
                    i
                    for i in nav_config["item_code"].tolist()
                    if i not in json.loads(app_config.process_group_codes.iloc[0])
                ]
                tagged_subpr = (
                    json.dumps(tagged_subprocess).replace('"', "'").replace("[", "(").replace("]", ")")
                )

                process_flowchart_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Process_subprocess_flowchart",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "related_item_code",
                                "condition": "IN",
                                "input_value": tagged_subpr,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                process_flowchart_config.drop(columns=["id"], inplace=True)
                app_config_json["process_flow_config"] = process_flowchart_config.to_dict("records")

                tabscreen_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "TabScreens",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "related_item_code",
                                "condition": "IN",
                                "input_value": tagged_subpr,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                tabscreen_config.drop(columns=["id"], inplace=True)
                app_config_json["tabscreen_config"] = tabscreen_config.to_dict("records")

                dashboard_user_config = pd.DataFrame()
                dashboard_condition_list = []
                for idx, row in tabscreen_config.iterrows():
                    if row["tab_type"] == "analysis":
                        dashboard_condition_list.append(
                            {
                                "column_name": "screen_url",
                                "condition": "Contains",
                                "input_value": row["related_item_code"],
                                "and_or": "",
                                "constraintName": "scrren_url",
                                "ruleSet": f"{idx}",
                            },
                        )
                    else:
                        continue
                dashboard_user_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "UserConfig",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "analysis_config",
                                "condition": "Not Equal to",
                                "input_value": "NULL",
                                "and_or": "",
                                "constraintName": "nullCon",
                                "ruleSet": "nullCon",
                            },
                            {
                                "column_name": "name",
                                "condition": "Equal to",
                                "input_value": request.user.username,
                                "and_or": "",
                                "constraintName": "createdBy",
                                "ruleSet": "createdBy",
                            },
                            *dashboard_condition_list,
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if not dashboard_user_config.empty:
                    dashboard_user_config.drop(columns=["id"], inplace=True)
                else:
                    pass
                app_config_json["dashboard_user_config"] = dashboard_user_config.to_dict("records")

                published_dashboard_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "dashboard_config",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "app_code",
                                "condition": "Contains",
                                "input_value": app_code,
                                "and_or": "",
                            }
                        ],
                    },
                )
                if not published_dashboard_config.empty:
                    published_dashboard_config.drop(columns=["id"], inplace=True)
                else:
                    pass
                app_config_json["published_dashboard_config"] = published_dashboard_config.to_dict("records")

                pivot_report_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "ConfigTable",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if not pivot_report_config.empty:
                    pivot_report_config.drop(columns=["id"], inplace=True)
                else:
                    pass
                app_config_json["pivot_report_config"] = pivot_report_config.to_dict("records")
            else:
                app_config_json["process_flow_config"] = []
                app_config_json["tabscreen_config"] = []
                app_config_json["dashboard_user_config"] = []
                app_config_json["published_dashboard_config"] = []
                app_config_json["pivot_report_config"] = []

            # Process Scheduler config
            tagged_process = app_config.process_group_codes.iloc[0]
            if tagged_process and tagged_process != "[]":
                scheduler_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "ProcessScheduler",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                scheduler_config.drop(columns=["id"], inplace=True)
            else:
                scheduler_config = pd.DataFrame()

            app_config_json["process_scheduler_config"] = scheduler_config.to_dict("records")

            tagged_comp_model = app_config.computation_model_names.iloc[0]
            if json.loads(tagged_comp_model):
                tagged_comp_model = tagged_comp_model.replace('"', "'").replace("[", "(").replace("]", ")")
                comp_model_configuration = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "computation_model_configuration",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "model_name",
                                "condition": "IN",
                                "input_value": tagged_comp_model,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                comp_model_configuration.drop(columns=["id"], inplace=True)
                app_config_json["comp_model_configuration"] = comp_model_configuration.to_dict("records")

                comp_model_flowchart_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "computation_model_flowchart",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "model_name",
                                "condition": "IN",
                                "input_value": tagged_comp_model,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                comp_model_flowchart_config.drop(columns=["id"], inplace=True)
                app_config_json["comp_model_flowchart_config"] = comp_model_flowchart_config.to_dict(
                    "records"
                )

                comp_output_repo = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "computation_output_repository",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "model_name",
                                "condition": "IN",
                                "input_value": tagged_comp_model,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                comp_output_repo.drop(columns=["id"], inplace=True)
                app_config_json["comp_output_repo"] = comp_output_repo.to_dict("records")
            else:
                app_config_json["comp_model_configuration"] = []
                app_config_json["comp_model_flowchart_config"] = []
                app_config_json["comp_output_repo"] = []

            tagged_data_tables = app_config.table_names.iloc[0]
            if tagged_data_tables:
                tagged_data_tables = tagged_data_tables.replace('"', "'").replace("[", "(").replace("]", ")")
                data_table_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Tables",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "tablename",
                                "condition": "IN",
                                "input_value": tagged_data_tables,
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
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                data_table_config.sort_values(by=["id"], ascending=[True], inplace=True)
                data_table_config.drop(columns=["id"], inplace=True)
                tables_list = data_table_config["tablename"].tolist()
                app_config_json["data_table_config"] = data_table_config.to_dict("records")
            else:
                tables_list = []
                app_config_json["data_table_config"] = []
            
            if permissions_backup:
                # User groups and permissions
                app_permissions = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "UserPermission_Master",
                            "Columns": ["*"],
                        },
                        "condition": [
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            }
                        ],
                    },
                ).drop(columns=["id", "instance_id"])
                groups_with_app_access = app_permissions.usergroup.unique().tolist()
                app_config_json["groups_with_app_access"] = groups_with_app_access
                app_config_json["app_permissions"] = app_permissions.to_dict("records")
                app_config_json["permissions_migration_option"] = permissions_migration_option
            else:
                pass

            if data_backup:
                app_data_backup = {
                    "app_code": app_code,
                }
                foreign_key_tables = []
                data_table_backup = {}
                for table in tables_list:
                    foreign_key = False
                    tb_field_config = json.loads(
                        data_table_config[data_table_config["tablename"] == table]["fields"].iloc[0]
                    )
                    model = ModelInfo(table, tb_field_config, other_config={})
                    for field in tb_field_config.values():
                        if field["internal_type"] == "ForeignKey":
                            foreign_key = True
                            break
                    table_data = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table,
                                "Columns": ["*"],
                            },
                            "condition": [],
                        },
                        engine2=user_db_engine,
                        engine_override=True,
                        db_type=db_type,
                    )
                    primary_key = model.pk.name
                    table_data.drop(columns=[primary_key], inplace=True)
                    if not foreign_key:
                        data_table_backup[table] = table_data.to_dict("records")
                    else:
                        for field in model.concrete_fields:
                            if field.internal_type == "ForeignKey":
                                __pt__, table_data, __th__ = nestedForeignKey(
                                    field,
                                    request,
                                    db_connection_name,
                                    table_data,
                                    field.name,
                                    db_engine=user_db_engine,
                                    db_type=db_type,
                                )
                            else:
                                continue
                        data_table_backup[table] = table_data.to_dict("records")
                context["foreign_key_tables"] = foreign_key_tables
                app_data_backup["user_data"] = data_table_backup
    return context, app_config_json, app_data_backup


def restore_app_from_backup(
    backup_file,
    db_connection_name,
    app_asthetic_input,
    backup_data_file,
    request,
    clone_app=True,
    generate_app_code=True,
    skip_if_exists=False,
):
    context = {}
    error_data_list = []
    instance = get_current_tenant()
    tenant = instance.name
    try:
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        context["response"] = f"Error connecting to the database! {str(e)}"
    else:
        app_config_json = backup_file
        if app_config_json.get("application_config"):
            application_config = app_config_json["application_config"]
            if application_config:
                application_config = pd.DataFrame(application_config)
                app_code = application_config["application_code"].iloc[0]
                if clone_app and generate_app_code:
                    new_app_code = "App" + standardised_functions.random_no_generator()
                    application_config["application_code"].iloc[0] = new_app_code
                else:
                    new_app_code = app_code
                if app_asthetic_input == "true":
                    customAppName = request.POST["customAppName"]
                    customAppDesc = request.POST["customAppDesc"]
                    appIcon = request.POST["appIcon"]
                    iconColor = request.POST["iconColor"]
                    cardColor = request.POST["cardColor"]
                    textColor = request.POST["textColor"]
                    application_config["application_name"].iloc[0] = customAppName
                    application_config["description"].iloc[0] = customAppDesc
                    application_config["app_icon"].iloc[0] = appIcon
                    application_config["app_icon_color"].iloc[0] = iconColor
                    application_config["app_card_color"].iloc[0] = cardColor
                    application_config["app_text_color"].iloc[0] = textColor
                existing_app_check = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Application",
                            "Columns": ["id"],
                        },
                        "condition": [
                            {
                                "column_name": "application_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(existing_app_check) == 0:
                    bm_exists_list = []
                    bm_code = application_config["business_model_codes"].iloc[0]
                    if len(json.loads(bm_code)) > 0 and app_config_json.get("business_model_config"):
                        new_bm_codes = bm_code.replace('"', "'").replace("[", "(").replace("]", ")")
                        existing_bm_check = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "Business_Models",
                                    "Columns": ["id", "business_model_code"],
                                },
                                "condition": [
                                    {
                                        "column_name": "business_model_code",
                                        "condition": "IN",
                                        "input_value": new_bm_codes,
                                        "and_or": "",
                                    }
                                ],
                            },
                            engine2=user_db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )
                        if skip_if_exists and not existing_bm_check.empty:
                            bm_exists_list = existing_bm_check.business_model_code.tolist()
                        if len(existing_bm_check) > 0 and not skip_if_exists:
                            context["response"] = (
                                f"Error loading the app! Business model already exists please select another database."
                            )
                        else:
                            navbar_validation_check = True
                            comp_validation_check = True
                            if app_config_json.get("navigationSidebar_config"):
                                navigationSidebar_config = app_config_json["navigationSidebar_config"]
                                skip_navbar_items = []
                                if len(navigationSidebar_config):
                                    navigationSidebar_config = pd.DataFrame(navigationSidebar_config)
                                    item_codes = navigationSidebar_config["item_code"].tolist()
                                    new_item_codes = (
                                        json.dumps(item_codes)
                                        .replace('"', "'")
                                        .replace("[", "(")
                                        .replace("]", ")")
                                    )
                                    existing_nav_check = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "NavigationSideBar",
                                                "Columns": ["id", "item_code"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "item_code",
                                                    "condition": "IN",
                                                    "input_value": new_item_codes,
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                        engine2=user_db_engine,
                                        db_type=db_type,
                                        engine_override=True,
                                    )
                                    if len(existing_nav_check) > 0:
                                        if skip_if_exists:
                                            navbar_validation_check = True
                                            skip_navbar_items = existing_nav_check["item_code"].tolist()
                                        else:
                                            navbar_validation_check = False
                                    else:
                                        pass

                                    new_comp_models = application_config["computation_model_names"].iloc[0]
                                    skip_comp_models = []
                                    if json.loads(new_comp_models):
                                        new_comp_models = (
                                            new_comp_models.replace('"', "'")
                                            .replace("[", "(")
                                            .replace("]", ")")
                                        )
                                        existing_comp_check = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "computation_model_configuration",
                                                    "Columns": ["id", "model_name"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "model_name",
                                                        "condition": "IN",
                                                        "input_value": new_comp_models,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                            engine2=user_db_engine,
                                            db_type=db_type,
                                            engine_override=True,
                                        )
                                        if len(existing_comp_check) > 0:
                                            if skip_if_exists:
                                                comp_validation_check = True
                                                skip_comp_models = existing_comp_check["model_name"].tolist()
                                            else:
                                                comp_validation_check = False
                                        else:
                                            comp_model_configuration = pd.DataFrame(
                                                app_config_json["comp_model_configuration"]
                                            )
                                            comp_model_configuration = comp_model_configuration[
                                                ~comp_model_configuration["model_name"].isin(skip_comp_models)
                                            ]
                                            comp_model_flowchart_config = pd.DataFrame(
                                                app_config_json["comp_model_flowchart_config"]
                                            )
                                            comp_model_flowchart_config = comp_model_flowchart_config[
                                                ~comp_model_flowchart_config["model_name"].isin(
                                                    skip_comp_models
                                                )
                                            ]
                                            comp_output_repo = pd.DataFrame(
                                                app_config_json["comp_output_repo"]
                                            )
                                            if not comp_model_configuration.empty:
                                                data_handling(
                                                    request,
                                                    comp_model_configuration,
                                                    "computation_model_configuration",
                                                    con=user_db_engine,
                                                    db_type=db_type,
                                                    engine_override=True,
                                                )
                                            if not comp_model_flowchart_config.empty:
                                                data_handling(
                                                    request,
                                                    comp_model_flowchart_config,
                                                    "computation_model_flowchart",
                                                    con=user_db_engine,
                                                    db_type=db_type,
                                                    engine_override=True,
                                                )
                                            if not comp_output_repo.empty:
                                                data_handling(
                                                    request,
                                                    comp_output_repo,
                                                    "computation_output_repository",
                                                    con=user_db_engine,
                                                    db_type=db_type,
                                                    engine_override=True,
                                                )
                                    else:
                                        pass
                                    if navbar_validation_check and comp_validation_check:
                                        navigationSidebar_config = pd.DataFrame(
                                            app_config_json["navigationSidebar_config"]
                                        )
                                        navigationSidebar_config = navigationSidebar_config[
                                            ~navigationSidebar_config["item_code"].isin(skip_navbar_items)
                                        ]

                                        process_flow_config = pd.DataFrame(
                                            app_config_json["process_flow_config"]
                                        )
                                        process_flow_config = process_flow_config[
                                            ~process_flow_config["related_item_code"].isin(skip_navbar_items)
                                        ]

                                        tabscreen_config = pd.DataFrame(app_config_json["tabscreen_config"])
                                        tabscreen_config = tabscreen_config[
                                            ~tabscreen_config["related_item_code"].isin(skip_navbar_items)
                                        ]

                                        if app_config_json.get("dashboard_user_config"):
                                            dashboard_user_config = pd.DataFrame(
                                                app_config_json["dashboard_user_config"]
                                            )
                                            dashboard_user_config = dashboard_user_config[
                                                ~dashboard_user_config["screen_url"].isin(skip_navbar_items)
                                            ]
                                            dashboard_user_config["name"] = request.user.username
                                        else:
                                            dashboard_user_config = pd.DataFrame()

                                        if app_config_json.get("published_dashboard_config"):
                                            published_dashboard_config = pd.DataFrame(
                                                app_config_json["published_dashboard_config"]
                                            )
                                            published_dashboard_config = published_dashboard_config[
                                                ~published_dashboard_config["subprocess_code"].isin(
                                                    skip_navbar_items
                                                )
                                            ]
                                            published_dashboard_config["shared_username"] = (
                                                request.user.username
                                            )
                                        else:
                                            published_dashboard_config = pd.DataFrame()

                                        if app_config_json.get("process_scheduler_config"):
                                            process_scheduler_config = pd.DataFrame(
                                                app_config_json["process_scheduler_config"]
                                            )
                                        else:
                                            process_scheduler_config = pd.DataFrame()

                                        if app_config_json.get("pivot_report_config"):
                                            pivot_report_config = pd.DataFrame(
                                                app_config_json["pivot_report_config"]
                                            )
                                        else:
                                            pivot_report_config = pd.DataFrame()

                                        if not navigationSidebar_config.empty:
                                            navigationSidebar_config["created_date"] = pd.to_datetime(
                                                navigationSidebar_config["created_date"]
                                            ).dt.strftime("%Y-%m-%d %H:%M:%S")
                                            data_handling(
                                                request,
                                                navigationSidebar_config,
                                                "NavigationSideBar",
                                                con=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )
                                        if not process_flow_config.empty:
                                            data_handling(
                                                request,
                                                process_flow_config,
                                                "Process_subprocess_flowchart",
                                                con=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )
                                        if not tabscreen_config.empty:
                                            data_handling(
                                                request,
                                                tabscreen_config,
                                                "TabScreens",
                                                con=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )
                                            for idx, tb_row in tabscreen_config.iterrows():
                                                if tb_row["tab_type"] == "message":
                                                    task_config = json.loads(tb_row["tab_body_content"])
                                                    if task_config["trigger_type"] == "schedule_based":
                                                        start_date = datetime.strptime(
                                                            task_config["config"]["scheduler_config"][
                                                                "start_date"
                                                            ],
                                                            "%Y-%m-%d",
                                                        )
                                                        end_date = datetime.strptime(
                                                            task_config["config"]["scheduler_config"][
                                                                "end_date"
                                                            ],
                                                            "%Y-%m-%d",
                                                        )
                                                        duration = task_config["config"]["scheduler_config"][
                                                            "duration"
                                                        ]
                                                        if duration == "Monthly":
                                                            day = start_date.day
                                                            month = "*"
                                                            day_of_week = "*"
                                                        elif duration == "Monthly/5th day":
                                                            day = "5"
                                                            month = "*"
                                                            day_of_week = "*"
                                                        elif duration == "Quarterly":
                                                            day = start_date.day
                                                            month = "1,4,7,10"
                                                            day_of_week = "*"
                                                        elif duration == "Pre-Quarterly":
                                                            day = "24"
                                                            month = "12,3,6,9"
                                                            day_of_week = "*"
                                                        elif duration == "Weekly":
                                                            day_of_week = start_date.weekday()
                                                            month = "*"
                                                            day = "*"
                                                        elif duration == "Daily":
                                                            month = "*"
                                                            day = "*"
                                                            day_of_week = "*"
                                                        elif duration == "Yearly":
                                                            month = start_date.month
                                                            day = start_date.day
                                                            day_of_week = "*"
                                                        time_var = task_config["config"]["scheduler_config"][
                                                            "time_interval"
                                                        ]
                                                        if time_var.split(":")[0][0] == "0":
                                                            hour = literal_eval(time_var.split(":")[0][1])
                                                        else:
                                                            hour = literal_eval(time_var.split(":")[0])
                                                        if time_var.split(":")[1][0] == "0":
                                                            minute = literal_eval(time_var.split(":")[1][1])
                                                        else:
                                                            minute = literal_eval(time_var.split(":")[1])

                                                        func = emailBox_functions.emailBox

                                                        job_id = tb_row["element_id"]

                                                        schedulerfunc.add_scheduler(
                                                            func,
                                                            job_id,
                                                            request,
                                                            month,
                                                            day_of_week,
                                                            day,
                                                            hour,
                                                            minute,
                                                            start_date,
                                                            end_date,
                                                        )

                                                else:
                                                    continue

                                        if not dashboard_user_config.empty:
                                            data_handling(
                                                request,
                                                dashboard_user_config,
                                                "UserConfig",
                                                con=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )

                                        if not pivot_report_config.empty:
                                            data_handling(
                                                request,
                                                pivot_report_config,
                                                "ConfigTable",
                                                con=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )

                                        if not published_dashboard_config.empty:
                                            for idx, row in published_dashboard_config.iterrows():
                                                user_dashboard_config = read_data_func(
                                                    request,
                                                    {
                                                        "inputs": {
                                                            "Data_source": "Database",
                                                            "Table": "UserConfig",
                                                            "Columns": ["id"],
                                                        },
                                                        "condition": [
                                                            {
                                                                "column_name": "screen_url",
                                                                "condition": "Contains",
                                                                "input_value": row["subprocess_code"],
                                                                "and_or": "AND",
                                                            },
                                                            {
                                                                "column_name": "name",
                                                                "condition": "Equal to",
                                                                "input_value": row["shared_username"],
                                                                "and_or": "",
                                                            },
                                                        ],
                                                    },
                                                    engine2=user_db_engine,
                                                    db_type=db_type,
                                                    engine_override=True,
                                                )
                                                if not user_dashboard_config.empty:
                                                    published_dashboard_config.loc[
                                                        idx, "dashboard_config_id"
                                                    ] = int(user_dashboard_config.iloc[0, 0])
                                                else:
                                                    pass
                                            published_dashboard_config["instance_id"] = instance.id
                                            data_handling(
                                                request, published_dashboard_config, "dashboard_config"
                                            )
                                        else:
                                            pass

                                        if not process_scheduler_config.empty:
                                            existing_scheduler_config = read_data_func(
                                                request,
                                                {
                                                    "inputs": {
                                                        "Data_source": "Database",
                                                        "Table": "ProcessScheduler",
                                                        "Columns": ["id"],
                                                    },
                                                    "condition": [
                                                        {
                                                            "column_name": "app_code",
                                                            "condition": "Equal to",
                                                            "input_value": app_code,
                                                            "and_or": "",
                                                        }
                                                    ],
                                                },
                                                engine2=user_db_engine,
                                                db_type=db_type,
                                                engine_override=True,
                                            )
                                            if not existing_scheduler_config.empty:
                                                delete_data_func(
                                                    request,
                                                    {
                                                        "inputs": {
                                                            "Data_source": "Database",
                                                            "Table": "ProcessScheduler",
                                                        },
                                                        "condition": [
                                                            {
                                                                "column_name": "app_code",
                                                                "condition": "Equal to",
                                                                "input_value": app_code,
                                                                "and_or": "",
                                                            }
                                                        ],
                                                    },
                                                )
                                            else:
                                                pass
                                            data_handling(
                                                request, process_scheduler_config, "ProcessScheduler"
                                            )
                                            for idx, sc_row in process_scheduler_config.iterrows():
                                                if sc_row["scheduler_type"] == "block":
                                                    block_config = json.loads(sc_row["config"])
                                                    if sc_row["trigger_option"] == "interval":
                                                        schedule_block(
                                                            request,
                                                            sc_row["element_id"],
                                                            block_config,
                                                            sc_row["item_code"],
                                                            sc_row["item_group_code"],
                                                        )
                                                    if block_config.get("additionalJobs"):
                                                        for b_idx, b_c in enumerate(
                                                            block_config["additionalJobs"]
                                                        ):
                                                            if b_c["schedulerTrigger"] == "interval":
                                                                schedule_block(
                                                                    request,
                                                                    sc_row["element_id"],
                                                                    b_c,
                                                                    sc_row["item_code"],
                                                                    sc_row["item_group_code"],
                                                                    b_index=b_idx,
                                                                )
                                                            else:
                                                                pass
                                                    else:
                                                        pass
                                                else:
                                                    schedule_flow(
                                                        request,
                                                        json.loads(sc_row["config"]),
                                                        sc_row["item_code"],
                                                        sc_row["item_group_code"],
                                                    )
                                        else:
                                            pass
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                pass
                            if navbar_validation_check and comp_validation_check:
                                if app_config_json.get("data_table_config"):
                                    new_table_name = application_config["table_names"].iloc[0]
                                    if json.loads(new_table_name):
                                        new_tables_list = json.loads(new_table_name)
                                        new_table_checker = (
                                            new_table_name.replace('"', "'")
                                            .replace("[", "(")
                                            .replace("]", ")")
                                        )
                                        existing_tables = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "Tables",
                                                    "Columns": ["tablename"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "tablename",
                                                        "condition": "IN",
                                                        "input_value": new_table_checker,
                                                        "and_or": "",
                                                    },
                                                ],
                                            },
                                            engine2=user_db_engine,
                                            db_type=db_type,
                                            engine_override=True,
                                        ).tablename.tolist()
                                        new_tables_list = [
                                            i for i in new_tables_list if i not in existing_tables
                                        ]
                                        data_table_config = pd.DataFrame(app_config_json["data_table_config"])
                                        data_table_config = data_table_config[
                                            data_table_config["tablename"].isin(new_tables_list)
                                        ]
                                        tables_error_dict = {}
                                        tables_created = []
                                        replica_tables_to_be_created = []
                                        for row, tb_row in data_table_config.iterrows():
                                            new_model_name = tb_row["tablename"]
                                            user_table_field = json.loads(tb_row["fields"])
                                            linked_table = tb_row["linked_table"]
                                            fields = []
                                            for f_name, f_attr in user_table_field.items():
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
                                                        field_config["choices"] = [i[0] for i in val]
                                                    elif attr == "max_length":
                                                        field_config["maximum length*"] = val
                                                    elif attr == "parent":
                                                        field_config["parent table"] = val
                                                    elif attr == "auto_now":
                                                        field_config["auto now?"] = val
                                                    elif attr == "editable":
                                                        field_config["editable?"] = val
                                                    elif attr == "mulsel_config":
                                                        field_config["mulsel_config"] = val
                                                    elif attr == "use_seconds":
                                                        field_config["Seconds precision?"] = val
                                                    else:
                                                        field_config[attr] = val
                                                if not field_config.get("unique"):
                                                    field_config["unique"] = "No"
                                                fields.append(field_config)
                                            try:
                                                dynamic_model_create.create_table_sql(
                                                    new_model_name,
                                                    fields,
                                                    request,
                                                    db_connection_name=db_connection_name,
                                                    restore=True,
                                                    linked_table=linked_table,
                                                )
                                                tables_created.append(new_model_name)
                                                if linked_table:
                                                    replica_tables_to_be_created.append(linked_table)
                                                else:
                                                    pass
                                            except Exception as e:
                                                logging.warning(
                                                    f"Following exception occured while creating {new_model_name} table in database - {e}"
                                                )
                                                tables_error_dict[new_model_name] = [fields, linked_table]
                                        for new_model_name, config in tables_error_dict.items():
                                            try:
                                                dynamic_model_create.create_table_sql(
                                                    new_model_name,
                                                    config[0],
                                                    request,
                                                    db_connection_name=db_connection_name,
                                                    restore=True,
                                                    linked_table=config[1],
                                                )
                                                tables_created.append(new_model_name)
                                                if linked_table:
                                                    replica_tables_to_be_created.append(linked_table)
                                                else:
                                                    pass
                                            except Exception as e:
                                                logging.warning(
                                                    f"Following exception occured while creating {new_model_name} table in database - {e}"
                                                )
                                        if replica_tables_to_be_created:
                                            tables_not_created = [
                                                i
                                                for i in replica_tables_to_be_created
                                                if i not in tables_created
                                            ]
                                            if tables_not_created:
                                                for replica_table in tables_not_created:
                                                    try:
                                                        Data_replica_utilities.create_replica_table(
                                                            request,
                                                            replica_table.rstrip("_mul"),
                                                            db_connection_name=db_connection_name,
                                                            engine2=user_db_engine,
                                                            db_type=db_type,
                                                            engine_override=True,
                                                        )
                                                    except Exception as e:
                                                        logging.warning(
                                                            f"Following exception occured while creating {replica_table} table in database - {e}"
                                                        )
                                            else:
                                                pass
                                        else:
                                            pass

                                if backup_data_file:
                                    data_app_code = backup_data_file["app_code"]
                                    if app_code == data_app_code:
                                        user_data = backup_data_file["user_data"]
                                        for table, t_data in user_data.items():
                                            data_for_push = pd.DataFrame(t_data)
                                            if not data_for_push.empty:
                                                try:
                                                    modelClass = dynamic_model_create.get_model_class(
                                                        table,
                                                        request,
                                                        db_engine=user_db_engine,
                                                        db_type=db_type,
                                                    )
                                                    for field in modelClass.concrete_fields:
                                                        if (
                                                            field.internal_type == "ForeignKey"
                                                            and field.name in data_for_push.columns
                                                        ):
                                                            if (
                                                                data_for_push[field.name]
                                                                .dropna()
                                                                .unique()
                                                                .tolist()
                                                            ):
                                                                parent_table = field.parent
                                                                parentModel = (
                                                                    dynamic_model_create.get_model_class(
                                                                        parent_table,
                                                                        request,
                                                                        db_engine=user_db_engine,
                                                                        db_type=db_type,
                                                                    )
                                                                )
                                                                foreignkey_data = (
                                                                    read_data_func(
                                                                        request,
                                                                        {
                                                                            "inputs": {
                                                                                "Data_source": "Database",
                                                                                "Table": parent_table,
                                                                                "Columns": [
                                                                                    parentModel.pk.name,
                                                                                    field.name,
                                                                                ],
                                                                            },
                                                                            "condition": [
                                                                                {
                                                                                    "column_name": field.name,
                                                                                    "condition": "IN",
                                                                                    "input_value": data_for_push[
                                                                                        field.name
                                                                                    ]
                                                                                    .dropna()
                                                                                    .unique()
                                                                                    .tolist(),
                                                                                    "and_or": "",
                                                                                },
                                                                            ],
                                                                        },
                                                                        engine2=user_db_engine,
                                                                        db_type=db_type,
                                                                        engine_override=True,
                                                                        fetch_all_entries=True,
                                                                        access_controller=False,
                                                                    )
                                                                    .set_index(field.name)[
                                                                        parentModel.pk.name
                                                                    ]
                                                                    .to_dict()
                                                                )
                                                                data_for_push[field.name] = data_for_push[
                                                                    field.name
                                                                ].replace(to_replace=foreignkey_data)
                                                            else:
                                                                continue
                                                        else:
                                                            continue
                                                    data_handling(
                                                        request,
                                                        data_for_push,
                                                        table,
                                                        con=user_db_engine,
                                                        db_type=db_type,
                                                        engine_override=True,
                                                    )
                                                except Exception as e:
                                                    logging.warning(f"Following exception occured - {e}")
                                                    error_data_list.append(table)

                                business_model_config = pd.DataFrame(app_config_json["business_model_config"])
                                business_model_config = business_model_config[
                                    ~business_model_config["business_model_code"].isin(bm_exists_list)
                                ]

                                if not business_model_config.empty:
                                    data_handling(
                                        request,
                                        business_model_config,
                                        "Business_Models",
                                        con=user_db_engine,
                                        db_type=db_type,
                                        engine_override=True,
                                    )

                                if not application_config.empty:
                                    data_handling(
                                        request,
                                        application_config,
                                        "Application",
                                        con=user_db_engine,
                                        db_type=db_type,
                                        engine_override=True,
                                    )
                                context["response"] = f"Successfully loaded the app."
                            else:
                                if not navbar_validation_check:
                                    context["response"] = (
                                        f"Error loading the app! Process/ Sub-process with the same code already exists please select another database."
                                    )
                                else:
                                    context["response"] = (
                                        f"Error loading the app! Computation model with the same name already exists please select another database."
                                    )
                    else:
                        data_handling(
                            request,
                            application_config,
                            "Application",
                            con=user_db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )
                        context["response"] = f"Successfully loaded the app."
                    
                    # Permissions Reload
                    if app_config_json.get("groups_with_app_access"):
                        groups_with_app_access = app_config_json["groups_with_app_access"]
                        permissions_migration_option = app_config_json.get("permissions_migration_option", "replace")
                        existing_group_check = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "auth_group",
                                    "Columns": ["name"],
                                },
                                "condition": [
                                    {
                                        "column_name": "name",
                                        "condition": "IN",
                                        "input_value": groups_with_app_access,
                                        "and_or": "",
                                    },
                                ],
                            },
                        ).name.tolist()
                        new_groups_to_be_added = [i for i in groups_with_app_access if i not in existing_group_check]
                        if new_groups_to_be_added:
                            groups_created = []
                            for grp in new_groups_to_be_added:
                                group, created = Group.objects.get_or_create(name=grp)
                                if created:
                                    groups_created.append(
                                        {
                                            "name": grp,
                                            "created_date": datetime.now(),
                                            "created_by": request.user.username,
                                            "modified_date": datetime.now(),
                                            "modified_by": request.user.username,
                                        }
                                    )
                                else:
                                    continue
                            if groups_created:
                                groups_created = pd.DataFrame(groups_created)
                                data_handling(request, groups_created, "group_details")
                            else:
                                pass
                        else:
                            pass
                    else:
                        groups_with_app_access = []
                    if app_config_json.get("app_permissions"):
                        permissions_migration_option = app_config_json.get("permissions_migration_option", "replace")
                        app_permissions = app_config_json["app_permissions"]
                        if permissions_migration_option == "append":
                            data_handling(request, pd.DataFrame(app_permissions), "UserPermission_Master")
                        else:
                            delete_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "UserPermission_Master",
                                    },
                                    "condition": [
                                        {
                                            "column_name": "app_code",
                                            "condition": "Equal to",
                                            "input_value": app_code,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                            data_handling(request, pd.DataFrame(app_permissions), "UserPermission_Master")
                    else:
                        pass
                else:
                    context["response"] = (
                        f"Error loading the app! App already exists please select another database."
                    )
            else:
                context["response"] = f"Error loading the app! Invalid backup provided."
        else:
            context["response"] = f"Error loading the app! Invalid backup provided."

    if context["response"] == f"Successfully loaded the app.":
        # Update App to database mapping json
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        new_tenant_app_code = tenant + "_" + new_app_code
        app_db_mapping[new_tenant_app_code] = db_connection_name
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json", "w") as outfile:
            json.dump(app_db_mapping, outfile, indent=4)
            outfile.close()

        alloted_apps = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "configuration_parameter",
                    "Columns": ["value"],
                },
                "condition": [
                    {
                        "column_name": "parameter",
                        "condition": "Equal to",
                        "input_value": "Allotted Applications",
                        "and_or": "",
                    }
                ],
            },
        ).value.iloc[0]
        alloted_apps = json.loads(alloted_apps)
        alloted_apps.append(new_app_code)
        alloted_apps = list(set(alloted_apps))
        alloted_apps = json.dumps(alloted_apps)
        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "configuration_parameter",
                    "Columns": [
                        {
                            "column_name": "value",
                            "input_value": alloted_apps,
                            "separator": "",
                        }
                    ],
                },
                "condition": [
                    {
                        "column_name": "parameter",
                        "condition": "Equal to",
                        "input_value": "Allotted Applications",
                        "and_or": "",
                    }
                ],
            },
        )
    return context


def compare_app_backup(app_code, update_backup_file, old_backup, db_connection_name, request, tenant):
    context = {}
    app_change_dict = pd.DataFrame(columns=["Type", "Name", "Application"])
    db_type = "MSSQL"
    context["app_change"] = []
    try:
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        context["response"] = f"Error connecting to the database! {str(e)}"
    else:
        if update_backup_file.get("application_config"):
            new_application_data = pd.DataFrame(update_backup_file["application_config"])
            old_application_data = pd.DataFrame(old_backup["application_config"])
            # Business Model removed
            old_app_business_model_codes = old_application_data["business_model_codes"].iloc[0]
            if old_app_business_model_codes:
                old_app_business_model_codes = json.loads(old_app_business_model_codes)
            else:
                old_app_business_model_codes = []
            new_app_business_model_codes = new_application_data["business_model_codes"].iloc[0]
            if new_app_business_model_codes:
                new_app_business_model_codes = json.loads(new_app_business_model_codes)
            else:
                new_app_business_model_codes = []
            bm_removed = [i for i in old_app_business_model_codes if i not in new_app_business_model_codes]

            for bm_r in bm_removed:
                bm_exists = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Application",
                            "Columns": ["id", "application_name"],
                        },
                        "condition": [
                            {
                                "column_name": "business_model_codes",
                                "condition": "Contains",
                                "input_value": bm_r,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "application_code",
                                "condition": "Not Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if len(bm_exists) > 0:
                    bm_name = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Business_Models",
                                "Columns": ["business_model_name"],
                            },
                            "condition": [
                                {
                                    "column_name": "business_model_code",
                                    "condition": "Equal to",
                                    "input_value": bm_r,
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        engine_override=True,
                        db_type=db_type,
                    ).business_model_name.iloc[0]
                    for app in bm_exists.application_name.tolist():
                        app_change_list1 = [{"Type": "Business Model", "Name": bm_name, "Application": app}]
                        app_change_list1_df = pd.DataFrame(app_change_list1)
                        app_change_dict = pd.concat([app_change_dict, app_change_list1_df], ignore_index=True)
                else:
                    bm_exists = None
                    del bm_exists
                    continue
            # Process removal checks
            old_app_process_group_codes = old_application_data["process_group_codes"].iloc[0]
            if old_app_process_group_codes:
                old_app_process_group_codes = json.loads(old_app_process_group_codes)
            else:
                old_app_process_group_codes = []
            new_app_process_group_codes = new_application_data["process_group_codes"].iloc[0]
            if new_app_process_group_codes:
                new_app_process_group_codes = json.loads(new_app_process_group_codes)
            else:
                new_app_process_group_codes = []
            prg_removed = [i for i in old_app_process_group_codes if i not in new_app_process_group_codes]

            for prg_r in prg_removed:
                prg_exists = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Application",
                            "Columns": ["id", "application_name"],
                        },
                        "condition": [
                            {
                                "column_name": "process_group_codes",
                                "condition": "Contains",
                                "input_value": prg_r,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "application_code",
                                "condition": "Not Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if len(prg_exists) > 0:
                    prg_name = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "NavigationSideBar",
                                "Columns": ["item_name"],
                            },
                            "condition": [
                                {
                                    "column_name": "item_code",
                                    "condition": "Contains",
                                    "input_value": prg_r,
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        engine_override=True,
                        db_type=db_type,
                    ).item_name.iloc[0]
                    for app in prg_exists.application_name.tolist():
                        app_change_list1 = [
                            {"Type": "Process dependency", "Name": prg_name, "Application": app}
                        ]
                        app_change_list1_df = pd.DataFrame(app_change_list1)
                        app_change_dict = pd.concat([app_change_dict, app_change_list1_df], ignore_index=True)
                else:
                    prg_exists = None
                    del prg_exists
                    continue

            # Computation model removal checks
            old_app_computation_model_names = old_application_data["computation_model_names"].iloc[0]
            if old_app_computation_model_names:
                old_app_computation_model_names = json.loads(old_app_computation_model_names)
            else:
                old_app_computation_model_names = []
            new_app_computation_model_names = new_application_data["computation_model_names"].iloc[0]
            if new_app_computation_model_names:
                new_app_computation_model_names = json.loads(new_app_computation_model_names)
            else:
                new_app_computation_model_names = []
            comp_removed = [
                i for i in old_app_computation_model_names if i not in new_app_computation_model_names
            ]

            for comp_r in comp_removed:
                comp_exists = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Application",
                            "Columns": ["id", "application_name"],
                        },
                        "condition": [
                            {
                                "column_name": "computation_model_names",
                                "condition": "Contains",
                                "input_value": comp_r,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "application_code",
                                "condition": "Not Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if len(comp_exists) > 0:
                    for app in comp_exists.application_name.tolist():
                        app_change_list1 = [
                            {"Type": "Computation model dependecy", "Name": comp_r, "Application": app}
                        ]
                        app_change_list1_df = pd.DataFrame(app_change_list1)
                        app_change_dict = pd.concat([app_change_dict, app_change_list1_df], ignore_index=True)
                else:
                    comp_exists = None
                    del comp_exists
                    continue

            # Data model removal checks
            old_app_table_names = old_application_data["table_names"].iloc[0]
            if old_app_table_names:
                old_app_table_names = json.loads(old_app_table_names)
            else:
                old_app_table_names = []
            new_app_table_names = new_application_data["table_names"].iloc[0]
            if new_app_table_names:
                new_app_table_names = json.loads(new_app_table_names)
            else:
                new_app_table_names = []
            tables_removed = [i for i in old_app_table_names if i not in new_app_table_names]

            for table_r in tables_removed:
                table_exists = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Application",
                            "Columns": ["id", "application_name"],
                        },
                        "condition": [
                            {
                                "column_name": "table_names",
                                "condition": "Contains",
                                "input_value": table_r,
                                "and_or": "AND",
                            },
                            {
                                "column_name": "application_code",
                                "condition": "Not Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    engine_override=True,
                    db_type=db_type,
                )
                if len(table_exists) > 0:
                    for app in table_exists.application_name.tolist():
                        app_change_list1 = [
                            {"Type": "Data model dependecy", "Name": table_r, "Application": app}
                        ]
                        app_change_list1_df = pd.DataFrame(app_change_list1)
                        app_change_dict = pd.concat([app_change_dict, app_change_list1_df], ignore_index=True)
                else:
                    table_exists = None
                    del table_exists
                    continue
            context["app_change"] = app_change_dict.to_dict("records")
        else:
            context["response"] = f"Invalid backup provided! Application config is missing."
    return context


def update_app_backup(app_code, update_backup_file, old_backup, db_connection_name, request, tenant):
    context = {"response": "Application updated successfully"}
    app_change_dict = pd.DataFrame(columns=["Type", "Name", "Application"])
    db_type = "MSSQL"
    try:
        user_db_engine, db_type = db_engine_extractor(db_connection_name)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        context["response"] = f"Error connecting to the database! {str(e)}"
    else:
        if update_backup_file.get("data_table_config"):
            new_data_table_data = pd.DataFrame(update_backup_file["data_table_config"])
            old_data_table_data = pd.DataFrame(old_backup["data_table_config"])
            data_table_change = old_data_table_data.equals(new_data_table_data)
            if not data_table_change:
                existing_table_list_all = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "Tables",
                            "Columns": ["tablename"],
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
                    engine_override=True,
                    db_type=db_type,
                ).tablename.tolist()
                data_update_handler(
                    old_data_table_data,
                    new_data_table_data,
                    existing_table_list_all,
                    request,
                    db_connection_name,
                )
            else:
                pass
        else:
            pass

        if update_backup_file.get("navigationSidebar_config"):
            new_navigation_sidebar_data = pd.DataFrame(update_backup_file["navigationSidebar_config"])
            old_navigation_sidebar_data = pd.DataFrame(old_backup["navigationSidebar_config"])
            navigation_sidebar_change = old_navigation_sidebar_data.equals(new_navigation_sidebar_data)
            if not navigation_sidebar_change:
                existing_navigationsidebar_data = new_navigation_sidebar_data[
                    (new_navigation_sidebar_data["item_code"].isin(old_navigation_sidebar_data["item_code"]))
                ].reset_index(drop=True)
                for idx, row in existing_navigationsidebar_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "NavigationSideBar",
                            },
                            "condition": [
                                {
                                    "column_name": "item_code",
                                    "condition": "Equal to",
                                    "input_value": row["item_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_navigationsidebar_data.iloc[[idx], :]
                    data_handling(request, row_data, "NavigationSideBar")
                exist_navigationsidebar_data = new_navigation_sidebar_data[
                    ~new_navigation_sidebar_data["item_code"].isin(old_navigation_sidebar_data["item_code"])
                ].reset_index(drop=True)
                for idx, row in exist_navigationsidebar_data.iterrows():
                    row_data = exist_navigationsidebar_data.iloc[[idx], :]
                    data_handling(request, row_data, "NavigationSideBar")
                removed_navigationsidebar_data = old_navigation_sidebar_data[
                    ~old_navigation_sidebar_data["item_code"].isin(new_navigation_sidebar_data["item_code"])
                ].reset_index(drop=True)
                for idx, row in removed_navigationsidebar_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "NavigationSideBar",
                            },
                            "condition": [
                                {
                                    "column_name": "item_code",
                                    "condition": "Equal to",
                                    "input_value": row["item_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )

        if update_backup_file.get("process_flow_config"):
            new_process_flow_data = pd.DataFrame(update_backup_file["process_flow_config"])
            old_process_flow_data = pd.DataFrame(old_backup["process_flow_config"])
            process_flow_change = old_process_flow_data.equals(new_process_flow_data)
            if not process_flow_change:
                existing_process_flow_data = new_process_flow_data[
                    (
                        new_process_flow_data["related_item_code"].isin(
                            old_process_flow_data["related_item_code"]
                        )
                    )
                ].reset_index(drop=True)
                for idx, row in existing_process_flow_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Process_subprocess_flowchart",
                            },
                            "condition": [
                                {
                                    "column_name": "related_item_code",
                                    "condition": "Equal to",
                                    "input_value": row["related_item_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_process_flow_data.iloc[[idx], :]
                    data_handling(request, row_data, "Process_subprocess_flowchart")
                existing_process_flow_data = new_process_flow_data[
                    ~new_process_flow_data["related_item_code"].isin(
                        old_process_flow_data["related_item_code"]
                    )
                ].reset_index(drop=True)
                for idx, row in existing_process_flow_data.iterrows():
                    row_data = existing_process_flow_data.iloc[[idx], :]
                    data_handling(request, row_data, "Process_subprocess_flowchart")
                removed_process_flow_data = old_process_flow_data[
                    ~old_process_flow_data["related_item_code"].isin(
                        new_process_flow_data["related_item_code"]
                    )
                ].reset_index(drop=True)
                for idx, row in removed_process_flow_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Process_subprocess_flowchart",
                            },
                            "condition": [
                                {
                                    "column_name": "related_item_code",
                                    "condition": "Equal to",
                                    "input_value": row["related_item_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )

        if update_backup_file.get("tabscreen_config"):
            new_tabscreens_data = pd.DataFrame(update_backup_file["tabscreen_config"])
            old_tabscreens_data = pd.DataFrame(old_backup["tabscreen_config"])
            tabscreens_change = old_tabscreens_data.equals(new_tabscreens_data)
            if not tabscreens_change:
                existing_tabscreens_data = new_tabscreens_data[
                    (new_tabscreens_data["related_item_code"].isin(old_tabscreens_data["related_item_code"]))
                ].reset_index(drop=True)
                for idx, row in existing_tabscreens_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "TabScreens",
                            },
                            "condition": [
                                {
                                    "column_name": "related_item_code",
                                    "condition": "Equal to",
                                    "input_value": row["related_item_code"],
                                    "and_or": "and",
                                },
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": row["element_id"],
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    row_data = existing_tabscreens_data.iloc[[idx], :]
                    data_handling(request, row_data, "TabScreens")
                newly_added_tabscreens_data = new_tabscreens_data[
                    ~new_tabscreens_data["related_item_code"].isin(old_tabscreens_data["related_item_code"])
                ].reset_index(drop=True)
                for idx, row in newly_added_tabscreens_data.iterrows():
                    row_data = newly_added_tabscreens_data.iloc[[idx], :]
                    data_handling(request, row_data, "TabScreens")
                removed_tabscreens_data = old_tabscreens_data[
                    ~old_tabscreens_data["related_item_code"].isin(new_tabscreens_data["related_item_code"])
                ].reset_index(drop=True)
                for idx, row in removed_tabscreens_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "TabScreens",
                            },
                            "condition": [
                                {
                                    "column_name": "related_item_code",
                                    "condition": "Equal to",
                                    "input_value": row["related_item_code"],
                                    "and_or": "and",
                                },
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": row["element_id"],
                                    "and_or": "",
                                },
                            ],
                        },
                    )

        if update_backup_file.get("process_scheduler_config"):
            new_scheduler_data = pd.DataFrame(update_backup_file["process_scheduler_config"])
            if old_backup.get("process_scheduler_config"):
                old_scheduler_data = pd.DataFrame(old_backup["process_scheduler_config"])
            else:
                old_scheduler_data = pd.DataFrame()
            scheduler_change = old_scheduler_data.equals(new_scheduler_data)
            if not scheduler_change:
                if not new_scheduler_data.empty:
                    existing_scheduler_config = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ProcessScheduler",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "app_code",
                                    "condition": "Equal to",
                                    "input_value": app_code,
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    if not existing_scheduler_config.empty:
                        delete_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "ProcessScheduler",
                                },
                                "condition": [
                                    {
                                        "column_name": "app_code",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    else:
                        pass
                    data_handling(request, new_scheduler_data, "ProcessScheduler")
                    for idx, sc_row in new_scheduler_data.iterrows():
                        if sc_row["scheduler_type"] == "block":
                            block_config = json.loads(sc_row["config"])
                            if sc_row["trigger_option"] == "interval":
                                schedule_block(
                                    request,
                                    sc_row["element_id"],
                                    block_config,
                                    sc_row["item_code"],
                                    sc_row["item_group_code"],
                                )
                            if block_config.get("additionalJobs"):
                                for b_idx, b_c in enumerate(block_config["additionalJobs"]):
                                    if b_c["schedulerTrigger"] == "interval":
                                        schedule_block(
                                            request,
                                            sc_row["element_id"],
                                            b_c,
                                            sc_row["item_code"],
                                            sc_row["item_group_code"],
                                            b_index=b_idx,
                                        )
                                    else:
                                        pass
                            else:
                                pass
                        else:
                            schedule_flow(
                                request,
                                json.loads(sc_row["config"]),
                                sc_row["item_code"],
                                sc_row["item_group_code"],
                            )
                else:
                    pass
            else:
                pass
        else:
            pass

        if update_backup_file.get("pivot_report_config"):
            new_pivot_report_data = pd.DataFrame(update_backup_file["pivot_report_config"])
            if old_backup.get("pivot_report_config"):
                old_pivot_report_data = pd.DataFrame(old_backup["pivot_report_config"])
            else:
                old_pivot_report_data = pd.DataFrame()
            scheduler_change = old_pivot_report_data.equals(new_pivot_report_data)
            if not scheduler_change:
                if not new_pivot_report_data.empty:
                    existing_pivot_report_config = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ConfigTable",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "app_code",
                                    "condition": "Equal to",
                                    "input_value": app_code,
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    if not existing_pivot_report_config.empty:
                        delete_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "ConfigTable",
                                },
                                "condition": [
                                    {
                                        "column_name": "app_code",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    else:
                        pass
                    data_handling(request, new_pivot_report_data, "ConfigTable")
                else:
                    pass
            else:
                pass
        else:
            pass

        if update_backup_file.get("comp_model_configuration"):
            new_comp_config_data = pd.DataFrame(update_backup_file["comp_model_configuration"])
            if old_backup.get("comp_model_configuration"):
                old_comp_config_data = pd.DataFrame(old_backup["comp_model_configuration"])
            else:
                old_comp_config_data = pd.DataFrame(
                    columns=["model_name", "element_id", "element_name", "element_config"]
                )
            comp_config_change = old_comp_config_data.equals(new_comp_config_data)
            if not comp_config_change:
                existing_comp_ele_data = new_comp_config_data[
                    (new_comp_config_data["model_name"].isin(old_comp_config_data["model_name"]))
                ].reset_index(drop=True)
                for idx, row in existing_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_model_configuration",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "AND",
                                },
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": row["element_id"],
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                    row_data = existing_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_model_configuration")
                exist_comp_ele_data = new_comp_config_data[
                    ~new_comp_config_data["model_name"].isin(old_comp_config_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in exist_comp_ele_data.iterrows():
                    row_data = exist_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_model_configuration")
                removed_comp_ele_data = old_comp_config_data[
                    ~old_comp_config_data["model_name"].isin(new_comp_config_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in removed_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_model_configuration",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "AND",
                                },
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": row["element_id"],
                                    "and_or": "",
                                },
                            ],
                        },
                    )

        if update_backup_file.get("comp_model_flowchart_config"):
            new_comp_flowchart_data = pd.DataFrame(update_backup_file["comp_model_flowchart_config"])
            if old_backup.get("comp_model_flowchart_config"):
                old_comp_flowchart_data = pd.DataFrame(old_backup["comp_model_flowchart_config"])
            else:
                old_comp_flowchart_data = pd.DataFrame(
                    columns=["model_name", "flowchart_xml", "flowchart_elements"]
                )
            comp_flowchart_change = old_comp_flowchart_data.equals(new_comp_flowchart_data)
            if not comp_flowchart_change:
                existing_comp_ele_data = new_comp_flowchart_data[
                    (new_comp_flowchart_data["model_name"].isin(old_comp_flowchart_data["model_name"]))
                ].reset_index(drop=True)
                for idx, row in existing_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_model_flowchart",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_model_flowchart")
                new_comp_ele_data = new_comp_flowchart_data[
                    ~new_comp_flowchart_data["model_name"].isin(old_comp_flowchart_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in new_comp_ele_data.iterrows():
                    row_data = new_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_model_flowchart")
                removed_comp_ele_data = old_comp_flowchart_data[
                    ~old_comp_flowchart_data["model_name"].isin(new_comp_flowchart_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in removed_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_model_flowchart",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )

        if update_backup_file.get("comp_output_repo"):
            new_comp_output_data = pd.DataFrame(
                update_backup_file["comp_output_repo"], columns=["model_name", "model_outputs"]
            )
            old_comp_output_data = pd.DataFrame(
                old_backup["comp_output_repo"], columns=["model_name", "model_outputs"]
            )
            comp_output_change = old_comp_output_data.equals(new_comp_output_data)
            if not comp_output_change:
                existing_comp_ele_data = new_comp_output_data[
                    (new_comp_output_data["model_name"].isin(old_comp_output_data["model_name"]))
                ].reset_index(drop=True)
                for idx, row in existing_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_output_repository",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_output_repository")
                new_comp_ele_data = new_comp_output_data[
                    ~new_comp_output_data["model_name"].isin(old_comp_output_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in new_comp_ele_data.iterrows():
                    row_data = new_comp_ele_data.iloc[[idx], :]
                    data_handling(request, row_data, "computation_output_repository")
                removed_comp_ele_data = old_comp_output_data[
                    ~old_comp_output_data["model_name"].isin(new_comp_output_data["model_name"])
                ].reset_index(drop=True)
                for idx, row in removed_comp_ele_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "computation_output_repository",
                            },
                            "condition": [
                                {
                                    "column_name": "model_name",
                                    "condition": "Equal to",
                                    "input_value": row["model_name"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )

        if update_backup_file.get("business_model_config"):
            new_business_model_data = pd.DataFrame(update_backup_file["business_model_config"])
            old_business_model_data = pd.DataFrame(old_backup["business_model_config"])
            business_model_change = old_business_model_data.equals(new_business_model_data)
            if not business_model_change:
                existing_business_model_data = new_business_model_data[
                    (
                        new_business_model_data["business_model_code"].isin(
                            old_business_model_data["business_model_code"]
                        )
                    )
                ].reset_index(drop=True)
                for idx, row in existing_business_model_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Business_Models",
                            },
                            "condition": [
                                {
                                    "column_name": "business_model_code",
                                    "condition": "Equal to",
                                    "input_value": row["business_model_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_business_model_data.iloc[[idx], :]
                    data_handling(request, row_data, "Business_Models")
                exist_business_model_data = new_business_model_data[
                    ~new_business_model_data["business_model_code"].isin(
                        old_business_model_data["business_model_code"]
                    )
                ].reset_index(drop=True)
                for idx, row in exist_business_model_data.iterrows():
                    row_data = exist_business_model_data.iloc[[idx], :]
                    data_handling(request, row_data, "Business_Models")
                removed_business_model_data = old_business_model_data[
                    ~old_business_model_data["business_model_code"].isin(
                        new_business_model_data["business_model_code"]
                    )
                ].reset_index(drop=True)
                for idx, row in removed_business_model_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Business_Models",
                            },
                            "condition": [
                                {
                                    "column_name": "business_model_code",
                                    "condition": "Equal to",
                                    "input_value": row["business_model_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )

        if update_backup_file.get("application_config"):
            new_application_data = pd.DataFrame(update_backup_file["application_config"])
            old_application_data = pd.DataFrame(old_backup["application_config"])
            app_change = old_application_data.equals(new_application_data)
            if not app_change:
                existing_application_data = new_application_data[
                    (new_application_data["application_code"].isin(old_application_data["application_code"]))
                ].reset_index(drop=True)
                for idx, row in existing_application_data.iterrows():
                    delete_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Application",
                            },
                            "condition": [
                                {
                                    "column_name": "application_code",
                                    "condition": "Equal to",
                                    "input_value": row["application_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                    row_data = existing_application_data.iloc[[idx], :]
                    data_handling(request, row_data, "Application")

        if update_backup_file.get("groups_with_app_access"):
            permissions_migration_option = update_backup_file.get("permissions_migration_option", "replace")
            new_group_config_data = pd.DataFrame(update_backup_file["groups_with_app_access"])
            if old_backup.get("groups_with_app_access"):
                old_group_config_data = pd.DataFrame(old_backup["groups_with_app_access"])
            else:
                old_group_config_data = pd.DataFrame(
                    columns=["name"]
                )
            group_config_change = old_group_config_data.equals(new_group_config_data)
            if not group_config_change:
                exist_user_group_data = new_group_config_data[
                    ~new_group_config_data["name"].isin(old_group_config_data["name"])
                ].reset_index(drop=True)
                groups_created = []
                for idx, row in exist_user_group_data.iterrows():
                    group_name = row["name"]
                    group, created = Group.objects.get_or_create(name=group_name)
                    if created:
                        groups_created.append(
                            {
                                "name": grp,
                                "created_date": datetime.now(),
                                "created_by": request.user.username,
                                "modified_date": datetime.now(),
                                "modified_by": request.user.username,
                            }
                        )
                    else:
                        continue
                if groups_created:
                    groups_created = pd.DataFrame(groups_created)
                    data_handling(request, groups_created, "group_details")
                else:
                    pass
                if permissions_migration_option == "replace":
                    removed_user_group_data = old_group_config_data[
                        ~old_group_config_data["name"].isin(new_group_config_data["name"])
                    ].reset_index(drop=True)
                    if not removed_user_group_data.empty:
                        user_groups = Group.objects.filter(name__in=removed_user_group_data["name"].tolist())
                        user_groups.delete()
                        delete_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "group_details",
                                },
                                "condition": [
                                    {
                                        "column_name": "name",
                                        "condition": "IN",
                                        "input_value": removed_user_group_data["name"].tolist(),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                        delete_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "UserPermission_Master",
                                    },
                                    "condition": [
                                        {
                                            "column_name": "usergroup",
                                            "condition": "IN",
                                            "input_value": removed_user_group_data["name"].tolist(),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                    else:
                        pass
                else:
                    pass
            else:
                pass

            if update_backup_file.get("app_permissions"):
                new_permissions_data = pd.DataFrame(update_backup_file["app_permissions"])
                if old_backup.get("app_permissions"):
                    old_permissions_data = pd.DataFrame(old_backup["app_permissions"])
                else:
                    old_permissions_data = pd.DataFrame(
                        columns=["usergroup","permission_type","permission_level","level_button_access","permission_name","application","application_dev","app_code","app_name","created_by","created_date","modified_by","modified_date","instance_id"]
                    )
                permissions_change = old_permissions_data.equals(new_permissions_data)
                if not permissions_change:
                    if permissions_migration_option == "replace":
                        delete_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "UserPermission_Master",
                                },
                                "condition": [
                                    {
                                        "column_name": "app_code",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                        data_handling(request, pd.DataFrame(new_permissions_data), "UserPermission_Master")
                    else:
                        new_permissions_added = new_permissions_data[
                            ~new_permissions_data["usergroup"].isin(old_permissions_data["usergroup"]) &
                            ~new_permissions_data["permission_type"].isin(old_permissions_data["permission_type"]) &
                            ~new_permissions_data["permission_level"].isin(old_permissions_data["permission_level"]) &
                            ~new_permissions_data["permission_name"].isin(old_permissions_data["permission_name"])
                        ].reset_index(drop=True)
                        if not new_permissions_added.empty:
                            data_handling(request, pd.DataFrame(new_permissions_added), "UserPermission_Master")
                        else:
                            pass
                else:
                    pass
        else:
            pass

    return context


def data_update_handler(
    sys_table_repo, model_table_repo, existing_table_list_all, request, db_connection_name
):
    existing_tables = sys_table_repo["tablename"].tolist()
    model_tables = model_table_repo["tablename"].tolist()
    deleted_models = [i for i in existing_tables if i not in model_tables]
    for table in model_table_repo["tablename"].tolist():
        logging.warning(table)
        sys_model_dict = json.loads(
            model_table_repo[model_table_repo["tablename"] == table]["fields"].values[0]
        )
        sys_table_dict = sys_table_repo[sys_table_repo["tablename"] == table]
        if not sys_table_dict.empty:
            sys_table_dict = json.loads(sys_table_dict.fields.values[0])
            if sys_model_dict != sys_table_dict:
                collated_fields = {i for i in list(sys_model_dict.keys()) + list(sys_table_dict.keys())}
                for field in collated_fields:
                    if not sys_model_dict.get(field) and sys_table_dict.get(field):
                        dynamic_model_create.delete_element(table, field, request, db_connection_name)
                for field in collated_fields:
                    if sys_model_dict.get(field) and sys_table_dict.get(field):
                        if (
                            sys_model_dict[field] != sys_table_dict[field]
                            and sys_model_dict[field]["internal_type"] != "AutoField"
                        ):
                            # Update field attribute
                            field_config = {"fieldName": field}
                            sql_update_required = False
                            if (
                                sys_model_dict[field]["internal_type"]
                                != sys_table_dict[field]["internal_type"]
                            ):
                                sql_update_required = True
                            else:
                                pass
                            if sys_model_dict[field]["null"] != sys_table_dict[field]["null"]:
                                sql_update_required = True
                            else:
                                pass
                            if sys_model_dict[field]["unique"] != sys_table_dict[field]["unique"]:
                                sql_update_required = True
                            else:
                                pass
                            if sys_model_dict[field].get("max_length") != sys_table_dict[field].get(
                                "max_length"
                            ):
                                sql_update_required = True
                            else:
                                pass
                            if sql_update_required:
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
                                        if val:
                                            if type(val) == list and type(val[0]) == list:
                                                field_config["fieldChoices"] = [i[0] for i in val]
                                            else:
                                                field_config["fieldChoices"] = val
                                        else:
                                            field_config["fieldChoices"] = val
                                    elif attr == "max_length":
                                        field_config["fieldMaxLength"] = val
                                    elif attr == "parent":
                                        field_config["fieldParentFKTable"] = val
                                        field_config["fieldFKTable"] = val
                                    elif attr == "related_column":
                                        field_config["fieldRelatedColumn"] = val
                                    elif attr == "validators":
                                        field_config["validators"] = val
                                    else:
                                        field_config[attr] = val
                                if not field_config.get("fieldUnique"):
                                    field_config["fieldUnique"] = "No"
                                logging.warning("field edited---------------------------->")
                                logging.warning(field)
                                logging.warning(sys_model_dict[field])
                                logging.warning(sys_table_dict[field])
                                dynamic_model_create.edit_element(
                                    table, field_config, request, db_connection_name
                                )
                            else:
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
                                                        "input_value": table,
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    )
                                    .iloc[0]
                                    .fields
                                )
                                model_fields[field] = sys_model_dict[field]
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
                                                },
                                            ],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "tablename",
                                                "condition": "Equal to",
                                                "input_value": table,
                                                "and_or": "",
                                            }
                                        ],
                                    },
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
                                if val:
                                    if type(val) == list and type(val[0]) == list:
                                        field_config["fieldChoices"] = [i[0] for i in val]
                                    else:
                                        field_config["fieldChoices"] = val
                                else:
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
                            elif attr == "validators":
                                field_config["validators"] = val
                            else:
                                field_config[attr] = val

                        dynamic_model_create.add_element(table, field_config, request, db_connection_name)
            else:
                pass
        else:
            if table not in existing_table_list_all:
                # Create new model
                new_model_name = table
                fields = []
                sys_cols = [
                    "created_by",
                    "modified_by",
                    "created_date",
                    "modified_date",
                    "active_from",
                    "active_to",
                    "transaction_id",
                    "is_active_flag",
                ]
                sys_model_dict = {key: value for key, value in sys_model_dict.items() if key not in sys_cols}
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
                            if val:
                                if type(val) == list and type(val[0]) == list:
                                    field_config["choices"] = [i[0] for i in val]
                                else:
                                    field_config["choices"] = val
                            else:
                                field_config["choices"] = val
                        elif attr == "max_length":
                            field_config["maximum length*"] = val
                        elif attr == "parent":
                            field_config["parent table"] = val
                        elif attr == "auto_now":
                            field_config["auto now?"] = val
                        elif attr == "editable":
                            field_config["editable?"] = val
                        elif attr == "validators":
                            field_config["validators"] = val
                        elif attr == "mulsel_config":
                            field_config["mulsel_config"] = val
                        else:
                            field_config[attr] = val
                    fields.append(field_config)
                dynamic_model_create.create_table_sql(
                    new_model_name,
                    fields,
                    request,
                    model_type="user defined",
                    db_connection_name=db_connection_name,
                )
            else:
                pass
    for delt in deleted_models:
        dynamic_model_create.delete_model(delt, request, db_connection_name)
    return True
