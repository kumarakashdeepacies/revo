import base64
from datetime import datetime
import json
import random
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from allauth.account.forms import ChangePasswordForm, LoginForm, ResetPasswordKeyForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_multitenant.utils import get_current_tenant
import pandas as pd

from platform_admin.db_centralised_function import postgres_push, read_data_func, update_data_func
from platform_admin.utilities import send_Emails


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
        schema = current_tenant.name

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
                messages.error(request, "Your account is locked")
                return HttpResponseRedirect("/platform_admin/accounts/login/")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                new_template = {
                    "session_id": request.session.session_key,
                    "user_name": request.user.username,
                    "time_logged_in": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ip": request.META.get("REMOTE_ADDR"),
                    "instance_id": request.user.instance_id,
                }
                new_template = pd.DataFrame([new_template])
                postgres_push(new_template, "users_login_trail", schema)
                return HttpResponseRedirect("/platform_admin/")
            else:
                # Return a 'disabled account' error message
                messages.error(request, "User is not active")
                return HttpResponseRedirect("/platform_admin/accounts/login/")
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
                messages.error(request, "Invalid username")
                return HttpResponseRedirect("/platform_admin/accounts/login/")
            else:
                messages.error(request, "Invalid password")
                return HttpResponseRedirect("/platform_admin/accounts/login/")
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

        return render(request, f"platform_admin/account/login.html", data)


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
            if password1 == username:
                messages.error(request, "Username and Password cannot be the same")
                return render(request, "platform_admin/account/password_change.html", data)

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
                messages.error(request, "Current Password entered is not correct")
                return render(request, "platform_admin/account/password_change.html", data)
            password_history = json.loads(password_history_from_db)
            if password_history_from_db != "[]":
                reused_password = False
                for previous_password in password_history:
                    if check_password(password1, previous_password):
                        reused_password = True
                if reused_password:
                    # password matches old password
                    messages.error(request, "Password matches old password, create a new password")

                    return render(request, "platform_admin/account/password_change.html", data)
                else:
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
                    if no_of_passwords < 3:
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
            messages.success(request, "Password updated successfully. Please log in again")
            return HttpResponseRedirect("/platform_admin/accounts/login/")
        else:
            # password1 doesn't match password2
            messages.error(request, "Passwords do not match")
            return render(request, "platform_admin/account/password_change.html", data)

    # request type is not POST
    return render(request, "platform_admin/account/password_change.html", data)


def user_logout(request):
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
    return HttpResponseRedirect("/platform_admin/accounts/login/")


def reset_password_new(request):
    data = {}
    data["username"] = request.POST.get("reset_email_username")
    if request.method == "POST":
        username = request.POST["reset_email_username"]
        username = username.lower()
        smtp_host_user = "notifications@acies.holdings"
        smtp_msg_content = "Click on the link below to reset your password."
        smtp_default_message = "Please contact your administrator for resetting your password"
        smtp_allow_reset = "true"

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
                    send_Emails(
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
        return HttpResponseRedirect("platform_admin/accounts/password/reset_p/")


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
            if password1 == username:
                return JsonResponse({"data": "error", "msg": "Username and Password cannot be same"})

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
                    return JsonResponse(
                        {"data": "error", "msg": "Password matches old password, create a new password"}
                    )

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
                if no_of_passwords < 3:
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
            return JsonResponse({"data": "error", "msg": "Passwords doesn't match"})
    else:
        return render(request, "platform_admin/account/password_reset_from_key.html", data)
