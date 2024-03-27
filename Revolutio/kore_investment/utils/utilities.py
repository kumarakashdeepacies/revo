from datetime import datetime
import json
import logging
import os
import re

from O365 import Account
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.core.management import execute_from_command_line
from django_multitenant.utils import get_current_tenant
import pyotp

from config.settings.base import PLATFORM_FILE_PATH, env, tenant_host_mapper


def hostname_from_request(request):
    return request.get_host().split(":")[0].lower()


def tenant_schema_from_request(request, app_name=["users"]):
    tenant = "public"
    global tenant_host_mapper
    if app_name:
        if app_name[0] != "platform_admin":
            hostname = hostname_from_request(request)
            if tenant_host_mapper.get(hostname):
                tenant = tenant_host_mapper[hostname]
            else:
                tenants_map = {}
                if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
                        tenants_map = json.load(json_file)
                        json_file.close()
                else:
                    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                            tenant_data = json.load(json_file)
                            for t_name, t_config in tenant_data.items():
                                if t_config.get("urlhost"):
                                    if isinstance(t_config["urlhost"], list):
                                        for url in t_config["urlhost"]:
                                            tenants_map[url] = t_name
                                    else:
                                        tenants_map[t_config["urlhost"]] = t_name
                            json_file.close()
                    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json", "w") as out_file:
                        json.dump(tenants_map, out_file, indent=4)
                        out_file.close()
                tenant_host_mapper = tenants_map
                if tenants_map.get(hostname):
                    tenant = tenants_map[hostname]
                else:
                    pass
            if app_name[0] == "tenant_admin":
                tenant += "_admin"
            else:
                pass
        else:
            tenant = "platform_admin"
    else:
        hostname = hostname_from_request(request)
        if tenant_host_mapper.get(hostname):
            tenant = tenant_host_mapper[hostname]
        else:
            tenants_map = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
                    tenants_map = json.load(json_file)
                    json_file.close()
            else:
                if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                        tenant_data = json.load(json_file)
                        for t_name, t_config in tenant_data.items():
                            if t_config.get("urlhost"):
                                if isinstance(t_config["urlhost"], list):
                                    for url in t_config["urlhost"]:
                                        tenants_map[url] = t_name
                                else:
                                    tenants_map[t_config["urlhost"]] = t_name
                        json_file.close()
                with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json", "w") as out_file:
                    json.dump(tenants_map, out_file, indent=4)
                    out_file.close()
            tenant_host_mapper = tenants_map
            if tenants_map.get(hostname):
                tenant = tenants_map[hostname]
            else:
                pass
    return tenant


def check_password_complexity(regex, password, common_passwords):
    if re.fullmatch(regex, password) and password not in common_passwords:
        return True
    else:
        return False


def sign_up_user(request):
    instance = get_current_tenant()
    User = get_user_model()
    username = request.POST["username"].lower()
    password = request.POST["password"]
    email = request.POST["email"].lower()
    if instance.name != "public":
        username += f".{instance.name}"
    else:
        pass

    is_developer = False

    context = {}

    try:
        user = User.objects.get(username=username)
        if user:
            context["response"] = "error"
            context["message"] = "Username already exists. Please try again."
            return context
    except User.DoesNotExist:
        pass

    user = User.objects.get_or_create(
        username=username,
        password=str(make_password(password)),
        email=email,
        is_staff=True,
        is_active=True,
        is_superuser=False,
        is_developer=is_developer,
        mfa_hash=pyotp.random_base32(),
        instance_id=instance.id,
    )
    context["response"] = "success"
    context["message"] = "Singup successful. Please login to continue."
    return context


def regex_generator(
    min_length=5,
    max_length=15,
    alphanumeric="false",
    capitalLetter="false",
    lowercaseLetter="false",
    symbols="false",
    restricted_characters=[],
    allowed_characters=[],
    restrict_characters="false",
):
    regex = ""

    if capitalLetter == "true":
        regex += "(?=.*[A-Z])"
    if lowercaseLetter == "true":
        regex += "(?=.*[a-z])"
    if alphanumeric == "true":
        regex += "(?=.*[A-Za-z])(?=.*[0-9])"
    if symbols == "true":
        if restrict_characters == "true" and len(allowed_characters):
            allowed_characters = json.loads(allowed_characters)
            regex += "(?:[" + "".join(allowed_characters) + "])"
        else:
            regex += "(?=.*[_@./\\<>'\"#&+-,;:|!~`$%^&*()\\[\\]?])"
    regex += ".{" + str(min_length) + "," + str(max_length) + "}$"
    return regex


def update_user_password(request, username, password):
    User = get_user_model()
    user = User.objects.get(username=username)
    instance = get_current_tenant()
    tenant = instance.name
    (
        regex_capital_letter,
        regex_alphanumeric,
        regex_symbol,
        regex_restricted_chars,
        regex_lowercase_letter,
        regex_restrict_chars,
    ) = ("", "", "", [], "", "")
    error_msg = ""
    tenant_data = {}
    regex = ""
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
    else:
        pass
    if tenant_data.get(tenant):
        t_config = tenant_data[tenant]
        if t_config.get("regex_pattern"):
            regex = t_config["regex_pattern"]
        else:
            regex = "(^.{4,32}$)"
        password_history_length = int(t_config["password_history_length"])
        regex_capital_letter = t_config["capitalLetter"]
        regex_lowercase_letter = t_config.get("lowercaseLetter")
        regex_min_length = t_config["min_length_of_password"]
        regex_alphanumeric = t_config["alphanumeric"]
        regex_max_length = t_config["max_length_of_password"]
        regex_symbol = t_config["symbols"]
        regex_restricted_chars = t_config.get("restricted_characters")
        regex_restrict_chars = t_config.get("restrict_characters")
        common_passwords = json.loads(t_config["common_passwords"])
    else:
        pass
    if check_password_complexity(regex, password, common_passwords):
        password_history = json.loads(user.password_history)
        if user.password_history:
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
    else:
        if password in common_passwords:
            error_msg = "Password entered is too common! Please select another password."
            return False, error_msg
        error_message = "Password should contain"
        if regex_alphanumeric == "true":
            error_message += " at least one letter, atleast one number,"
        if regex_capital_letter == "true":
            error_message += " at least one Capital Letter,"
        if regex_lowercase_letter == "true":
            error_message += " at least one Lowercase Letter,"
        if regex_symbol == "true":
            error_message += " at least one Symbol,"
            if regex_restrict_chars == "true" and len(regex_restricted_chars):
                error_message = error_message.rstrip(",")
                error_message += " except [" + " , ".join(json.loads(regex_restricted_chars)) + "] ,"
        error_message = error_message.rstrip(",")
        if regex_min_length:
            error_message += " with a minimum length of " + str(regex_min_length)
        if regex_max_length:
            error_message += " and a maximum length of " + str(regex_max_length)
        return False, error_message


def send_update_email(
    to_email,
    content,
    from_email="srijanraychaudhuri@acies.consulting",
    subject="Credentials Changed for Revolutio",
):
    try:
        credentials = (
            "b99d0515-5aef-411a-af5f-fdab0a2d6206",
            "_cU62ve6R6a0~351WvI_g0wkQW9O01x3.W",
        )
        account = Account(
            credentials,
            auth_flow_type="credentials",
            tenant_id="4bf6db98-c05a-4a1e-ac6a-340dcfa47097",
        )
        if account.authenticate():
            m = account.mailbox(resource=f"{from_email}")
            m = account.new_message(resource=f"{from_email}")
            m.to.add(to_email)
            m.subject = f"{subject}"
            m.body = f"{content}"
            m.send()
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")


def create_tenant(tenant):
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json1_file:
            tenant_data = json.load(json1_file)
            if tenant_data.get(tenant):
                return False
            else:
                pass
    else:
        pass
    domain_name = env("PLATFORM_DOMAIN_NAME", default="revolutio.digital")
    t_data = {
        tenant: {
            "urlhost": [
                str(tenant) + "." + domain_name,
            ],
            "password_validity": 180,
            "min_length_of_password": 4,
            "max_length_of_password": 32,
            "alphanumeric": "false",
            "capitalLetter": "false",
            "symbols": "false",
            "lowercaseLetter": "false",
            "regex_pattern": "(^.{4,32}$)",
            "password_history_length": 3,
            "incorrect_password": 3,
            "common_passwords": "[]",
            "session_count": 5,
            "db_connection_check_interval": 1,
            "developer_mode": "True",
            "allow_user_forum": "True",
            "allow_user_planner": "True",
        }
    }
    tenant_data.update(t_data)
    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
        json.dump(tenant_data, json_file, indent=4)
        json_file.close()

    tenants_map = {}
    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
        tenants_map = json.load(json_file)
        json_file.close()
    tenants_map[str(tenant) + "." + domain_name] = tenant
    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json", "w") as outfile:
        json.dump(tenants_map, outfile, indent=4)
        outfile.close()

    if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_host.txt"):
        with open(f"{PLATFORM_FILE_PATH}allowed_host.txt", "a") as txt_data:
            txt_data.write("," + str(tenant) + "." + domain_name)
            txt_data.close()
    else:
        with open(f"{PLATFORM_FILE_PATH}allowed_host.txt", "w") as txt_data:
            txt_data.write("localhost,127.0.0.1," + str(tenant) + "." + domain_name)
            txt_data.close()
    global ALLOWED_HOSTS
    ALLOWED_HOSTS += [f"{tenant}.{domain_name}"]
    json1_file.close()
    return True


def migrate_tenant():
    migration_arguements = ["manage.py", "migrate"]
    execute_from_command_line(migration_arguements)
    return True


def delete_user(username, schema):
    if username:
        User = get_user_model()
        if isinstance(username, list):
            for i in username:
                user_object = User.objects.get(username=i)
                user_object.delete()
        else:
            user_object = User.objects.get(username=username)
            user_object.delete()
    else:
        pass
    return None
