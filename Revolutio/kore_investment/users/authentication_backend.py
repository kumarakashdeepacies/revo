import base64
from datetime import datetime, timedelta
import json
import logging
import os
import pickle
import random
import re
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from allauth.account.forms import ChangePasswordForm, LoginForm, ResetPasswordKeyForm
from allauth.socialaccount.models import SocialApp
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django_multitenant.utils import get_current_tenant
import numpy as np
import pandas as pd
import pyotp
import qrcode

import config.settings.base as settings
from config.settings.base import (
    PLATFORM_DATA_PATH,
    PLATFORM_FILE_PATH,
    env,
    redis_instance,
    tenant_host_mapper,
)
from kore_investment.users import scheduler as schedulerfunc
from kore_investment.users.computations import standardised_functions
from kore_investment.users.computations.db_centralised_function import (
    db_engine_extractor,
    postgres_push,
    read_data_func,
    update_data_func,
)
from kore_investment.utils.utilities import check_password_complexity, sign_up_user

from .computations.alert_utils import alert_failedlogin


def check_username_validation(request):
    username = request.POST["username"]
    username = username.lower()
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        if user:
            return JsonResponse({"response": "error"})
    except User.DoesNotExist:
        return JsonResponse({"response": "success"})


def check_password_validation(request):
    password = request.POST["password"]
    instance = get_current_tenant()
    tenant = instance.name
    regex_pattern = "(^.{4,32}$)"
    tenant_data = {}
    common_passwords = []

    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
        tenant_data = json.load(json_file)
        json_file.close()
    if tenant_data.get(tenant):
        if tenant_data[tenant].get("regex_pattern"):
            regex_pattern = tenant_data[tenant]["regex_pattern"]
        else:
            pass
        if tenant_data[tenant].get("common_passwords"):
            common_passwords = json.loads(tenant_data[tenant]["common_passwords"])
        else:
            pass
    else:
        pass

    if check_password_complexity(regex_pattern, password, common_passwords):
        return JsonResponse({"response": "success"})
    else:
        if password in common_passwords:
            return JsonResponse({"response": "common"})
        else:
            return JsonResponse({"response": "policy"})


def check_email_validation(request):
    email = request.POST["email"].lower()
    email_pattern = r"^([\w\.\-]+)@([\w\-]+)((\.(\w){2,63}){1,3})$"

    User = get_user_model()
    context = {}

    if re.fullmatch(email_pattern, email):
        if User.objects.filter(email=email).exists() == True:
            context["response"] = "email_exists_error"
        else:
            context["response"] = "success"
    else:
        context["response"] = "pattern_error"

    return JsonResponse(context)


def user_sign_up(request):
    instance = get_current_tenant()
    tenant = instance.name
    User = get_user_model()
    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
    else:
        pass
    user_count = User.objects.filter(role="User").count()
    if tenant_data[tenant].get("set_user_limit") == "True" and tenant_data[tenant].get("user_limit_count"):
        limit = int(tenant_data[tenant].get("user_limit_count"))
        if user_count >= limit:
            messages.warning(
                request, "Maximum number of users allowed has been reached. Please contact the administrator."
            )
            return HttpResponseRedirect("/applicationlogin/")
    else:
        pass
    context = sign_up_user(request)
    if context["response"] == "success":
        messages.success(request, context["message"])
    else:
        messages.error(request, context["message"])
    return HttpResponseRedirect("/applicationlogin/")


def user_login(request):
    if request.method == "POST":
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
        username = username.lower()
        next_url = request.POST.get("next")

        current_tenant = get_current_tenant()
        tenant = current_tenant.name

        if tenant != "public":
            username += f".{tenant}"
        else:
            pass

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
                return HttpResponseRedirect("/applicationlogin/")

        User = get_user_model()
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
                message = getMessage(request, "account_locked_message", tenant)
                if message is None:
                    messages.error(request, "Your account is locked")
                else:
                    messages.error(request, message)

                alert_failedlogin(request, username)
                return HttpResponseRedirect("/applicationlogin/")

        tenant_data = {}
        authentication_type = None
        is_applicable = "False"
        otp_applicable = "False"
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        else:
            pass
        t_config = tenant_data[tenant]
        if t_config.get("mfa_configs"):
            if t_config["mfa_configs"].get("mfa_password") is not None:
                if t_config["mfa_configs"]["mfa_password"] == "true":
                    is_applicable = "True"
                else:
                    is_applicable = "False"
            else:
                pass
        else:
            pass
        if t_config.get("mfa_configs"):
            if t_config["mfa_configs"].get("mfa_otp") is not None:
                if t_config["mfa_configs"]["mfa_otp"].get("auth_type") == "true":
                    authentication_type = "auth_type"
                    otp_applicable = "True"
                elif t_config["mfa_configs"]["mfa_otp"].get("email_type") == "true":
                    authentication_type = "email_type"
                    otp_applicable = "True"
                elif t_config["mfa_configs"]["mfa_otp"].get("sms_type") == "true":
                    authentication_type = "sms_type"
                    otp_applicable = "True"
                else:
                    pass
            else:
                pass
        else:
            pass

        operation = request.POST.get("operation")

        if operation == "authenticator_registration":
            password = request.POST.get("password")
            password = decrypt_hashing(password, k_val, h_val.encode("utf-8"))
            password = password.decode("utf-8", "ignore")
            user = authenticate(request, username=username, password=password)
        elif operation == "email_otp":
            generate_email_otp(request)
            return HttpResponseRedirect("/applicationlogin/")
        elif is_applicable == "True" and otp_applicable == "True" and authentication_type == "auth_type":
            try:
                operation = request.POST["operation"]
            except:
                operation = None
            if operation == "OTPcheck":
                loginotp = request.POST.get("loginotp")
                mfa_hash = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user",
                            "Columns": [
                                "mfa_hash",
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
                )["mfa_hash"].iloc[0]
                totp = pyotp.TOTP(mfa_hash)
                otp_verify = totp.now()
                if otp_verify == loginotp:
                    user = User.objects.get(username=username)
                    user.backend = "django.contrib.auth.backends.ModelBackend"
                else:
                    user = None
            else:
                context_response = {}
                context_response["username"] = username
                context_response["authentication_type"] = authentication_type
                password = request.POST.get("password")
                password = decrypt_hashing(password, k_val, h_val.encode("utf-8"))
                password = password.decode("utf-8", "ignore")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    context_response.update(getConfig(request, tenant))
                    return render(
                        request, "account/otp_form.html", context_response
                    )  # haripriya to change. Send username with this and send back username with otp form as login variable. We need the user information.

        elif is_applicable == "False" and otp_applicable == "True" and authentication_type == "auth_type":
            loginotp = request.POST.get("loginotp")
            mfa_hash = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "user",
                        "Columns": [
                            "mfa_hash",
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
            )["mfa_hash"].iloc[0]
            totp = pyotp.TOTP(mfa_hash)
            otp_verify = totp.now()
            if otp_verify == loginotp:
                user = User.objects.get(username=username)
                user.backend = "django.contrib.auth.backends.ModelBackend"
            else:
                user = None
        elif is_applicable == "True" and otp_applicable == "True" and authentication_type == "email_type":
            try:
                operation = request.POST["operation"]
            except:
                operation = None
            if operation == "OTPcheck":
                loginotp = request.POST.get("loginotp")
                mfa_hash = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "user",
                            "Columns": [
                                "mfa_hash",
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
                )["mfa_hash"].iloc[0]
                totp = pyotp.TOTP(mfa_hash, interval=60)
                otp_verify = totp.verify(loginotp)
                if otp_verify is True:
                    user = User.objects.get(username=username)
                    user.backend = "django.contrib.auth.backends.ModelBackend"
                else:
                    user = None
            else:
                context_response = {}
                context_response["username"] = username
                context_response["authentication_type"] = authentication_type
                password = request.POST.get("password")
                password = decrypt_hashing(password, k_val, h_val.encode("utf-8"))
                password = password.decode("utf-8", "ignore")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    context_response.update(getConfig(request, tenant, tenant_data))
                    return render(request, "account/otp_form.html", context_response)
        elif is_applicable == "False" and otp_applicable == "True" and authentication_type == "email_type":
            loginotp = request.POST.get("loginotp")
            mfa_hash = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "user",
                        "Columns": [
                            "mfa_hash",
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
            )["mfa_hash"].iloc[0]
            totp = pyotp.TOTP(mfa_hash, interval=60)
            otp_verify = totp.verify(loginotp)
            if otp_verify is True:
                user = User.objects.get(username=username)
                user.backend = "django.contrib.auth.backends.ModelBackend"
            else:
                user = None
        else:
            password = request.POST.get("password")
            password = decrypt_hashing(password, k_val, h_val.encode("utf-8"))
            password = password.decode("utf-8", "ignore")
            user = authenticate(request, username=username, password=password)
            if tenant_data.get(tenant):
                if "remembermeConfig" in tenant_data[tenant]:
                    if tenant_data[tenant]["remembermeConfig"]["timed_rememberme"] == "true":
                        days = int(tenant_data[tenant]["remembermeConfig"]["rememberme_days"]) * 86400
                        hours = int(tenant_data[tenant]["remembermeConfig"]["rememberme_hours"]) * 3600
                        minutes = int(tenant_data[tenant]["remembermeConfig"]["rememberme_minutes"]) * 60
                        settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                        request.session.set_expiry(days + hours + minutes)
                    elif tenant_data[tenant]["remembermeConfig"]["always_rememberme"] == "true":
                        settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                        request.session.set_expiry(86400 * 365)
                    elif tenant_data[tenant]["remembermeConfig"]["dont_rememberme"] == "true":
                        request.session.set_expiry(0)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        schema = tenant
        session_count = 2
        user_password_fail_count_name = schema + "_" + username + "_" + "failed_password_count"
        if tenant_data.get(schema):
            t_config = tenant_data[schema]
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
                tenant_data[schema] = t_config
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tenant_data, json_file, indent=4)
                    json_file.close()
        else:
            tenant_data[schema] = {
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
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                json.dump(tenant_data, json_file, indent=4)
                json_file.close()
            password_validity_in_days = 180
            max_login_failure_allowed = 3
        if user is not None:
            if user.is_active:
                date_user = np.array(user.last_password_update_date).astype("datetime64[D]")
                date_now = np.array(datetime.now()).astype("datetime64[D]")
                days_difference = (date_now - date_user).astype("int")
                days_difference = int(days_difference)
                if (days_difference) > password_validity_in_days and user.from_ldap != True:
                    form = ChangePasswordForm()
                    data = {"form": form, "username": username}
                    hash_val = "".join(
                        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                        for _ in range(16)
                    )
                    key_val = "".join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(16)
                    )
                    data["h_value"] = hash_val
                    data["k_value"] = key_val
                    request.session["h_value"] = hash_val
                    request.session["k_value"] = key_val

                    messages.error(request, "Password expired- please update your password")

                    data.update(getConfig(request, tenant, tenant_data))
                    return render(request, "account/password_change.html", data)
                elif user.last_login is None and user.from_ldap != True:
                    form = ChangePasswordForm()
                    data = {"form": form, "username": username}
                    hash_val = "".join(
                        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                        for _ in range(16)
                    )
                    key_val = "".join(
                        random.choice(string.ascii_uppercase + string.digits) for _ in range(16)
                    )
                    data["h_value"] = hash_val
                    data["k_value"] = key_val
                    request.session["h_value"] = hash_val
                    request.session["k_value"] = key_val
                    data.update(getConfig(request, tenant, tenant_data))

                    if "termsAndConditions" not in data:
                        with open(f"kore_investment/templates/accounts_base/terms.html") as terms_file:
                            terms_data = terms_file.read()
                            data.update({"termsAndConditions": terms_data})
                            terms_file.close()

                    messages.error(request, "Please set a new password for your account")
                    return render(request, "account/password_change.html", data)
                elif user.from_ldap:
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
                        "instance_id": request.user.instance_id,
                    }
                    new_template = pd.DataFrame([new_template])
                    postgres_push(new_template, "users_login_trail", schema, app_db_transaction=False)
                    if len(ss) >= session_count:
                        logout_user(ss, username, request, schema)
                    is_app_update_available = False
                    return HttpResponseRedirect(
                        f"/users/selectApplication/?is_app_update_available={is_app_update_available}"
                    )
                else:
                    try:
                        operation = request.POST["operation"]
                    except:
                        operation = None
                    if operation == "authenticator_registration":
                        mfa_hash = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "user",
                                    "Columns": [
                                        "mfa_hash",
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
                        )["mfa_hash"].iloc[0]
                        if mfa_hash is None:
                            mfa_hash_temp = pyotp.random_base32()
                            User.objects.filter(username=username).update(mfa_hash=mfa_hash_temp)
                            mfa_hash = mfa_hash_temp
                        unique_name = username + "_" + schema
                        uri = pyotp.totp.TOTP(mfa_hash).provisioning_uri(
                            f"{unique_name}", issuer_name="Revolutio"
                        )
                        QR_CODE_PATH = "kore_investment/media/QR_CODE/"
                        if not os.path.exists(QR_CODE_PATH):
                            os.makedirs(QR_CODE_PATH)

                        qr_code = qrcode.make(uri)
                        qr_code.save(f"{QR_CODE_PATH}{unique_name}_qrcode_.png")
                        totp = pyotp.TOTP(user.mfa_hash)
                        return JsonResponse({"qrcode": f"/media/QR_CODE/{unique_name}_qrcode_.png"})
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
                            "instance_id": request.user.instance_id,
                        }
                        new_template = pd.DataFrame([new_template])
                        postgres_push(new_template, "users_login_trail", schema, app_db_transaction=False)
                        if redis_instance.exists(user_password_fail_count_name):
                            redis_instance.delete(user_password_fail_count_name)
                        if len(ss) >= session_count:
                            logout_user(ss, username, request, schema)

                        is_app_update_available = False
                        developer_mode = False
                        if tenant_data.get(tenant):
                            developer_mode = tenant_data[tenant].get("developer_mode")
                        else:
                            pass

                        if user.is_superuser or user.is_developer or developer_mode == "True":
                            model_json = {}
                            if os.path.exists(f"{PLATFORM_DATA_PATH}app_config_tables.json"):
                                with open(
                                    f"{PLATFORM_DATA_PATH}app_config_tables.json", encoding="utf-8"
                                ) as json_file:
                                    model_json = json.load(json_file)
                                    json_file.close()
                            else:
                                pass
                            model_json = {k: v["version"] for k, v in model_json.items()}

                            connected_database = {}
                            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                                    user_database = json.load(json_file)
                                    connected_database = {
                                        k for k in user_database if user_database[k].get("tenant") == tenant
                                    }
                                    json_file.close()
                            else:
                                pass

                            for k in connected_database:
                                user_db_engine, db_type = db_engine_extractor(k)
                                if user_db_engine != ["", None]:
                                    try:
                                        app_config_tables = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "Tables",
                                                    "Columns": ["tablename", "version"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "model_type",
                                                        "condition": "Equal to",
                                                        "input_value": "system defined",
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                            engine2=user_db_engine,
                                            db_type=db_type,
                                            engine_override=True,
                                        )
                                        app_config_tables["platform_version"] = app_config_tables[
                                            "tablename"
                                        ].map(model_json)
                                        is_app_update_available = (
                                            not app_config_tables["version"]
                                            .eq(app_config_tables["platform_version"], fill_value="1.0.0")
                                            .all()
                                        )
                                        if is_app_update_available:
                                            break
                                        else:
                                            continue
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        continue
                                else:
                                    continue
                        else:
                            pass
                        if next_url == "None":
                            redirect_url = (
                                f"/users/selectApplication/?is_app_update_available={is_app_update_available}"
                            )
                        else:
                            redirect_url = next_url
                        return HttpResponseRedirect(redirect_url)
            else:
                # Return a 'disabled account' error message
                message = getMessage(request, "user_inactive_message", tenant, tenant_data)
                if message is None:
                    messages.error(request, "User is not active")
                else:
                    messages.error(request, message)

                return HttpResponseRedirect("/applicationlogin/")
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
                message = getMessage(request, "invalid_username_message", tenant, tenant_data)
                if message is None:
                    messages.error(request, "Invalid username")
                else:
                    messages.error(request, message)
                return HttpResponseRedirect("/applicationlogin/")
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

                        user_failedlogins_days = 60
                        user_failedlogins_hours = 0
                        user_failedlogins_minutes = 0
                        if tenant_data.get(schema):
                            t_config = tenant_data[schema]
                            if (
                                t_config.get("user_failedlogins_days")
                                and t_config.get("user_failedlogins_hours")
                                and t_config.get("user_failedlogins_minutes")
                            ):
                                user_failedlogins_days = t_config["user_failedlogins_days"]
                                user_failedlogins_hours = t_config["user_failedlogins_hours"]
                                user_failedlogins_minutes = t_config["user_failedlogins_minutes"]
                            else:
                                pass
                        else:
                            pass
                        job_id = f"{username}-reactivate_locked_users_password_job"
                        scheduled_time = datetime.utcnow() + timedelta(
                            days=int(user_failedlogins_days),
                            hours=int(user_failedlogins_hours),
                            minutes=int(user_failedlogins_minutes),
                        )
                        schedulerfunc.add_db_health_scheduler(
                            "schedulercheck.reactivate_locked_users_password_setting",
                            job_id,
                            schema,
                            start_date=scheduled_time,
                        )

                        message = getMessage(request, "exceeding_attempts_message", tenant, tenant_data)
                        if message is None:
                            messages.error(
                                request, "Maximum failed Login attempts made. Your account is locked"
                            )
                        else:
                            messages.error(request, message)

                        return HttpResponseRedirect("/applicationlogin/")

                    message = getMessage(request, "invalid_password_message", tenant, tenant_data)
                    if message is None:
                        error_message = "Invalid password. Remaining attempts: " + str(
                            max_login_failure_allowed - fail_count
                        )
                    else:
                        error_message = message.replace(
                            "{Remaining attemps}", str(max_login_failure_allowed - fail_count)
                        )

                    alert_failedlogin(request, username)
                    messages.error(request, error_message)
                    return HttpResponseRedirect("/applicationlogin/")
                else:
                    redis_instance.set(user_password_fail_count_name, 1)
                    alert_failedlogin(request, username)
                    message = getMessage(request, "invalid_password_message", tenant, tenant_data)
                    if message is None:
                        error_message = "Invalid password. Remaining attempts: " + str(
                            max_login_failure_allowed - 1
                        )
                    else:
                        error_message = message.replace(
                            "{Remaining attemps}", str(max_login_failure_allowed - 1)
                        )
                    messages.error(request, error_message)
                    return HttpResponseRedirect("/applicationlogin/")
    else:
        # the login is a  GET request, so just show the user the login form.
        if request.GET.get("next"):
            redirect_url = f"/applicationlogin/?next={request.GET.get('next')}"
        else:
            redirect_url = "/applicationlogin/"
        return HttpResponseRedirect(redirect_url, {"next": request.GET.get("next")})


@never_cache
def new_user_login(request):
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
    instance = get_current_tenant()
    tenant = instance.name
    tenant_data = {}
    tenant_host_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
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
    else:
        pass

    tenant_present = False
    hostname = request.get_host().split(":")[0].lower()
    if tenant_host_mapper.get(hostname):
        tenant_present = True
    else:
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
                tenant_host_data = json.load(json_file)
                if tenant_host_data.get(hostname):
                    tenant_present = True
                else:
                    pass
                json_file.close()
        else:
            pass
    if not tenant_present:
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

    facebook_config = microsoft_config = google_config = twitter_config = amazon_config = apple_config = False
    queryset = SocialApp.objects.all().values_list("provider", flat=True)
    if "microsoft" in queryset:
        microsoft_config = True
    if "facebook" in queryset:
        facebook_config = True
    if "google" in queryset:
        google_config = True
    if "twitter" in queryset:
        twitter_config = True
    if "amazon" in queryset:
        amazon_config = True
    if "apple" in queryset:
        apple_config = True

    data.update(
        {
            "microsoft_config": microsoft_config,
            "facebook_config": facebook_config,
            "google_config": google_config,
            "twitter_config": twitter_config,
            "amazon_config": amazon_config,
            "apple_config": apple_config,
        }
    )
    data.update(getConfig(request, tenant, tenant_data))
    data["next"] = request.GET.get("next")
    return render(request, f"account/login.html", data)


@never_cache
def admin_login(request):
    form = LoginForm()
    tenant_data = {}
    instance = get_current_tenant()
    tenant = instance.name
    data = {"form": form, "tenant_data": tenant_data}
    hash_val = "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16)
    )
    key_val = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    data["h_value"] = hash_val
    data["k_value"] = key_val
    request.session["h_value"] = hash_val
    request.session["k_value"] = key_val

    data.update(getConfig(request, tenant))

    return render(request, f"account/admin_login.html", data)


@never_cache
def update_password(request):
    username = request.user.username
    username = username.lower()
    form = ChangePasswordForm()
    data = {"form": form, "username": username}
    instance = get_current_tenant()
    tenant = instance.name
    if request.method == "POST":
        oldpassword = request.POST.get("oldpassword")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if "h_value" in request.session:
            h_val = request.session["h_value"]
            del request.session["h_value"]

        if "k_value" in request.session:
            k_val = request.session["k_value"]
            del request.session["k_value"]
        oldpassword = decrypt_hashing(oldpassword, k_val, h_val.encode("utf-8"))
        oldpassword = oldpassword.decode("utf-8")
        password1 = decrypt_hashing(password1, k_val, h_val.encode("utf-8"))
        password1 = password1.decode("utf-8")
        password2 = decrypt_hashing(password2, k_val, h_val.encode("utf-8"))
        password2 = password2.decode("utf-8")
        if not username:
            username = request.POST.get("username")
            username = decrypt_hashing(username, k_val, h_val.encode("utf-8"))
            username = username.decode("utf-8")
        data["username"] = username
        if password1 == password2:
            if oldpassword != password1:
                (
                    regex_capital_letter,
                    regex_alphanumeric,
                    regex_symbol,
                    regex_restricted_chars,
                    regex_lowercase_letter,
                    regex_restrict_chars,
                ) = ("", "", "", [], "", "")
                tenant_data = {}
                if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
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
                        regex_restrict_chars = t_config.get("restrict_characters")
                        common_passwords = json.loads(t_config["common_passwords"])
                    else:
                        password_history_length = 3
                        regex = "(^.{4,32}$)"
                        common_passwords = []
                        regex_capital_letter = "false"
                        regex_lowercase_letter = "false"
                        regex_min_length = 4
                        regex_alphanumeric = "false"
                        regex_max_length = 32
                        regex_symbol = "false"
                        regex_restrict_chars = "false"
                        regex_restricted_chars = []
                else:
                    pass

                if password1 == username:
                    message = getMessage(request, "pass_match_user_message", tenant, tenant_data)
                    if message is None:
                        messages.error(request, "Username and Password cannot be the same")
                    else:
                        messages.error(request, message)

                    data.update(getConfig(request, tenant, tenant_data))

                    return render(request, "account/password_change.html", data)
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
                    data_from_db = password_data_from_db.iloc[0, 0]
                    last_password = password_data_from_db.iloc[0, 1]
                    if not check_password(oldpassword, last_password):
                        message = getMessage(request, "invalid_current_password_message", tenant, tenant_data)
                        if message is None:
                            messages.error(request, "Current Password entered is not correct")
                        else:
                            messages.error(request, message)

                        data.update(getConfig(request, tenant, tenant_data))

                        return render(request, "account/password_change.html", data)
                    password_history = json.loads(data_from_db)
                    if data_from_db != "[]":
                        reused_password = False
                        for previous_password in password_history:
                            if check_password(password1, previous_password):
                                reused_password = True
                        if reused_password:
                            # password matches old password
                            message = getMessage(request, "new_pass_old_pass_message", tenant, tenant_data)
                            if message is None:
                                messages.error(
                                    request, "Password matches old password, create a new password"
                                )
                            else:
                                messages.error(request, message)

                            data.update(getConfig(request, tenant, tenant_data))

                            return render(request, "account/password_change.html", data)
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
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "user",
                                        "Columns": [
                                            {
                                                "column_name": "password",
                                                "input_value": encrypted_password,
                                                "separator": ",",
                                            },
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
                    messages.success(request, "Password updated successfully. Please log in again")
                    return HttpResponseRedirect("/applicationlogin/")
                else:
                    # complexity fail
                    if password1 in common_passwords:
                        message = getMessage(request, "password_common_message", tenant, tenant_data)
                        if message is None:
                            messages.error(
                                request, "Password entered is too common! Please select another password"
                            )
                        else:
                            messages.error(request, message)

                        data.update(getConfig(request, tenant, tenant_data))

                        return render(request, "account/password_change.html", data)
                    error_message = "Password should contain"
                    if regex_alphanumeric == "true":
                        error_message += " at least one letter, at least one number,"
                    if regex_capital_letter == "true":
                        error_message += " at least one Capital Letter,"
                    if regex_lowercase_letter == "true":
                        error_message += " at least one Lowercase Letter,"
                    if regex_symbol == "true":
                        error_message += " at least one Symbol,"
                        if regex_restrict_chars == "true" and len(regex_restricted_chars):
                            error_message = error_message.rstrip(",")
                            error_message += (
                                " except [" + " , ".join(json.loads(regex_restricted_chars)) + "] ,"
                            )

                    error_message = error_message.rstrip(",")
                    if regex_min_length:
                        error_message += " minimum length of " + str(regex_min_length)
                    if regex_max_length:
                        error_message += " and maximum length of " + str(regex_max_length)
                    messages.error(request, error_message)

                    data.update(getConfig(request, tenant, tenant_data))

                    return render(request, "account/password_change.html", data)
            else:
                message = getMessage(request, "new_pass_current_pas_message", tenant)
                if message is None:
                    messages.error(
                        request,
                        "New password cannot be the same as the cuurent one! Please enter another password",
                    )
                else:
                    messages.error(request, message)

                data.update(getConfig(request, tenant))

                return render(request, "account/password_change.html", data)
        else:
            # password1 doesn't match password2
            message = getMessage(request, "passwords_donotmatch_message", tenant)
            if message is None:
                messages.error(request, "Passwords do not match")
            else:
                messages.error(request, message)

            data.update(getConfig(request, tenant))

            return render(request, "account/password_change.html", data)

    hash_val = "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16)
    )
    key_val = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    data["h_value"] = hash_val
    data["k_value"] = key_val
    request.session["h_value"] = hash_val
    request.session["k_value"] = key_val
    data.update(getConfig(request, tenant))
    return render(request, "account/password_change.html", data)


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
        instance = get_current_tenant()
        schema = instance.name
        if schema != "public":
            username += f".{schema}"
        else:
            pass
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
                    )

                    return JsonResponse({"data": "success", "msg": ""})
                else:
                    return JsonResponse({"data": "error", "msg": smtp_default_message})
            else:
                return JsonResponse(
                    {"data": "error", "msg": "The email id for the specified username is not present."}
                )
    else:
        return HttpResponseRedirect("/accounts/password/reset_p/")


@never_cache
def reset_update_password(request, username=None):
    form = ResetPasswordKeyForm()
    data = {"form": form, "username": username}

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        username = str(urlsafe_base64_decode(username), "utf-8")
        username = username.lower()
        if "h_value" in request.session:
            h_val = request.session["h_value"]
            del request.session["h_value"]

        if "k_value" in request.session:
            k_val = request.session["k_value"]
            del request.session["k_value"]
        password1 = decrypt_hashing(password1, k_val, h_val.encode("utf-8"))
        password1 = password1.decode("utf-8")
        password2 = decrypt_hashing(password2, k_val, h_val.encode("utf-8"))
        password2 = password2.decode("utf-8")
        username = username.lower()
        data["username"] = username
        instance = get_current_tenant()
        tenant = instance.name
        if password1 == password2:
            common_passwords = []
            password_history_length = 3
            regex_capital_letter = "false"
            regex_lowercase_letter = "false"
            regex_min_length = 4
            regex_alphanumeric = "false"
            regex_max_length = 32
            regex_symbol = "false"
            regex_restricted_chars = []
            regex_restrict_chars = []
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
                    regex_restrict_chars = t_config.get("restrict_characters")
                    common_passwords = json.loads(t_config["common_passwords"])
                else:
                    pass
            else:
                pass
            if password1 == username:
                message = getMessage(request, "pass_match_user_message", tenant, tenant_data)
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
                data_from_db = password_data_from_db.iloc[0, 0]
                password_history = json.loads(data_from_db)
                if data_from_db != "[]":
                    reused_password = False
                    for previous_password in password_history:
                        if check_password(password1, previous_password):
                            reused_password = True
                    if reused_password:
                        # password matches old password
                        message = getMessage(request, "new_pass_old_pass_message", tenant, tenant_data)
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
                    encrypted_password = str(make_password(password1))
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
                                        "column_name": "password",
                                        "input_value": encrypted_password,
                                        "separator": "AND",
                                    },
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
                    message = getMessage(request, "password_common_message", tenant, tenant_data)
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
            message = getMessage(request, "passwords_donotmatch_message", tenant)
            if message is None:
                message = "Passwords doesn't match"
            return JsonResponse({"data": "error", "msg": message})
    else:
        hash_val = "".join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(16)
        )
        key_val = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        data["h_value"] = hash_val
        data["k_value"] = key_val
        request.session["h_value"] = hash_val
        request.session["k_value"] = key_val
        return render(request, "account/password_reset_from_key.html", data)


def generate_email_otp(request):
    if request.method == "POST":
        username = request.POST["login"]
        username = username.lower()
        instance = get_current_tenant()
        tenant = instance.name
        tenant_data = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        else:
            pass
        if tenant_data.get(tenant):
            t_config = tenant_data[tenant]
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
                    smtp_default_message = "Please contact your administrator for resetting your password"
            else:
                return JsonResponse(
                    {
                        "data": "error",
                        "msg": "Configuration for SMTP not found. Please contact your administrator.",
                    }
                )
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
                        "mfa_hash",
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
            mfa_hash = username_data_from_db["mfa_hash"].iloc[0]
            totp = pyotp.TOTP(mfa_hash, interval=60)
            otp_verify = totp.now()
            smtp_msg_content = f"The OTP for application authentication is {otp_verify}"
            user_email = username_data_from_db.iloc[0, 1]
            if user_email:
                encoded_username = urlsafe_base64_encode(force_bytes(username))
                standardised_functions.send_Emails(
                    request,
                    smtp_host_user,
                    [user_email],
                    "OTP for Authentication",
                    smtp_msg_content,
                    encoded_username,
                )

                return JsonResponse(
                    {"data": "success", "msg": "OTP has been sent to registered email address"}
                )
            else:
                return JsonResponse(
                    {"data": "error", "msg": "The email id for the specified username is not present."}
                )
    else:
        return HttpResponseRedirect("/applicationlogin/")


def decrypt_hashing(enc, key, iv):
    enc = base64.b64decode(enc)
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc), 16)


def getMessage(request, key, tenant, tenant_data={}):
    message = None
    if not tenant_data:
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        else:
            pass
    else:
        pass
    if tenant_data.get(tenant):
        t_config = tenant_data[tenant]
        if t_config.get("customLoginMessages"):
            if key in t_config["customLoginMessages"]:
                message = t_config["customLoginMessages"][key]
            else:
                pass
        else:
            pass
    else:
        pass
    return message


def getConfig(request, tenant, tenant_data=None):
    outputData = {"tenant": tenant}
    if not tenant_data:
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        else:
            pass
    else:
        pass
    t_config = tenant_data[tenant]

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
    else:
        pass
    return outputData


def user_logout(request):

    clear_cache = request.POST.get("clear_cache")

    instance = get_current_tenant()
    tenant = instance.name

    if clear_cache:
        user_name = request.user.username
        user_name_tenant = user_name + tenant
        if redis_instance.exists(user_name_tenant) == 1:
            redis_instance.delete(user_name_tenant)

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
                        "input_value": "User",
                        "separator": "",
                    },
                ],
            },
            "condition": [
                {
                    "column_name": "session_id",
                    "condition": "Equal to",
                    "input_value": request.session.session_key,
                    "and_or": "",
                }
            ],
        },
    )
    logout(request)
    return HttpResponseRedirect("/applicationlogin/")


def session_breach_check(user, tenant):
    if user:
        tenant_data = {}
        if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                tenant_data = json.load(json_file)
                json_file.close()
        else:
            pass
        if tenant_data.get(tenant):
            if tenant_data[tenant].get("session_count"):
                session_count = tenant_data[tenant]["session_count"]
                ss = []
                sessions = Session.objects.filter(expire_date__gte=timezone.now()).order_by("-expire_date")
                temp = 0
                for s in sessions:
                    if str(s.get_decoded().get("_auth_user_id")) == str(user.id):
                        if temp < session_count:
                            ss.append(s)
                            temp = temp + 1
                ss.reverse()
                if len(ss) >= session_count:
                    s = ss[0]
                    session_key = s.session_key
                    s.delete()
                    user_login_info = {}
                    user_login_info["username"] = user.username
                    user_login_info["session_key"] = session_key
                    user_login_info["device"] = ""
                    user_login_info["ip"] = ""
                    redis_instance.set(tenant + "mulsession" + user.username, pickle.dumps(user_login_info))
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass
    return None
