from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import os
import shutil
import smtplib

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password

from config.settings.base import MEDIA_ROOT, PLATFORM_FILE_PATH, env
from kore_investment.users import scheduler as schedulerfunc


def tenant_schema_from_request(request, original=False):
    return "platform_admin"


def update_user_password(request, username, password):
    User = get_user_model()
    user = User.objects.get(username=username)
    password_history_length = 3
    password_history = json.loads(user.password_history)
    if user.password_history != "[]":
        reused_password = False
        for previous_password in password_history:
            if check_password(password, previous_password):
                reused_password = True
        if reused_password:
            error_msg = "Password matches old password, create a new password"
            return False, error_msg
        else:
            encrypted_password = str(make_password(password))
            user.password = encrypted_password
            no_of_passwords = len(password_history)
            if no_of_passwords < password_history_length:
                password_history.append(encrypted_password)
                password_history_to_db = json.dumps(password_history)
            else:
                password_history.pop(0)
                password_history.append(encrypted_password)
                password_history_to_db = json.dumps(password_history)
            user.password_history = password_history_to_db
    else:
        encrypted_password = str(make_password(password))
        user.password = encrypted_password
        password_history.append(encrypted_password)
        password_history_to_db = json.dumps(password_history)
        user.password_history = password_history_to_db
    user.last_password_update_date = datetime.now().strftime("%Y-%m-%d")
    user.save()
    return True, error_msg


def run_tenant_deletion_command(command):
    if command:
        deleted_host, deleted_csrf_origin = delete_tenant(command)
        delete_tenant_admin_schema(command)

    else:
        deleted_host, deleted_csrf_origin = None, None
        logging.error("No Custom Command Passed")
    return deleted_host, deleted_csrf_origin


def delete_tenant_admin_schema(command):
    command + "_admin"
    return True


def delete_tenant(tenant):
    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json1_file:
            tenant_data = json.load(json1_file)
            json1_file.close()

        if tenant in tenant_data:
            del tenant_data[tenant]
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
            json.dump(tenant_data, json_file, indent=4)
            json_file.close()

    domain_name = env("PLATFORM_DOMAIN_NAME", default="revolutio.digital")
    environment = env("KUBERNETES_ENV", default="true")
    if environment == "true":
        scheme = "https://"
    else:
        scheme = "http://"

    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
        tenants_map = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
            tenants_map = json.load(json_file)
            json_file.close()
        del_key = []
        for key, value in tenants_map.items():
            if value == tenant:
                del_key.append(key)

        for i in del_key:
            tenants_map.pop(i)

        with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json", "w") as outfile:
            json.dump(tenants_map, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_host.txt"):
        txt_data, txt_allowed_hosts = "", []
        with open(rf"{PLATFORM_FILE_PATH}allowed_host.txt") as txt_file:
            txt_data = txt_file.read()
            txt_file.close()

        if txt_data:
            txt_allowed_hosts = txt_data.split(",")
            if str(tenant) + "." + domain_name in txt_allowed_hosts:
                txt_allowed_hosts.remove(str(tenant) + "." + domain_name)

        with open(rf"{PLATFORM_FILE_PATH}allowed_host.txt", "w") as txt_file:
            txt_file.write(",".join(txt_allowed_hosts))
            txt_file.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_domains.json"):
        allowed_domains = []
        with open(f"{PLATFORM_FILE_PATH}allowed_domains.json") as json_file:
            allowed_domains = json.load(json_file)
            json_file.close()
        if f"{scheme}{tenant}.{domain_name}" in allowed_domains:
            allowed_domains.remove(f"{scheme}{tenant}.{domain_name}")
        with open(f"{PLATFORM_FILE_PATH}allowed_domains.json", "w") as outfile:
            json.dump(allowed_domains, outfile)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        user_dbs, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            user_dbs = json.load(json_file)
            json_file.close()

        for key, value in user_dbs.items():
            if value["tenant"] == tenant:
                del_key.append(key)

        for i in del_key:
            user_dbs.pop(i)

        with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
            json.dump(user_dbs, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        app_database_mapping, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_database_mapping = json.load(json_file)
            json_file.close()

        for key, value in app_database_mapping.items():
            if tenant in key:
                del_key.append(key)

        for i in del_key:
            app_database_mapping.pop(i)

        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json", "w") as outfile:
            json.dump(app_database_mapping, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}recently_used_dashboard.json"):
        recently_used_dashboard, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}recently_used_dashboard.json") as json_file:
            recently_used_dashboard = json.load(json_file)
            json_file.close()

        for key, value in recently_used_dashboard.items():
            if tenant in key:
                del_key.append(key)

        for i in del_key:
            recently_used_dashboard.pop(i)

        with open(f"{PLATFORM_FILE_PATH}recently_used_dashboard.json", "w") as outfile:
            json.dump(recently_used_dashboard, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}recently_used_apps.json"):
        recently_used_apps, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}recently_used_apps.json") as json_file:
            recently_used_apps = json.load(json_file)
            json_file.close()

        for key, value in recently_used_apps.items():
            if tenant in key:
                del_key.append(key)

        for i in del_key:
            recently_used_apps.pop(i)

        with open(f"{PLATFORM_FILE_PATH}recently_used_apps.json", "w") as outfile:
            json.dump(recently_used_apps, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
        ldap_configs = {}
        with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
            ldap_configs = json.load(json_file)
            json_file.close()

        if tenant in ldap_configs:
            del ldap_configs[tenant]

        with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json", "w") as outfile:
            json.dump(ldap_configs, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}hidden_apps.json"):
        hidden_apps, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}hidden_apps.json") as json_file:
            hidden_apps = json.load(json_file)
            json_file.close()

        for key, value in hidden_apps.items():
            if tenant in key:
                del_key.append(key)

        for i in del_key:
            hidden_apps.pop(i)

        with open(f"{PLATFORM_FILE_PATH}hidden_apps.json", "w") as outfile:
            json.dump(hidden_apps, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}external_app_database_mapping.json"):
        external_app_database_mapping, del_key = {}, []
        with open(f"{PLATFORM_FILE_PATH}external_app_database_mapping.json") as json_file:
            external_app_database_mapping = json.load(json_file)
            json_file.close()

        for key, value in external_app_database_mapping.items():
            if tenant in key:
                del_key.append(key)

        for i in del_key:
            external_app_database_mapping.pop(i)

        with open(f"{PLATFORM_FILE_PATH}external_app_database_mapping.json", "w") as outfile:
            json.dump(external_app_database_mapping, outfile, indent=4)
            outfile.close()

    if os.path.exists(f"{MEDIA_ROOT}/{tenant}"):
        shutil.rmtree(f"{MEDIA_ROOT}/{tenant}")

    if os.path.exists(f"kore_investment/templates/user_defined_template/{tenant}"):
        shutil.rmtree(f"kore_investment/templates/user_defined_template/{tenant}")

    job_id = f"DB_health_check_{tenant}"
    tenant_inactive_user_scheduler_job = str(tenant) + "_inactive_user_scheduler_job"
    tenant_delete_user_scheduler_job = str(tenant) + "_delete_user_scheduler_job"

    schedulerfunc.delete_scheduler(job_id)
    schedulerfunc.delete_scheduler(tenant_inactive_user_scheduler_job)
    schedulerfunc.delete_scheduler(tenant_delete_user_scheduler_job)

    global ALLOWED_HOSTS
    if f"{tenant}.{domain_name}" in ALLOWED_HOSTS:
        ALLOWED_HOSTS.remove(f"{tenant}.{domain_name}")
    global CSRF_TRUSTED_ORIGINS
    if f"{scheme}{tenant}.{domain_name}" in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.remove(f"{scheme}{tenant}.{domain_name}")
    return (f"{tenant}.{domain_name}", f"{scheme}{tenant}.{domain_name}")


def send_Emails(request, from_user, to_user, subject, content, username=None, approval=0):
    mimemsg = MIMEMultipart()
    mimemsg["To"] = ", ".join(to_user)
    mimemsg["Subject"] = subject
    html = """\
        <html>
        <head></head>
        <body>
            <p>$(message_body)</p>
            $(reset_url)$(en_uname)
        </body>
        </html>
        """

    if username:
        html = html.replace("$(message_body)", content)
        reset_url = request.build_absolute_uri("/platform_admin/accounts/password/new_password/")
        if request.scheme == "https":
            reset_url.replace("http", "https")
        html = html.replace("$(reset_url)", reset_url)
        html = html.replace("$(en_uname)", username + "/")
    else:
        html = html.replace("$(message_body)", content)
        html = html.replace("$(reset_url)", "")
        html = html.replace("$(en_uname)", "")

    smtp_host = "smtp.office365.com"
    smtp_host_user = "notifications@acies.holdings"
    smtp_host_password = "Fus85757"
    smtp_port = 587

    mimemsg["From"] = from_user
    mimemsg.attach(MIMEText(html, "html"))
    connection = smtplib.SMTP(host=smtp_host, port=smtp_port)
    connection.ehlo()
    connection.starttls()
    connection.ehlo()
    connection.login(smtp_host_user, smtp_host_password)
    connection.send_message(mimemsg)
    connection.quit()

    return None
