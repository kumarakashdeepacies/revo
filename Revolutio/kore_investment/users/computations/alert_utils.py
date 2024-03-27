import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import os
import pickle
import random
import smtplib
import string
import time
import urllib

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
from turbodbc import connect, make_options

from config.settings.base import (
    PLATFORM_FILE_PATH,
    central_database_config,
    database_engine_dict,
    engine,
    turbodbc_connection,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.queue_manager import enqueue_jobs
from kore_investment.utils.utilities import tenant_schema_from_request


def random_no_generator(N=16):
    code = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(N))
    return code


def send_email_alert(request, from_user, to_user, subject, content, username=None, approval=0, tenant=None):
    try:
        mimemsg = MIMEMultipart()
        mimemsg["To"] = ", ".join(to_user)
        mimemsg["Subject"] = subject
        if request is not None:
            tenant = tenant_schema_from_request(request)
        html = f"""\
            <html>
            <head></head>
            <body>
                <p>{content}</p>
            </body>
            </html>
            """
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                for t_name, t_config in tenant_data.items():
                    if t_name == tenant:
                        if not approval:
                            if (
                                t_config.get("smtp_host")
                                and t_config.get("smtp_host_user")
                                and t_config.get("smtp_host_password")
                                and t_config.get("smtp_port")
                            ):
                                smtp_host = t_config["smtp_host"]
                                smtp_host_user = t_config["smtp_host_user"]
                                smtp_host_password = t_config["smtp_host_password"]
                                smtp_port = int(t_config["smtp_port"])
                        else:
                            if (
                                t_config.get("mail_provider")
                                and t_config.get("approval_password")
                                and t_config.get("approval_email")
                            ):
                                smtp_host = t_config["mail_provider"]
                                smtp_host_user = t_config["approval_email"]
                                smtp_host_password = t_config["approval_password"]
                                smtp_port = int(t_config.get("approval_smtp_port", "587"))
                                from_user = t_config["approval_email"]
                json_file.close()

        mimemsg["From"] = from_user
        mimemsg.attach(MIMEText(html, "html"))
        connection = smtplib.SMTP(host=smtp_host, port=smtp_port)
        connection.ehlo()
        connection.starttls()
        connection.ehlo()
        connection.login(smtp_host_user, smtp_host_password)
        connection.send_message(mimemsg)
        connection.quit()
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
    return None


def current_app_db_extractor_url(username, url_string, tenant):
    # request.username/ redis username -> combination
    app_code = ""
    db_connection_name = ""
    if (
        not any(
            url_match in url_string
            for url_match in [
                "/users/selectApplication/",
                "/users/adminPanel/",
                "/users/alertsSetup/",
                "/users/customizeTheme/",
                "/users/dashboard/",
                "/users/previewTheme/",
                "/users/planner/",
                "/users/forum/",
                "/users/profile/",
                "/users/changeprofilename/",
                "/users/ajax/profilephoto_upload/",
                "/users/ajax/coverphoto_upload/",
                "/accounts/login/",
                "/accounts/logout/",
                "forum",
                "/media/",
            ]
        )
        and "/create_new/dev/application" not in url_string.lower()
        and not url_string.startswith("/account")
        and not url_string.startswith("/static")
    ):
        f_occ = url_string.find("/", url_string.find("/") + 1)
        s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
        app_code = url_string[f_occ + 1 : s_occ]
    else:
        app_code = ""
    if app_code:
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = tenant + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
    return app_code, db_connection_name


def alert_event_message(alert_event, alert_type, request_username):
    if alert_type == "DB":
        alert_event, table_name = alert_event.split("__")
        if alert_event == "update_data_func":
            message = f"User '{request_username}' updated the row(s) in '{table_name}' table"
        elif alert_event == "delete_data_func":
            message = f"User '{request_username}' deleted the row(s) in '{table_name}' table"
        elif alert_event == "read_data_func":
            message = f"User '{request_username}' readed the row(s) in '{table_name}' table"
        elif alert_event == "data_handling":
            message = f"User '{request_username}' inserted the row(s) in '{table_name}' table"
    elif alert_type == "Access alerts":
        message = (
            f"User '{request_username}' accessed '{alert_event.split('__')[1]}' screen in the Application."
        )
    return message


def sql_engine_gen(db_connection_name):
    engine_temp, turbodbc_con = "", None
    db_type = "MSSQL"
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            db_data = db_data[db_connection_name]
            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                db_data["server"],
                db_data["port"],
                db_data["db_name"],
                db_data["username"],
                db_data["password"],
                db_data["connection_code"],
            )
            db_data["HOST"] = db_server
            db_data["PORT"] = port
            db_data["NAME"] = db_name
            db_data["USER"] = username
            db_data["PASSWORD"] = password
            del db_data["server"]
            del db_data["port"]
            del db_data["db_name"]
            del db_data["username"]
            del db_data["password"]
            db_type = db_data["db_type"]
            if db_data["db_type"] == "MSSQL":
                del db_data["db_type"]
                try:
                    quoted_temp = urllib.parse.quote_plus(
                        "driver={ODBC Driver 18 for SQL Server};server="
                        + db_data["HOST"]
                        + ","
                        + db_data["PORT"]
                        + ";database="
                        + db_data["NAME"]
                        + ";Uid="
                        + db_data["USER"]
                        + ";Pwd="
                        + db_data["PASSWORD"]
                        + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                    )
                    engine_temp = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_temp}")
                    turbodbc_con = connect(
                        driver="ODBC Driver 18 for SQL Server",
                        server=db_data["HOST"] + "," + db_data["PORT"],
                        database=db_data["NAME"],
                        uid=db_data["USER"],
                        pwd=db_data["PASSWORD"] + ";Encrypt=yes;TrustServerCertificate=yes;",
                        turbodbc_options=make_options(
                            prefer_unicode=True,
                            use_async_io=True,
                            varchar_max_character_limit=10000000,
                            autocommit=True,
                        ),
                    )
                    conn = engine_temp.connect()
                    conn.close()
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_con], "MSSQL"
                    db_data["ENGINE"] = "sql_server.pyodbc"
                    db_data["OPTIONS"] = {
                        "driver": "ODBC Driver 18 for SQL Server",
                        "extra_params": "Encrypt=yes;TrustServerCertificate=yes;",
                    }
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            elif db_data["db_type"] == "PostgreSQL":
                del db_data["db_type"]
                try:
                    engine_temp = create_engine(
                        f"postgresql+psycopg2://{db_data['USER']}:{db_data['PASSWORD']}@{db_data['HOST']}:{db_data['PORT']}/{db_data['NAME']}"
                    )
                    conn = engine_temp.connect()
                    conn.close()
                    turbodbc_con = None
                    database_engine_dict[db_connection_name] = [engine_temp, turbodbc_con], "PostgreSQL"
                    db_data["OPTIONS"] = {
                        "driver": "ODBC Driver 18 for SQL Server",
                        "extra_params": "Encrypt=yes;TrustServerCertificate=yes;",
                    }
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
            json_file.close()
    return [engine_temp, turbodbc_con], db_type


def pandas_push(table, db_table_name, con, if_exists="append", chunksize=10**5):
    table.to_sql(
        db_table_name,
        con=con,
        if_exists=if_exists,
        chunksize=chunksize,
        index=False,
    )
    return True


def app_engine_generator(request):
    # request.username/ redis username -> combination
    user_db_engine = ["", None]
    db_type = ""
    db_connection_name = ""
    tenant = tenant_schema_from_request(request)
    schema = tenant
    url_string = request.path
    app_code, db_connection_name = current_app_db_extractor_url(request.user.username, url_string, tenant)
    if app_code != "":
        app_db_mapping = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                app_db_mapping = json.load(json_file)
                json_file.close()
        if app_db_mapping:
            tenant_app_code = schema + "_" + app_code
            db_connection_name = app_db_mapping[tenant_app_code]
            global database_engine_dict
            engine_dict = database_engine_dict.copy()
            if engine_dict.get(db_connection_name):
                user_db_engine, db_type = engine_dict[db_connection_name]
            else:
                user_db_engine, db_type = sql_engine_gen(db_connection_name)
    return user_db_engine, db_type, schema


def alert_builer(request, tenant, curr_app_code, db_connection_name, alert_type, alert_event):
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
    username = request.user.username

    alert_data = []
    app_engine, db_type, schema = app_engine_generator(request)

    group_list = non_standard_read_data_func(
        f"SELECT usergroup FROM users_alerts WHERE app_code='{curr_app_code}' AND alert_type='{alert_type}';",
        app_engine,
    )
    if len(group_list) > 0:
        group_list = group_list["usergroup"].tolist()
        group_list = list({int(x) for x in group_list})
    else:
        return []
    message = ""
    alert_owner = ""
    sql_engine = psycopg2.connect(
        dbname=central_database_config["dbname"],
        user=central_database_config["user"],
        password=central_database_config["password"],
        host=central_database_config["host"],
        port=central_database_config["port"],
    )
    cursor = sql_engine.cursor()
    df_log = pd.DataFrame(
        columns=[
            "usergroup",
            "alert_owner",
            "alert_type",
            "alert_options",
            "events",
            "alert_message",
            "app_code",
            "created_by",
            "created_date",
        ]
    )
    for group in group_list:
        alert_config_row = non_standard_read_data_func(
            f"SELECT * FROM users_alerts WHERE usergroup='{group}' AND app_code='{curr_app_code}' AND alert_type='{alert_type}';",
            app_engine,
        )
        alert_exclude_user = alert_config_row[alert_config_row["alert_owner"] != "admin"][
            "alert_owner"
        ].tolist()
        if len(alert_config_row) > 0:
            cursor.execute(sql.SQL(f"SELECT user_id FROM users_user_groups WHERE group_id='{group}';"))
            user_group_emails = pd.DataFrame(
                cursor.fetchall(),
                columns=[
                    "user_id",
                ],
            )
            if len(user_group_emails) > 0:
                user_group_emails = str(tuple(user_group_emails["user_id"].tolist())).replace(",)", ")")
                cursor.execute(
                    sql.SQL(f"SELECT id, email, username FROM users_user WHERE id IN {user_group_emails};")
                )
                all_email_list = pd.DataFrame(
                    cursor.fetchall(),
                    columns=[
                        "id",
                        "email",
                        "username",
                    ],
                )
            else:
                all_email_list = []
            for row in range(len(alert_config_row)):
                alert_owner = alert_config_row.iloc[row]["alert_owner"]
                if len(all_email_list) > 0:
                    if alert_owner == "admin":
                        email_list = all_email_list[~all_email_list["username"].isin(alert_exclude_user)]
                    else:
                        email_list = all_email_list[all_email_list["username"] == alert_owner]

                    if len(email_list) > 0:
                        email_list = email_list["email"].tolist()
                else:
                    email_list = []
                alert_config = json.loads(alert_config_row.iloc[row]["events"])
                alert_options = json.loads(alert_config_row.iloc[row]["alert_options"])
                if alert_type == "DB":
                    if db_connection_name in alert_config:
                        if alert_options["notification"]:
                            message = f"{alert_event_message(alert_event, alert_type, username)} of '{db_connection_name}' database"
                            df_log_dict = {
                                "usergroup": group,
                                "alert_owner": alert_owner,
                                "alert_type": alert_type,
                                "alert_options": "Notifications",
                                "events": alert_event,
                                "alert_message": message,
                                "app_code": curr_app_code,
                                "created_by": username,
                                "created_date": datetime.datetime.now(),
                            }
                            df_log1 = pd.DataFrame.from_dict([df_log_dict])
                            df_log = pd.concat([df_log, df_log1], ignore_index=True)
                            alert_data.append(
                                [username, group_list, tenant, message, alert_owner, alert_exclude_user]
                            )
                        if alert_options["email"]:
                            message = f"{alert_event_message(alert_event, alert_type, username)} of '{db_connection_name}' database"
                            df_log_dict = {
                                "usergroup": group,
                                "alert_owner": alert_owner,
                                "alert_type": alert_type,
                                "alert_options": "Email",
                                "events": alert_event,
                                "alert_message": message,
                                "app_code": curr_app_code,
                                "created_by": username,
                                "created_date": datetime.datetime.now(),
                            }
                            df_log1 = pd.DataFrame.from_dict([df_log_dict])
                            df_log = pd.concat([df_log, df_log1], ignore_index=True)
                            send_email_alert(
                                request,
                                "notifications@Acies.Consulting",
                                email_list,
                                "DB Alert",
                                message,
                                username=None,
                                approval=0,
                            )
                        continue
                elif alert_type == "Application":
                    e_id, event = alert_event.split("__")
                    if e_id in alert_config.keys():
                        if event in alert_config[e_id]["event"]:
                            element_name = alert_config[e_id]["element_name"]
                            if alert_options[alert_event]["notification"]:
                                message = f"User '{username}' executed '{event}' in {element_name}"
                                df_log_dict = {
                                    "usergroup": group,
                                    "alert_owner": alert_owner,
                                    "alert_type": alert_type,
                                    "alert_options": "Notifications",
                                    "events": f"{element_name} - {event}",
                                    "alert_message": message,
                                    "app_code": curr_app_code,
                                    "created_by": username,
                                    "created_date": datetime.datetime.now(),
                                }
                                df_log1 = pd.DataFrame.from_dict([df_log_dict])
                                df_log = pd.concat([df_log, df_log1], ignore_index=True)
                                alert_data.append(
                                    [username, group_list, tenant, message, alert_owner, alert_exclude_user]
                                )
                            if alert_options[alert_event]["email"] and len(email_list) > 0:
                                message = f"User '{username}' executed '{event}' in {element_name}"
                                df_log_dict = {
                                    "usergroup": group,
                                    "alert_owner": alert_owner,
                                    "alert_type": alert_type,
                                    "alert_options": "Email",
                                    "events": f"{element_name} - {event}",
                                    "alert_message": message,
                                    "app_code": curr_app_code,
                                    "created_by": username,
                                    "created_date": datetime.datetime.now(),
                                }
                                df_log1 = pd.DataFrame.from_dict([df_log_dict])
                                df_log = pd.concat([df_log, df_log1], ignore_index=True)
                                send_email_alert(
                                    request,
                                    "notifications@Acies.Consulting",
                                    email_list,
                                    "Application Alert",
                                    message,
                                    username=None,
                                    approval=0,
                                )
                            continue

                elif alert_type == "Access alerts":
                    for x in alert_config:
                        if x.startswith(alert_event + "__"):
                            if alert_options[x]["notification"]:
                                message = alert_event_message(x, alert_type, username)
                                df_log_dict = {
                                    "usergroup": group,
                                    "alert_owner": alert_owner,
                                    "alert_type": alert_type,
                                    "alert_options": "Notifications",
                                    "events": x.split("__")[1],
                                    "alert_message": message,
                                    "app_code": curr_app_code,
                                    "created_by": username,
                                    "created_date": datetime.datetime.now(),
                                }
                                df_log1 = pd.DataFrame.from_dict([df_log_dict])
                                df_log = pd.concat([df_log, df_log1], ignore_index=True)
                                alert_data.append(
                                    [username, group_list, tenant, message, alert_owner, alert_exclude_user]
                                )
                            if (alert_options[x]["email"]) and len(email_list) > 0:
                                message = alert_event_message(x, alert_type, username)
                                df_log_dict = {
                                    "usergroup": group,
                                    "alert_owner": alert_owner,
                                    "alert_type": alert_type,
                                    "alert_options": "Email",
                                    "events": x.split("__")[1],
                                    "alert_message": message,
                                    "app_code": curr_app_code,
                                    "created_by": username,
                                    "created_date": datetime.datetime.now(),
                                }
                                df_log1 = pd.DataFrame.from_dict([df_log_dict])
                                df_log = pd.concat([df_log, df_log1], ignore_index=True)
                                send_email_alert(
                                    request,
                                    "notifications@Acies.Consulting",
                                    email_list,
                                    "Access alerts",
                                    message,
                                    username=None,
                                    approval=0,
                                )
                            break
                        else:
                            continue
                elif alert_type == "Unauthorized access alert":
                    if alert_options["notification"]:
                        message = alert_event
                        df_log_dict = {
                            "usergroup": group,
                            "alert_owner": alert_owner,
                            "alert_type": alert_type,
                            "alert_options": "Notifications",
                            "events": alert_event,
                            "alert_message": message,
                            "app_code": curr_app_code,
                            "created_by": username,
                            "created_date": datetime.datetime.now(),
                        }
                        df_log1 = pd.DataFrame.from_dict([df_log_dict])
                        df_log = pd.concat([df_log, df_log1], ignore_index=True)
                        alert_data.append(
                            [username, group_list, tenant, message, alert_owner, alert_exclude_user]
                        )
                    if (alert_options["email"]) and len(email_list) > 0:
                        message = alert_event
                        df_log_dict = {
                            "usergroup": group,
                            "alert_owner": alert_owner,
                            "alert_type": alert_type,
                            "alert_options": "Email",
                            "events": alert_event,
                            "alert_message": message,
                            "app_code": curr_app_code,
                            "created_by": username,
                            "created_date": datetime.datetime.now(),
                        }
                        df_log1 = pd.DataFrame.from_dict([df_log_dict])
                        df_log = pd.concat([df_log, df_log1], ignore_index=True)
                        send_email_alert(
                            request,
                            "notifications@Acies.Consulting",
                            email_list,
                            "Unauthorized access alerts",
                            message,
                            username=None,
                            approval=0,
                        )
                    continue
        else:
            continue
    pandas_push(df_log, "users_alertslog", app_engine[0])
    cursor.close()
    time.sleep(5)
    return alert_data


def log_each_appdb(group, tenant_app_code, alert_owner, alert_options, username, message):
    df_log = pd.DataFrame(
        columns=[
            "usergroup",
            "alert_owner",
            "alert_type",
            "alert_options",
            "events",
            "alert_message",
            "app_code",
            "created_by",
            "created_date",
        ]
    )
    app_db_mapping = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()
    if app_db_mapping:
        if tenant_app_code in app_db_mapping:
            df_log = df_log[0:0]
            db_connection_name = app_db_mapping[tenant_app_code]
            global database_engine_dict
            engine_dict = database_engine_dict.copy()
            if engine_dict.get(db_connection_name):
                user_db_engine, db_type = engine_dict[db_connection_name]
            else:
                user_db_engine = sql_engine_gen(db_connection_name)
            df_log_dict = {
                "usergroup": group,
                "alert_owner": alert_owner,
                "alert_type": "Failed login alerts",
                "alert_options": alert_options,
                "events": "failed_login_alerts",
                "alert_message": message,
                "app_code": tenant_app_code.split("_")[1],
                "created_by": username,
                "created_date": datetime.datetime.now(),
            }
            df_log1 = pd.DataFrame.from_dict([df_log_dict])
            df_log = pd.concat([df_log, df_log1], ignore_index=True)
            pandas_push(df_log, "users_alertslog", user_db_engine[0])


def alert_failed_function(username, tenant, failed_login_alerts, user_group_emails, all_email_list):
    failed_login_alerts = pickle.loads(failed_login_alerts)
    user_group_emails = pickle.loads(user_group_emails)
    all_email_list_main = pickle.loads(all_email_list)
    alert_data = []
    if len(failed_login_alerts) > 0:
        group_list = failed_login_alerts["usergroup"].tolist()
        group_list = list({int(x) for x in group_list})
    else:
        return []
    message = ""
    alert_owner = ""
    for group in group_list:
        alert_config_row = failed_login_alerts[failed_login_alerts["usergroup"] == str(group)]
        alert_exclude_user = alert_config_row[alert_config_row["alert_owner"] != "admin"][
            "alert_owner"
        ].tolist()

        if len(alert_config_row) > 0:
            user_group_emails_1 = user_group_emails[user_group_emails["group_id"] == group]
            if len(user_group_emails_1) > 0:
                user_group_emails_1 = list(set(user_group_emails_1["user_id"].tolist()))
                all_email_list = all_email_list_main[all_email_list_main["id"].isin(user_group_emails_1)]
            else:
                all_email_list = []
            for row in range(len(alert_config_row)):
                alert_owner = alert_config_row.iloc[row]["alert_owner"]
                if len(all_email_list) > 0:
                    if alert_owner == "admin":
                        email_list = all_email_list[~all_email_list["username"].isin(alert_exclude_user)]
                    else:
                        email_list = all_email_list[all_email_list["username"] == alert_owner]

                    if len(email_list) > 0:
                        email_list = email_list["email"].tolist()
                else:
                    email_list = []
                alert_options = json.loads(alert_config_row.iloc[row]["alert_options"])
                if alert_options["notification"]:
                    message = f"User '{username}' tried to login in Application with incorrect password"
                    log_each_appdb(
                        group,
                        tenant + "_" + alert_config_row.iloc[row]["app_code"],
                        alert_owner,
                        "Notifications",
                        username,
                        message,
                    )
                    alert_data.append(
                        [username, group_list, tenant, message, alert_owner, alert_exclude_user]
                    )
                if alert_options["email"] and len(email_list) > 0:
                    message = f"User '{username}' tried to login in Application with incorrect password"
                    log_each_appdb(
                        group,
                        tenant + "_" + alert_config_row.iloc[row]["app_code"],
                        alert_owner,
                        "Email",
                        username,
                        message,
                    )
                    send_email_alert(
                        None,
                        "notifications@Acies.Consulting",
                        email_list,
                        "Failed login Alert",
                        message,
                        username=None,
                        approval=0,
                        tenant=tenant,
                    )
                continue
        else:
            continue
    time.sleep(5)
    return alert_data


def alert_failedlogin(request, username):
    random_num = random_no_generator()
    job_id = "all_alerts_" + random_num
    tenant = tenant_schema_from_request(request)
    sql_engine = psycopg2.connect(
        dbname=central_database_config["dbname"],
        user=central_database_config["user"],
        password=central_database_config["password"],
        host=central_database_config["host"],
        port=central_database_config["port"],
    )
    cursor = sql_engine.cursor()
    cursor.execute(
        f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = 'users_failed_login_alerts' AND table_schema = 'public'"
    )
    columns_records = cursor.fetchall()
    cursor.execute(sql.SQL(f"SELECT * FROM users_failed_login_alerts;"))
    failed_login_alerts = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in np.array(columns_records)])

    cursor.execute(
        f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = 'users_user_groups' AND table_schema = 'public'"
    )
    columns_records = cursor.fetchall()
    cursor.execute(sql.SQL(f"SELECT * FROM users_user_groups;"))
    user_group_emails = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in np.array(columns_records)])

    cursor.execute(sql.SQL(f"SELECT id, email, username FROM users_user;"))
    all_email_list = pd.DataFrame(cursor.fetchall(), columns=["id", "email", "username"])
    cursor.close()
    job_kwargs = {
        "username": username,
        "tenant": tenant,
        "failed_login_alerts": pickle.dumps(failed_login_alerts),
        "user_group_emails": pickle.dumps(user_group_emails),
        "all_email_list": pickle.dumps(all_email_list),
    }
    enqueue_jobs(
        alert_failed_function,
        job_id,
        args=(),
        kwargs=job_kwargs,
        result_ttl=60,
        job_type="alerts",
        description=f"Alerts",
    )
    return True


def alert_main(request, alert_type, alert_event, curr_app_code, db_connection_name):
    if request.user.username not in ["AnonymousUser", ""]:
        job_id = "all_alerts_" + random_no_generator()
        tenant = tenant_schema_from_request(request)
        if os.path.exists(f"{PLATFORM_FILE_PATH}alerts_config.json"):
            with open(f"{PLATFORM_FILE_PATH}alerts_config.json") as json_file:
                alerts_data = json.load(json_file)
                json_file.close()
        else:
            alerts_data = {}
        if alerts_data:
            app_tenant_code = tenant + "_" + curr_app_code
            if alerts_data.get(app_tenant_code):
                if alert_type in alerts_data[app_tenant_code]:
                    if hasattr(request.user.__class__, "objects"):
                        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
                        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
                        job_kwargs = {
                            "request": request2,
                            "tenant": tenant,
                            "curr_app_code": curr_app_code,
                            "db_connection_name": db_connection_name,
                            "alert_type": alert_type,
                            "alert_event": alert_event,
                        }
                        enqueue_jobs(
                            alert_builer,
                            job_id,
                            args=(),
                            kwargs=job_kwargs,
                            result_ttl=60,
                            job_type="alerts",
                            description=f"Alerts",
                        )
    else:
        pass
    return None


def alert_json(request, alerts_data):
    alert_json = {}
    app_db_mapping = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()
    for key in app_db_mapping.keys():
        app_alert_type_list = []
        for alert_type in ["Application", "DB", "Access alerts", "Unauthorized access alert"]:
            alerts_type_data = alerts_data[alerts_data["alert_type"] == alert_type]
            if len(alerts_type_data) > 0:
                alerts_type_data = alerts_type_data["app_code"].tolist()
                if key.endswith(f"_{alerts_type_data[0]}"):
                    app_alert_type_list.append(alert_type)
        alert_json[key] = app_alert_type_list

    with open(f"{PLATFORM_FILE_PATH}alerts_config.json", "w") as json_file:
        json_file.write(json.dumps(alert_json))
        json_file.close()
    return True


def execute_read_query(sql_query, con_detail, chunksize=10**5):
    sql_query = sql_query.split(";")[0]
    sql_engine, turb_connection = con_detail
    if turb_connection not in ["", None]:
        try:
            cursor = turb_connection.cursor()
            table = cursor.execute(sql_query).fetchallarrow().to_pandas(use_threads=True)
            cursor.close()
        except Exception as e:
            logging.warning(f"Following exception occured while reading data using Turbodbc - {e}")
            table = pd.DataFrame()
            for chunk in pd.read_sql_query(sql_query, sql_engine, chunksize=chunksize):
                table = pd.concat([table, chunk], ignore_index=True)
    else:
        table = pd.DataFrame()
        for chunk in pd.read_sql_query(sql_query, sql_engine, chunksize=chunksize):
            table = pd.concat([table, chunk], ignore_index=True)
    return table


def non_standard_read_data_func(sql_query, engine2=[engine, turbodbc_connection]):
    table = execute_read_query(sql_query, engine2)
    return table
