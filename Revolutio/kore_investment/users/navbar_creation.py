import ast
from datetime import datetime
import json
import logging

import pandas as pd

from kore_investment.users.computations.db_centralised_function import (
    current_app_db_extractor,
    data_handling,
    postgres_push,
    read_data_func,
    update_data_func,
)
from kore_investment.users.global_functions import creatingListOfDictAsFinalResponseForDefaultSideNavBar


def navbar_update(
    request,
    userName,
    app_code,
    user,
    groupname,
    tenant,
    instance_id,
    final_items_list={},
    build_process_type="Not Selected",
    action="append",
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
    if app_code == "":
        app_code, db_connection_name = current_app_db_extractor(request, tenant=tenant)
    else:
        pass
    try:
        user_groups = (
            (
                read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user_groups",
                            "Columns": [
                                "group_id",
                            ],
                        },
                        "condition": [
                            {
                                "column_name": "user_id",
                                "condition": "Equal to",
                                "input_value": f"{user['id']}",
                                "and_or": "",
                            }
                        ],
                    },
                )
            )
            .group_id.unique()
            .tolist()
        )
        if len(user_groups) == 1:
            condition = "Equal to"
            user_groups = f"{user_groups[0]}"
        else:
            condition = "IN"
            user_groups = f"{tuple(user_groups)}"
        if len(user_groups) > 0 and user_groups != "()":
            user_group_names = read_data_func(
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
                            "condition": condition,
                            "input_value": user_groups,
                            "and_or": "",
                        }
                    ],
                },
            ).name.tolist()
        else:
            user_group_names = []
        if final_items_list != {}:
            if str(final_items_list["level"]) == "0":
                process_codes_requested = final_items_list["permissions"]
            else:
                if str(final_items_list["level"]) == "1":
                    sub_process_codes = final_items_list["permissions"]
                else:
                    sub_process_codes = []
                    for j in final_items_list["permissions"]:
                        sub_process_code = (j.split("__"))[0]
                        if sub_process_code not in sub_process_codes:
                            sub_process_codes.append(sub_process_code)
                if len(sub_process_codes) == 1:
                    condition = "Equal to"
                    sub_process_code = sub_process_codes[0]
                    if isinstance(sub_process_code, list):
                        sub_process_code = sub_process_code[0]
                else:
                    condition = "IN"
                    sub_process_code = f"{tuple(sub_process_codes)}"
                process_codes_requested = (
                    (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "NavigationSideBar",
                                    "Columns": ["item_group_code"],
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "Equal to",
                                        "input_value": "1",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_code",
                                        "condition": condition,
                                        "input_value": sub_process_code,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                    )
                    .item_group_code.unique()
                    .tolist()
                )
        else:
            process_codes_requested = []
        if groupname != "":
            if isinstance(groupname, (list, tuple)):
                user_groups = groupname
            else:
                user_groups = [groupname]
            if len(user_groups) == 1:
                condition = "Equal to"
                user_group = user_groups[0]
            else:
                condition = "IN"
                user_group = f"{tuple(user_groups)}"
            user_permission_master = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "UserPermission_Master",
                        "Columns": ["permission_level", "application_dev", "app_code"],
                    },
                    "condition": [
                        {
                            "column_name": "usergroup",
                            "condition": condition,
                            "input_value": user_group,
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
            user_permission_master = []
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
            "process_icon",
            "subprocess_icon",
            "created_by",
            "created_date",
            "share_with_group",
        ]
        if build_process_type == "draft":
            configDF = read_data_func(
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
                            "input_value": instance_id,
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
            configDF = read_data_func(
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
                            "input_value": instance_id,
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
        existing_config = False
        if action != "regenerate":
            if len(configDF) > 0:
                original_list = json.loads(configDF.navbar_list.iloc[0])
                if len(original_list) > 0:
                    existing_config = True
                else:
                    existing_config = False
                    original_list = []
            else:
                existing_config = False
                original_list = []
        else:
            existing_config = False
            original_list = []
        if len(user_permission_master) > 0:
            dev_access_data = user_permission_master.loc[
                user_permission_master["permission_level"] == "Administrative access"
            ]
        else:
            dev_access_data = []
        if len(dev_access_data) > 0 or user["is_superuser"]:
            if user["is_superuser"]:
                dev_access = 1
            else:
                dev_access = dev_access_data.application_dev.iloc[0]
            if dev_access == 1:
                config_params = read_data_func(
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
                application_mode = config_params.loc[
                    config_params["parameter"] == "Application mode", "value"
                ].iloc[0]
                dev_mode = config_params.loc[config_params["parameter"] == "Developer mode", "value"].iloc[0]
                if dev_mode == "Edit + Build":
                    current_dev_mode = "Build"
                else:
                    current_dev_mode = "Edit"
            else:
                current_dev_mode = "Not Selected"
        else:
            if build_process_type != "draft":
                current_dev_mode = "Not Selected"
            else:
                current_dev_mode = "Build"

        if app_code:
            if existing_config:
                del_list = []
                for l in range(0, len(original_list)):
                    if original_list[l]["level0Code"] in process_codes_requested:
                        del_list.append(l)
                for m in del_list:
                    del original_list[m]
            if action == "delete" and final_items_list["level"] == "0":
                sql_query = ""
                sql_query2 = ""
            else:
                if current_dev_mode == "Build" and build_process_type == "draft":
                    user_groups = "|".join(user_groups)
                    if build_process_type == "draft":
                        process_data = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "DraftProcess",
                                    "Columns": ["item_code", "created_by", "share_with_group"],
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "Equal to",
                                        "input_value": "0",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "application",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                        process_data.fillna("", inplace=True)
                        process_codes_user = process_data[
                            process_data["created_by"] == userName
                        ].item_code.tolist()
                        process_codes_group = process_data[
                            process_data["share_with_group"].str.contains(user_groups)
                        ].item_code.tolist()
                        process_codes = process_codes_user + process_codes_group
                        process_codes = list(set(process_codes))
                        p_string = "("
                        for ind, i in enumerate(process_codes):
                            p_string += "'" + i + "'"
                            if (len(process_codes) - 1) != ind:
                                p_string += ","
                            else:
                                p_string += ")"
                        if len(process_codes) == 0:
                            p_string += "'')"
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

                        sub_process_data2 = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "DraftProcess",
                                    "Columns": colAll,
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "Equal to",
                                        "input_value": "0",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_code",
                                        "condition": "NOT IN",
                                        "input_value": p_string,
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "application",
                                        "condition": "Equal to",
                                        "input_value": app_code,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                        if len(sub_process_data2) > 0:
                            sub_process_data2.fillna("", inplace=True)
                            sub_process_codes_user = sub_process_data2[
                                sub_process_data2["created_by"] == userName
                            ].item_code.tolist()
                            sub_process_codes_group = sub_process_data2[
                                sub_process_data2["share_with_group"].str.contains(user_groups)
                            ].item_code.tolist()
                            sub_process_codes_df = sub_process_codes_user + sub_process_codes_group
                            sub_process_data2 = sub_process_data2[
                                sub_process_data2["Item_code"].isin(sub_process_codes_df)
                            ]
                            p_string = p_string.replace(")", ",")
                            for ind, i in enumerate(sub_process_data2.item_code.tolist()):
                                p_string += "'" + i + "'"
                                if (len(sub_process_data2.item_code.tolist()) - 1) != ind:
                                    p_string += ","
                                else:
                                    p_string += ")"
                            process_codes = list(set(sub_process_data2["item_group_code"].tolist()))
                            p_string_add = "("
                            for ind, i in enumerate(process_codes):
                                p_string_add += "'" + i + "'"
                                if (len(process_codes) - 1) != ind:
                                    p_string_add += ","
                                else:
                                    p_string_add += ")"
                            if len(process_codes) == 0:
                                p_string_add += "'')"

                            sql_query2 = {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "NavigationSideBar",
                                    "Columns": colAll,
                                },
                                "condition": [
                                    {
                                        "column_name": "item_level",
                                        "condition": "Equal to",
                                        "input_value": "0",
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_code",
                                        "condition": "IN",
                                        "input_value": p_string_add,
                                        "and_or": "",
                                    },
                                ],
                            }
                        else:
                            sql_query2 = ""

                        sql_query = {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "DraftProcess",
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
                                    "navbar_order",
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
                    sql_navbar_order = sql_query_app["navbar_order"]
                    if not sql_query_app.empty:
                        if sql_query_app.process_group_codes.iloc[0]:
                            process_codes = json.loads(sql_query_app.process_group_codes.iloc[0])
                            if len(process_codes_requested) > 0:
                                process_codes = [i for i in process_codes if i in process_codes_requested]
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
                            sql_query2 = ""
                        else:
                            sql_query = ""
                            sql_query2 = ""
                    else:
                        sql_query = ""
                        sql_query2 = ""
        else:
            sql_query = ""
            sql_query2 = ""

        if sql_query != "":
            rawData = read_data_func(request, sql_query)
        else:
            rawData = pd.DataFrame(columns=colAll)
        if sql_query2 != "":
            rawData = pd.concat([rawData, read_data_func(request, sql_query2)], ignore_index=True)

        if user_group_names:
            user_permission_master = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "UserPermission_Master",
                        "Columns": ["permission_level", "permission_name"],
                    },
                    "condition": [
                        {
                            "column_name": "usergroup",
                            "condition": "IN",
                            "input_value": str(tuple(user_group_names)).replace(",)", ")"),
                            "and_or": "and",
                        },
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "permission_type",
                            "condition": "Equal to",
                            "input_value": "Navbar",
                            "and_or": "",
                        },
                    ],
                },
            )
        else:
            user_permission_master = pd.DataFrame(columns=["permission_level", "permission_name"])
        if action == "delete" and final_items_list["level"] == "0":
            finalList1 = original_list
        else:
            groupByItemGroupName = rawData.groupby(["item_group_code"])
            listOfDfAfterGrouping = []
            userSpecificgroupCodeList = []
            for x in groupByItemGroupName.groups:
                access_check = has_process_group_access(
                    request,
                    user,
                    {"process_group_code": x, "app_code": app_code, "user_group_names": user_group_names},
                    user_permission_master,
                    tenant,
                )
                if access_check:
                    userSpecificgroupCodeList.append(x)
                    listOfDfAfterGrouping.append(groupByItemGroupName.get_group(x))
            df2 = pd.DataFrame(columns=rawData.columns)
            for icode in rawData["item_code"]:
                if has_process_access(
                    request,
                    user,
                    {"process_code": icode, "app_code": app_code, "user_group_names": user_group_names},
                    user_permission_master,
                    tenant,
                ):
                    filteredProcessCodeDf = rawData.loc[rawData["item_code"] == icode]
                    rows = filteredProcessCodeDf[
                        ~filteredProcessCodeDf["item_group_code"].isin(userSpecificgroupCodeList)
                    ]
                    if not rows.empty:
                        df2 = pd.concat([df2, rows], ignore_index=True)
                else:
                    pass
            groupByItemGroupName1 = df2.groupby(["item_group_code"])
            for x in groupByItemGroupName1.groups:
                listOfDfAfterGrouping.append(groupByItemGroupName1.get_group(x))
            try:
                if len(sql_navbar_order) != 0:
                    navbar_order = sql_navbar_order.tolist()
                else:
                    navbar_order = []
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                navbar_order = sql_navbar_order.tolist()
            if len(navbar_order) == 0:
                rawData.drop(
                    columns=["created_by", "created_date", "app_allocation_status", "share_with_group"],
                    inplace=True,
                )
                listOfDfAfterGrouping.drop(
                    columns=["created_by", "created_date", "app_allocation_status", "share_with_group"],
                    inplace=True,
                )
            finalList, config_navbar = creatingListOfDictAsFinalResponseForDefaultSideNavBar(
                listOfDfAfterGrouping, request
            )
            for i in original_list:
                if i["level0Code"]:
                    pname = i["level0Code"]
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
                                "input_value": pname,
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
                i["level0IconClass"] = icon

                for j in i["childrenOfLevel0"]:
                    if j["item_name"]:
                        spname = j["item_name"]
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
                                        "input_value": pname,
                                        "and_or": "AND",
                                    },
                                    {
                                        "column_name": "item_name",
                                        "condition": "Equal to",
                                        "input_value": spname,
                                        "and_or": "",
                                    },
                                ],
                            },
                        )
                    if len(subprocess_icon) > 0:
                        subprocess_icon = subprocess_icon.loc[0, "subprocess_icon"]
                    else:
                        subprocess_icon = ""
                    if subprocess_icon:
                        subprocess_icon = subprocess_icon
                    else:
                        subprocess_icon = "fa fa-edit"
                    j["subprocess_icon"] = subprocess_icon
            finalList = original_list + finalList

            ####################### delete code ##############################

            finalList1 = finalList
            if navbar_order:
                if navbar_order[0]:
                    finalList1 = []
                    navbar_order = json.loads(navbar_order[0])
                    pr_count = 0
                    for pr, config in navbar_order.items():
                        pr_count += 1
                        for nav_pr_config in finalList:
                            if nav_pr_config["level0Code"] == pr:
                                nav_sub_config = []
                                process_config = nav_pr_config.copy()
                                nav_subpr_config = nav_pr_config["childrenOfLevel0"]
                                for subpr_order in range(1, len(config[str(pr_count)].keys()) + 1):
                                    subpr_name = config[str(pr_count)][str(subpr_order)]
                                    for subpr in nav_subpr_config:
                                        if subpr["item_code"] == subpr_name:
                                            nav_sub_config.append(subpr)
                                            break
                                        else:
                                            continue
                                process_config["childrenOfLevel0"] = nav_sub_config
                                finalList1.append(process_config)
                                break
                            else:
                                continue
        if len(finalList1) > 0:
            count = 0
            if action == "delete" and final_items_list["level"] == "0":
                pass
            else:
                for i in finalList1:
                    count1 = 0
                    for k in i["childrenOfLevel0"]:
                        keys_i = list(k.keys())
                        if "created_by" in keys_i:
                            del k["created_by"]
                        if "created_date" in keys_i:
                            del k["created_date"]
                        if "app_allocation_status" in keys_i:
                            del k["app_allocation_status"]
                        if "share_with_group" in keys_i:
                            del k["share_with_group"]
                        dic = {}
                        dic["dictionary_item"] = {}
                        count2 = 0
                        for key, val in k["dictionary_item"].items():
                            if not user["is_superuser"]:
                                val1 = json.loads(val)
                                if has_category_access(
                                    request,
                                    user,
                                    (val1["code"] + "__" + val1["tab_type"] + "__" + str(val1["id"])),
                                    app_code,
                                    user_group_names,
                                    user_permission_master,
                                    tenant,
                                ):
                                    count2 = count2 + 1
                                    dic["dictionary_item"]["data-button" + str(count2)] = val
                        finalList1[count]["childrenOfLevel0"][count1]["dictionary_item"] = dic[
                            "dictionary_item"
                        ]
                        count1 = count1 + 1
                    count = count + 1
            if len(configDF) > 0:
                update_data_func(
                    request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user_navbar",
                            "Columns": [
                                {
                                    "column_name": "navbar_list",
                                    "input_value": json.dumps(finalList1),
                                    "separator": "",
                                }
                            ],
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
                                "input_value": instance_id,
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
                finalConfigDict = {
                    "user_name": userName,
                    "instance_id": instance_id,
                    "navbar_list": json.dumps(finalList1),
                    "build_process_type": build_process_type,
                    "app_code": app_code,
                    "created_by": request.user.username,
                    "modified_by": request.user.username,
                    "created_date": datetime.now(),
                    "modified_date": datetime.now(),
                }
                finalConfigDF = pd.DataFrame([finalConfigDict])
                data_handling(request, finalConfigDF, "user_navbar")

        noti_msg = f'Permissions/process details have been updated for user - {userName} <i class="fas fa-refresh refreshNavbarView" aria-hidden="true" data-new="new" data-toggle="tooltip" title="Click here to refresh view"></i>'

        data_df = pd.DataFrame(
            [
                {
                    "user_name": request.user.username,
                    "category": "system notification",
                    "status": "unread",
                    "notification_message": noti_msg,
                    "created_date": datetime.now(),
                    "instance_id": instance_id,
                }
            ]
        )
        postgres_push(
            data_df,
            "users_notification_management",
            schema=tenant,
            app_db_transaction=False,
        )

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
                        "and_or": "and",
                    },
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance_id,
                        "and_or": "",
                    },
                ],
            },
            schema=tenant,
        ).iloc[0]["id"]

        return True, userName, request.user.username, tenant, str(notification_id)

    except Exception as e:
        logging.warning(f"Following exception occurred while updating navbar - {e}")
        noti_msg = f"Permissions/process details update failed for user - {userName}."

        data_df = pd.DataFrame(
            [
                {
                    "user_name": request.user.username,
                    "category": "system notification",
                    "status": "unread",
                    "notification_message": noti_msg,
                    "created_date": datetime.now(),
                    "instance_id": instance_id,
                }
            ]
        )

        postgres_push(
            data_df,
            "users_notification_management",
            schema=tenant,
            app_db_transaction=False,
        )

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
                        "and_or": "and",
                    },
                    {
                        "column_name": "instance_id",
                        "condition": "Equal to",
                        "input_value": instance_id,
                        "and_or": "",
                    },
                ],
            },
            schema=tenant,
        ).iloc[0]["id"]

        return False, userName, request.user.username, tenant, str(notification_id)


def has_process_access(request, user, process_code, user_perm, schema):
    if isinstance(process_code, dict):
        usergroup_list = process_code["user_group_names"]
        process_code = process_code["process_code"]

    if user["is_superuser"]:
        return True

    if usergroup_list != []:
        pass
    else:
        return False
    # Extract user group permissions
    user_perm_level_1 = user_perm[user_perm["permission_level"] == "1"]

    user_perm_list_1 = user_perm_level_1["permission_name"].to_list()
    process_list = []
    for i in user_perm_list_1:
        ll_1 = ast.literal_eval(i)
        process_list = process_list + ll_1
    # Extract group level permissions basis level 1 permissions provided
    user_perm_level_2 = user_perm[user_perm["permission_level"] == "2"]
    user_perm_list_2 = user_perm_level_2["permission_name"].to_list()

    level_2_list = []
    for i in user_perm_list_2:

        ll_2 = ast.literal_eval(i)
        level_2_list = level_2_list + ll_2

    Level_2_process_list = [sub.split("_")[0] for sub in level_2_list]
    process_list = process_list + Level_2_process_list

    process_check = process_code

    return process_check in process_list


def has_process_group_access(request, user, process_group_code, user_perm, schema):
    if isinstance(process_group_code, dict):
        usergroup_list = process_group_code["user_group_names"]
        process_group_code = process_group_code["process_group_code"]
    if user["is_superuser"]:
        return True

    if usergroup_list != []:
        pass
    else:
        return False
    user_perm_level_0 = user_perm[user_perm["permission_level"] == "0"]

    user_perm_list_0 = user_perm_level_0["permission_name"].to_list()
    process_group_list = []
    for i in user_perm_list_0:
        ll_1 = ast.literal_eval(i)
        process_group_list = process_group_list + ll_1
    process_group_check = process_group_code
    return process_group_check in process_group_list


def has_category_access(request, user, category_code, appCode, usergroup_list, user_perm, schema):
    if user["is_superuser"]:
        return True
    if usergroup_list != []:
        pass
    else:
        return False

    user_perm_level_2 = user_perm[user_perm["permission_level"] == "2"]

    user_perm_list_2 = user_perm_level_2["permission_name"].to_list()
    category_list = []
    for i in user_perm_list_2:
        ll_1 = ast.literal_eval(i)
        category_list = category_list + ll_1
    user_perm_level_1 = user_perm[user_perm["permission_level"] == "1"]
    user_perm_list_1 = user_perm_level_1["permission_name"].to_list()
    process_list = []
    for i in user_perm_list_1:
        ll_1 = ast.literal_eval(i)
        process_list = process_list + ll_1

    user_perm_level_0 = user_perm[user_perm["permission_level"] == "0"]

    user_perm_list_0 = user_perm_level_0["permission_name"].to_list()
    process_group_list = []
    for i in user_perm_list_0:
        ll_1 = ast.literal_eval(i)
        process_group_list = process_group_list + ll_1
    category_check = category_code
    process_code = category_code.split("_")[0]
    group_code_df = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "NavigationSideBar",
                "Columns": ["item_group_code"],
            },
            "condition": [
                {
                    "column_name": "item_code",
                    "condition": "Equal to",
                    "input_value": process_code,
                    "and_or": "",
                }
            ],
        },
        schema=schema,
    )
    group_code = group_code_df["item_group_code"][0]

    return (
        (category_check in category_list)
        or (process_code in process_list)
        or (group_code in process_group_list)
    )
