import base64
from datetime import datetime, timedelta
import json
import logging
import os
import pickle
import random
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from allauth.account.forms import ChangePasswordForm, LoginForm, ResetPasswordKeyForm
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_multitenant.utils import get_current_tenant
import numpy as np
import pandas as pd

from config.settings.base import PLATFORM_FILE_PATH, env, redis_instance
from kore_investment.users.computations import standardised_functions
from tenant_admin.db_centralised_function import postgres_push, read_data_func, update_data_func
from tenant_admin.utilities import check_password_complexity, tenant_schema_from_request


def decrypt_hashing(enc, key, iv):
    enc = base64.b64decode(enc)
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc), 16)


def user_login(request):

    if request.method == "POST":
        username = request.POST.get("login")
        username = username.lower()
        password = request.POST.get("password")
        h_val = ""
        k_val = ""

        if "h_value" in request.session:
            h_val = request.session["h_value"]
            del request.session["h_value"]

        if "k_value" in request.session:
            k_val = request.session["k_value"]
            del request.session["k_value"]

        username = request.POST.get("login")
        username = decrypt_hashing(username, k_val, h_val.encode("utf-8"))
        username = username.decode("utf-8", "ignore")
        password = decrypt_hashing(password, k_val, h_val.encode("utf-8"))
        password = password.decode("utf-8", "ignore")
        current_tenant = get_current_tenant()
        tenant = current_tenant.name

        username += f".{tenant}"

        deactivated_tenant_data = {}
        deactivated_tenant = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}deactivated_tenants.json"):
            with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json") as json_file:
                deactivated_tenant = json.load(json_file)
                json_file.close()

        if tenant in deactivated_tenant:
            deactivated_tenant_data = deactivated_tenant[tenant]
            reactivate_option = deactivated_tenant_data["reactivate_option"]
            deactivated_time = deactivated_tenant_data["deactivated_time"]
            deactivated_time = datetime.strptime(deactivated_time, "%Y-%m-%d %H:%M:%S")

            if reactivate_option == "custom":
                reactivation_days = deactivated_tenant_data["reactivation_days"]
                reactivation_hours = deactivated_tenant_data["reactivation_hours"]
                reactivation_minutes = deactivated_tenant_data["reactivation_minutes"]
            elif reactivate_option == "manually":
                messages.error(
                    request, "Tenant is currently deactivated. Please contact the platform administrator."
                )
                return HttpResponseRedirect("/applicationlogin/")
            else:
                pass

            reactivation_time = deactivated_time + timedelta(
                days=int(reactivation_days), hours=int(reactivation_hours), minutes=int(reactivation_minutes)
            )

            if datetime.now() >= reactivation_time:
                del deactivated_tenant[tenant]

                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json", "w") as json1_file:
                    json.dump(deactivated_tenant, json1_file, indent=4, default=str)
                    json1_file.close()

            else:
                messages.error(
                    request, "Tenant is currently deactivated. Please contact the platform administrator."
                )
                return HttpResponseRedirect("/tenant_admin/accounts/login/")

        is_active = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "user",
                    "Columns": [
                        "is_active",
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
        )
        if len(is_active):
            if not is_active.is_active.values[0]:
                message = getMessage(request, "account_locked_message")
                if message is None:
                    messages.error(request, "Your account is locked")
                else:
                    messages.error(request, message)
                return HttpResponseRedirect("/tenant_admin/accounts/login/")
        user = authenticate(request, username=username, password=password)
        tenant_data = {}
        schema = tenant_schema_from_request(request, original=True)
        session_count = 2
        user_password_fail_count_name = schema + "_" + username + "_" + "failed_password_count"
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                for t_name, t_config in tenant_data.items():
                    if t_name == schema:
                        if (
                            t_config.get("password_validity")
                            and t_config.get("incorrect_password")
                            and t_config.get("common_passwords")
                            and t_config.get("session_count")
                            and t_config.get("developer_mode")
                            and t_config.get("allow_user_forum")
                            and t_config.get("allow_user_planner")
                        ):
                            password_validity_in_days = t_config["password_validity"]
                            max_login_failure_allowed = t_config["incorrect_password"]
                            session_count = t_config["session_count"]
                        else:
                            password_validity_in_days = 180
                            max_login_failure_allowed = 3
                            t_config["password_validity"] = 180
                            t_config["min_length_of_password"] = 4
                            t_config["max_length_of_password"] = 32
                            t_config["alphanumeric"] = "false"
                            t_config["capitalLetter"] = "false"
                            t_config["lowercaseLetter"] = "false"
                            t_config["symbols"] = "false"
                            t_config["regex_pattern"] = "(^.{4,32}$)"
                            t_config["password_history_length"] = 3
                            t_config["incorrect_password"] = 3
                            t_config["common_passwords"] = "[]"
                            t_config["session_count"] = session_count
                            t_config["developer_mode"] = "True"
                            t_config["allow_user_forum"] = "True"
                            t_config["allow_user_planner"] = "True"
                            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                                json.dump(tenant_data, json_file, indent=4)
                                json_file.close()
                            if t_config.get("db_connection_check_interval"):
                                t_config["db_connection_check_interval"]
                json_file.close()
        else:
            json_data = {
                schema: {
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
                    "session_count": session_count,
                    "db_connection_check_interval": 1,
                    "developer_mode": "True",
                    "allow_user_forum": "True",
                    "allow_user_planner": "True",
                }
            }
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                json.dump(json_data, json_file, indent=4)
                json_file.close()
            password_validity_in_days = 180
            max_login_failure_allowed = 3
        if user is not None:
            if user.is_active:
                date_user = np.array(user.last_password_update_date).astype("datetime64[D]")
                date_now = np.array(datetime.now()).astype("datetime64[D]")
                days_difference = (date_now - date_user).astype("int")
                days_difference = int(days_difference)
                if (days_difference) > password_validity_in_days:
                    form = ChangePasswordForm()
                    data = {"form": form, "username": username}

                    update_session_auth_hash(request, user)
                    messages.error(request, "Password expired- please update your password")

                    data.update(getConfig(request))

                    return render(request, "tenant_admin/account/password_change.html", data)
                elif user.last_login is None:
                    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                        tenant_data_file = {}
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                            data_file = json.load(json_file)
                            json_file.close()
                        for t_name, t_config in data_file.items():
                            if t_name == tenant_schema_from_request(request, original=True):
                                tenant_data_file = t_config
                    form = ChangePasswordForm()
                    if "terms_conditions_mandatory" in tenant_data_file.keys():
                        data = {
                            "form": form,
                            "username": username,
                            "tenant_data": tenant_data_file["terms_conditions_mandatory"],
                        }
                    else:
                        data = {"form": form, "username": username, "tenant_data": "terms_at_every_login"}
                    if "addTermsAndCondition" in tenant_data_file.keys():
                        if tenant_data_file["addTermsAndCondition"] == "True":
                            if "termsAndConditions" in tenant_data_file.keys():
                                data.update(
                                    {"termsandConditionsfromTenant": tenant_data_file["termsAndConditions"]}
                                )
                        else:
                            with open(f"kore_investment/templates/accounts_base/terms.html") as terms_file:
                                terms_data = terms_file.read()
                                data.update({"termsandConditionsfromTenant": terms_data})
                                terms_file.close()
                    update_session_auth_hash(request, user)
                    messages.error(request, "Please set a new password for your account")

                    data.update(getConfig(request))
                    return render(request, "tenant_admin/account/password_change.html", data)
                else:
                    ss = []
                    sessions = Session.objects.filter(expire_date__gte=timezone.now()).order_by(
                        "-expire_date"
                    )
                    temp = 0
                    for s in sessions:
                        if str(s.get_decoded().get("_auth_user_id")) == str(user.id):
                            if temp < session_count:
                                ss.append(s.session_key)
                                temp = temp + 1
                    ss.reverse()
                    login(request, user)
                    new_template = {
                        "session_id": request.session.session_key,
                        "user_name": request.user.username,
                        "time_logged_in": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ip": request.META.get("REMOTE_ADDR"),
                        "instance_id": current_tenant.id,
                    }
                    new_template = pd.DataFrame([new_template])
                    postgres_push(new_template, "users_login_trail", schema, app_db_transaction=False)
                    if redis_instance.exists(user_password_fail_count_name):
                        redis_instance.delete(user_password_fail_count_name)
                    if len(ss) >= session_count:
                        session_schema = schema + "_admin"
                        logout_user(ss, username, request, session_schema)
                    return HttpResponseRedirect("/tenant_admin/")
            else:
                # Return a 'disabled account' error message
                message = getMessage(request, "user_inactive_message")
                if message is None:
                    messages.error(request, "User is not active")
                else:
                    messages.error(request, message)
                return HttpResponseRedirect("/tenant_admin/accounts/login/")
        else:
            # Return an 'invalid login' error message.
            user_id = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "user",
                        "Columns": [
                            "id",
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
            )
            if user_id.empty:
                message = getMessage(request, "invalid_username_message")
                if message is None:
                    messages.error(request, "Invalid username")
                else:
                    messages.error(request, message)
                return HttpResponseRedirect("/tenant_admin/accounts/login/")
            else:
                if redis_instance.exists(user_password_fail_count_name):
                    fail_count = int(redis_instance.get(user_password_fail_count_name))
                    fail_count += 1
                    redis_instance.set(user_password_fail_count_name, fail_count)
                    if fail_count >= max_login_failure_allowed:
                        update_data_func(
                            request,
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
                                        "column_name": "username",
                                        "condition": "Equal to",
                                        "input_value": username,
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                        message = getMessage(request, "exceeding_attempts_message")
                        if message is None:
                            messages.error(
                                request, "Maximum failed Login attempts made. Your account is locked"
                            )
                        else:
                            messages.error(request, message)
                        return HttpResponseRedirect("/tenant_admin/accounts/login/")
                    message = getMessage(request, "invalid_password_message")
                    if message is None:
                        error_message = "Invalid password. Remaining attempts: " + str(
                            max_login_failure_allowed - fail_count
                        )
                    else:
                        error_message = message.replace(
                            "{Remaining attemps}", str(max_login_failure_allowed - fail_count)
                        )
                    messages.error(request, error_message)
                    return HttpResponseRedirect("/tenant_admin/accounts/login/")
                else:
                    redis_instance.set(user_password_fail_count_name, 1)
                    message = getMessage(request, "invalid_password_message")
                    if message is None:
                        error_message = "Invalid password. Remaining attempts: " + str(
                            max_login_failure_allowed - 1
                        )
                    else:
                        error_message = message.replace(
                            "{Remaining attemps}", str(max_login_failure_allowed - 1)
                        )
                    messages.error(request, error_message)
                    return HttpResponseRedirect("/tenant_admin/accounts/login/")
    else:
        # the login is a  GET request, so just show the user the login form.

        update_session_auth_hash(request, request.user)
        form = LoginForm()
        data = {"form": form}
        hash_val = "".join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16)
        )
        key_val = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        data["h_value"] = hash_val
        data["k_value"] = key_val
        request.session["h_value"] = hash_val
        request.session["k_value"] = key_val
        tenant = tenant_schema_from_request(request, original=True)
        tenant_data = {}
        tenant_host_data = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                t_config = tenant_data[tenant]
                if t_config.get("mfa_configs"):
                    if t_config["mfa_configs"].get("mfa_password") is not None:
                        data["mfa_password"] = t_config["mfa_configs"]["mfa_password"]

                    if t_config["mfa_configs"].get("mfa_otp") is not None:
                        data["mfa_otp"] = t_config["mfa_configs"]["mfa_otp"]

                if t_config.get("remembermeConfig"):
                    if t_config["remembermeConfig"].get("always_rememberme") is not None:
                        data["always_rememberme"] = t_config["remembermeConfig"]["always_rememberme"]

                    if t_config["remembermeConfig"].get("dont_rememberme") is not None:
                        data["dont_rememberme"] = t_config["remembermeConfig"]["dont_rememberme"]

                    if t_config["remembermeConfig"].get("timed_rememberme") is not None:
                        data["timed_rememberme"] = t_config["remembermeConfig"]["timed_rememberme"]

        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
                tenant_host_data = json.load(json_file)
                json_file.close()

        hostname = request.get_host().split(":")[0].lower()
        if hostname not in tenant_host_data:
            redirect_url = request.scheme + "://"
            public_urls = tenant_data["public"]["urlhost"]
            domain = env("PLATFORM_DOMAIN_NAME", default="revolutio.digital")
            matched_url = [i for i in public_urls if i.endswith(domain)]
            if matched_url:
                redirect_url += matched_url[0]
            else:
                port = request.get_host().split(":")[1].lower()
                redirect_url += public_urls[0]
                redirect_url += ":" + port
            return HttpResponseRedirect(redirect_url)
        else:
            pass

        data.update(getConfig(request))
        return render(request, f"tenant_admin/account/login.html", data)


def update_password(request):
    username = request.user.username
    username = username.lower()
    form = ChangePasswordForm()
    data = {"form": form, "username": username}
    if request.method == "POST":
        oldpassword = request.POST.get("oldpassword")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if not username:
            username = request.POST.get("username")
        data["username"] = username
        if password1 == password2:
            tenant = tenant_schema_from_request(request, original=True)
            (
                regex_capital_letter,
                regex_alphanumeric,
                regex_symbol,
                regex_restricted_chars,
                regex_lowercase_letter,
                regex_restrict_chars,
            ) = ("", "", "", [], "", "")
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                regex = "(^.{4,32}$)"
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()
                t_config = tenant_data[tenant]
                if t_config.get("regex_pattern") and t_config.get("password_history_length"):
                    regex = t_config["regex_pattern"]
                    password_history_length = int(t_config["password_history_length"])
                    regex_capital_letter = t_config["capitalLetter"]
                    regex_lowercase_letter = t_config.get("lowercaseLetter", "false")
                    regex_min_length = t_config["min_length_of_password"]
                    regex_alphanumeric = t_config["alphanumeric"]
                    regex_max_length = t_config["max_length_of_password"]
                    regex_symbol = t_config["symbols"]
                    regex_restricted_chars = t_config.get("restricted_characters")
                    common_passwords = json.loads(t_config["common_passwords"])
                    regex_restrict_chars = t_config.get("restrict_characters")
                else:
                    password_history_length = 3
                    regex = "(^.{4,32}$)"
                    common_passwords = []
                    regex_capital_letter = "false"
                    regex_lowercase_letter = "false"
                    regex_min_length = 4
                    regex_alphanumeric = "false"
                    regex_max_length = 32
                    regex_restrict_chars = "false"
                    regex_symbol = "false"
                    regex_restricted_chars = []
            if password1 == username:
                message = getMessage(request, "pass_match_user_message")
                if message is None:
                    messages.error(request, "Username and Password cannot be the same")
                else:
                    messages.error(request, message)

                data.update(getConfig(request))
                return render(request, "tenant_admin/account/password_change.html", data)
            if check_password_complexity(regex, password1, common_passwords):

                password_data_from_db = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user",
                            "Columns": [
                                "password_history",
                                "password",
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
                )
                password_history_from_db = password_data_from_db.iloc[0, 0]
                last_password = password_data_from_db.iloc[0, 1]
                if not check_password(oldpassword, last_password):
                    message = getMessage(request, "invalid_current_password_message")
                    if message is None:
                        messages.error(request, "Current Password entered is not correct")
                    else:
                        messages.error(request, message)

                    data.update(getConfig(request))
                    return render(request, "tenant_admin/account/password_change.html", data)
                password_history = json.loads(password_history_from_db)
                if password_history_from_db != "[]":
                    reused_password = False
                    for previous_password in password_history:
                        if check_password(password1, previous_password):
                            reused_password = True
                    if reused_password:
                        # password matches old password
                        message = getMessage(request, "new_pass_old_pass_message")
                        if message is None:
                            messages.error(request, "Password matches old password, create a new password")
                        else:
                            messages.error(request, message)

                        data.update(getConfig(request))
                        return render(request, "tenant_admin/account/password_change.html", data)
                    else:
                        encrypted_password = str(make_password(password1))
                        no_of_passwords = len(password_history)
                        if no_of_passwords < password_history_length:
                            password_history.append(encrypted_password)
                            password_history_to_db = json.dumps(password_history)
                        else:
                            password_history.pop(0)
                            password_history.append(encrypted_password)
                            password_history_to_db = json.dumps(password_history)
                        update_data_func(
                            request,
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "User",
                                    "Columns": [
                                        {
                                            "column_name": "password",
                                            "input_value": encrypted_password,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "password_history",
                                            "input_value": password_history_to_db,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "last_password_update_date",
                                            "input_value": datetime.now().strftime("%Y-%m-%d"),
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "last_login",
                                            "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
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
                        )
                else:
                    # password history is []
                    encrypted_password = str(make_password(password1))
                    password_history.append(encrypted_password)
                    password_history_to_db = json.dumps(password_history)
                    update_data_func(
                        request,
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "User",
                                "Columns": [
                                    {
                                        "column_name": "password",
                                        "input_value": encrypted_password,
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "password_history",
                                        "input_value": password_history_to_db,
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "last_password_update_date",
                                        "input_value": datetime.now().strftime("%Y-%m-%d"),
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "last_login",
                                        "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
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
                    )
                messages.success(request, "Password updated successfully. Please log in again")
                return HttpResponseRedirect("/tenant_admin/accounts/login/")
            else:
                # complexity fail
                if password1 in common_passwords:
                    message = getMessage(request, "password_common_message")
                    if message is None:
                        messages.error(
                            request, "Password entered is too common! Please select another password"
                        )
                    else:
                        messages.error(request, message)

                    data.update(getConfig(request))
                    return render(request, "tenant_admin/account/password_change.html", data)
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
                messages.error(request, error_message)

                data.update(getConfig(request))
                return render(request, "tenant_admin/account/password_change.html", data)

        else:
            # password1 doesn't match password2
            message = getMessage(request, "passwords_donotmatch_message")
            if message is None:
                messages.error(request, "Passwords do not match")
            else:
                messages.error(request, message)

            data.update(getConfig(request))
            return render(request, "tenant_admin/account/password_change.html", data)

    # request type is not POST
    data.update(getConfig(request))
    return render(request, "tenant_admin/account/password_change.html", data)


def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/tenant_admin/accounts/login/")


def logout_user(session_list, username, request, schema):
    found_delete = False
    device = request.META["HTTP_USER_AGENT"]
    ip = request.META.get("REMOTE_ADDR")
    for i in session_list:
        try:
            s = Session.objects.get(session_key=i)
        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        else:
            found_delete = True
            s.delete()
            update_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "login_trail",
                        "Columns": [
                            {
                                "column_name": "time_logged_out",
                                "input_value": datetime.now(),
                                "separator": ",",
                            },
                            {
                                "column_name": "logout_type",
                                "input_value": "Auto",
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "session_id",
                            "condition": "Equal to",
                            "input_value": i,
                            "and_or": "",
                        }
                    ],
                },
            )
            if redis_instance.exists(schema + "mulsession" + username) == 1:
                user_login_info = pickle.loads(redis_instance.get(schema + "mulsession" + username))
                user_login_info["session_key"] = i
                user_login_info["device"] = device
                user_login_info["ip"] = ip
            else:
                user_login_info = {}
                user_login_info["username"] = username
                user_login_info["session_key"] = i
                user_login_info["device"] = device
                user_login_info["ip"] = ip

            redis_instance.set(schema + "mulsession" + username, pickle.dumps(user_login_info))
        break

    return found_delete


def reset_password_new(request):
    data = {}
    data["username"] = request.POST.get("reset_email_username")
    if request.method == "POST":
        username = request.POST["reset_email_username"]
        username = username.lower()
        current_tenant = get_current_tenant()
        tenant = current_tenant.name
        username += f".{tenant}"

        schema = tenant_schema_from_request(request, original=True)
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                for t_name, t_config in tenant_data.items():
                    if t_name == schema:
                        if (
                            t_config.get("smtp_host")
                            and t_config.get("smtp_host_user")
                            and t_config.get("smtp_host_password")
                            and t_config.get("smtp_port")
                            and t_config.get("smtp_allow_reset")
                        ):
                            smtp_host_user = t_config["smtp_host_user"]
                            smtp_msg_content = t_config["smtp_msg_content"]
                            smtp_default_message = t_config["smtp_default_message"]
                            if not smtp_default_message:
                                smtp_default_message = (
                                    "Please contact your administrator for resetting your password"
                                )
                            smtp_allow_reset = t_config["smtp_allow_reset"]
                        else:
                            return JsonResponse(
                                {
                                    "data": "error",
                                    "msg": "Configuration for SMTP not found. Please contact your administrator.",
                                }
                            )
                json_file.close()
        else:
            return JsonResponse(
                {
                    "data": "error",
                    "msg": "Configuration for SMTP not found. Please contact your administrator.",
                }
            )

        username_data_from_db = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "user",
                    "Columns": [
                        "username",
                        "email",
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
        )
        if username_data_from_db.empty:
            return JsonResponse({"data": "error", "msg": "The username specified is not correct."})

        else:
            user_email = username_data_from_db.iloc[0, 1]
            if user_email:
                if smtp_allow_reset == "true":
                    encoded_username = urlsafe_base64_encode(force_bytes(username))
                    standardised_functions.send_Emails(
                        request,
                        smtp_host_user,
                        [user_email],
                        "Password Reset Notification",
                        smtp_msg_content,
                        encoded_username,
                        tenant_id="tenant_admin",
                    )

                    return JsonResponse({"data": "success", "msg": ""})
                else:
                    return JsonResponse({"data": "error", "msg": smtp_default_message})
            else:
                return JsonResponse(
                    {"data": "error", "msg": "The email id for the specified username is not present."}
                )
    else:
        return HttpResponseRedirect("tenant_admin/accounts/password/reset_p/")


def reset_update_password(request, username=None):
    form = ResetPasswordKeyForm()
    data = {"form": form, "username": username}

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        username = str(urlsafe_base64_decode(username), "utf-8")
        username = username.lower()
        data["username"] = username
        if password1 == password2:
            tenant = tenant_schema_from_request(request, original=True)
            common_passwords = []
            password_history_length = 3
            regex_capital_letter = "false"
            regex_lowercase_letter = "false"
            regex_min_length = 4
            regex_alphanumeric = "false"
            regex_max_length = 32
            regex_symbol = "false"
            regex_restrict_chars = "false"
            regex_restricted_chars = []
            regex_restricted_chars = t_config.get("restricted_characters")
            tenant_data = {}
            regex = "(^.{4,32}$)"

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()
            else:
                pass
            if tenant_data.get(tenant):
                t_config = tenant_data[tenant]
                if (
                    t_config.get("regex_pattern")
                    and t_config.get("password_history_length")
                    and t_config.get("capitalLetter")
                    and t_config.get("lowercaseLetter")
                    and t_config.get("min_length_of_password")
                    and t_config.get("alphanumeric")
                    and t_config.get("max_length_of_password")
                    and t_config.get("symbols")
                    and t_config.get("common_passwords")
                ):
                    regex = t_config["regex_pattern"]
                    password_history_length = int(t_config["password_history_length"])
                    regex_capital_letter = t_config["capitalLetter"]
                    regex_lowercase_letter = t_config.get("lowercaseLetter", "false")
                    regex_min_length = t_config["min_length_of_password"]
                    regex_alphanumeric = t_config["alphanumeric"]
                    regex_max_length = t_config["max_length_of_password"]
                    regex_symbol = t_config["symbols"]
                    regex_restricted_chars = t_config.get("restricted_characters")
                    common_passwords = json.loads(t_config["common_passwords"])
                    regex_restrict_chars = t_config.get("restrict_characters")
                else:
                    pass
            else:
                pass

            if password1 == username:
                message = getMessage(request, "pass_match_user_message")
                if message is None:
                    message = "Username and Password cannot be the same"

                return JsonResponse({"data": "error", "msg": message})
            if check_password_complexity(regex, password1, common_passwords):

                password_data_from_db = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user",
                            "Columns": [
                                "password_history",
                                "password",
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
                )
                password_history_from_db = password_data_from_db.iloc[0, 0]
                password_history = json.loads(password_history_from_db)
                if password_history_from_db != "[]":
                    reused_password = False
                    for previous_password in password_history:
                        if check_password(password1, previous_password):
                            reused_password = True
                    if reused_password:
                        # password matches old password
                        message = getMessage(request, "new_pass_old_pass_message")
                        if message is None:
                            message = "Password matches old password, create a new password"

                        return JsonResponse({"data": "error", "msg": message})

                    encrypted_password = str(make_password(password1))
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "user",
                                "Columns": [
                                    {
                                        "column_name": "password",
                                        "input_value": encrypted_password,
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
                    )
                    no_of_passwords = len(password_history)
                    if no_of_passwords < password_history_length:
                        password_history.append(encrypted_password)
                        password_history_to_db = json.dumps(password_history)
                    else:
                        password_history.pop(0)
                        password_history.append(encrypted_password)
                        password_history_to_db = json.dumps(password_history)
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "user",
                                "Columns": [
                                    {
                                        "column_name": "password_history",
                                        "input_value": password_history_to_db,
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
                    )

                else:
                    # password history is []
                    encrypted_password = str(make_password(password1))
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "user",
                                "Columns": [
                                    {
                                        "column_name": "password",
                                        "input_value": encrypted_password,
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
                    )
                    password_history.append(encrypted_password)
                    password_history_to_db = json.dumps(password_history)
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "user",
                                "Columns": [
                                    {
                                        "column_name": "password_history",
                                        "input_value": password_history_to_db,
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
                    )
                # update last password update date regardless of password history length
                update_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user",
                            "Columns": [
                                {
                                    "column_name": "last_password_update_date",
                                    "input_value": datetime.now().strftime("%Y-%m-%d"),
                                    "separator": ",",
                                },
                                {
                                    "column_name": "last_login",
                                    "input_value": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
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
                )
                return JsonResponse(
                    {"data": "success", "msg": "Password reset successfully. Please log in again."}
                )
            else:
                # complexity fail
                if password1 in common_passwords:
                    message = getMessage(request, "password_common_message")
                    if message is None:
                        message = "Password entered is too common! Please select another password"
                    return JsonResponse({"data": "error", "msg": message})
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
                return JsonResponse({"data": "error", "msg": error_message})
        else:
            message = getMessage(request, "passwords_donotmatch_message")
            if message is None:
                message = "Passwords doesn't match"
            return JsonResponse({"data": "error", "msg": message})
    else:
        data.update(getConfig(request))
        return render(request, "tenant_admin/account/password_reset_from_key.html", data)


def getMessage(request, key):
    tenant = tenant_schema_from_request(request, original=True)
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
        t_config = tenant_data[tenant]

        if t_config.get("customLoginMessages"):
            if key in t_config["customLoginMessages"]:
                return t_config["customLoginMessages"][key]


def getConfig(request):
    tenant = tenant_schema_from_request(request, original=True)
    outputData = {}
    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
        t_config = tenant_data[tenant]

        outputData["tenant"] = tenant

        if "remove_all_social" in t_config:
            outputData["remove_all_social"] = t_config["remove_all_social"]
        if "remove_facebook" in t_config:
            outputData["remove_facebook"] = t_config["remove_facebook"]
        if "remove_google" in t_config:
            outputData["remove_google"] = t_config["remove_google"]
        if "remove_microsoft" in t_config:
            outputData["remove_microsoft"] = t_config["remove_microsoft"]
        if "remove_twitter" in t_config:
            outputData["remove_twitter"] = t_config["remove_twitter"]
        if "remove_amazon" in t_config:
            outputData["remove_amazon"] = t_config["remove_amazon"]
        if "remove_apple" in t_config:
            outputData["remove_apple"] = t_config["remove_apple"]
        if "signup_header" in t_config:
            outputData["signup_header"] = t_config["signup_header"]
        if "signup_msg" in t_config:
            outputData["signup_msg"] = t_config["signup_msg"]
        if "rename_username" in t_config:
            outputData["rename_username"] = t_config["rename_username"]
        if "rename_email" in t_config:
            outputData["rename_email"] = t_config["rename_email"]
        if "rename_password" in t_config:
            outputData["rename_password"] = t_config["rename_password"]
        if "rename_confirm_password" in t_config:
            outputData["rename_confirm_password"] = t_config["rename_confirm_password"]
        if t_config.get("remove_signup"):
            outputData["remove_signup"] = t_config["remove_signup"]
        if t_config.get("remove_remember_me"):
            outputData["remove_remember_me"] = t_config["remove_remember_me"]
        if t_config.get("remove_terms"):
            outputData["remove_terms"] = t_config["remove_terms"]
        if t_config.get("remove_admin_toggle"):
            outputData["remove_admin_toggle"] = t_config["remove_admin_toggle"]
        if t_config.get("block_autocomplete_credentials"):
            outputData["block_autocomplete_credentials"] = t_config["block_autocomplete_credentials"]

        if "add_icons" in t_config:
            outputData["add_icons"] = t_config["add_icons"]
            if t_config.get("icon_bgcolor"):
                outputData["icon_bgcolor"] = t_config["icon_bgcolor"]

        if t_config.get("remove_labels"):
            outputData["remove_labels"] = t_config["remove_labels"]
        if t_config.get("sign_btn_bgcolor"):
            outputData["sign_btn_bgcolor"] = t_config["sign_btn_bgcolor"]
        if t_config.get("terms_conditions_mandatory"):
            outputData["terms_conditions_mandatory"] = t_config["terms_conditions_mandatory"]
        if t_config.get("addTermsAndCondition"):
            outputData["addTermsAndCondition"] = t_config["addTermsAndCondition"]
            if t_config.get("termsAndConditions") and t_config["addTermsAndCondition"] == "True":
                outputData["termsAndConditions"] = t_config["termsAndConditions"]

        if t_config.get("static_image"):
            outputData["static_image"] = t_config["static_image"]
        if t_config.get("static_image_file"):
            outputData["static_image_file"] = t_config["static_image_file"]
        if t_config.get("video_on_loop"):
            outputData["video_on_loop"] = t_config["video_on_loop"]
        if t_config.get("video_URL"):
            outputData["video_URL"] = t_config["video_URL"]
        if t_config.get("video_url_bg"):
            outputData["video_url_bg"] = t_config["video_url_bg"]
        if t_config.get("video_File"):
            outputData["video_File"] = t_config["video_File"]
        if t_config.get("video_file_bg"):
            outputData["video_file_bg"] = t_config["video_file_bg"]
        if t_config.get("image_slider"):
            outputData["image_slider"] = t_config["image_slider"]
        if t_config.get("play_on_loop"):
            outputData["play_on_loop"] = t_config["play_on_loop"]
        if t_config.get("transition_speed"):
            outputData["transition_speed"] = t_config["transition_speed"]
        if t_config.get("login_slider_style"):
            outputData["login_slider_style"] = t_config["login_slider_style"]

        if t_config.get("sign_font_bgcolor"):
            outputData["sign_font_bgcolor"] = t_config["sign_font_bgcolor"]

        if t_config.get("add_logo_screen"):
            outputData["add_logo_screen"] = t_config["add_logo_screen"]
            if t_config.get("add_logo_screen") == "True" and t_config.get("logo_on_screen"):
                outputData["logo_on_screen"] = t_config["logo_on_screen"]

        if t_config.get("login_card_bgcolor"):
            outputData["login_card_bgcolor"] = t_config["login_card_bgcolor"]

        if t_config.get("set_title_login") and t_config["set_title_login"] == "True":
            outputData["title_data"] = t_config["login_title"]

        if (
            t_config.get("add_logo_login")
            and t_config["add_logo_login"] == "True"
            and t_config.get("logo_on_form")
        ):
            outputData["logo_on_form"] = t_config["logo_on_form"]

        if t_config.get("customize_footer") and t_config["customize_footer"] == "True":
            outputData["customize_footer"] = t_config["customize_footer"]
            outputData["footer_text"] = t_config["footer_text"]
            if t_config.get("login-footer-size"):
                outputData["loginFooterSize"] = t_config["login-footer-size"]
            if t_config.get("footer_placement"):
                outputData["footer_placement"] = t_config["footer_placement"]
            if t_config.get("login_footer_bgcolor"):
                outputData["login_footer_bgcolor"] = t_config["login_footer_bgcolor"]

        if t_config.get("allow_copy_paste_username"):
            outputData["allow_copy_paste_username"] = t_config["allow_copy_paste_username"]

        if t_config.get("allow_copy_paste_password"):
            outputData["allow_copy_paste_password"] = t_config["allow_copy_paste_password"]

        if t_config.get("allow_copy_paste_email"):
            outputData["allow_copy_paste_email"] = t_config["allow_copy_paste_email"]

        if t_config.get("set_favicon_login"):
            outputData["set_favicon_login"] = t_config["set_favicon_login"]
            if t_config.get("login_favicon_file") and t_config.get("set_favicon_login") == "True":
                outputData["login_favicon_file"] = t_config["login_favicon_file"]

        if t_config.get("set_app_drawer_theme") and t_config["set_app_drawer_theme"] == "True":
            root_css = f"""
            :root {{
            --primary-color: {t_config["primary_bgcolor"]};
            --secondary-color: {t_config["secondary_color"]};
            --font-color: {t_config["font_color"]};
            --font-hover-color: {t_config["font_hover_color"]};
            --font-family:{t_config["font_family"]};
            }}
            """

            outputData["root_css"] = root_css

    return outputData
