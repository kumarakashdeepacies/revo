import datetime
import glob
import json
import logging
import os
import pickle
import time

from O365 import Account
import pandas as pd
import psycopg2

from config.settings.base import (
    PLATFORM_FILE_PATH,
    central_database_config,
    database_engine_dict,
    database_type,
    engine,
    get_tenants_map,
    redis_instance,
)
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    delete_data_func,
    execute_read_query,
    postgres_push,
    read_data_func,
    update_data_func,
)
from kore_investment.users.computations.standardised_functions import (
    check_approval_condition,
    execute_auto_run_computation,
)
from kore_investment.utils.User_Management import migrate_tenant, run_custom_command


def schedulercheck(job_id):
    return None


def schedulercheck1(job_id):
    return None


def schedulercheck2(job_id):
    return None


def scheduler_email(request, job_id):
    credentials = ("b99d0515-5aef-411a-af5f-fdab0a2d6206", "_cU62ve6R6a0~351WvI_g0wkQW9O01x3.W")
    task_config = json.loads(
        (
            read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "jobs_scheduled",
                        "Columns": ["task_config"],
                    },
                    "condition": [
                        {
                            "column_name": "job_id",
                            "condition": "Equal to",
                            "input_value": job_id,
                            "and_or": "",
                        }
                    ],
                },
            )
        ).task_config.iloc[0]
    )
    from_email = task_config["from_email"]
    to_list = task_config["to_email"]
    subject = task_config["subject_email"]
    content = task_config["text_email"]
    account = Account(
        credentials, auth_flow_type="credentials", tenant_id="4bf6db98-c05a-4a1e-ac6a-340dcfa47097"
    )
    if account.authenticate():
        m = account.mailbox(resource=f"{from_email}")
        m = account.new_message(resource=f"{from_email}")
        m.to.add(to_list)
        m.subject = f"{subject}"
        m.body = f"{content}"
        m.send()
    return None


def mark_users_inactive(job_id, schema):
    inactive_users_after_days, delete_users_after_days = read_tenant_json_date(schema)
    inactive_date = datetime.datetime.now() - datetime.timedelta(inactive_users_after_days)
    update_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "user",
                "Columns": [
                    {
                        "column_name": "is_active",
                        "input_value": str(0),
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {
                    "column_name": "last_login",
                    "condition": "Smaller than",
                    "input_value": str(inactive_date),
                    "and_or": "",
                }
            ],
        },
        schema=schema,
        engine_override=True,
        engine2=[engine],
        db_type=database_type,
    )

    func = "schedulercheck.reactivate_locked_users"
    job_id = "reactivate_locked_users_job"

    user_inactivity_days, user_inactivity_hours, user_inactivity_minutes = read_tenant_user_expiry(schema)

    scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(
        days=int(user_inactivity_days), hours=int(user_inactivity_hours), minutes=int(user_inactivity_minutes)
    )
    from kore_investment.users import scheduler as schedulerfunc

    schedulerfunc.add_db_health_scheduler(func, job_id, schema, start_date=scheduled_time)

    return True


def reactivate_locked_users(job_id, schema):

    user_inactivity_days, user_inactivity_hours, user_inactivity_minutes = read_tenant_user_expiry(schema)

    inactive_users_after_days, delete_users_after_days = read_tenant_json_date(schema)
    inactive_date = datetime.datetime.now() - datetime.timedelta(inactive_users_after_days)
    inactive_date = inactive_date - datetime.timedelta(
        days=int(user_inactivity_days), hours=int(user_inactivity_hours), minutes=int(user_inactivity_minutes)
    )

    update_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "user",
                "Columns": [
                    {
                        "column_name": "is_active",
                        "input_value": str(1),
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {
                    "column_name": "last_login",
                    "condition": "Smaller than",
                    "input_value": str(inactive_date),
                    "and_or": "",
                }
            ],
        },
        schema=schema,
        engine_override=True,
        engine2=[engine],
        db_type=database_type,
    )
    return True


def reactivate_locked_users_password_setting(job_id, schema):

    username = job_id.split("-")[0]
    update_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "user",
                "Columns": [
                    {
                        "column_name": "is_active",
                        "input_value": str(1),
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {
                    "column_name": "username",
                    "condition": "Equal to",
                    "input_value": username,
                    "and_or": "",
                }
            ],
        },
        schema=schema,
        engine_override=True,
        engine2=[engine],
        db_type=database_type,
    )
    return True


def delete_inactive_users(job_id, schema):
    inactive_users_after_days, delete_users_after_days = read_tenant_json_date(schema)
    inactive_date = datetime.datetime.now() - datetime.timedelta(delete_users_after_days)
    delete_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "user",
            },
            "condition": [
                {
                    "column_name": "last_login",
                    "condition": "Smaller than",
                    "input_value": inactive_date,
                    "and_or": "",
                },
            ],
        },
        schema=schema,
    )
    return True


def delete_expired_notifications(job_id, tenant):
    tenant_db = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_db = json.load(json_file)
            json_file.close()

    for tenant in tenant_db:
        tenant_data = tenant_db[tenant]
        noti_expiry_days = 20
        noti_expiry_hours = 0
        noti_expiry_minutes = 0
        if (
            tenant_data.get("noti_expiry_days")
            and tenant_data.get("noti_expiry_hours")
            and tenant_data.get("noti_expiry_minutes")
        ):
            noti_expiry_days = tenant_data["noti_expiry_days"]
            noti_expiry_hours = tenant_data["noti_expiry_hours"]
            noti_expiry_minutes = tenant_data["noti_expiry_minutes"]
        else:
            pass

        expiry_date = datetime.datetime.now() - datetime.timedelta(
            days=int(noti_expiry_days), hours=int(noti_expiry_hours), minutes=int(noti_expiry_minutes)
        )
        expiry_date = expiry_date.strftime("%Y-%m-%d %I:%M %p")

        delete_data_func(
            "",
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "notification_management",
                },
                "condition": [
                    {
                        "column_name": "created_date",
                        "condition": "Smaller than",
                        "input_value": expiry_date,
                        "and_or": "",
                    }
                ],
            },
            schema=tenant,
        )
    return True


def read_tenant_json_date(schema):
    inactive_users_after_days = 60
    delete_users_after_days = 180
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == schema:
                    if t_config.get("inactive_users_after_days") and t_config.get("delete_users_after_days"):
                        inactive_users_after_days = t_config["inactive_users_after_days"]
                        delete_users_after_days = t_config["delete_users_after_days"]
            json_file.close()
    return inactive_users_after_days, delete_users_after_days


def read_tenant_user_expiry(schema):
    user_inactivity_days = 60
    user_inactivity_hours = 0
    user_inactivity_minutes = 0
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            if schema in tenant_data:
                t_config = tenant_data[schema]
                if t_config.get("user_inactivity_days"):
                    user_inactivity_days = t_config["user_inactivity_days"]
                if t_config.get("user_inactivity_hours"):
                    user_inactivity_hours = t_config["user_inactivity_hours"]
                if t_config.get("user_inactivity_minutes"):
                    user_inactivity_minutes = t_config["user_inactivity_minutes"]
            json_file.close()
    return user_inactivity_days, user_inactivity_hours, user_inactivity_minutes


def db_con_checker(job_id, schema):
    db_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            json_file.close()
    conn_dbs = {k: v for k, v in db_data.items() if v["tenant"] == schema}
    connected_db_status = {}
    for k, v in conn_dbs.items():
        if database_engine_dict.get(k):
            try:
                sql_engine, db_type = database_engine_dict[k]
                if db_type == "Oracle":
                    query = "select 'test' as mytest from dual"
                else:
                    query = "Select 1"
                execute_read_query(query, sql_engine, db_type)
                connected_db_status[k] = "Healthy"
            except Exception as e:
                if k in database_engine_dict:
                    del database_engine_dict[k]
                logging.warning(f"Following exception occurred - {e}")
                connected_db_status[k] = "Database connection is broken! Please reconnect"
        else:
            connected_db_status[k] = "Database not connected"
    redis_instance.set(job_id, pickle.dumps(connected_db_status))
    return None


def migration_checker(job_id, tenant):
    # Migration checker
    list_of_files = glob.glob("kore_investment/users/migrations/*.py")

    list_of_files = [
        i.replace("kore_investment/users/migrations/", "").replace(".py", "")
        for i in list_of_files
        if "__init__.py" not in i
    ]
    sql_engine = psycopg2.connect(
        dbname=central_database_config["dbname"],
        user=central_database_config["user"],
        password=central_database_config["password"],
        host=central_database_config["host"],
        port=central_database_config["port"],
    )
    sql_query = f"SELECT name FROM public.django_migrations WHERE app='users'"
    try:
        cursor = sql_engine.cursor()
        cursor.execute(sql_query)
        applied_migration_list = cursor.fetchall()
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        # New instance run the initial migrations and create default users
        migrate_tenant()
        tenants_data = get_tenants_map()
        schemas_list = tenants_data.keys()
        tenant_list = ["platform_admin"]
        for i in schemas_list:
            tenant_list.append(i)
            tenant_list.append(f"{i}_admin")
        tenant_data = pd.DataFrame({"name": tenant_list})
        postgres_push(tenant_data, "users_instance", "public", con=[sql_engine, None])
        for schema in tenant_list:
            if schema.endswith("_admin") and schema != "platform_admin":
                mode = "tenant_admin"
                role = "Tenant Admin"
            elif schema == "platform_admin":
                mode = "platform_admin"
                role = "Platform Admin"
            else:
                mode = "user"
                role = "Developer"
            run_custom_command(schema, mode=mode, role=role)
    else:
        # Existing instance check for any un-applied migrations
        unapplied_migrations = [i for i in list_of_files if i not in applied_migration_list]
        if unapplied_migrations:
            migrate_tenant()
        else:
            pass
    return None


def execute_block(request, job_id, block_config, retries, interval_between_retries):
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
    subprocess_code = job_id.split("_")[0]
    block_element_id = job_id.split("_")[1]
    last_element_status = "pass"
    start_time = time.time()
    execution_date = datetime.date.today()
    if retries != "":
        retries = int(retries)
        if not retries:
            retries = 1
    else:
        retries = 1
    attempt = 1
    job_status_details = {}
    while attempt <= retries and last_element_status == "pass":
        try:
            if block_element_id.startswith("parallelogram"):
                start_time = time.time()
                execution_date = datetime.date.today()
                result = execute_auto_run_computation(
                    block_element_id, subprocess_code, request, attempt=retries
                )
                end_time = time.time()
                execution_time = end_time - start_time
                if result.get("element_error_message") != "Success":
                    last_element_status == "fail"
                    execution_information = result.get("element_error_message")
                else:
                    last_element_status == "pass"
                    execution_information = "Executed"
                execution_time = round(execution_time, 4)
                job_status_details = {
                    "block_element_id": block_element_id,
                    "subprocess_code": subprocess_code,
                    "execution_date": execution_date,
                    "status": last_element_status,
                    "execution_time": str(execution_time),
                    "execution_information": execution_information,
                }
            elif block_element_id.startswith("decision"):
                if block_config["blockTriggerConfig"].get("previousElement"):
                    previous_element = block_config["blockTriggerConfig"].get("previousElement")
                    action = block_config["schedulerAction"]
                    condition = []
                    start_time = time.time()
                    if block_config["schedulerAction"] in [
                        "approve_with_condition",
                        "reject_with_condition",
                    ] and block_config.get("schedulerActionCondition"):
                        condition = block_config["schedulerActionCondition"]["underlying_table_conditions"]
                        approval_condition = block_config["schedulerActionCondition"]["approval_conditions"]
                        check_approval_condition(
                            condition,
                            request,
                            block_config["schedulerAction"],
                            approval_condition=approval_condition,
                        )
                    else:
                        check_approval_condition([], request, block_config["schedulerAction"])
                    end_time = time.time()
                    last_element_status == "pass"
                    execution_time = end_time - start_time
                    execution_time = round(execution_time, 4)
                    job_status_details = {
                        "block_element_id": block_element_id,
                        "subprocess_code": subprocess_code,
                        "execution_date": execution_date,
                        "status": last_element_status,
                        "execution_time": str(execution_time),
                        "execution_information": "Executed",
                    }
                else:
                    pass
            else:
                pass
            break
        except Exception as e:
            logging.warning(e)
            if interval_between_retries and attempt < retries:
                time.sleep(int(interval_between_retries) * 60)
            else:
                pass
            last_element_status == "fail"
            job_status_details = {
                "block_element_id": block_element_id,
                "subprocess_code": subprocess_code,
                "execution_date": execution_date,
                "status": last_element_status,
                "execution_time": None,
                "execution_information": str(e),
            }
        attempt += 1
    if job_status_details:
        job_status_details = pd.DataFrame([job_status_details])
        data_handling(
            request,
            job_status_details,
            "scheduler_event_status",
        )
    else:
        pass
    return True


def execute_flow(request, job_id, retries, interval_between_retries):
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
    process_code = job_id.split("_")[0]
    subprocess_code = job_id.split("_")[1]

    if retries != "":
        retries = int(retries)
        if not retries:
            retries = 1
    else:
        retries = 1

    scheduler_config = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "processScheduler",
                "Columns": ["config"],
            },
            "condition": [
                {
                    "column_name": "item_group_code",
                    "condition": "Equal to",
                    "input_value": process_code,
                    "and_or": "and",
                },
                {
                    "column_name": "item_code",
                    "condition": "Equal to",
                    "input_value": subprocess_code,
                    "and_or": "and",
                },
                {
                    "column_name": "scheduler_type",
                    "condition": "Equal to",
                    "input_value": "flow",
                    "and_or": "",
                },
            ],
        },
    )
    if not scheduler_config.empty:
        block_config = json.loads(scheduler_config.config.iloc[0])["blockConfig"]
        flow_connector_details = (
            read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "TabScreens",
                        "Columns": ["tab_body_content"],
                    },
                    "condition": [
                        {
                            "column_name": "related_item_code",
                            "condition": "Equal to",
                            "input_value": subprocess_code,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "tab_type",
                            "condition": "Equal to",
                            "input_value": "connector",
                            "and_or": "",
                        },
                    ],
                },
            )
            .tab_body_content.apply(json.loads)
            .tolist()
        )
        if flow_connector_details:
            subprocess_flow_data = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "process_subprocess_flowchart",
                        "Columns": ["flowchart_elements"],
                    },
                    "condition": [
                        {
                            "column_name": "related_item_code",
                            "condition": "Equal to",
                            "input_value": subprocess_code,
                            "and_or": "",
                        }
                    ],
                },
            ).flowchart_elements.iloc[0]
            subprocess_flow_data = json.loads(subprocess_flow_data)
            subprocess_flow_data = {
                ele["shapeID"]: ele
                for ele in subprocess_flow_data
                if ele["child"] != "#" or ele["parent"] != "#"
            }
            flow_ended = False
            current_element = list(subprocess_flow_data.keys())[0]
            last_element_status = "pass"

            while not flow_ended and last_element_status == "pass":
                for conn in flow_connector_details:
                    if conn["parent"] == current_element or conn["child"] == current_element:
                        executed_time = datetime.datetime.now()
                        execution_date = datetime.date.today()
                        start_time = time.time()
                        current_element_details = subprocess_flow_data[current_element]
                        attempt = 1
                        while attempt <= retries:
                            try:
                                if current_element_details["shape"] == "parallelogram":
                                    current_element_name = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "TabScreens",
                                                "Columns": ["tab_header_name"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "element_id",
                                                    "condition": "Equal to",
                                                    "input_value": current_element,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    ).tab_header_name.iloc[0]
                                    current_element_name = json.loads(current_element_name)
                                    start_time = time.time()
                                    execute_auto_run_computation(
                                        current_element, subprocess_code, request, attempt=retries
                                    )
                                    end_time = time.time()
                                    last_element_status = "pass"
                                    execution_time = end_time - start_time
                                    execution_time = round(execution_time, 4)
                                    job_status_details = {
                                        "process_code": process_code,
                                        "subprocess_code": subprocess_code,
                                        "block_element_id": current_element_name[0]["tab_header_name"],
                                        "execution_date": execution_date,
                                        "status": last_element_status,
                                        "execution_time": str(execution_time),
                                        "execution_information": "Executed",
                                        "executed_time": str(executed_time.hour),
                                    }
                                    job_status_details = pd.DataFrame([job_status_details])
                                    data_handling(
                                        request,
                                        job_status_details,
                                        "process_flow_event_status",
                                    )
                                elif current_element.startswith("decision"):
                                    current_element_name = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "TabScreens",
                                                "Columns": ["tab_header_name"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "element_id",
                                                    "condition": "Equal to",
                                                    "input_value": current_element,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                    current_element_name = current_element_name.to_dict("records")
                                    previous_element = subprocess_flow_data[current_element]["parent"][0]
                                    action = block_config[current_element]["schedulerAction"]
                                    condition = []
                                    start_time = time.time()
                                    check_approval_condition(
                                        previous_element,
                                        subprocess_code,
                                        "create",
                                        condition,
                                        request,
                                        action,
                                    )
                                    end_time = time.time()
                                    last_element_status = "pass"
                                    execution_time = end_time - start_time
                                    execution_time = round(execution_time, 4)
                                    job_status_details = {
                                        "process_code": process_code,
                                        "subprocess_code": subprocess_code,
                                        "block_element_id": current_element_name[0]["tab_header_name"],
                                        "execution_date": execution_date,
                                        "status": last_element_status,
                                        "execution_time": str(execution_time),
                                        "execution_information": "Executed",
                                        "executed_time": str(executed_time.hour),
                                    }
                                    job_status_details = pd.DataFrame([job_status_details])
                                    data_handling(
                                        request,
                                        job_status_details,
                                        "process_flow_event_status",
                                    )
                                else:
                                    current_element_name = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "TabScreens",
                                                "Columns": ["tab_header_name"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "element_id",
                                                    "condition": "Equal to",
                                                    "input_value": current_element,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                    current_element_name = current_element_name.to_dict("records")
                                    end_time = time.time()
                                    execution_time = end_time - start_time
                                    execution_time = round(execution_time, 4)
                                    job_status_details = {
                                        "process_code": process_code,
                                        "subprocess_code": subprocess_code,
                                        "block_element_id": current_element_name[0]["tab_header_name"],
                                        "execution_date": execution_date,
                                        "status": last_element_status,
                                        "execution_time": str(execution_time),
                                        "execution_information": "Executed",
                                        "executed_time": str(executed_time.hour),
                                    }
                                    job_status_details = pd.DataFrame([job_status_details])
                                    data_handling(
                                        request,
                                        job_status_details,
                                        "process_flow_event_status",
                                    )
                                    last_element_status = "User_Input_Required"

                                if current_element_details["child"] == "#":
                                    end_time = time.time()
                                    flow_ended = True
                                else:
                                    current_element = current_element_details["child"][0]
                                    current_element_name = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "TabScreens",
                                                "Columns": ["tab_header_name"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "element_id",
                                                    "condition": "Equal to",
                                                    "input_value": current_element,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                    current_element_name = current_element_name.to_dict("records")
                                    end_time = time.time()
                                    execution_time = end_time - start_time
                                    execution_time = round(execution_time, 4)
                                    job_status_details = {
                                        "process_code": process_code,
                                        "subprocess_code": subprocess_code,
                                        "block_element_id": current_element_name[0]["tab_header_name"],
                                        "execution_date": execution_date,
                                        "status": last_element_status,
                                        "execution_time": str(execution_time),
                                        "execution_information": "Executed",
                                        "executed_time": str(executed_time.hour),
                                    }
                                    job_status_details = pd.DataFrame([job_status_details])
                                    data_handling(
                                        request,
                                        job_status_details,
                                        "process_flow_event_status",
                                    )
                                break
                            except Exception as e:
                                current_element_name = read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "TabScreens",
                                            "Columns": ["tab_header_name"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "element_id",
                                                "condition": "Equal to",
                                                "input_value": current_element,
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                                current_element_name = current_element_name.to_dict("records")
                                execution_information = str(e)
                                last_element_status = "fail"
                                job_status_details = {
                                    "process_code": process_code,
                                    "subprocess_code": subprocess_code,
                                    "block_element_id": current_element_name[0]["tab_header_name"],
                                    "execution_date": execution_date,
                                    "status": last_element_status,
                                    "execution_time": None,
                                    "execution_information": "Not_Executed",
                                    "executed_time": str(executed_time.hour),
                                }
                                job_status_details = pd.DataFrame([job_status_details])
                                data_handling(
                                    request,
                                    job_status_details,
                                    "process_flow_event_status",
                                )
                                if interval_between_retries and attempt < retries:
                                    time.sleep(int(interval_between_retries) * 60)
                                else:
                                    pass

                            attempt += 1
                        if last_element_status == "pass":
                            end_time = time.time()
                            execution_time = end_time - start_time
                            execution_time = round(execution_time, 4)
                            job_status_details = {
                                "process_code": process_code,
                                "subprocess_code": subprocess_code,
                                "execution_date": execution_date,
                                "status": last_element_status,
                                "execution_time": str(execution_time),
                                "execution_information": "Executed",
                                "executed_time": str(executed_time.hour),
                            }
                            job_status_details = pd.DataFrame([job_status_details])
                            data_handling(
                                request,
                                job_status_details,
                                "scheduler_event_status",
                            )
                        elif last_element_status == "User_Input_Required":
                            end_time = time.time()
                            execution_time = end_time - start_time
                            execution_time = round(execution_time, 4)
                            job_status_details = {
                                "process_code": process_code,
                                "subprocess_code": subprocess_code,
                                "execution_date": execution_date,
                                "status": last_element_status,
                                "execution_time": str(execution_time),
                                "execution_information": "User_Input_Required",
                                "executed_time": str(executed_time.hour),
                            }
                            job_status_details = pd.DataFrame([job_status_details])
                            data_handling(
                                request,
                                job_status_details,
                                "scheduler_event_status",
                            )
                        else:
                            job_status_details = {
                                "process_code": process_code,
                                "subprocess_code": subprocess_code,
                                "execution_date": execution_date,
                                "status": last_element_status,
                                "execution_time": None,
                                "execution_information": execution_information,
                                "executed_time": str(executed_time.hour),
                            }
                            job_status_details = pd.DataFrame([job_status_details])
                            data_handling(
                                request,
                                job_status_details,
                                "scheduler_event_status",
                            )
                        if current_element_details["child"] == "#":
                            flow_ended = True
                            end_time = time.time()
                        else:
                            pass
                        break
                    else:
                        continue
        else:
            pass
    else:
        pass
    return True
