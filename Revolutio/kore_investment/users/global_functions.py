from datetime import datetime
import json
import logging
import os
import pickle

from django.urls import resolve
from django_multitenant.utils import get_current_tenant
import pandas as pd

from config.settings.base import PLATFORM_DATA_PATH, PLATFORM_FILE_PATH, redis_instance
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    db_engine_extractor,
    read_data_func,
)
from kore_investment.users.computations.standardised_functions import current_app_db_extractor, getNavPoints


def sideNavBarLoad(request):
    apps = resolve(request.path_info).app_names
    if apps:
        if apps[0] != "users":
            return {}
    else:
        return {}
    userName = request.user.username
    tenant_object = get_current_tenant()
    tenant = tenant_object.name
    current_path = request.path
    curr_app_code, db_connection_name = current_app_db_extractor(request, tenant=tenant)
    if (
        current_path
        not in [
            "/",
            "/users/selectApplication/",
            "/users/dashboard/",
            "/users/selectDashboard/",
            "/applicationlogin/",
            "/accounts/login/",
            "/accounts/logout/",
            "/users/adminPanel/",
            "/users/customizeTheme/",
            "/users/previewTheme/",
            "/users/alertsSetup/",
            "/accounts/password/change/",
        ]
        and userName
        and curr_app_code
        and "application" not in current_path
        and resolve(request.path_info).url_name not in ["url_not_found", "404"]
        and "static/" not in current_path
    ):
        username_tenant = userName + tenant
        if redis_instance.exists(username_tenant) == 1:
            user_info = pickle.loads(redis_instance.get(username_tenant))
        else:
            user_info = {}
        url_string = request.path
        f_occ = url_string.find("/", url_string.find("/") + 1)
        s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
        t_occ = url_string.find("/", url_string.find("/") + s_occ + 1)
        app_code = url_string[f_occ + 1 : s_occ]
        current_dev_mode = url_string[s_occ + 1 : t_occ]
        build_process_type = "Not Selected"
        if request.user.is_superuser or not request.user.is_anonymous:
            if build_process_type == "draft":
                finalList1 = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user_navbar",
                            "Columns": ["navbar_list"],
                        },
                        "condition": [
                            {
                                "column_name": "user_name",
                                "condition": "Equal to",
                                "input_value": userName,
                                "and_or": "and",
                            },
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": tenant_object.id,
                                "and_or": "and",
                            },
                            {
                                "column_name": "build_process_type",
                                "condition": "Equal to",
                                "input_value": build_process_type,
                                "and_or": "and",
                            },
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                )
            else:
                finalList1 = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user_navbar",
                            "Columns": ["navbar_list"],
                        },
                        "condition": [
                            {
                                "column_name": "user_name",
                                "condition": "Equal to",
                                "input_value": userName,
                                "and_or": "and",
                            },
                            {
                                "column_name": "instance_id",
                                "condition": "Equal to",
                                "input_value": tenant_object.id,
                                "and_or": "and",
                            },
                            {
                                "column_name": "app_code",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            },
                        ],
                    },
                )
            if len(finalList1) > 0:
                finalList1 = json.loads(finalList1.navbar_list.iloc[0])
            else:
                finalList1 = []
            user_info["user_navbar_config"] = {"defaultNavData": finalList1, "operation": "defaultSideNavBar"}
            user_info["user_state_save"] = {
                "app_code": app_code,
                "current_dev_mode": current_dev_mode,
                "build_process_type": build_process_type,
            }
            redis_instance.set(username_tenant, pickle.dumps(user_info))
            finalist2 = getNavPoints(current_dev_mode, request, app_code, tenant)

            system_management_data = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "system_management_table",
                        "Columns": ["preference_config"],
                        "condition": [
                            {
                                "column_name": "screens",
                                "condition": "Equal to",
                                "input_value": "SideNavBar",
                                "and_or": "",
                            }
                        ],
                    }
                },
            )

            # default values
            home_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-home"}
            approval_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-check-circle"}
            report_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-chart-pie"}

            # Parse preference configuration data
            if not system_management_data.empty:
                preference_config_dict = json.loads(system_management_data["preference_config"][0])
                for config in preference_config_dict:
                    for key in config.keys():
                        stripped_key = key.strip().lower()
                        if "home" in stripped_key:
                            home_configs.update(config[key])
                        elif "approval" in stripped_key:
                            approval_configs.update(config[key])
                        elif "report" in stripped_key:
                            report_configs.update(config[key])
            return {
                "defaultNavData": finalList1,
                "operation": "defaultSideNavBar",
                "config_navbar": finalist2,
                "request_user": userName,
                "sys_mgmt_home_configs_Show_or_hide_on_Navbar": home_configs.get("Show_or_hide_on_Navbar"),
                "sys_mgmt_home_configs_icon": home_configs.get("icon"),
                "sys_mgmt_approval_configs_Show_or_hide_on_Navbar": approval_configs.get(
                    "Show_or_hide_on_Navbar"
                ),
                "sys_mgmt_approval_configs_icon": approval_configs.get("icon"),
                "sys_mgmt_report_configs_Show_or_hide_on_Navbar": report_configs.get(
                    "Show_or_hide_on_Navbar"
                ),
                "sys_mgmt_report_configs_icon": report_configs.get("icon"),
            }
        # * should we perform user access checks for anonymous users
        else:
            if app_code:
                if current_dev_mode == "Build" and build_process_type in ["draft", "Final"]:
                    colAll = [
                        "item_code",
                        "item_name",
                        "item_shortname",
                        "item_group_code",
                        "item_group_name",
                        "item_group_shortname",
                        "hover_option",
                        "item_level",
                        "item_popup_config",
                        "item_url",
                        "item_extra_details",
                        "related_entity",
                        "app_allocation_status",
                        "created_by",
                        "created_date",
                        "share_with_group",
                    ]
                    sql_query = {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "NavigationSideBar",
                            "Columns": colAll,
                        },
                        "condition": [
                            {
                                "column_name": "item_level",
                                "condition": "IN",
                                "input_value": "('0','1')",
                                "and_or": "AND",
                            },
                            {
                                "column_name": "item_code",
                                "condition": "IN",
                                "input_value": "('')",
                                "and_or": "",
                            },
                        ],
                    }
                else:
                    sql_query_app = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Application",
                                "Columns": [
                                    "id",
                                    "application_code",
                                    "application_name",
                                    "business_model_codes",
                                    "business_model_names",
                                    "process_group_codes",
                                    "process_group_names",
                                    "computation_model_codes",
                                    "computation_model_names",
                                    "table_names",
                                    "description",
                                    "app_icon",
                                    "app_icon_color",
                                    "app_card_color",
                                    "app_text_color",
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
                    if not sql_query_app.empty:
                        if sql_query_app.process_group_codes.iloc[0]:
                            process_codes = json.loads(sql_query_app.process_group_codes.iloc[0])
                        else:
                            process_codes = []
                        if len(process_codes) > 0:
                            p_string = "("
                            for ind, i in enumerate(process_codes):
                                p_string += "'" + i + "'"
                                if (len(process_codes) - 1) != ind:
                                    p_string += ","
                                else:
                                    p_string += ")"

                            sub_process_data = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "NavigationSideBar",
                                        "Columns": ["item_code"],
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
                            ).item_code.to_list()
                            if len(sub_process_data) > 0:
                                p_string = p_string.replace(")", ",")
                                for ind, i in enumerate(sub_process_data):
                                    p_string += "'" + i + "'"
                                    if (len(sub_process_data) - 1) != ind:
                                        p_string += ","
                                    else:
                                        p_string += ")"
                            colAll = [
                                "item_code",
                                "item_name",
                                "item_shortname",
                                "item_group_code",
                                "item_group_name",
                                "item_group_shortname",
                                "hover_option",
                                "item_level",
                                "item_popup_config",
                                "item_url",
                                "item_extra_details",
                                "related_entity",
                                "app_allocation_status",
                                "created_by",
                                "created_date",
                                "share_with_group",
                            ]
                            sql_query = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "NavigationSideBar",
                                    "Columns": colAll,
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "IN",
                                        "input_value": "('0','1')",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_code",
                                        "condition": "IN",
                                        "input_value": p_string,
                                        "and_or": "",
                                    },
                                ],
                            }
                        else:
                            colAll = [
                                "item_code",
                                "item_name",
                                "item_shortname",
                                "item_group_code",
                                "item_group_name",
                                "item_group_shortname",
                                "hover_option",
                                "item_level",
                                "item_popup_config",
                                "item_url",
                                "item_extra_details",
                                "related_entity",
                                "app_allocation_status",
                                "created_by",
                                "created_date",
                                "share_with_group",
                            ]
                            sql_query = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "NavigationSideBar",
                                    "Columns": colAll,
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "IN",
                                        "input_value": "('0','1')",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_code",
                                        "condition": "IN",
                                        "input_value": "('')",
                                        "and_or": "",
                                    },
                                ],
                            }
                    else:
                        colAll = [
                            "item_code",
                            "item_name",
                            "item_shortname",
                            "item_group_code",
                            "item_group_name",
                            "item_group_shortname",
                            "hover_option",
                            "item_level",
                            "item_popup_config",
                            "item_url",
                            "item_extra_details",
                            "related_entity",
                            "app_allocation_status",
                            "created_by",
                            "created_date",
                            "share_with_group",
                        ]
                        sql_query = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "NavigationSideBar",
                                "Columns": colAll,
                            },
                            "condition": [
                                {
                                    "column_name": "item_level",
                                    "condition": "IN",
                                    "input_value": "('0','1')",
                                    "and_or": "AND",
                                },
                                {
                                    "column_name": "item_code",
                                    "condition": "IN",
                                    "input_value": "('')",
                                    "and_or": "",
                                },
                            ],
                        }
            else:
                colAll = [
                    "item_code",
                    "item_name",
                    "item_shortname",
                    "item_group_code",
                    "item_group_name",
                    "item_group_shortname",
                    "hover_option",
                    "item_level",
                    "item_popup_config",
                    "item_url",
                    "item_extra_details",
                    "related_entity",
                    "app_allocation_status",
                    "created_by",
                    "created_date",
                    "share_with_group",
                ]
                sql_query = {
                    "inputs": {"Data_source": "Database", "Table": "NavigationSideBar", "Columns": colAll},
                    "condition": [
                        {
                            "column_name": "item_level",
                            "condition": "IN",
                            "input_value": "('0','1')",
                            "and_or": "AND",
                        },
                        {"column_name": "item_code", "condition": "IN", "input_value": "('')", "and_or": ""},
                    ],
                }
            rawData = read_data_func(request, sql_query)
            groupByItemGroupName = rawData.groupby(["item_group_name"])
            listOfDfAfterGrouping = [groupByItemGroupName.get_group(x) for x in groupByItemGroupName.groups]
            finalList, config_navbar = creatingListOfDictAsFinalResponseForDefaultSideNavBar(
                listOfDfAfterGrouping, request
            )
            finalist2 = getNavPoints(current_dev_mode, request, app_code, tenant)

            system_management_data = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "system_management_table",
                        "Columns": ["preference_config"],
                        "condition": [
                            {
                                "column_name": "screens",
                                "condition": "Equal to",
                                "input_value": "SideNavBar",
                                "and_or": "",
                            }
                        ],
                    }
                },
            )

            # default values
            home_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-home"}
            approval_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-check-circle"}
            report_configs = {"Show_or_hide_on_Navbar": True, "icon": "fa fa-chart-pie"}

            # Parse preference configuration data
            if not system_management_data.empty:
                preference_config_dict = json.loads(system_management_data["preference_config"][0])
                for config in preference_config_dict:
                    for key in config.keys():
                        stripped_key = key.strip().lower()
                        if "home" in stripped_key:
                            home_configs.update(config[key])
                        elif "approval" in stripped_key:
                            approval_configs.update(config[key])
                        elif "report" in stripped_key:
                            report_configs.update(config[key])
            return {
                "defaultNavData": finalList,
                "operation": "defaultSideNavBar",
                "config_navbar": finalist2,
                "request_user": userName,
                "sys_mgmt_home_configs_Show_or_hide_on_Navbar": home_configs.get("Show_or_hide_on_Navbar"),
                "sys_mgmt_home_configs_icon": home_configs.get("icon"),
                "sys_mgmt_approval_configs_Show_or_hide_on_Navbar": approval_configs.get(
                    "Show_or_hide_on_Navbar"
                ),
                "sys_mgmt_approval_configs_icon": approval_configs.get("icon"),
                "sys_mgmt_report_configs_Show_or_hide_on_Navbar": report_configs.get(
                    "Show_or_hide_on_Navbar"
                ),
                "sys_mgmt_report_configs_icon": report_configs.get("icon"),
            }
    else:
        return {"response": "success", "config_navbar": {"new": {"Build": {}, "User": {}}, "existing": {}}}


def creatingListOfDictAsFinalResponseForDefaultSideNavBar(listOfDf, request):
    finalList = []
    for df in listOfDf:
        gName = df["item_group_name"].unique()
        gCode = df["item_group_code"].unique()
        gshortname = df["item_group_shortname"].unique()
        process_icon = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": ["process_icon"],
                },
                "condition": [
                    {
                        "column_name": "item_code",
                        "condition": "Equal to",
                        "input_value": gCode[0],
                        "and_or": "",
                    },
                ],
            },
        )
        process_icon = process_icon.loc[0, "process_icon"]
        if process_icon:
            icon = process_icon
        else:
            icon = "fa fa-edit"
        dfToDictInAList = list(df.fillna("").to_dict("records"))
        for innerDfDict in dfToDictInAList:
            if innerDfDict["item_popup_config"]:
                innerDfDict["item_popup_config"] = json.loads(innerDfDict["item_popup_config"])
            item_code = innerDfDict["item_code"]
            item_grp_code = innerDfDict["item_group_code"]
            subprocess_icon = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "NavigationSideBar",
                        "Columns": ["subprocess_icon"],
                    },
                    "condition": [
                        {
                            "column_name": "item_group_code",
                            "condition": "Equal to",
                            "input_value": item_grp_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "item_code",
                            "condition": "Equal to",
                            "input_value": item_code,
                            "and_or": "",
                        },
                    ],
                },
            )
            subprocess_icon = subprocess_icon.loc[0, "subprocess_icon"]
            if subprocess_icon:
                subprocess_icon = subprocess_icon
            else:
                subprocess_icon = "fa fa-edit"
            innerDfDict["subprocess_icon"] = subprocess_icon

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
                            "input_value": item_code,
                            "and_or": "",
                        }
                    ],
                },
            )
            sqldataitemcodel4list = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "TabScreens",
                        "Columns": [
                            "tab_icon",
                            "tab_header_name",
                            "related_item_code",
                            "id",
                            "tab_type",
                            "element_id",
                            "tab_body_content",
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "related_item_code",
                            "condition": "Equal to",
                            "input_value": item_code,
                            "and_or": "",
                        }
                    ],
                },
            )
            l3iconslist = sqldataitemcodel4list.tab_icon.tolist()
            l3codelist = sqldataitemcodel4list.related_item_code.tolist()
            l3idlist = sqldataitemcodel4list.id.tolist()
            l3tabtypelist = sqldataitemcodel4list.tab_type.tolist()
            l3itemlist = sqldataitemcodel4list.tab_header_name.tolist()
            l3element_idlist = sqldataitemcodel4list.element_id.tolist()
            l3tab_body_contentlist = sqldataitemcodel4list.tab_body_content.tolist()

            if not processDF.empty:
                related_item_flowchart = processDF.to_dict()
                flowchart_element = json.loads(related_item_flowchart["flowchart_elements"][0])
                parent_rel_child_list = []
                for i in flowchart_element:
                    for ele_id in l3element_idlist:
                        child_list = []
                        create_view_check_dict = {}
                        if (i["shapeID"] == ele_id) and (i["text"] == "Create View"):
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
                                if parent_rel_child_list[i]["child"][inner_child] in l3element_idlist:
                                    list_main_index = l3element_idlist.index(
                                        parent_rel_child_list[i]["child"][inner_child]
                                    )
                                    list_view_content = json.loads(l3tab_body_contentlist[list_main_index])
                                    if "create_view_selection_checker" in list_view_content.keys():
                                        if not list_view_content["create_view_selection_checker"]:
                                            if parent_rel_child_list[i]["parent"] in l3element_idlist:
                                                main_index = l3element_idlist.index(
                                                    parent_rel_child_list[i]["parent"]
                                                )
                                                l3iconslist.pop(main_index)
                                                l3codelist.pop(main_index)
                                                l3idlist.pop(main_index)
                                                l3tabtypelist.pop(main_index)
                                                l3itemlist.pop(main_index)
                                                l3element_idlist.pop(main_index)

            len_button = len(l3itemlist) + 1
            listofbuttons = []
            listtabs = []
            for i in range(1, len_button):
                data_button = str(i)
                valueofbuttons = "data-button" + data_button
                listofbuttons.append(valueofbuttons)

            for j in range(0, len(l3itemlist)):

                data = json.dumps(
                    {
                        "tab_header": l3itemlist[j],
                        "tab_icon": l3iconslist[j],
                        "tab_type": l3tabtypelist[j],
                        "id": l3idlist[j],
                        "code": l3codelist[j],
                    }
                )
                listtabs.append(data)

            finaldict = dict(zip(listofbuttons, listtabs))

            innerDfDict["dictionary_item"] = finaldict
            innerDfDict["l3_length"] = len(l3itemlist)
        finalList.append(
            {
                "shortname": gshortname[0],
                "level0Name": gName[0],
                "level0Code": gCode[0],
                "level0IconClass": icon,
                "childrenOfLevel0": dfToDictInAList,
            }
        )
    return finalList, {}


def getCodebyName(url, nav_items):
    item_row = None
    for item in nav_items:
        if item["item_code"] == url:
            item_row = item
            break
    return item_row


def breadcrumbs(request):
    path_info = resolve(request.path_info)
    apps = path_info.app_names
    if apps:
        if apps[0] != "users":
            return {}
    else:
        return {}
    current_url = path_info.url_name
    userName = request.user.username
    instance = get_current_tenant()
    tenant = instance.name
    if not current_url:
        return {}
    if (
        current_url
        in [
            "applicationlanding",
            "applicationlogin",
            "select_application",
            "dashboard",
            "selectDashboard",
            "account_login",
            "application",
            "admin_panel",
            "alerts_setup",
            "customize_theme",
            "preview_theme",
            "account_change_password",
            "userprofile",
            "accounts/password/change/",
            "password_change",
            "login",
            "home",
            "homePage",
            "account_logout",
            "planner",
            "plannerAPI",
            "index",
            "userprofile",
            "userprofileApp",
            "url_not_found",
            "detail",
            "404",
            "500",
            "dynamicVal",
            "logout",
        ]
        or current_url.startswith("index")
        or current_url.__contains__("dashboard")
    ):
        return {}
    if redis_instance.exists(userName + tenant) == 1:
        url = "users" + ":" + current_url
        nav_items = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": ["item_code", "item_name", "item_url", "item_group_code", "item_group_name"],
                },
                "condition": [],
            },
        )
        nav_items = nav_items.to_dict("records")

        select_currentRow = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "NavigationSideBar",
                    "Columns": ["item_url", "item_code"],
                },
                "condition": [
                    {"column_name": "item_url", "condition": "Equal to", "input_value": url, "and_or": ""}
                ],
            },
        )
        if select_currentRow.empty:
            return {}
        get_row = getCodebyName(select_currentRow["item_code"][0], nav_items)
        breadcrumb_list = []
        breadcrumb_list.append(get_row)
        breadcrumb_list = customfunc(get_row, breadcrumb_list, nav_items)
        breadcrumb_list.reverse()
    else:
        return {}
    return {"breadcrumbs": breadcrumb_list}


def customfunc(get_row, breadcrumb_list, nav_items):
    if get_row["item_group_code"] is None:
        return breadcrumb_list
    else:
        newRes = getCodebyName(get_row["item_group_code"], nav_items)
        breadcrumb_list.append(newRes)

        return customfunc(newRes, breadcrumb_list, nav_items)


def application_list(request):
    path_info = resolve(request.path_info)
    apps = path_info.app_names
    if apps:
        if apps[0] != "users":
            return {}
    else:
        return {}
    user_name = request.user.username
    instance = get_current_tenant()
    tenant = instance.name
    configuration_parameters = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "configuration_parameter",
                "Columns": ["parameter", "value"],
            },
            "condition": [],
        },
    )
    if configuration_parameters.empty:
        with open(f"{PLATFORM_DATA_PATH}config_parameter_data.json") as f:
            config_json_data = json.load(f)
            config_dataframe = pd.DataFrame(config_json_data)
            data_handling(
                request,
                config_dataframe,
                "configuration_parameter",
            )
        app_mode = config_dataframe[config_dataframe["parameter"] == "Application mode"].value.tolist()[0]
        dev_mode = config_dataframe[config_dataframe["parameter"] == "Developer mode"].value.tolist()[0]
        allotted_apps_list = config_dataframe[
            config_dataframe["parameter"] == "Allotted Applications"
        ].value.tolist()[0]
    else:
        configuration_parameters = configuration_parameters.set_index("parameter").to_dict()["value"]
        app_mode = configuration_parameters["Application mode"]
        dev_mode = configuration_parameters["Developer mode"]
        allotted_apps_list = configuration_parameters["Allotted Applications"]

    if allotted_apps_list:
        allotted_apps_list = json.loads(allotted_apps_list)
    else:
        allotted_apps_list = []
    if user_name == "":
        return {"applications": [], "is_user_dev": "false", "dev_applications": [], "app_mode": app_mode}
    else:
        user_grp_list = list(request.user.groups.values_list("name", flat=True))
        grp_string = "("
        for ind, i in enumerate(user_grp_list):
            grp_string += "'" + str(i) + "'"
            if (len(user_grp_list) - 1) != ind:
                grp_string += ","
            else:
                grp_string += ")"
        if len(user_grp_list) == 0:
            grp_string += "'')"
        connected_database = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
            with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                db_data = json.load(json_file)
                connected_database = {k: v for k, v in db_data.items() if v.get("tenant") == tenant}
                json_file.close()
        apps_deactivated = (
            read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "applicationAccess",
                        "Columns": [
                            "app_code",
                        ],
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
            )
        ).app_code.tolist()
        if apps_deactivated:
            app_condition = [
                {
                    "column_name": "application_code",
                    "condition": "NOT IN",
                    "input_value": apps_deactivated,
                    "and_or": "",
                }
            ]
        else:
            app_condition = []
        sql_query_app = pd.DataFrame(
            columns=[
                "application_code",
                "application_name",
                "app_ui_config",
            ]
        )
        dev_application_set = set()
        if len(connected_database) > 0:
            for k, config in connected_database.items():
                if k != "default":
                    user_db_engine, db_type = db_engine_extractor(k)
                    if user_db_engine != ["", None]:
                        try:
                            sql_query_app = pd.concat(
                                [
                                    sql_query_app,
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "Application",
                                                "Columns": [
                                                    "application_code",
                                                    "application_name",
                                                    "app_ui_config",
                                                ],
                                            },
                                            "condition": app_condition,
                                        },
                                        engine2=user_db_engine,
                                        engine_override=True,
                                        db_type=db_type,
                                    ),
                                ]
                            )
                            sql_query_app.fillna("", inplace=True)
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            continue
            sql_query_app.drop_duplicates(
                subset=["application_code"], keep="last", inplace=True, ignore_index=True
            )
            sql_query_app["description"] = ""
            sql_query_app["app_icon"] = ""
            sql_query_app["app_icon_color"] = ""
            sql_query_app["app_card_color"] = ""
            sql_query_app["app_text_color"] = ""
            sql_query_app["app_text_description_color"] = ""
            sql_query_app["t3_app_size"] = ""

            for ind, row in sql_query_app.iterrows():

                if row["app_ui_config"]:
                    sql_query_app.loc[ind, "description"] = json.loads(row["app_ui_config"])["description"]
                    sql_query_app.loc[ind, "app_icon"] = json.loads(row["app_ui_config"])["app_icon"]
                    sql_query_app.loc[ind, "app_icon_color"] = json.loads(row["app_ui_config"])[
                        "app_icon_color"
                    ]
                    sql_query_app.loc[ind, "app_card_color"] = json.loads(row["app_ui_config"])[
                        "app_card_color"
                    ]
                    sql_query_app.loc[ind, "app_text_color"] = json.loads(row["app_ui_config"])[
                        "app_text_color"
                    ]
                    if "app_text_description_color" in json.loads(row["app_ui_config"]):
                        sql_query_app.loc[ind, "app_text_description_color"] = json.loads(
                            row["app_ui_config"]
                        )["app_text_description_color"]
                    if "t3_app_size" in json.loads(row["app_ui_config"]):
                        sql_query_app.loc[ind, "t3_app_size"] = json.loads(row["app_ui_config"])[
                            "t3_app_size"
                        ]

            sql_query_app.drop(["app_ui_config"], axis=1, inplace=True)

        grp_app_list = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "UserPermission_Master",
                    "Columns": ["app_code", "application_dev"],
                },
                "condition": [
                    {
                        "column_name": "usergroup",
                        "condition": "IN",
                        "input_value": grp_string,
                        "and_or": "",
                    }
                ],
            },
        )
        dev_application_set = grp_app_list[grp_app_list["application_dev"] == "1"].app_code.tolist()
        if dev_application_set:
            is_user_dev = "true"
        else:
            is_user_dev = "false"
        dev_application_list = sql_query_app[sql_query_app["application_code"].isin(dev_application_set)]
        grp_app_list_2 = grp_app_list.app_code.tolist()

        # ? Should we do this
        sql_query_app = sql_query_app[sql_query_app["application_code"].isin(allotted_apps_list)]
        if app_mode == "App + Dev":
            if request.user.is_superuser:
                is_user_superuser = "true"
                application_list = sql_query_app.to_dict("records")
                dev_application_list = sql_query_app.to_dict("records")
            else:
                is_user_superuser = "false"
                sql_query_app = sql_query_app[sql_query_app["application_code"].isin(grp_app_list_2)]
                application_list = sql_query_app.to_dict("records")
                dev_application_list = dev_application_list[
                    dev_application_list["application_code"].isin(allotted_apps_list)
                ]
                dev_application_list = dev_application_list.to_dict("records")
        else:
            if request.user.is_superuser:
                is_user_superuser = "true"
                application_list = sql_query_app.to_dict("records")
                dev_application_list = []
            else:
                is_user_superuser = "false"
                sql_query_app = sql_query_app[sql_query_app["application_code"].isin(grp_app_list_2)]
                application_list = sql_query_app.to_dict("records")
                dev_application_list = []
            is_user_dev = "false"

        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            for i in application_list:
                app_code = i["application_code"]
                tenant_app_code = tenant + "_" + app_code
                db_connection_name = app_db_mapping[tenant_app_code]
                i.update({"db_connection_name": db_connection_name})

        allow_users_to_config_smtp = False
        remove_bell_icon = False
        limit_notification = 5
        tenant_data = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        for t_name, t_config in tenant_data.items():
            if t_name == tenant:
                if "allow_user_forum" in t_config:
                    allow_user_forum = t_config["allow_user_forum"]
                else:
                    allow_user_forum = "True"
                    t_config.update({"allow_user_forum": "True"})
                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_data, json_file, indent=4)
                        json_file.close()

                if "allow_user_planner" in t_config:
                    allow_user_planner = t_config["allow_user_planner"]
                else:
                    allow_user_planner = "True"
                    t_config.update({"allow_user_planner": "True"})
                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_data, json_file, indent=4)
                        json_file.close()

                if "allow_user_profile" in t_config:
                    allow_user_profile = t_config["allow_user_profile"]
                else:
                    allow_user_profile = "True"
                    t_config.update({"allow_user_profile": "True"})
                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_data, json_file, indent=4)
                        json_file.close()

                if "developer_mode" in t_config:
                    developer_mode = t_config["developer_mode"]
                else:
                    developer_mode = "True"
                    t_config.update({"developer_mode": "True"})
                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_data, json_file, indent=4)
                        json_file.close()

                block_custom_homepage = block_add_navpoint = block_remove_navpoint = "False"

                if (
                    "/Build/" in request.path or "/User/" in request.path
                ) and "block_custom_homepage_dev" in t_config:
                    if t_config["block_custom_homepage_dev"] == "true":
                        block_custom_homepage = "True"

                if "/User/" in request.path and "block_custom_homepage_user" in t_config:
                    if t_config["block_custom_homepage_user"] == "true":
                        block_custom_homepage = "True"

                if (
                    "/Build/" in request.path or "/User/" in request.path
                ) and "block_add_navpoints_dev" in t_config:
                    if t_config["block_add_navpoints_dev"] == "true":
                        block_add_navpoint = "True"

                if "/User/" in request.path and "block_add_navpoints_user" in t_config:
                    if t_config["block_add_navpoints_user"] == "true":
                        block_add_navpoint = "True"

                if (
                    "/Build/" in request.path or "/User/" in request.path
                ) and "block_remove_navpoints_dev" in t_config:
                    if t_config["block_remove_navpoints_dev"] == "true":
                        block_remove_navpoint = "True"

                if "/User/" in request.path and "block_remove_navpoints_user" in t_config:
                    if t_config["block_remove_navpoints_user"] == "true":
                        block_remove_navpoint = "True"

                if "allow_users_to_config_smtp" in t_config:
                    allow_users_to_config_smtp = json.loads(t_config["allow_users_to_config_smtp"])

                if os.path.exists(f"{PLATFORM_FILE_PATH}applications_order.json"):
                    with open(f"{PLATFORM_FILE_PATH}applications_order.json") as json_file:
                        app_order_dict = json.load(json_file)
                        if app_order_dict.get(tenant):
                            app_order = app_order_dict[tenant]
                        else:
                            app_order = []
                    json_file.close()
                else:
                    app_order = []
                if "remove_bell_icon" in t_config:
                    remove_bell_icon = json.loads(t_config["remove_bell_icon"])

                if "limit_notification" in t_config:
                    limit_notification = t_config["limit_notification"]

        show_dashboard = "false"
        show_planner = "false"
        tenant_db = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_db = json.load(json_file)
                json_file.close()

        if tenant_db.get(tenant):
            if tenant_db[tenant].get("show_dashboard"):
                show_dashboard = tenant_db[tenant].get("show_dashboard")

            if tenant_db[tenant].get("show_planner"):
                show_planner = tenant_db[tenant].get("show_planner")

        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()

        dashboard_display_config = {"show_dashboard": show_dashboard}
        if show_dashboard == "true" and app_db_mapping.get(f"{tenant}_dashboard"):
            dashboard_db_conn = app_db_mapping[f"{tenant}_dashboard"]

            db_type = ""
            user_db_engine, db_type = db_engine_extractor(dashboard_db_conn)

            dashboard_config = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "system_application_master",
                        "Columns": ["display_config"],
                    },
                    "condition": [
                        {
                            "column_name": "app_name",
                            "condition": "Equal to",
                            "input_value": "dashboard",
                            "and_or": "",
                        }
                    ],
                },
                engine2=user_db_engine,
                engine_override=True,
                db_type=db_type,
            ).display_config

            if dashboard_config.iloc[0]:
                dashboard_display_config.update(json.loads(dashboard_config.iloc[0]))

        planner_display_config = {"show_planner": show_planner}
        if show_planner == "true" and app_db_mapping.get(f"{tenant}_planner"):
            planner_db_conn = app_db_mapping[f"{tenant}_planner"]

            db_type = ""
            user_db_engine, db_type = db_engine_extractor(planner_db_conn)

            planner_config = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "system_application_master",
                        "Columns": ["display_config"],
                    },
                    "condition": [
                        {
                            "column_name": "app_name",
                            "condition": "Equal to",
                            "input_value": "planner",
                            "and_or": "",
                        }
                    ],
                },
                engine2=user_db_engine,
                engine_override=True,
                db_type=db_type,
            ).display_config

            if planner_config.iloc[0]:
                planner_display_config.update(json.loads(planner_config.iloc[0]))

        return {
            "applications": application_list,
            "applications_order": app_order,
            "is_user_superuser": is_user_superuser,
            "is_user_dev": is_user_dev,
            "dev_applications": dev_application_list,
            "system_dev_mode": dev_mode,
            "allow_user_forum": allow_user_forum,
            "allow_user_planner": allow_user_planner,
            "developer_mode": developer_mode,
            "allow_user_profile": allow_user_profile,
            "block_custom_homepage": block_custom_homepage,
            "block_add_navpoint": block_add_navpoint,
            "block_remove_navpoint": block_remove_navpoint,
            "tenant": tenant,
            "allow_users_to_config_smtp": allow_users_to_config_smtp,
            "remove_bell_icon": remove_bell_icon,
            "limit_notification": limit_notification,
            "dashboard_display_config": dashboard_display_config,
            "planner_display_config": planner_display_config,
        }


def current_application(request):
    path_info = resolve(request.path_info)
    apps = path_info.app_names
    if apps:
        if apps[0] != "users":
            return {}
    else:
        return {}
    instance = get_current_tenant()
    tenant = instance.name
    app_code = None
    url_string = request.path
    max_alert = 100
    allow_user_mode_smtp = False
    if (
        not any(
            url_match in url_string
            for url_match in [
                "/users/selectApplication/",
                "/users/dashboard/",
                "/users/selectDashboard/",
                "/users/alertsSetup/",
                "/users/adminPanel/",
                "/users/customizeTheme/",
                "/users/planner/",
                "/users/plannerAPI/",
                "/users/forum/",
                "/users/profile/",
                "/users/changeprofilename/",
                "/users/ajax/profilephoto_upload/",
                "/users/ajax/coverphoto_upload/",
                "/accounts/login/",
                "/accounts/logout/",
                "/users/plannerAPI/",
                "forum",
                "/applicationlogin/",
            ]
        )
        and "create_new/dev/application" not in url_string.lower()
        and not url_string.startswith("/account")
        and not url_string.startswith("/static")
    ):
        f_occ = url_string.find("/", url_string.find("/") + 1)
        s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
        t_occ = url_string.find("/", url_string.find("/") + s_occ + 1)
        app_code2 = url_string[f_occ + 1 : s_occ]
        current_dev_mode = url_string[s_occ + 1 : t_occ]
        current_access_mode = "User"
        if current_dev_mode in ["Build", "Edit"]:
            app_code = "Dev"
            current_access_mode = current_dev_mode
        else:
            app_code = app_code2

        if app_code == "Dev":
            if current_dev_mode == "Edit":
                edit_app_code = app_code2
                build_app_code = "Not Selected"
                build_process_type = "Not Selected"
            elif current_dev_mode == "Build":
                build_app_code = app_code2
                build_process_type = "Final"
                edit_app_code = "Not Selected"
            else:
                build_process_type = "Not Selected"
                build_app_code = "Not Selected"
                edit_app_code = "Not Selected"
            app_selected = "false"
            selected_any_app = "true"
        else:
            build_app_code = "Not Selected"
            build_process_type = "Not Selected"
            edit_app_code = "Not Selected"
            current_dev_mode = "Not Selected"
            app_selected = "true"
            selected_any_app = "true"

        if current_access_mode == "User":
            user_in_groups = list(request.user.groups.values_list("name", flat=True))
            if user_in_groups:
                conditions_list = [
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": app_code2,
                        "and_or": "",
                        "constraintName": "app",
                        "ruleSet": "app",
                    }
                ]
                for group in user_in_groups:
                    conditions_list.append(
                        {
                            "column_name": "group_assigned",
                            "condition": "Contains",
                            "input_value": f'"{group}"',
                            "and_or": "",
                            "constraintName": "group",
                            "ruleSet": group,
                        }
                    )
                developer_saved_groups = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "smtp_configuration",
                            "Agg_Type": "Count(server_name)",
                            "Columns": [],
                        },
                        "condition": conditions_list,
                    },
                )
                if not developer_saved_groups.empty:
                    if developer_saved_groups.iloc[0, 0]:
                        allow_user_mode_smtp = True
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
    elif any(url_match in url_string for url_match in ["/users/selectDashboard/", "/users/dashboard/"]):

        app_code2 = "dashboard"
        build_app_code = "Not Selected"
        build_process_type = "Not Selected"
        edit_app_code = "Not Selected"
        current_dev_mode = "Not Selected"
        app_selected = "false"
        selected_any_app = "false"
        current_access_mode = ""

    elif any(url_match in url_string for url_match in ["/users/planner/"]):
        app_code2 = "planner"
        build_app_code = "Not Selected"
        build_process_type = "Not Selected"
        edit_app_code = "Not Selected"
        current_dev_mode = "Not Selected"
        app_selected = "false"
        selected_any_app = "false"
        current_access_mode = ""

    else:
        app_code2 = ""
        build_app_code = "Not Selected"
        build_process_type = "Not Selected"
        edit_app_code = "Not Selected"
        current_dev_mode = "Not Selected"
        app_selected = "false"
        selected_any_app = "false"
        current_access_mode = ""
    data1 = {}
    if os.path.exists(f"{PLATFORM_DATA_PATH}icons.json"):
        with open(f"{PLATFORM_DATA_PATH}icons.json") as json_file:
            icons_data = json.load(json_file)
            json_file.close()
    else:
        icons_data = {}

    icons_without_category = []
    for key in icons_data:
        icons_without_category += icons_data[key]
    data1["icons_data"] = icons_data
    data1["icons_without_category"] = icons_without_category
    if (
        app_code2 == ""
        or not os.path.exists(
            os.getcwd()
            + f"/kore_investment/templates/user_defined_template/{tenant}/{app_code2}/theme/Global"
        )
        or not os.path.isfile(
            f"kore_investment/templates/user_defined_template/{tenant}/{app_code2}/theme/Global/base_all.html"
        )
    ):
        extend_template = "base_all.html"
    else:
        extend_template = f"user_defined_template/{tenant}/{app_code2}/theme/Global/base_all.html"
    return {
        "max_alert": max_alert,
        "application_selected": app_selected,
        "current_application_code": app_code,
        "current_dev_mode": current_dev_mode,
        "edit_app_code": edit_app_code,
        "build_process_type": build_process_type,
        "build_app_code": build_app_code,
        "selected_any_app": selected_any_app,
        "current_app_code": app_code2,
        "current_access_mode": current_access_mode,
        "extend_template": extend_template,
        "data1": data1,
        "allow_user_mode_smtp": allow_user_mode_smtp,
    }
