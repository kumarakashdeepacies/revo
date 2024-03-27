import json
import os

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql

from config.settings.base import PLATFORM_FILE_PATH

current_central_db_engine = psycopg2.connect(
    dbname="Platform_DB",
    user="postgres_user",
    password="N5a5EqK2DJFUWbsZYVBqBF",
    host="postgres15",
    port="5432",
)

new_central_db_engine = psycopg2.connect(
    dbname="Platform_DB",
    user="postgres_user",
    password="N5a5EqK2DJFUWbsZYVBqBF",
    host="postgres15-new",
    port="5432",
)

admin_tables = [
    "user",
    "Profile",
    "auth_group",
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
    "user_navbar",
    "failed_login_alerts",
    "dashboard_config",
    "login_trail",
    "audit_trail",
    "notification_management",
]


def postgres_push(data_table, db_table_name, sql_engine):
    data_table.drop(columns=data_table.columns[data_table.isna().all()], inplace=True)
    column = sql.SQL(", ").join([sql.Identifier(field.lower()) for field in data_table.columns])

    # preparing value place holders
    val_place_holder = ["%s" for col in data_table.columns]
    sql_val = "("
    sql_val += ", ".join(val_place_holder)
    sql_val += ")"

    postgres_table_name = sql.Identifier(db_table_name)

    # writing sql query for postgres
    sql_query = sql.SQL("INSERT INTO {table} ({columnnames}) VALUES {sql_val}").format(
        table=postgres_table_name, columnnames=column, sql_val=sql.SQL(sql_val)
    )

    cursor = sql_engine.cursor()
    cursor.executemany(sql_query, data_table.to_numpy().tolist())
    sql_engine.commit()
    cursor.close()
    return True


tenant_data = []
if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
        tenant_data = list(json.load(json_file).keys())
        json_file.close()
else:
    pass
print("tenant_data------------------------------------------------------->")
print(tenant_data)

# Instance Data
sql_table_name = "users_instance"
sql_table_name = sql.Identifier(sql_table_name)
sql_query = sql.SQL("select id, name from {sql_table_name};").format(sql_table_name=sql_table_name)
cursor = new_central_db_engine.cursor()
cursor.execute(sql_query)
instance_records = cursor.fetchall()
cursor.close()
instance_data = pd.DataFrame(instance_records, columns=["id", "name"])
instance_data = instance_data.set_index("name").to_dict()["id"]
print("instance_data----------------------------------------------------------------->")
print(instance_data)

# User Migration
user_data = pd.DataFrame(
    columns=[
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "date_joined",
        "name",
        "last_password_update_date",
        "password_history",
        "tenant",
        "is_developer",
        "mfa_hash",
        "from_ldap",
        "department",
        "job_title",
        "contact_number",
        "location",
        "instance_id",
        "role",
    ]
)
user_profile_data = pd.DataFrame(
    columns=[
        "id",
        "first_name",
        "last_name",
        "job_title",
        "bio",
        "location",
        "profile_pic",
        "date_joined",
        "last_login",
        "username",
        "email",
        "is_superuser",
        "is_staff",
        "is_active",
        "user_id",
        "contact_number",
        "cover_photo",
        "facebook",
        "github",
        "linkedin",
        "twitter",
        "no_of_alert",
        "department",
        "tagged_user",
    ]
)
configuration_parameter_data = pd.DataFrame(columns=["id", "parameter", "value"])
userpermission_master_data = pd.DataFrame(
    columns=[
        "id",
        "usergroup",
        "permission_type",
        "permission_level",
        "permission_name",
        "application",
        "application_dev",
        "app_code",
        "app_name",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
        "level_button_access",
    ]
)
userpermission_interim_data = pd.DataFrame(
    columns=[
        "id",
        "usergroup",
        "permission_type",
        "permission_level",
        "permission_name",
        "permission_level1",
        "approval_status",
        "application",
        "application_dev",
        "app_code",
        "app_name",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
        "level_button_access",
    ]
)
user_approval_data = pd.DataFrame(
    columns=[
        "id",
        "username",
        "password",
        "email",
        "approval_status",
        "authentication_type",
        "action_requested",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
        "is_developer",
    ]
)
allocated_licences_data = pd.DataFrame(columns=["id", "username", "authentication_type"])
auth_group_data = pd.DataFrame(columns=["id", "name"])
group_details_data = pd.DataFrame(
    columns=["id", "name", "created_by", "created_date", "modified_by", "modified_date"]
)
user_groups_data = pd.DataFrame(columns=["user_id", "group_id"])
usergroup_approval_data = pd.DataFrame(
    columns=[
        "id",
        "user_id",
        "group_id",
        "approval_status",
        "user_name",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
    ]
)
user_navbar_data = pd.DataFrame(
    columns=[
        "id",
        "user_name",
        "app_code",
        "tenant",
        "navbar_list",
        "build_process_type",
        "created_by",
        "created_date",
        "modified_by",
        "modified_date",
    ]
)
dashboard_config_data = pd.DataFrame(
    columns=[
        "id",
        "app_code",
        "application_name",
        "tenant",
        "subprocess_code",
        "subprocess_name",
        "element_id",
        "config_id",
        "dashboard_type",
        "dashboard_id",
        "dashboard_config_id",
        "edit_type",
        "tab_id",
        "tab_name",
        "plots_id",
        "plots_name",
        "shared_username",
        "shared_type",
        "subprocess_group",
        "dashboard_index",
    ]
)
login_trail_data = pd.DataFrame(
    columns=[
        "id",
        "session_id",
        "user_name",
        "time_logged_in",
        "time_logged_out",
        "logout_type",
        "ip",
        "inactivity_time",
    ]
)
audit_trail_data = pd.DataFrame(
    columns=[
        "id",
        "session_id",
        "ip",
        "user_name",
        "app_code",
        "url_current",
        "url_from",
        "screen",
        "logged_date",
        "logged_time",
        "time_spent",
    ]
)


for tenant in tenant_data:
    print("tenant------------------------------------------------->", tenant)

    # User Data
    sql_table_name = "users_user"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    table = pd.DataFrame(
        records,
        columns=[
            "id",
            "password",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "name",
            "last_password_update_date",
            "password_history",
            "tenant",
            "is_developer",
            "mfa_hash",
            "from_ldap",
            "department",
            "job_title",
            "contact_number",
            "location",
        ],
    )
    table["instance_id"] = instance_data[tenant]
    table["role"] = np.where(table["is_developer"], "Developer", "User")
    if tenant != "public":
        table["username"] += f".{tenant}"
    else:
        pass
    user_data = pd.concat([user_data, table], axis=0, ignore_index=True)

    # Profile Data
    sql_table_name = "users_profile"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL(
        "select * from {sql_table_name} where username not in ('revolutio_admin', 'revolutio_admin2');"
    ).format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    profile_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "first_name",
            "last_name",
            "job_title",
            "bio",
            "location",
            "profile_pic",
            "date_joined",
            "last_login",
            "username",
            "email",
            "is_superuser",
            "is_staff",
            "is_active",
            "user_id",
            "contact_number",
            "cover_photo",
            "facebook",
            "github",
            "linkedin",
            "twitter",
            "no_of_alert",
            "department",
            "tagged_user",
        ],
    )
    profile_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        profile_table["username"] += f".{tenant}"
    else:
        pass
    user_profile_data = pd.concat([user_profile_data, profile_table])

    # Configuration Parameter Data
    sql_table_name = "users_configuration_parameter"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select parameter, value from {sql_table_name};").format(
        sql_table_name=sql_table_name
    )
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    configuration_parameter_table = pd.DataFrame(records, columns=["parameter", "value"])
    configuration_parameter_table["instance_id"] = instance_data[tenant]
    configuration_parameter_data = pd.concat([configuration_parameter_data, configuration_parameter_table])

    # User Permission Data
    sql_table_name = "users_userpermission_master"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    userpermission_master_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "usergroup",
            "permission_type",
            "permission_level",
            "permission_name",
            "application",
            "application_dev",
            "app_code",
            "app_name",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
            "level_button_access",
        ],
    )
    userpermission_master_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        userpermission_master_table["created_by"] += f".{tenant}"
        userpermission_master_table["modified_by"] += f".{tenant}"
    else:
        pass
    userpermission_master_data = pd.concat([userpermission_master_data, userpermission_master_table])

    # User Permission Interim Data
    sql_table_name = "users_userpermission_interim"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    userpermission_interim_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "usergroup",
            "permission_type",
            "permission_level",
            "permission_name",
            "permission_level1",
            "approval_status",
            "application",
            "application_dev",
            "app_code",
            "app_name",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
            "level_button_access",
        ],
    )
    userpermission_interim_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        userpermission_interim_table["created_by"] += f".{tenant}"
        userpermission_interim_table["modified_by"] += f".{tenant}"
    else:
        pass
    userpermission_interim_data = pd.concat([userpermission_interim_data, userpermission_interim_table])

    # User Approval Data
    sql_table_name = "users_user_approval"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    user_approval_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "username",
            "password",
            "email",
            "approval_status",
            "authentication_type",
            "action_requested",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
            "is_developer",
        ],
    )
    user_approval_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        user_approval_table["username"] += f".{tenant}"
        user_approval_table["created_by"] += f".{tenant}"
        user_approval_table["modified_by"] += f".{tenant}"
    else:
        pass
    user_approval_data = pd.concat([user_approval_data, user_approval_table])

    # Allocated license Data
    sql_table_name = "users_allocated_licences"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    allocated_licences_table = pd.DataFrame(records, columns=["id", "username", "authentication_type"])
    allocated_licences_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        allocated_licences_table["username"] += f".{tenant}"
    else:
        pass
    allocated_licences_data = pd.concat([allocated_licences_data, allocated_licences_table])

    # Auth Group Data
    sql_table_name = "auth_group"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select id, name from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    auth_group_table = pd.DataFrame(records, columns=["id", "name"])
    auth_group_data = pd.concat([auth_group_data, auth_group_table])

    # Group Details Data
    sql_table_name = "users_group_details"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    group_details_table = pd.DataFrame(
        records, columns=["id", "name", "created_by", "created_date", "modified_by", "modified_date"]
    )
    group_details_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        group_details_table["created_by"] += f".{tenant}"
        group_details_table["modified_by"] += f".{tenant}"
    else:
        pass
    group_details_data = pd.concat([group_details_data, group_details_table])

    # User Group Data
    sql_table_name = "users_user_groups"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select user_id, group_id from {sql_table_name};").format(
        sql_table_name=sql_table_name
    )
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    user_groups_table = pd.DataFrame(records, columns=["user_id", "group_id"])
    user_groups_table["user_id"] = [
        table[table["id"] == i]["username"].values[0] for i in user_groups_table["user_id"].tolist()
    ]
    user_groups_table["group_id"] = [
        auth_group_table[auth_group_table["id"] == i]["name"].values[0]
        for i in user_groups_table["group_id"].tolist()
    ]
    user_groups_data = pd.concat([user_groups_data, user_groups_table])

    # User Group Approval Data
    sql_table_name = "users_usergroup_approval"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    usergroup_approval_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "user_id",
            "group_id",
            "approval_status",
            "user_name",
            "group_name",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ],
    )
    usergroup_approval_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        usergroup_approval_table["user_name"] += f".{tenant}"
    else:
        pass
    usergroup_approval_data = pd.concat([usergroup_approval_data, usergroup_approval_table])

    # User Navbar Data
    sql_table_name = "users_user_navbar"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    user_navbar_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "user_name",
            "app_code",
            "tenant",
            "navbar_list",
            "build_process_type",
            "created_by",
            "created_date",
            "modified_by",
            "modified_date",
        ],
    )
    user_navbar_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        user_navbar_table["user_name"] += f".{tenant}"
        user_navbar_table["created_by"] += f".{tenant}"
        user_navbar_table["modified_by"] += f".{tenant}"
    else:
        pass
    user_navbar_data = pd.concat([user_navbar_data, user_navbar_table])

    # Dashboard Config Data
    sql_table_name = "users_dashboard_config"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    dashboard_config_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "app_code",
            "application_name",
            "subprocess_code",
            "subprocess_name",
            "element_id",
            "config_id",
            "dashboard_type",
            "dashboard_id",
            "dashboard_config_id",
            "edit_type",
            "tab_id",
            "tab_name",
            "plots_id",
            "plots_name",
            "shared_username",
            "shared_type",
            "subprocess_group",
            "dashboard_index",
        ],
    )
    dashboard_config_table["instance_id"] = instance_data[tenant]
    dashboard_config_table["tenant"] = ""
    if tenant != "public":
        dashboard_config_table["shared_username"] += f".{tenant}"
    else:
        pass
    dashboard_config_data = pd.concat([dashboard_config_data, dashboard_config_table])

    # Login Trail Data
    sql_table_name = "users_login_trail"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    login_trail_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "session_id",
            "user_name",
            "time_logged_in",
            "time_logged_out",
            "logout_type",
            "ip",
            "inactivity_time",
        ],
    )
    login_trail_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        login_trail_table["user_name"] += f".{tenant}"
    else:
        pass
    login_trail_table["time_logged_in"] = login_trail_table["time_logged_in"].replace(
        {np.nan: None, pd.NaT: None}
    )
    login_trail_table["time_logged_out"] = login_trail_table["time_logged_out"].replace(
        {np.nan: None, pd.NaT: None}
    )
    login_trail_data = pd.concat([login_trail_data, login_trail_table])

    # Audit Trail Data
    sql_table_name = "users_audit_trail"
    sql_table_name = sql.Identifier(tenant, sql_table_name)
    sql_query = sql.SQL("select * from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    audit_trail_table = pd.DataFrame(
        records,
        columns=[
            "id",
            "session_id",
            "ip",
            "user_name",
            "app_code",
            "url_current",
            "url_from",
            "screen",
            "logged_date",
            "logged_time",
            "time_spent",
        ],
    )
    audit_trail_table["instance_id"] = instance_data[tenant]
    if tenant != "public":
        audit_trail_table["user_name"] += f".{tenant}"
    else:
        pass
    audit_trail_data = pd.concat([audit_trail_data, audit_trail_table])


configuration_parameter_data.drop(columns=["id"], inplace=True)
print("Configuration parameter-------------------------------------->", configuration_parameter_data)

print("Users-------------------------------------->", user_data)


# * New User Data
sql_table_name = "users_user"
sql_table_name = sql.Identifier(sql_table_name)
sql_query = sql.SQL("select id, username from {sql_table_name};").format(sql_table_name=sql_table_name)
cursor = new_central_db_engine.cursor()
cursor.execute(sql_query)
records = cursor.fetchall()
cursor.close()
new_user_data = pd.DataFrame(records, columns=["id", "username"])
new_user_data = new_user_data.set_index("username").to_dict()["id"]
print("new_user_data----------------------------------------------->")
print(new_user_data)


#     pass

userpermission_master_data.drop(columns=["id"], inplace=True)
print("User Permission-------------------------------------->", userpermission_master_data)
if not userpermission_master_data.empty:
    pass
else:
    pass

userpermission_interim_data.drop(columns=["id"], inplace=True)
print("User Permission Interim-------------------------------------->", userpermission_interim_data)
if not userpermission_interim_data.empty:
    pass
else:
    pass

user_approval_data.drop(columns=["id"], inplace=True)
print("User Approval data-------------------------------------->", user_approval_data)
if not user_approval_data.empty:
    pass
else:
    pass

allocated_licences_data.drop(columns=["id"], inplace=True)
print("Allocated licenses data-------------------------------------->", allocated_licences_data)
if not allocated_licences_data.empty:
    pass
else:
    pass

auth_group_data.drop(columns=["id"], inplace=True)
print("Auth Group data-------------------------------------->", auth_group_data)
if not auth_group_data.empty:
    auth_group_data.drop_duplicates(inplace=True)
else:
    pass

# * New Group Data
sql_table_name = "auth_group"
sql_table_name = sql.Identifier(sql_table_name)
sql_query = sql.SQL("select id, name from {sql_table_name};").format(sql_table_name=sql_table_name)
cursor = new_central_db_engine.cursor()
cursor.execute(sql_query)
records = cursor.fetchall()
cursor.close()
new_group_data = pd.DataFrame(records, columns=["id", "name"])
new_group_data = new_group_data.set_index("name").to_dict()["id"]


group_details_data.drop(columns=["id"], inplace=True)
print("Group Details data-------------------------------------->", group_details_data)
if not group_details_data.empty:
    group_details_data.drop_duplicates(subset=["name", "instance_id"], inplace=True)
else:
    pass

print("User Groups data-------------------------------------->", user_groups_data)
if not user_groups_data.empty:
    user_groups_data["user_id"] = [
        new_user_data[i] if i in new_user_data else None for i in user_groups_data["user_id"].to_list()
    ]
    user_groups_data["group_id"] = [
        new_group_data[i] if i in new_group_data else None for i in user_groups_data["group_id"].to_list()
    ]
    user_groups_data.dropna(subset=["user_id", "group_id"], inplace=True)
    postgres_push(user_groups_data, "users_user_groups", new_central_db_engine)
else:
    pass

print("User Group Approval data-------------------------------------->", usergroup_approval_data)
if not usergroup_approval_data.empty:
    usergroup_approval_data.drop(columns=["id"], inplace=True)
    usergroup_approval_data["user_id"] = [
        new_user_data[i] if i in new_user_data else None
        for i in usergroup_approval_data["user_name"].to_list()
    ]
    usergroup_approval_data["group_id"] = [
        new_group_data[i] if i in new_group_data else None
        for i in usergroup_approval_data["group_name"].to_list()
    ]
    usergroup_approval_data.dropna(subset=["user_id", "group_id"], inplace=True)
    postgres_push(usergroup_approval_data, "users_usergroup_approval", new_central_db_engine)
else:
    pass

user_navbar_data.drop(columns=["id", "tenant"], inplace=True)
print("User Navbar data-------------------------------------->", user_navbar_data)
if not user_navbar_data.empty:
    postgres_push(user_navbar_data, "users_user_navbar", new_central_db_engine)
else:
    pass

dashboard_config_data.drop(columns=["id", "tenant"], inplace=True)
print("Dashboard Config data-------------------------------------->", dashboard_config_data)
if not dashboard_config_data.empty:
    postgres_push(dashboard_config_data, "users_dashboard_config", new_central_db_engine)
else:
    pass

login_trail_data.drop(columns=["id"], inplace=True)
print("Login Trail data-------------------------------------->", login_trail_data)
if not login_trail_data.empty:
    postgres_push(login_trail_data, "users_login_trail", new_central_db_engine)
else:
    pass

audit_trail_data.drop(columns=["id"], inplace=True)
print("Audit Trail data-------------------------------------->", audit_trail_data)
if not audit_trail_data.empty:
    postgres_push(audit_trail_data, "users_audit_trail", new_central_db_engine)
else:
    pass

# Social account data
sql_table_name = "socialaccount_socialaccount"
sql_table_name = sql.Identifier(sql_table_name)
sql_query = sql.SQL(
    "select provider, uid, last_login, date_joined, extra_data, user_id from {sql_table_name};"
).format(sql_table_name=sql_table_name)
cursor = current_central_db_engine.cursor()
cursor.execute(sql_query)
socialuser_records = cursor.fetchall()
cursor.close()
socialuser_data = pd.DataFrame(
    socialuser_records, columns=["provider", "uid", "last_login", "date_joined", "extra_data", "user_id"]
)

if not socialuser_data.empty:
    sql_table_name = "users_user"
    sql_table_name = sql.Identifier(sql_table_name)
    sql_query = sql.SQL("select id, username from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = current_central_db_engine.cursor()
    cursor.execute(sql_query)
    user_records = cursor.fetchall()
    cursor.close()
    user_data = pd.DataFrame(user_records, columns=["id", "username"])
    user_data = user_data.set_index("id").to_dict()["username"]

    sql_table_name = "users_user"
    sql_table_name = sql.Identifier(sql_table_name)
    sql_query = sql.SQL("select id, username from {sql_table_name};").format(sql_table_name=sql_table_name)
    cursor = new_central_db_engine.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    cursor.close()
    new_user_data = pd.DataFrame(records, columns=["id", "username"])
    new_user_data = new_user_data.set_index("username").to_dict()["id"]
    new_user_ids = {i: new_user_data[name] for i, name in user_data.items()}
    socialuser_data["user_id"] = socialuser_data["user_id"].replace(new_user_ids)
    postgres_push(socialuser_data, "socialaccount_socialaccount", new_central_db_engine)
else:
    pass

print("<--------------------------- End of Central Migration ----------------------------->")
