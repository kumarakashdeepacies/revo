from datetime import datetime
import json
import logging
import os
import re

from O365 import Account
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password

from config.settings.base import PLATFORM_FILE_PATH


def hostname_from_request(request):
    return request.get_host().split(":")[0].lower()


def tenant_schema_from_request(request, original=False):
    hostname = hostname_from_request(request)
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
    if tenants_map.get(hostname):
        schema = tenants_map.get(hostname)
        if not original:
            schema += "_admin"
        return schema
    else:
        if not original:
            return "public_admin"
        else:
            return "public"


def check_password_complexity(regex, password, common_passwords):
    if re.fullmatch(regex, password) and password not in common_passwords:
        return True
    else:
        return False


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
    tenant = tenant_schema_from_request(request)
    (
        regex_capital_letter,
        regex_alphanumeric,
        regex_symbol,
        regex_restricted_chars,
        regex_lowercase_letter,
        regex_restrict_chars,
    ) = ("", "", "", [], "", "")
    error_msg = ""
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data = {}
        regex = ""
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == tenant:
                    regex = t_config["regex_pattern"]
                    password_history_length = int(t_config["password_history_length"])
                    regex_capital_letter = t_config["capitalLetter"]
                    regex_lowercase_letter = t_config["lowercaseLetter"]
                    regex_min_length = t_config["min_length_of_password"]
                    regex_alphanumeric = t_config["alphanumeric"]
                    regex_max_length = t_config["max_length_of_password"]
                    regex_symbol = t_config["symbols"]
                    regex_restricted_chars = t_config.get("restricted_characters")
                    regex_restrict_chars = t_config.get("restrict_characters")
                    common_passwords = json.loads(t_config["common_passwords"])
            json_file.close()
    if check_password_complexity(regex, password, common_passwords):
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
    from_email="notifications@acies.consulting",
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


def check_password_complexity(regex, password, common_passwords):
    if re.fullmatch(regex, password) and password not in common_passwords:
        return True
    else:
        return False
