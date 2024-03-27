import ast
import json
import pickle

from django.contrib.auth import get_user_model
import rules

from config.settings.base import redis_instance
from kore_investment.users.computations.db_centralised_function import (
    current_app_db_extractor,
    read_data_func,
)

User = get_user_model()


# Predicates


def has_category_access(request, category_code):
    user = request.user
    if user.is_superuser:
        return True
    schema = user.instance.name
    appCode, db_connection_name = current_app_db_extractor(request)
    usergroup = user.groups.values_list("name", flat=True)
    usergroup_list = list(usergroup)

    placeholders = ", ".join("'" + i + "'" for i in usergroup_list)
    if not placeholders.startswith("("):
        placeholders = "(" + placeholders
    if not placeholders.endswith(")"):
        placeholders = placeholders + ")"
    if usergroup_list != []:

        user_perm = read_data_func(
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
                        "input_value": placeholders,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": appCode,
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
            schema=schema,
        )
    else:
        return False
    # Extract user group permissions
    user_perm = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "UserPermission_Master",
                "Columns": ["permission_level", "permission_name"],
            },
            "condition": [
                {"column_name": "usergroup", "condition": "IN", "input_value": placeholders, "and_or": "AND"},
                {
                    "column_name": "app_code",
                    "condition": "Equal to",
                    "input_value": appCode,
                    "and_or": "",
                },
            ],
        },
        schema=schema,
    )
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
    group_code_df = user_perm = read_data_func(
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


@rules.predicate
def has_process_access(user, process_code):
    if isinstance(process_code, dict):
        appCode = process_code["app_code"]
        process_code = process_code["process_code"]
    else:
        appCode = ""
    if user.is_superuser:
        return True
    user_name = str(user)
    schema = user.instance.name
    if appCode == "":
        if redis_instance.exists(user_name + schema) == 1:
            user_info = pickle.loads(redis_instance.get(user_name + schema))
            if user_info.get("current_application_code"):
                appCode = user_info.get("current_application_code")
                if appCode == "Dev":
                    if user_info.get("current_developer_mode"):
                        current_dev_mode = user_info.get("current_developer_mode")
                        if current_dev_mode == "Edit":
                            if user_info.get("edit_app_code"):
                                appCode = user_info.get("edit_app_code")
                        elif current_dev_mode == "Build":
                            if user_info.get("build_app_code"):
                                appCode = user_info.get("build_app_code")
    usergroup = user.groups.values_list("name", flat=True)
    usergroup_list = list(usergroup)
    placeholders = ", ".join("'" + i + "'" for i in usergroup_list)
    if not placeholders.startswith("("):
        placeholders = "(" + placeholders
    if not placeholders.endswith(")"):
        placeholders = placeholders + ")"
    if usergroup_list != []:
        user_perm = read_data_func(
            "",
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
                        "input_value": placeholders,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": appCode,
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
            schema=schema,
        )
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


@rules.predicate
def has_process_group_access(user, process_group_code):
    if isinstance(process_group_code, dict):
        appCode = process_group_code["app_code"]
        process_group_code = process_group_code["process_group_code"]
    else:
        appCode = ""
    if user.is_superuser:
        return True
    user_name = str(user)
    schema = user.instance.name
    if redis_instance.exists(user_name + schema) == 1:
        user_info = pickle.loads(redis_instance.get(user_name + schema))
        if user_info.get("current_application_code"):
            appCode = user_info.get("current_application_code")
            if appCode == "Dev":
                if user_info.get("current_developer_mode"):
                    current_dev_mode = user_info.get("current_developer_mode")
                    if current_dev_mode == "Edit":
                        if user_info.get("edit_app_code"):
                            appCode = user_info.get("edit_app_code")
                    elif current_dev_mode == "Build":
                        if user_info.get("build_app_code"):
                            appCode = user_info.get("build_app_code")
    usergroup = user.groups.values_list("name", flat=True)
    usergroup_list = list(usergroup)
    placeholders = ", ".join("'" + i + "'" for i in usergroup_list)
    # Extract user group permissions
    if not placeholders.startswith("("):
        placeholders = "(" + placeholders
    if not placeholders.endswith(")"):
        placeholders = placeholders + ")"

    if usergroup_list != []:
        user_perm = read_data_func(
            "",
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
                        "input_value": placeholders,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": appCode,
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
            schema=schema,
        )
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


def has_data_hierarchy_access(request, raw_data):
    user = request.user
    if user.is_superuser:
        return [True for i in range(len(raw_data))]
    schema = user.instance.name
    usergroup_list = list(user.groups.values_list("name", flat=True))
    if usergroup_list == []:
        placeholders = ""
    else:
        placeholders = ", ".join("'" + i + "'" for i in usergroup_list)
    # Extract user group permissions
    if not placeholders.startswith("("):
        placeholders = "(" + placeholders
    if not placeholders.endswith(")"):
        placeholders = placeholders + ")"

    user_perm = read_data_func(
        request,
        config_dict={
            "inputs": {
                "Data_source": "Database",
                "Table": "UserPermission_Master",
                "Columns": ["permission_level", "permission_name"],
            },
            "condition": [
                {"column_name": "usergroup", "condition": "IN", "input_value": placeholders, "and_or": "AND"},
                {
                    "column_name": "permission_type",
                    "condition": "Equal to",
                    "input_value": "Data hierarchy",
                    "and_or": "",
                },
            ],
        },
        schema=schema,
    )
    user_perm_list = user_perm["permission_name"].to_list()
    data_access_list = []
    for i in user_perm_list:
        ll_1 = ast.literal_eval(i)
        data_access_list = data_access_list + ll_1

    hierarchy_mapping = eval(raw_data["Hierarchy_dict"].tolist()[0])
    hierarchy_groups = []
    for key in hierarchy_mapping:
        hierarchy_groups.append(key)

    if hierarchy_groups == []:
        placeholders1 = ""
    else:
        placeholders1 = ", ".join("'" + i + "'" for i in hierarchy_groups)
    if not placeholders1.startswith("("):
        placeholders1 = "(" + placeholders1
    if not placeholders1.endswith(")"):
        placeholders1 = placeholders1 + ")"
    Hierarchy_df = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Hierarchy_table",
                "Columns": ["hierarchy_group", "hierarchy_name", "hierarchy_parent_name"],
            },
            "condition": [
                {
                    "column_name": "hierarchy_group",
                    "condition": "IN",
                    "input_value": placeholders1,
                    "and_or": "",
                }
            ],
        },
        schema=schema,
    )
    hierarchy_dict = {}
    for data_access in data_access_list:
        ll1 = data_access.split("__")[0]
        ll2 = data_access.split("__")[1]
        access_list = []
        loop_list = []
        access_list.append(ll2)
        loop_list.append(ll2)
        hierarchy_dict.setdefault(ll1, [])
        while (
            len(Hierarchy_df[Hierarchy_df["hierarchy_parent_name"].isin(loop_list)].hierarchy_name.to_list())
            > 0
        ):
            for hierarchy_name in Hierarchy_df[
                Hierarchy_df["hierarchy_parent_name"].isin(loop_list)
            ].hierarchy_name.to_list():
                access_list.append(hierarchy_name)
            loop_list = Hierarchy_df[
                Hierarchy_df["hierarchy_parent_name"].isin(loop_list)
            ].hierarchy_name.to_list()
        [hierarchy_dict.setdefault(ll1, []).append(item) for item in access_list]
    results = []

    for key in hierarchy_mapping:
        f_cols = hierarchy_mapping[key]
        f_string = ""
        for idx, col in enumerate(f_cols):
            f_string += f"(raw_data['{col}'].isin(hierarchy_dict[key]))"
            if len(f_cols) - 1 != idx:
                f_string += " & "
        result = eval(f_string)
        result = result.tolist()
        if len(results) > 0:
            results = [results[res] | result[res] for res in range(len(results))]
        else:
            results = result
    return results


def data_hierarchy_access_list(request, hierarchy_mapping):
    user = request.user
    schema = user.instance.name
    usergroup_list = list(user.groups.values_list("name", flat=True))
    hierarchy_dict = {}
    if usergroup_list:
        placeholders = ", ".join("'" + i + "'" for i in usergroup_list)
        # Extract user group permissions
        if not placeholders.startswith("("):
            placeholders = "(" + placeholders
        if not placeholders.endswith(")"):
            placeholders = placeholders + ")"
        user_perm = read_data_func(
            request,
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "UserPermission_Master",
                    "Columns": ["permission_level", "permission_name"],
                },
                "condition": [
                    {
                        "column_name": "usergroup",
                        "condition": "IN",
                        "input_value": placeholders,
                        "and_or": "AND",
                    },
                    {
                        "column_name": "permission_type",
                        "condition": "Equal to",
                        "input_value": "Data hierarchy",
                        "and_or": "",
                    },
                ],
            },
            schema=schema,
        )
        user_perm_list = user_perm["permission_name"].to_list()
        data_access_list = []
        for i in user_perm_list:
            ll_1 = ast.literal_eval(i)
            data_access_list = data_access_list + ll_1

        hierarchy_groups = []
        for key in hierarchy_mapping:
            hierarchy_groups.append(key)

        if hierarchy_groups == []:
            placeholders1 = ""
        else:
            placeholders1 = ", ".join("'" + i + "'" for i in hierarchy_groups)
        if not placeholders1.startswith("("):
            placeholders1 = "(" + placeholders1
        if not placeholders1.endswith(")"):
            placeholders1 = placeholders1 + ")"
        Hierarchy_df = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Hierarchy_table",
                    "Columns": ["hierarchy_group", "hierarchy_name", "hierarchy_parent_name"],
                },
                "condition": [
                    {
                        "column_name": "hierarchy_group",
                        "condition": "IN",
                        "input_value": placeholders1,
                        "and_or": "",
                    }
                ],
            },
            schema=schema,
        )
        for data_access in data_access_list:
            ll1 = data_access.split("__")[0]
            ll2 = data_access.split("__")[1]
            access_list = []
            loop_list = []
            access_list.append(ll2)
            loop_list.append(ll2)

            while (
                len(
                    Hierarchy_df[
                        Hierarchy_df["hierarchy_parent_name"].isin(loop_list)
                    ].hierarchy_name.to_list()
                )
                > 0
            ):
                for hierarchy_name in Hierarchy_df[
                    Hierarchy_df["hierarchy_parent_name"].isin(loop_list)
                ].hierarchy_name.to_list():
                    access_list.append(hierarchy_name)
                loop_list = Hierarchy_df[
                    Hierarchy_df["hierarchy_parent_name"].isin(loop_list)
                ].hierarchy_name.to_list()
            [hierarchy_dict.setdefault(ll1, []).append(item) for item in access_list]
    else:
        pass
    return hierarchy_dict


@rules.predicate
def has_application_admin_access(user, app):
    if user.is_superuser:
        return True
    if app == "Dev":
        return True
    usergroup = user.groups.values_list("name", flat=True)
    schema = user.instance.name
    usergroup_list = list(usergroup)
    cond = []
    cond.append(
        {
            "column_name": "app_code",
            "condition": "Equal to",
            "input_value": app,
            "and_or": "AND",
        }
    )
    for i in usergroup_list:
        dic = {
            "column_name": "usergroup",
            "condition": "Equal to",
            "input_value": i,
            "and_or": "OR",
        }
        cond.append(dic)
    cond[len(cond) - 1]["and_or"] = ""
    data = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "UserPermission_Master",
                "Columns": ["application", "permission_level"],
            },
            "condition": cond,
        },
        schema=schema,
    )
    l0 = 2
    l1 = 2
    l2 = 2
    l3 = 2
    if not data.empty:
        data = data.to_dict("records")
        for i in data:
            if i["application"] not in [None]:
                application = json.loads(i["application"])
                if app + "_admin" in list(application.keys()) and i["permission_level"] != "Data hierarchy":
                    if i["permission_level"] == "Administrative access":
                        if int(application[app + "_admin"]) == 1:
                            l3 = 1
                        else:
                            l3 = 0
                    elif int(i["permission_level"]) == 2:
                        if int(application[app + "_admin"]) == 1:
                            l2 = 1
                        else:
                            l2 = 0
                    elif int(i["permission_level"]) == 1:
                        if int(application[app + "_admin"]) == 1:
                            l1 = 1
                        else:
                            l1 = 0
                    elif int(i["permission_level"]) == 0:
                        if int(application[app + "_admin"]) == 1:
                            l0 = 1
                        else:
                            l0 = 0
    if l3 == 1:
        return True
    elif l3 == 0:
        return False
    if l0 == 1:
        return True
    elif l0 == 0:
        return False
    elif l1 == 1:
        return True
    elif l1 == 0:
        return False
    elif l2 == 1:
        return True
    elif l2 == 0:
        return False
    else:
        return False


@rules.predicate
def has_process_admin_access(user):
    return True


@rules.predicate
def has_data_admin_access(user):
    return True


@rules.predicate
def is_boss(user):
    return user.is_superuser


# Rules


rules.add_rule("has_process_access", has_process_access | is_boss)
rules.add_rule("has_process_group_access", has_process_group_access | is_boss)
rules.add_rule("has_category_access", has_category_access)
rules.add_rule("has_data_hierarchy_access", has_data_hierarchy_access)
rules.add_rule("has_application_admin_access", has_application_admin_access | is_boss)
rules.add_rule("has_process_admin_access", has_process_admin_access | is_boss)
rules.add_rule("has_data_admin_access", has_process_admin_access | is_boss)
# Permissions

rules.add_perm("users.has_process_access", has_process_access | is_boss)
rules.add_perm("users.has_process_group_access", has_process_group_access | is_boss)
rules.add_perm("users.has_category_access", has_category_access)
rules.add_perm("users.has_data_hierarchy_access", has_data_hierarchy_access)
rules.add_perm("users.has_application_admin_access", has_application_admin_access | is_boss)
rules.add_perm("users.has_process_admin_access", has_process_admin_access | is_boss)
rules.add_perm("users.has_data_admin_access", has_process_admin_access | is_boss)
