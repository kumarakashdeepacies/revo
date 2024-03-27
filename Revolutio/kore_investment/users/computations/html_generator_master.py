from datetime import datetime
import json
import logging
import os
import pickle
import random
import string

import pandas as pd

from config.settings.base import redis_instance
from kore_investment.users.computations import html_generator
from kore_investment.users.computations.db_centralised_function import (
    postgres_push,
    read_data_func,
    update_data_func,
)
from kore_investment.users.computations.dynamic_model_create import get_model_class
from kore_investment.users.queue_manager import enqueue_jobs
from kore_investment.utils.utilities import tenant_schema_from_request


def request_to_dict(request):
    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
    request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
    return request2


def request_to_dict2(request):
    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
    request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
    return request2


def random_no_generator(N=16):
    code = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(N))
    return code


def removeNavConfig(user_name, tenant):
    user_name_tenant = user_name + tenant
    if redis_instance.exists(user_name_tenant) == 1:
        user_info = pickle.loads(redis_instance.get(user_name_tenant))
        if user_info.get("user_navbar_config"):
            user_info.pop("user_navbar_config")
            redis_instance.set(user_name_tenant, pickle.dumps(user_info))
    user_name_tenant_navpoint = tenant + user_name + "navbar"
    if redis_instance.exists(user_name_tenant_navpoint) == 1:
        redis_instance.delete(user_name_tenant_navpoint)


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


def html_generator_app(grp_code, table_list, request, skip_gen, cur_app_code, pr_code__={}):
    if isinstance(request, dict):
        request["user"] = AttrDict(request["user"])
        request = AttrDict(request)
    sql_query_app_list = [cur_app_code]
    current_approval_data = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "ApprovalTable",
                "Columns": ["id", "approved_by", "approval_level_config", "type_of_approval"],
            },
            "condition": [
                {
                    "column_name": "approved_by",
                    "condition": "Not Equal to",
                    "input_value": "NULL",
                    "and_or": "",
                },
            ],
        },
    )
    for idx, row in current_approval_data.iterrows():
        approved_by = json.loads(row["approved_by"])
        if isinstance(approved_by, list):
            if row["type_of_approval"] == "multi_level":
                level_config = json.loads(row["approval_level_config"])
                current_level = level_config["current_level"]
                approved_by = {current_level: approved_by}
            else:
                approved_by = {"0": approved_by}
            update_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ApprovalTable",
                        "Columns": [
                            {
                                "column_name": "approved_by",
                                "input_value": json.dumps(approved_by),
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "id",
                            "condition": "Equal to",
                            "input_value": str(row["id"]),
                            "and_or": "",
                        }
                    ],
                },
            )
        else:
            continue

    sub_pr_job_id = {}
    for process_code in grp_code:
        if len(pr_code__) == 0:
            sub_grp_name = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "NavigationSideBar",
                        "Columns": ["item_name"],
                    },
                    "condition": [
                        {
                            "column_name": "item_group_code",
                            "condition": "Equal to",
                            "input_value": process_code,
                            "and_or": "",
                        },
                    ],
                },
            ).item_name.tolist()
        else:
            sub_grp_name = pr_code__[process_code]

        for j in sub_grp_name:
            job_id = "htmlGenerateAll" + random_no_generator() + j
            job_args = (process_code, j, request, sql_query_app_list, skip_gen)
            enqueue_jobs(
                create_process_htmls,
                job_id,
                args=job_args,
                kwargs={},
                job_type="html_generation",
                description=f"Sub-process regeneration - {j}",
            )
            sub_pr_job_id[j] = job_id
    return sub_pr_job_id, request.user.username


def create_process_htmls(process_code, subprocess_name, request, sql_query_app_list, skip_gen):
    user_name = request.user.username
    tenant = tenant_schema_from_request(request)
    try:
        sqlReadData = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": [
                        "item_code",
                        "item_name",
                        "item_group_name",
                        "tab_header_color_config",
                        "design_mode",
                    ],
                },
                "condition": [
                    {
                        "column_name": "item_group_code",
                        "condition": "Equal to",
                        "input_value": process_code,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "item_name",
                        "condition": "Equal to",
                        "input_value": subprocess_name,
                        "and_or": "",
                    },
                ],
            },
        )
        if len(sqlReadData) == 0:

            sqlReadData = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "DraftProcess",
                        "Columns": ["item_code", "item_name", "item_group_name"],
                    },
                    "condition": [
                        {
                            "column_name": "item_group_code",
                            "condition": "Equal to",
                            "input_value": process_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "item_name",
                            "condition": "Equal to",
                            "input_value": subprocess_name,
                            "and_or": "",
                        },
                    ],
                },
            )
        # Updating business models and applications containing this process
        update_process_BM_App(process_code, request)
        element_id_ct_del = []
        related_item_code = sqlReadData["item_code"].tolist()
        tab_color_config = sqlReadData["tab_header_color_config"].iloc[0]
        if tab_color_config not in [None]:
            tab_color_config = json.loads(tab_color_config)
        else:
            tab_color_config = {}
        design_mode = sqlReadData["design_mode"].iloc[0]
        processDF = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Process_subprocess_flowchart",
                    "Columns": [
                        "related_item_code",
                        "flowchart_xml",
                        "flowchart_dict",
                        "filename_xml",
                        "flowchart_elements",
                    ],
                },
                "condition": [
                    {
                        "column_name": "related_item_code",
                        "condition": "Equal to",
                        "input_value": related_item_code[0],
                        "and_or": "",
                    }
                ],
            },
        )

        cond = []
        cond.append(
            {
                "column_name": "related_item_code",
                "condition": "Equal to",
                "input_value": related_item_code[0],
                "and_or": "AND",
            }
        )
        cond.append(
            {
                "column_name": "tab_type",
                "condition": "Not Equal to",
                "input_value": "connector",
                "and_or": "",
            }
        )

        tabScreenElementIDList1 = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "TabScreens",
                    "Columns": [
                        "id",
                        "element_id",
                        "tab_header_name",
                        "tab_body_content",
                        "tab_type",
                        "table_name",
                        "tabs_multi_function",
                    ],
                },
                "condition": cond,
            },
        )
        tab_header_name_list = tabScreenElementIDList1.tab_header_name.tolist()
        tab_body_content_list = tabScreenElementIDList1.tab_body_content.tolist()
        table_name_list = tabScreenElementIDList1.table_name.tolist()
        ids = tabScreenElementIDList1.id.tolist()
        tab_type_list = tabScreenElementIDList1.tab_type.tolist()
        tabs_multi_function_list = tabScreenElementIDList1.tabs_multi_function.tolist()
        tabScreenElementIDList1 = tabScreenElementIDList1.element_id.tolist()
        breadcrumbs = [
            {"item_name": (sqlReadData["item_group_name"].tolist())[0], "item_url": ""},
            {"item_name": subprocess_name, "item_url": ""},
        ]
        html = ""
        create_view_tab = False

        # Create View Mode
        # extracting parent and child element id
        main_index = ""
        if not processDF.empty:
            related_item_flowchart = processDF.to_dict()
            flowchart_element = json.loads(related_item_flowchart["flowchart_elements"][0])
            parent_rel_child_list = []
            for i in flowchart_element:
                for ele_id in tabScreenElementIDList1:
                    child_list = []
                    create_view_check_dict = {}
                    if (i["shapeID"] == ele_id) and (i["shape"] == "wrap"):
                        for child in i["child"]:
                            if child.startswith("process"):
                                child_list.append(child)
                        if len(child_list) > 0:
                            create_view_check_dict["parent"] = i["shapeID"]
                            create_view_check_dict["child"] = child_list
                            parent_rel_child_list.append(create_view_check_dict)

            if len(parent_rel_child_list) > 0:
                for i in range(len(parent_rel_child_list)):
                    if len(parent_rel_child_list[i]["child"]) > 0:
                        for inner_child in range(len(parent_rel_child_list[i]["child"])):
                            if parent_rel_child_list[i]["child"][inner_child] in tabScreenElementIDList1:
                                list_main_index = tabScreenElementIDList1.index(
                                    parent_rel_child_list[i]["child"][inner_child]
                                )
                                list_view_content = json.loads(tab_body_content_list[list_main_index])
                                if list_view_content.get("reportingView"):
                                    list_view_content = list_view_content
                                else:
                                    mul_def_vew = ""
                                    for key_1, v_1 in list_view_content.items():
                                        mul_def_vew = v_1["mulview_def"]
                                        break
                                    list_view_content = list_view_content[mul_def_vew]
                                if (
                                    "MultipleTableMapping"
                                    in list_view_content["Category_attributes"]["Mandatory"]
                                ):
                                    mconfig = len(
                                        list_view_content["Category_attributes"]["Mandatory"].get(
                                            "MultipleTableMapping"
                                        )
                                    )
                                if "create_view_selection_checker" not in list_view_content.keys():
                                    list_view_content["create_view_selection_checker"] = False
                                if "create_view_selection_checker" in list_view_content.keys():
                                    if (not list_view_content["create_view_selection_checker"]) or mconfig:
                                        if parent_rel_child_list[i]["parent"] in tabScreenElementIDList1:
                                            main_index = tabScreenElementIDList1.index(
                                                parent_rel_child_list[i]["parent"]
                                            )
                                            tab_header_name_list.pop(main_index)
                                            tab_body_content_list.pop(main_index)
                                            table_name_list.pop(main_index)
                                            ids.pop(main_index)
                                            tab_type_list.pop(main_index)
                                            tabScreenElementIDList1.pop(main_index)
                                            tabs_multi_function_list.pop(main_index)
                                            create_view_tab = True

        for indx, val in enumerate(tab_type_list):
            if val == "create_view":
                try:
                    temp_config = json.loads(tab_body_content_list[indx])

                    sqlReadData_version = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "TabScreens",
                                "Columns": ["update_version"],
                            },
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": str(tabScreenElementIDList1[indx]),
                                    "and_or": "",
                                },
                            ],
                        },
                    ).update_version.iloc[0]

                    if sqlReadData_version is None:
                        sqlReadData_version = "1.0.0"

                    if sqlReadData_version != "1.1.0":
                        temp_table_name = temp_config["Category_sub_elements"][0][
                            "Category_sub_element_attributes"
                        ][0]["value"][0]
                        act_modelname = get_model_class(temp_table_name, request)
                        verb_to_fname_dict = {
                            field.verbose_name: field.name for field in act_modelname.concrete_fields
                        }
                        verb_to_fname_dict2 = {
                            field.verbose_name.title(): field.name for field in act_modelname.concrete_fields
                        }
                        if temp_config["Category_attributes"]["Template"].get("carousel_view"):
                            for key, value in temp_config["Category_attributes"]["Template"][
                                "carousel_view"
                            ].items():
                                new_val = []
                                for i in value:
                                    try:
                                        new_val.append(verb_to_fname_dict[i])
                                    except Exception as e:
                                        try:
                                            new_val.append(verb_to_fname_dict2[i])
                                        except Exception as e:
                                            new_val.append(i)
                                temp_config["Category_attributes"]["Template"]["carousel_view"][key] = new_val

                        if temp_config["Category_attributes"]["Template"].get("carousel_view_min_fields"):
                            for key, value in temp_config["Category_attributes"]["Template"][
                                "carousel_view_min_fields"
                            ].items():
                                new_val = []
                                for i in value["fields"]:
                                    try:
                                        new_val.append(verb_to_fname_dict[i])
                                    except Exception as e:
                                        try:
                                            new_val.append(verb_to_fname_dict2[i])
                                        except Exception as e:
                                            new_val.append(i)
                                temp_config["Category_attributes"]["Template"]["carousel_view_min_fields"][
                                    key
                                ]["fields"] = new_val

                        if temp_config["Category_attributes"]["Template"].get("column_reorder"):
                            new_val = {}
                            for key, value in temp_config["Category_attributes"]["Template"][
                                "column_reorder"
                            ].items():
                                try:
                                    new_val[key] = verb_to_fname_dict[value]
                                except Exception as e:
                                    try:
                                        new_val[key] = verb_to_fname_dict2[value]
                                    except Exception as e:
                                        new_val[key] = value
                            temp_config["Category_attributes"]["Template"]["column_reorder"] = new_val

                        if temp_config.get("edit_labels"):
                            new_val = {}
                            for key, value in temp_config["edit_labels"].items():
                                try:
                                    new_val[verb_to_fname_dict[key]] = value
                                except Exception as e:
                                    try:
                                        new_val[verb_to_fname_dict2[key]] = value
                                    except Exception as e:
                                        new_val[key] = value
                            temp_config["edit_labels"] = new_val

                        tab_body_content_list[indx] = json.dumps(temp_config)

                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "TabScreens",
                                    "Columns": [
                                        {
                                            "column_name": "tab_body_content",
                                            "input_value": json.dumps(temp_config),
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "update_version",
                                            "input_value": "1.1.0",
                                            "separator": "",
                                        },
                                    ],
                                },
                                "condition": [
                                    {
                                        "column_name": "element_id",
                                        "condition": "Equal to",
                                        "input_value": str(tabScreenElementIDList1[indx]),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                except Exception as e:
                    logging.warning(
                        f"Following exception occured while regenerating html for createview ---> {e}"
                    )

            if val == "list_view":
                try:
                    temp_config = json.loads(tab_body_content_list[indx])

                    sqlReadData_version = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "TabScreens",
                                "Columns": ["update_version"],
                            },
                            "condition": [
                                {
                                    "column_name": "element_id",
                                    "condition": "Equal to",
                                    "input_value": str(tabScreenElementIDList1[indx]),
                                    "and_or": "",
                                },
                            ],
                        },
                    ).update_version.iloc[0]

                    if sqlReadData_version is None:
                        sqlReadData_version = "1.0.0"

                    if sqlReadData_version != "1.1.0":

                        if temp_config.get("Category_attributes"):
                            temp_table_name = temp_config["Category_attributes"]["Mandatory"]["Table_name"]

                            if temp_table_name.startswith("["):
                                if isinstance(
                                    temp_config["Category_attributes"]["Mandatory"]["DroppedFields"], dict
                                ):
                                    drp_new_val = {}
                                    for k, v in temp_config["Category_attributes"]["Mandatory"][
                                        "DroppedFields"
                                    ].items():
                                        act_modelname_drp = get_model_class(k, request)
                                        verb_to_fname_dict_drp = {
                                            field.verbose_name: field.name
                                            for field in act_modelname_drp.concrete_fields
                                        }
                                        verb_to_fname_dict2_drp = {
                                            field.verbose_name.title(): field.name
                                            for field in act_modelname_drp.concrete_fields
                                        }
                                        new_val = []
                                        for i in v:
                                            try:
                                                new_val.append(verb_to_fname_dict_drp[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2_drp[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        drp_new_val[k] = new_val
                                    temp_config["Category_attributes"]["Mandatory"][
                                        "DroppedFields"
                                    ] = drp_new_val

                                if temp_config["Category_attributes"]["Mandatory"].get(
                                    "listViewEmbededComputationMultiple"
                                ):
                                    for itmss in temp_config["Category_attributes"]["Mandatory"][
                                        "listViewEmbededComputationMultiple"
                                    ]:
                                        for k, v in itmss.items():
                                            new_val = []
                                            for model_name, model_config in v.items():
                                                for m2, mc2 in model_config.items():
                                                    act_modelname = get_model_class(m2, request)
                                                    verb_to_fname_dict = {
                                                        field.verbose_name: field.name
                                                        for field in act_modelname.concrete_fields
                                                    }
                                                    verb_to_fname_dict2 = {
                                                        field.verbose_name.title(): field.name
                                                        for field in act_modelname.concrete_fields
                                                    }
                                                    for i in mc2:
                                                        n_Va = []
                                                        if isinstance(i, list):
                                                            for j in i:
                                                                try:
                                                                    n_Va.append(verb_to_fname_dict[j])
                                                                except Exception as e:
                                                                    n_Va.append(verb_to_fname_dict2[j])
                                                            new_val.append(n_Va)
                                                        else:
                                                            new_val.append(i)
                                        itmss[k][model_name][m2] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("titleRowFormatting"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "titleRowFormatting"
                                    ].items():
                                        act_modelname = get_model_class(tab_name, request)
                                        verb_to_fname_dict = {
                                            field.verbose_name: field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        verb_to_fname_dict2 = {
                                            field.verbose_name.title(): field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        for kk, value_config in configs.items():
                                            if kk == "exception":
                                                new_val = {}
                                                for exp_name, conf in value_config.items():
                                                    try:
                                                        new_val[verb_to_fname_dict[exp_name]] = conf
                                                    except Exception as e:
                                                        new_val[verb_to_fname_dict2[exp_name]] = conf
                                                temp_config["Category_attributes"]["Mandatory"][
                                                    "titleRowFormatting"
                                                ][tab_name][kk] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("configActionButtons"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "configActionButtons"
                                    ].items():
                                        act_modelname = get_model_class(tab_name, request)
                                        verb_to_fname_dict = {
                                            field.verbose_name: field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        verb_to_fname_dict2 = {
                                            field.verbose_name.title(): field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        for kk, value_config in configs.items():
                                            if kk == "columnOrder":
                                                new_val = []
                                                for i in value_config:
                                                    try:
                                                        new_val.append(verb_to_fname_dict[i])
                                                    except Exception as e:
                                                        try:
                                                            new_val.append(verb_to_fname_dict2[i])
                                                        except Exception as e:
                                                            new_val.append(i)
                                                temp_config["Category_attributes"]["Mandatory"][
                                                    "configActionButtons"
                                                ][tab_name][kk] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("columnHeadersHide"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "columnHeadersHide"
                                    ].items():
                                        act_modelname = get_model_class(tab_name, request)
                                        verb_to_fname_dict = {
                                            field.verbose_name: field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        verb_to_fname_dict2 = {
                                            field.verbose_name.title(): field.name
                                            for field in act_modelname.concrete_fields
                                        }
                                        new_val = []
                                        for i in configs:
                                            try:
                                                new_val.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        temp_config["Category_attributes"]["Mandatory"]["columnHeadersHide"][
                                            tab_name
                                        ] = new_val

                                tab_body_content_list[indx] = json.dumps(temp_config)

                                update_data_func(
                                    request,
                                    config_dict={
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "TabScreens",
                                            "Columns": [
                                                {
                                                    "column_name": "tab_body_content",
                                                    "input_value": json.dumps(temp_config),
                                                    "separator": ",",
                                                },
                                                {
                                                    "column_name": "update_version",
                                                    "input_value": "1.1.0",
                                                    "separator": "",
                                                },
                                            ],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "element_id",
                                                "condition": "Equal to",
                                                "input_value": str(tabScreenElementIDList1[indx]),
                                                "and_or": "",
                                            },
                                        ],
                                    },
                                )
                            else:

                                act_modelname = get_model_class(temp_table_name, request)
                                verb_to_fname_dict = {
                                    field.verbose_name: field.name for field in act_modelname.concrete_fields
                                }
                                verb_to_fname_dict2 = {
                                    field.verbose_name.title(): field.name
                                    for field in act_modelname.concrete_fields
                                }

                                if temp_config["Category_attributes"]["Mandatory"].get("DroppedFields"):
                                    new_val = []
                                    for i in temp_config["Category_attributes"]["Mandatory"]["DroppedFields"]:
                                        try:
                                            new_val.append(verb_to_fname_dict[i])
                                        except Exception as e:
                                            try:
                                                new_val.append(verb_to_fname_dict2[i])
                                            except Exception as e:
                                                new_val.append(i)
                                    temp_config["Category_attributes"]["Mandatory"]["DroppedFields"] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("RestrictFields"):
                                    new_val = []
                                    for i in temp_config["Category_attributes"]["Mandatory"][
                                        "RestrictFields"
                                    ]:
                                        try:
                                            new_val.append(verb_to_fname_dict[i])
                                        except Exception as e:
                                            try:
                                                new_val.append(verb_to_fname_dict2[i])
                                            except Exception as e:
                                                new_val.append(i)
                                    temp_config["Category_attributes"]["Mandatory"][
                                        "RestrictFields"
                                    ] = new_val

                                if temp_config.get("reportingView"):
                                    if temp_config["reportingView"].get("reportingViewColumns"):
                                        new_val = []
                                        for i in temp_config["reportingView"]["reportingViewColumns"]:
                                            try:
                                                new_val.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        temp_config["reportingView"]["reportingViewColumns"] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("allowEditColConfig"):
                                    new_val_list = []
                                    for i in temp_config["Category_attributes"]["Mandatory"][
                                        "allowEditColConfig"
                                    ]:
                                        new_val = {}
                                        for key, value in i.items():
                                            if key == "column":
                                                try:
                                                    new_val[key] = verb_to_fname_dict[value]
                                                except Exception as e:
                                                    try:
                                                        new_val[key] = verb_to_fname_dict2[value]
                                                    except Exception as e:
                                                        new_val[key] = value
                                            else:
                                                new_val[key] = value
                                        new_val_list.append(new_val)
                                    temp_config["Category_attributes"]["Mandatory"][
                                        "allowEditColConfig"
                                    ] = new_val_list

                                if temp_config["Category_attributes"]["Mandatory"].get("configActionButtons"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "configActionButtons"
                                    ].items():
                                        for kk, value_config in configs.items():
                                            if kk == "columnOrder":
                                                new_val = []
                                                for i in value_config:
                                                    try:
                                                        new_val.append(verb_to_fname_dict[i])
                                                    except Exception as e:
                                                        try:
                                                            new_val.append(verb_to_fname_dict2[i])
                                                        except Exception as e:
                                                            new_val.append(i)
                                                temp_config["Category_attributes"]["Mandatory"][
                                                    "configActionButtons"
                                                ][tab_name][kk] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("columnHeadersHide"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "columnHeadersHide"
                                    ].items():
                                        new_val = []
                                        for i in configs:
                                            try:
                                                new_val.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        temp_config["Category_attributes"]["Mandatory"]["columnHeadersHide"][
                                            tab_name
                                        ] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get("titleRowFormatting"):
                                    for tab_name, configs in temp_config["Category_attributes"]["Mandatory"][
                                        "titleRowFormatting"
                                    ].items():
                                        for kk, value_config in configs.items():
                                            if kk == "exception":
                                                new_val = {}
                                                for exp_name, conf in value_config.items():
                                                    try:
                                                        new_val[verb_to_fname_dict[exp_name]] = conf
                                                    except Exception as e:
                                                        new_val[verb_to_fname_dict2[exp_name]] = conf
                                                temp_config["Category_attributes"]["Mandatory"][
                                                    "titleRowFormatting"
                                                ][tab_name][kk] = new_val

                                if temp_config["Category_attributes"]["Mandatory"].get(
                                    "listViewEmbededComputation"
                                ):
                                    for k, v in temp_config["Category_attributes"]["Mandatory"][
                                        "listViewEmbededComputation"
                                    ].items():
                                        new_val = []
                                        for model_name, model_config in v.items():
                                            for i in model_config:
                                                n_Va = []
                                                if isinstance(i, list):
                                                    for j in i:
                                                        try:
                                                            n_Va.append(verb_to_fname_dict[j])
                                                        except Exception as e:
                                                            n_Va.append(verb_to_fname_dict2[j])
                                                    new_val.append(n_Va)
                                                else:
                                                    new_val.append(i)
                                        temp_config["Category_attributes"]["Mandatory"][
                                            "listViewEmbededComputation"
                                        ][k][model_name] = new_val

                                if temp_config.get("table_header_data"):
                                    for k, v in temp_config["table_header_data"].items():
                                        nn = []
                                        for i in v:
                                            try:
                                                nn.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                nn.append(verb_to_fname_dict2[i])
                                        temp_config["table_header_data"][k] = nn

                                tab_body_content_list[indx] = json.dumps(temp_config)

                                update_data_func(
                                    request,
                                    config_dict={
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "TabScreens",
                                            "Columns": [
                                                {
                                                    "column_name": "tab_body_content",
                                                    "input_value": json.dumps(temp_config),
                                                    "separator": ",",
                                                },
                                                {
                                                    "column_name": "update_version",
                                                    "input_value": "1.1.0",
                                                    "separator": "",
                                                },
                                            ],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "element_id",
                                                "condition": "Equal to",
                                                "input_value": str(tabScreenElementIDList1[indx]),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                        else:
                            for view_name, config in temp_config.items():
                                temp_table_name = config["Category_attributes"]["Mandatory"]["Table_name"]

                                act_modelname = get_model_class(temp_table_name, request)
                                verb_to_fname_dict = {
                                    field.verbose_name: field.name for field in act_modelname.concrete_fields
                                }
                                verb_to_fname_dict2 = {
                                    field.verbose_name.title(): field.name
                                    for field in act_modelname.concrete_fields
                                }

                                if config["Category_attributes"]["Mandatory"].get("DroppedFields"):
                                    new_val = []
                                    for i in config["Category_attributes"]["Mandatory"]["DroppedFields"]:
                                        try:
                                            new_val.append(verb_to_fname_dict[i])
                                        except Exception as e:
                                            try:
                                                new_val.append(verb_to_fname_dict2[i])
                                            except Exception as e:
                                                new_val.append(i)
                                    config["Category_attributes"]["Mandatory"]["DroppedFields"] = new_val

                                if config["Category_attributes"]["Mandatory"].get("RestrictFields"):
                                    new_val = []
                                    for i in config["Category_attributes"]["Mandatory"]["RestrictFields"]:
                                        try:
                                            new_val.append(verb_to_fname_dict[i])
                                        except Exception as e:
                                            try:
                                                new_val.append(verb_to_fname_dict2[i])
                                            except Exception as e:
                                                new_val.append(i)
                                    config["Category_attributes"]["Mandatory"]["RestrictFields"] = new_val

                                if config.get("reportingView"):
                                    if config["reportingView"].get("reportingViewColumns"):
                                        new_val = []
                                        for i in config["reportingView"]["reportingViewColumns"]:
                                            try:
                                                new_val.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        config["reportingView"]["reportingViewColumns"] = new_val

                                if config["Category_attributes"]["Mandatory"].get("allowEditColConfig"):
                                    new_val_list = []
                                    for i in config["Category_attributes"]["Mandatory"]["allowEditColConfig"]:
                                        new_val = {}
                                        for key, value in i.items():
                                            if key == "column":
                                                try:
                                                    new_val[key] = verb_to_fname_dict[value]
                                                except Exception as e:
                                                    try:
                                                        new_val[key] = verb_to_fname_dict2[value]
                                                    except Exception as e:
                                                        new_val[key] = value
                                            else:
                                                new_val[key] = value
                                        new_val_list.append(new_val)
                                    config["Category_attributes"]["Mandatory"][
                                        "allowEditColConfig"
                                    ] = new_val_list

                                if config["Category_attributes"]["Mandatory"].get("configActionButtons"):
                                    for tab_name, configs in config["Category_attributes"]["Mandatory"][
                                        "configActionButtons"
                                    ].items():
                                        for kk, value_config in configs.items():
                                            if kk == "columnOrder":
                                                new_val = []
                                                for i in value_config:
                                                    try:
                                                        new_val.append(verb_to_fname_dict[i])
                                                    except Exception as e:
                                                        try:
                                                            new_val.append(verb_to_fname_dict2[i])
                                                        except Exception as e:
                                                            new_val.append(i)
                                                config["Category_attributes"]["Mandatory"][
                                                    "configActionButtons"
                                                ][tab_name][kk] = new_val

                                if config["Category_attributes"]["Mandatory"].get("columnHeadersHide"):
                                    for tab_name, configs in config["Category_attributes"]["Mandatory"][
                                        "columnHeadersHide"
                                    ].items():
                                        new_val = []
                                        for i in configs:
                                            try:
                                                new_val.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                try:
                                                    new_val.append(verb_to_fname_dict2[i])
                                                except Exception as e:
                                                    new_val.append(i)
                                        config["Category_attributes"]["Mandatory"]["columnHeadersHide"][
                                            tab_name
                                        ] = new_val

                                if config["Category_attributes"]["Mandatory"].get("titleRowFormatting"):
                                    for tab_name, configs in config["Category_attributes"]["Mandatory"][
                                        "titleRowFormatting"
                                    ].items():
                                        for kk, value_config in configs.items():
                                            if kk == "exception":
                                                new_val = {}
                                                for exp_name, conf in value_config.items():
                                                    try:
                                                        new_val[verb_to_fname_dict[exp_name]] = conf
                                                    except Exception as e:
                                                        new_val[verb_to_fname_dict2[exp_name]] = conf
                                                config["Category_attributes"]["Mandatory"][
                                                    "titleRowFormatting"
                                                ][tab_name][kk] = new_val

                                if config["Category_attributes"]["Mandatory"].get(
                                    "listViewEmbededComputation"
                                ):
                                    for k, v in config["Category_attributes"]["Mandatory"][
                                        "listViewEmbededComputation"
                                    ].items():
                                        new_val = []
                                        for model_name, model_config in v.items():
                                            for i in model_config:
                                                n_Va = []
                                                if isinstance(i, list):
                                                    for j in i:
                                                        try:
                                                            n_Va.append(verb_to_fname_dict[j])
                                                        except Exception as e:
                                                            n_Va.append(verb_to_fname_dict2[j])
                                                    new_val.append(n_Va)
                                                else:
                                                    new_val.append(i)
                                        config["Category_attributes"]["Mandatory"][
                                            "listViewEmbededComputation"
                                        ][k][model_name] = new_val

                                if config.get("table_header_data"):
                                    for k, v in config["table_header_data"].items():
                                        nn = []
                                        for i in v:
                                            try:
                                                nn.append(verb_to_fname_dict[i])
                                            except Exception as e:
                                                nn.append(verb_to_fname_dict2[i])
                                        config["table_header_data"][k] = nn

                            tab_body_content_list[indx] = json.dumps(temp_config)

                            update_data_func(
                                request,
                                config_dict={
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "TabScreens",
                                        "Columns": [
                                            {
                                                "column_name": "tab_body_content",
                                                "input_value": json.dumps(temp_config),
                                                "separator": ",",
                                            },
                                            {
                                                "column_name": "update_version",
                                                "input_value": "1.1.0",
                                                "separator": "",
                                            },
                                        ],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "element_id",
                                            "condition": "Equal to",
                                            "input_value": str(tabScreenElementIDList1[indx]),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )

                except Exception as e:
                    logging.warning(
                        f"Following exception occured while regenerating html for listview ---> {e}"
                    )

        l3_ct = False
        if design_mode:
            html = ""
            l3_ct = True
        else:
            html = html + html_generator.navLink(
                tab_header_name_list,
                tab_body_content_list,
                tabScreenElementIDList1,
                tab_type_list,
                ids,
                breadcrumbs,
                tabs_multi_function_list,
                request,
                tab_color_config,
            )
        screen_path = f"/users/{related_item_code[0]}/"
        data1 = {}
        sqlReadData = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "UserConfig",
                    "Columns": ["id", "plot_config_home_page"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "Equal to",
                        "input_value": user_name,
                        "and_or": "and",
                    },
                    {
                        "column_name": "plot_config_home_page",
                        "condition": "Not Equal to",
                        "input_value": "NULL",
                        "and_or": "and",
                    },
                    {
                        "column_name": "screen_url",
                        "condition": "Equal to",
                        "input_value": screen_path,
                        "and_or": "",
                    },
                ],
            },
        )

        if not sqlReadData.empty:
            data1["plot_config_data"] = sqlReadData["plot_config_home_page"][0]
            data1["bokeh_chart_load_yes_or_no"] = "YES"
        else:
            data1["bokeh_chart_load_yes_or_no"] = "NO"

        redis_data = {
            "data1": data1,
            "tab_header_name_list": tab_header_name_list,
            "tabScreenElementIDList1": tabScreenElementIDList1,
            "tab_type_list": tabScreenElementIDList1,
            "ids": ids,
            "breadcrumbs": breadcrumbs,
            "process_code": process_code,
            "main_index": str(main_index),
        }
        redis_instance.set(related_item_code[0], pickle.dumps(redis_data))
        html_, script, error_canvas = html_generator.html_generator_all(
            request,
            tab_header_name_list,
            tab_body_content_list,
            tabScreenElementIDList1,
            table_name_list,
            tab_type_list,
            data1,
            process_code,
            related_item_code[0],
            tabs_multi_function_list,
            [],
            element_id_ct_del,
            tab_color_config,
            regenerate=True,
            skip_gen=skip_gen,
            create_view_tab=create_view_tab,
            design_mode=design_mode,
        )
        html = html + html_
        for k in sql_query_app_list:
            if os.path.exists(f"kore_investment/templates/user_defined_template/{tenant}/{k}"):
                if not l3_ct:
                    hs = open(
                        f"kore_investment/templates/user_defined_template/{tenant}/{k}/{process_code}_{related_item_code[0]}_html.html",
                        "w",
                    )
                    hs.write(html)
                    final_html = html_generator.importScript(request, k, related_item_code[0]) + html
                    hs.close()
                    hs = open(
                        f"kore_investment/templates/user_defined_template/{tenant}/{k}/{process_code}_{related_item_code[0]}_script.html",
                        "w",
                    )
                    hs.write(script)
                    hs.close()
                    final_html += script
                    final_html += html_generator.navLinkScript()
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/{k}/{process_code}_{related_item_code[0]}.html",
                        "w",
                    ) as f:
                        f.write(final_html + "{%endblock%}")
                        f.close()

            else:
                os.makedirs(f"kore_investment/templates/user_defined_template/{tenant}/{k}")
                if not l3_ct:
                    hs = open(
                        f"kore_investment/templates/user_defined_template/{tenant}/{k}/{process_code}_{related_item_code[0]}_html.html",
                        "w",
                    )
                    hs.write(html)
                    hs.close()
                    hs = open(
                        f"kore_investment/templates/user_defined_template/{tenant}/{k}/{process_code}_{related_item_code[0]}_script.html",
                        "w",
                    )
                    hs.write(script)
                    hs.close()

        noti_msg = f"Regeneration of <b>{subprocess_name}</b> in the application has been successful."

        data_df = pd.DataFrame(
            [
                {
                    "user_name": request.user.username,
                    "category": "system notification",
                    "status": "unread",
                    "notification_message": noti_msg,
                    "created_date": datetime.now(),
                    "instance_id": request.user.instance_id,
                }
            ]
        )

        postgres_push(data_df, "users_notification_management", schema=tenant)
        notification_id = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "notification_management",
                    "Order_Type": "ORDER BY created_date DESC",
                    "Agg_Type": "TOP(1)",
                    "Columns": ["id"],
                },
                "condition": [
                    {
                        "column_name": "user_name",
                        "condition": "Equal to",
                        "input_value": request.user.username,
                        "and_or": "",
                    },
                ],
            },
            schema=tenant,
        ).iloc[0]["id"]
        return True, request.user.username, subprocess_name, tenant, str(notification_id)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        noti_msg = f"Regeneration of <b>{subprocess_name}</b> in the application has been unsuccessful."

        data_df = pd.DataFrame(
            [
                {
                    "user_name": request.user.username,
                    "category": "system notification",
                    "status": "unread",
                    "notification_message": noti_msg,
                    "created_date": datetime.now(),
                    "instance_id": request.user.instance_id,
                }
            ]
        )

        postgres_push(data_df, "users_notification_management", schema=tenant)

        notification_id = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "notification_management",
                    "Order_Type": "ORDER BY created_date DESC",
                    "Agg_Type": "TOP(1)",
                    "Columns": ["id"],
                },
                "condition": [
                    {
                        "column_name": "user_name",
                        "condition": "Equal to",
                        "input_value": request.user.username,
                        "and_or": "",
                    }
                ],
            },
            schema=tenant,
        ).iloc[0]["id"]

        return False, request.user.username, subprocess_name, tenant, str(notification_id)


def update_process_BM_App(process_code, request, final_items_list={}):

    sql_query_bm_list = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Business_Models",
                "Columns": [
                    "business_model_code",
                    "process_group_codes",
                    "computation_model_names",
                    "table_names",
                ],
            },
            "condition": [
                {
                    "column_name": "process_group_codes",
                    "condition": "Contains",
                    "input_value": process_code,
                    "and_or": "",
                }
            ],
        },
    )

    sql_query_app_list = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Application",
                "Columns": [
                    "application_code",
                    "business_model_codes",
                    "computation_model_names",
                    "table_names",
                ],
            },
            "condition": [
                {
                    "column_name": "process_group_codes",
                    "condition": "Contains",
                    "input_value": process_code,
                    "and_or": "",
                }
            ],
        },
    )

    # Editing business model's data
    for bm_row in range(len(sql_query_bm_list)):
        row_data = sql_query_bm_list.iloc[bm_row,]
        bm_code = row_data["business_model_code"]
        processList = json.loads(row_data["process_group_codes"])
        p_string = "("
        for ind, i in enumerate(processList):
            p_string += "'" + i + "'"
            if (len(processList) - 1) != ind:
                p_string += ","
            else:
                p_string += ")"
        if len(processList) == 0:
            p_string += "'')"

        sub_process_code = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": ["item_code", "item_group_name"],
                },
                "condition": [
                    {
                        "column_name": "item_group_code",
                        "condition": "IN",
                        "input_value": p_string,
                        "and_or": "",
                    }
                ],
            },
        )
        sub_process_codes = sub_process_code.item_code.to_list()
        sub_p_string = "("
        for ind, i in enumerate(sub_process_codes):
            sub_p_string += "'" + i + "'"
            if (len(sub_process_codes) - 1) != ind:
                sub_p_string += ","
            else:
                sub_p_string += ")"
        if len(sub_process_codes) == 0:
            sub_p_string += "'')"
        process_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "TabScreens",
                    "Columns": ["table_name", "computation_name", "dependent_computations"],
                },
                "condition": [
                    {
                        "column_name": "related_item_code",
                        "condition": "IN",
                        "input_value": sub_p_string,
                        "and_or": "",
                    }
                ],
            },
        )
        process_table_list = process_data.table_name.to_list()
        process_computation_list = process_data.computation_name.to_list()
        process_dep_computation_list = process_data.dependent_computations.dropna().to_list()
        process_table_set = set()
        for i in process_table_list:
            if i is not None:
                if i.startswith("["):
                    i = json.loads(i)
                    for tb in i:
                        process_table_set.add(tb)
                else:
                    process_table_set.add(i)
        bm_table_names = json.dumps(list(process_table_set))
        process_computation_set = set()
        for i in process_computation_list:
            if i is not None:
                if i.startswith("["):
                    i = json.loads(i)
                    for tb in i:
                        process_computation_set.add(tb)
                else:
                    process_computation_set.add(i)
        for i in process_dep_computation_list:
            if i:
                i = json.loads(i)
                for tb in i:
                    process_computation_set.add(tb)
            else:
                continue
        bm_computation_names = json.dumps(list(process_computation_set))
        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Business_Models",
                    "Columns": [
                        {
                            "column_name": "computation_model_names",
                            "input_value": bm_computation_names,
                            "separator": ",",
                        },
                        {
                            "column_name": "table_names",
                            "input_value": bm_table_names,
                            "separator": "",
                        },
                    ],
                },
                "condition": [
                    {
                        "column_name": "business_model_code",
                        "condition": "Equal to",
                        "input_value": bm_code,
                        "and_or": "",
                    }
                ],
            },
        )

    # Editing application's data
    for app_row in range(len(sql_query_app_list)):
        row_data = sql_query_app_list.iloc[app_row,]
        app_code = row_data["application_code"]
        bm_list = json.loads(row_data["business_model_codes"])

        bm_string = "("
        for ind, i in enumerate(bm_list):
            bm_string += "'" + i + "'"
            if (len(bm_list) - 1) != ind:
                bm_string += ","
            else:
                bm_string += ")"
        if len(bm_list) == 0:
            bm_string += "'')"

        bm_data = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Business_Models",
                    "Columns": [
                        "computation_model_names",
                        "table_names",
                        "additional_table_names",
                    ],
                },
                "condition": [
                    {
                        "column_name": "business_model_code",
                        "condition": "IN",
                        "input_value": bm_string,
                        "and_or": "",
                    }
                ],
            },
        )
        app_computation_list = bm_data.computation_model_names.tolist()
        app_tables_list = bm_data.table_names.tolist()
        app_tables_list.extend(bm_data.additional_table_names.tolist())
        app_table_names = set()
        for i in app_tables_list:
            if i is not None:
                if i.startswith("["):
                    i = json.loads(i)
                    for tb in i:
                        app_table_names.add(tb)
                else:
                    app_table_names.add(i)
        app_table_names = json.dumps(list(app_table_names))
        app_computation_names = set()
        for i in app_computation_list:
            if i is not None:
                if i.startswith("["):
                    i = json.loads(i)
                    for tb in i:
                        app_computation_names.add(tb)
                else:
                    app_computation_names.add(i)
        app_computation_names = json.dumps(list(app_computation_names))

        update_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Application",
                    "Columns": [
                        {
                            "column_name": "computation_model_names",
                            "input_value": app_computation_names,
                            "separator": ",",
                        },
                        {
                            "column_name": "table_names",
                            "input_value": app_table_names,
                            "separator": "",
                        },
                    ],
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
        )


def request_to_dict(request):
    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
    request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
    return request2
