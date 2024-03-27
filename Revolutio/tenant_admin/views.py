from base64 import b64encode
from datetime import datetime
import json
import logging
import os
import re
import shutil
import urllib
import zipfile

from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site
from django.db.models import Q as djangoQuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
import environ
import oracledb
import pandas as pd
import psycopg2
import pyotp
from rq.worker import Worker
from sqlalchemy import create_engine, text
from turbodbc import connect, make_options

from config.settings.base import (
    APPS_DIR,
    MEDIA_ROOT,
    PLATFORM_DATA_PATH,
    PLATFORM_FILE_PATH,
    database_engine_dict,
    redis_instance,
)
from kore_investment.users import scheduler as schedulerfunc
from kore_investment.users.computations import dynamic_model_create, update_application
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    db_engine_extractor,
    delete_data_func,
    execute_read_query,
    non_standard_read_data_func,
    read_data_func,
    update_data_func,
)
from kore_investment.users.computations.db_credential_encrytion import (
    decrypt_db_credential,
    decrypt_existing_db_credentials,
    encrypt_db_credentials,
)
from kore_investment.users.models import Profile
from tenant_admin.utilities import check_password_complexity, regex_generator, tenant_schema_from_request

# Create your views here.


def getContextData(context_data, tenant):
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == tenant:
                    if "developer_mode" not in t_config:
                        t_config.update({"developer_mode": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "allow_user_forum" not in t_config:
                        t_config.update({"allow_user_forum": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "allow_user_planner" not in t_config:
                        t_config.update({"allow_user_planner": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "allow_user_profile" not in t_config:
                        t_config.update({"allow_user_profile": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "allow_dashboard_portal" not in t_config:
                        t_config.update({"allow_dashboard_portal": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "block_third_party" not in t_config:
                        t_config.update({"block_third_party": "True"})
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(tenant_data, json_file, indent=4)
                            json_file.close()

                    if "add_logo_tenant" in t_config:
                        context_data["add_logo_tenant"] = t_config["add_logo_tenant"]
                        if t_config["add_logo_tenant"] == "True" and "logo_on_tenant" in t_config:
                            context_data["logo_on_tenant"] = t_config["logo_on_tenant"]

                    if "set_tenant_admin_theme" in t_config:
                        context_data["set_tenant_admin_theme"] = t_config["set_tenant_admin_theme"]

                    if "tenant_primary_bgcolor" in t_config:
                        context_data["tenant_primary_bgcolor"] = t_config["tenant_primary_bgcolor"]

                    if "tenant_secondary_bgcolor" in t_config:
                        context_data["tenant_secondary_bgcolor"] = t_config["tenant_secondary_bgcolor"]

                    if "tenant_font_bgcolor" in t_config:
                        context_data["tenant_font_bgcolor"] = t_config["tenant_font_bgcolor"]

                    if "tenant_hover_bgcolor" in t_config:
                        context_data["tenant_hover_bgcolor"] = t_config["tenant_hover_bgcolor"]

                    if "set_tenantbg_bgcolor" in t_config:
                        context_data["set_tenantbg_bgcolor"] = t_config["set_tenantbg_bgcolor"]

                    if "tenantbg_bgcolor" in t_config:
                        context_data["tenantbg_bgcolor"] = t_config["tenantbg_bgcolor"]

                    if "font_family_tenant" in t_config:
                        context_data["font_family_tenant"] = t_config["font_family_tenant"]

                    if "tenant_static_image" in t_config:
                        context_data["tenant_static_image"] = t_config["tenant_static_image"]

                    if "tenant_static_image_file" in t_config:
                        context_data["tenant_static_image_file"] = t_config["tenant_static_image_file"]

                    if "add_bg_tenant_admin" in t_config:
                        context_data["add_bg_tenant_admin"] = t_config["add_bg_tenant_admin"]

                    if "tenant_video_on_loop" in t_config:
                        context_data["tenant_video_on_loop"] = t_config["tenant_video_on_loop"]

                    if "video_URL_tenant" in t_config:
                        context_data["video_URL_tenant"] = t_config["video_URL_tenant"]

                    if "video_url_bg_tenant" in t_config:
                        context_data["video_url_bg_tenant"] = t_config["video_url_bg_tenant"]

                    if "video_File_tenant" in t_config:
                        context_data["video_File_tenant"] = t_config["video_File_tenant"]

                    if "video_file_bg_tenant" in t_config:
                        context_data["video_file_bg_tenant"] = t_config["video_file_bg_tenant"]

                    if "tenant_image_slider" in t_config:
                        context_data["tenant_image_slider"] = t_config["tenant_image_slider"]

                    if "tenant_slider_style" in t_config:
                        context_data["tenant_slider_style"] = t_config["tenant_slider_style"]

                    if "block_third_party" in t_config:
                        context_data["block_third_party"] = t_config["block_third_party"]

    context_data["tenant"] = tenant
    return context_data


def getAppList(request, context_data, tenant):

    connected_database = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
        with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
            db_data = json.load(json_file)
            connected_database = {k: v for k, v in db_data.items() if v.get("tenant") == tenant}
            json_file.close()
    sql_query_app = pd.DataFrame(columns=["application_code", "application_name"])
    if len(connected_database) > 0:
        for k, config in connected_database.items():
            if k != "default":
                user_db_engine, db_type = db_engine_extractor(k)
                if user_db_engine != ["", []]:
                    try:
                        sql_query_app = pd.concat(
                            [
                                sql_query_app,
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "Application",
                                            "Columns": ["application_code", "application_name"],
                                        },
                                        "condition": [],
                                    },
                                    engine2=user_db_engine,
                                    engine_override=True,
                                    db_type=db_type,
                                ),
                            ]
                        )
                        sql_query_app.fillna("", inplace=True)
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        continue
        sql_query_app.drop_duplicates(
            subset=["application_code"], keep="last", inplace=True, ignore_index=True
        )
    application_list = sql_query_app.to_dict("records")

    context_data["applications"] = application_list

    return context_data


@never_cache
def index(request):
    tenant = tenant_schema_from_request(request, original=True)
    if request.method == "POST":
        if request.POST["operation"] == "saveDashboardAppConfig":
            show_dashboard = request.POST["show_dashboard"]
            display_position = request.POST["display_position"]
            db_connection_name = request.POST["db_conn"]

            if show_dashboard == "true":

                db_type = ""
                user_db_engine, db_type = database_engine_dict[db_connection_name]

                dashboard_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "system_application_master",
                            "Columns": ["app_name", "display_config"],
                        },
                        "condition": [
                            {
                                "column_name": "app_name",
                                "condition": "Equal to",
                                "input_value": "dashboard",
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

                if len(dashboard_config) > 0:
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "system_application_master",
                                "Columns": [
                                    {
                                        "column_name": "display_config",
                                        "input_value": json.dumps({"display_position": display_position}),
                                        "separator": "",
                                    }
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": "app_name",
                                    "condition": "Equal to",
                                    "input_value": "dashboard",
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                else:

                    dashboard_config_df = pd.DataFrame(
                        [
                            {
                                "app_name": "dashboard",
                                "display_config": json.dumps({"display_position": display_position}),
                            }
                        ]
                    )
                    data_handling(
                        request,
                        dashboard_config_df,
                        "system_application_master",
                        con=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

                app_db_mapping = {}
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        app_db_mapping = json.load(json_file)
                        json_file.close()

                app_db_mapping[f"{tenant}_dashboard"] = db_connection_name

                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json", "w") as outfile:
                    json.dump(app_db_mapping, outfile, indent=4)
                    outfile.close()

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    json_file.close()

                if data.get(tenant):
                    data[tenant]["show_dashboard"] = show_dashboard
                else:
                    pass

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as old_file:
                    json.dump(data, old_file, indent=4)
                    old_file.close()

            return JsonResponse({"response": "Configuration saved successfully!", "icon": "success"})

        if request.POST["operation"] == "savePlannerAppConfig":
            show_planner = request.POST["show_planner"]
            display_position = request.POST["display_position"]
            db_connection_name = request.POST["db_conn"]

            if show_planner == "true":
                db_type = ""
                user_db_engine, db_type = database_engine_dict[db_connection_name]

                planner_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "system_application_master",
                            "Columns": ["app_name", "display_config"],
                        },
                        "condition": [
                            {
                                "column_name": "app_name",
                                "condition": "Equal to",
                                "input_value": "planner",
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

                if len(planner_config) > 0:
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "system_application_master",
                                "Columns": [
                                    {
                                        "column_name": "display_config",
                                        "input_value": json.dumps({"display_position": display_position}),
                                        "separator": "",
                                    }
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": "app_name",
                                    "condition": "Equal to",
                                    "input_value": "planner",
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                else:

                    planner_config_df = pd.DataFrame(
                        [
                            {
                                "app_name": "planner",
                                "display_config": json.dumps({"display_position": display_position}),
                            }
                        ]
                    )
                    data_handling(
                        request,
                        planner_config_df,
                        "system_application_master",
                        con=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

                app_db_mapping = {}
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        app_db_mapping = json.load(json_file)
                        json_file.close()

                app_db_mapping[f"{tenant}_planner"] = db_connection_name

                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json", "w") as outfile:
                    json.dump(app_db_mapping, outfile, indent=4)
                    outfile.close()

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    json_file.close()

                if data.get(tenant):
                    data[tenant]["show_planner"] = show_planner
                else:
                    pass

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as old_file:
                    json.dump(data, old_file, indent=4)
                    old_file.close()

            return JsonResponse({"response": "Configuration saved successfully!", "icon": "success"})

        if request.POST["operation"] == "save_noti_settings":
            remove_bell_icon = request.POST["remove_bell_icon"]
            limit_notification = request.POST["limit_notification"]

            noti_expiry_days = request.POST["noti_expiry_days"]
            noti_expiry_hours = request.POST["noti_expiry_hours"]
            noti_expiry_minutes = request.POST["noti_expiry_minutes"]

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config_data = t_config
                    json_file.close()

                t_config_data["remove_bell_icon"] = remove_bell_icon
                t_config_data["limit_notification"] = limit_notification

                t_config_data["noti_expiry_days"] = noti_expiry_days
                t_config_data["noti_expiry_hours"] = noti_expiry_hours
                t_config_data["noti_expiry_minutes"] = noti_expiry_minutes

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as old_file:
                    json.dump(data, old_file, indent=4)
                    old_file.close()

            return JsonResponse({"response": "Configuration saved successfully!", "icon": "success"})

        if request.POST["operation"] == "reset_tenant_theme":
            media_path = f"{MEDIA_ROOT}/{tenant}/TenantTheme/"
            if os.path.exists(media_path):
                if os.path.exists(f"{media_path}/appdrawer"):
                    shutil.rmtree(f"{media_path}/appdrawer")

                if os.path.exists(f"{media_path}/custom_error_pages"):
                    shutil.rmtree(f"{media_path}/custom_error_pages")

                if os.path.exists(f"{media_path}/login_screen"):
                    shutil.rmtree(f"{media_path}/login_screen")

                if os.path.exists(f"{media_path}/export_json.json"):
                    os.remove(f"{media_path}/export_json.json")

            tenant_theme_data = {}

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_theme_data = json.load(json_file)
                    json_file.close()

                if tenant_theme_data.get(tenant):

                    tenant_theme_keys = [
                        "loginBg",
                        "static_image",
                        "static_image_file",
                        "image_slider",
                        "video_on_loop",
                        "counter",
                        "transition_default_speed",
                        "loop_default",
                        "animation_name",
                        "play_on_loop",
                        "slider_play_on_loop",
                        "last_image",
                        "transition_speed_enable",
                        "transition_speed",
                        "transition_speed_enable",
                        "totalImages",
                        "login_slider_style",
                        "add_videobg",
                        "video_URL",
                        "video_File",
                        "video_url_bg",
                        "video_file_bg",
                        "add_logo_screen",
                        "logo_on_screen",
                        "add_logo_login",
                        "logo_on_form",
                        "terms_conditions_mandatory",
                        "addTermsAndCondition",
                        "termsAndConditions",
                        "customize_footer",
                        "footer_text",
                        "login-footer-size",
                        "footer_placement",
                        "login_footer_bgcolor",
                        "footer_text",
                        "signup_header",
                        "signup_msg",
                        "rename_username",
                        "rename_email",
                        "rename_password",
                        "rename_confirm_password",
                        "remove_signup",
                        "remove_remember_me",
                        "remove_admin_toggle",
                        "block_autocomplete_credentials",
                        "remove_terms",
                        "remove_labels",
                        "allow_copy_paste_username",
                        "allow_copy_paste_email",
                        "allow_copy_paste_password",
                        "add_icons",
                        "icon_bgcolor",
                        "sign_btn_bgcolor",
                        "sign_font_bgcolor",
                        "login_card_bgcolor",
                        "remove_all_social",
                        "remove_facebook",
                        "remove_google",
                        "remove_microsoft",
                        "remove_twitter",
                        "remove_amazon",
                        "remove_apple",
                        "set_title_login",
                        "login_title",
                        "set_favicon_login",
                        "login_favicon_file",
                        "customize_appdrawer_bg",
                        "change_appdrawer_bg_file",
                        "appdrawer_bg_image_name",
                        "appdrawer_bg_image",
                        "appdrawer_bgColor",
                        "appdrawer_bgColorCode",
                        "set_app_drawer_theme",
                        "set_appdrawer_template",
                        "app_template",
                        "widgets_template_value",
                        "add_logo_appdrawer",
                        "logo-file-appdrawer",
                        "add_logo_topnavbar",
                        "logo-file-topnavbar",
                        "customize_app_footer",
                        "app_footer_text",
                        "app_footer_size",
                        "app_footer_placement",
                        "app_footer_bgcolor",
                        "set_title_appdrawer",
                        "appdrawer_title",
                        "set_favicon_appdrawer",
                        "appdrawer_favicon_file",
                        "add_logo_error",
                        "logo_file_error_page",
                        "add_logo_error",
                        "add_bg_error_subprocess",
                        "subprocess_bg",
                        "add_favicon_error_subprocess",
                        "subprocess_favicon",
                        "change_subprocess_text",
                        "change_subprocess_button",
                        "buttons_subprocess",
                        "add_bg_error404",
                        "404bg",
                        "add_favicon_error404",
                        "404favicon",
                        "change_404_text",
                        "text_404",
                        "change_404_button",
                        "buttons_404",
                        "add_bg_error500",
                        "500bg",
                        "add_favicon_error500",
                        "500favicon",
                        "change_500_text",
                        "text_500",
                        "change_500_button",
                        "buttons_500",
                        "add_bg_error403",
                        "403bg",
                        "add_favicon_error403",
                        "403favicon",
                        "change_403_text",
                        "text_403",
                        "change_403_button",
                        "buttons_403",
                        "add_bg_error502",
                        "502bg",
                        "add_favicon_error502",
                        "502favicon",
                        "add_favicon_error502",
                        "change_502_text",
                        "text_502",
                        "change_502_button",
                        "buttons_502",
                        "add_bg_error503",
                        "503bg",
                        "add_favicon_error503",
                        "503favicon",
                        "change_503_text",
                        "text_503",
                        "change_503_button",
                        "buttons_503",
                        "add_bg_error_permission",
                        "permission_bg",
                        "add_favicon_error_permission",
                        "permission_favicon",
                        "change_permission_text",
                        "permission_text",
                        "change_permission_button",
                        "buttons_permission",
                        "add_footer_error",
                        "error_footer_text",
                        "error_footer_size",
                        "error_footer_placement",
                        "error_footer_bgcolor",
                        "primary_bgcolor",
                        "secondary_color",
                        "font_color",
                        "font_hover_color",
                        "font_family",
                    ]
                    for key in tenant_theme_keys:
                        if key in tenant_theme_data[tenant]:
                            del tenant_theme_data[tenant][key]

                    for key in list(tenant_theme_data[tenant].keys()):
                        if key.startswith("image_slider_file"):
                            del tenant_theme_data[tenant][key]

                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_theme_data, json_file, indent=4)
                        json_file.close()

            return JsonResponse({"message": "Theme reset to default."})

        if request.POST["operation"] == "export_theme":
            path = f"{MEDIA_ROOT}/{tenant}/TenantTheme/"
            if not os.path.exists(path):
                os.makedirs(path)

            data = fetch_tenant_config(request)
            temp_file_path = f"{MEDIA_ROOT}/{tenant}"

            def zipFile(source, path):
                with zipfile.ZipFile(f"{temp_file_path}/{tenant} Tenant Theme Package.zip", "a") as zipped_f:
                    zipped_f.write(source, path)

            if data:

                with zipfile.ZipFile(f"{temp_file_path}/{tenant} Tenant Theme Package.zip", "a") as zipped_f:
                    zipped_f.writestr("export_json.json", json.dumps(data, default=str))
                    zipped_f.close()

                if data.get("static_image") == "True" and "static_image_file" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/background_images/{data["static_image_file"]}'
                    zipFile(source, f'login_screen/background_images/{data["static_image_file"]}')

                if data.get("image_slider") == "True" and "totalImages" in data:
                    for i in range(1, int(data["totalImages"]) + 1):
                        image = "image_slider_file" + str(i)
                        source = f"{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/slider_images/{data[image]}"
                        zipFile(source, f"login_screen/slider_images/{data[image]}")

                if (
                    data.get("video_on_loop") == "True"
                    and data.get("video_File") == "True"
                    and "video_file_bg" in data
                ):
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/background_video/{data["video_file_bg"]}'
                    zipFile(source, f'login_screen/background_video/{data["video_file_bg"]}')

                if data.get("add_logo_screen") == "True" and "logo_on_screen" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/logo/{data["logo_on_screen"]}'
                    zipFile(source, f'login_screen/logo/{data["logo_on_screen"]}')

                if data.get("add_logo_login") == "True" and "logo_on_form" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/logo/{data["logo_on_form"]}'
                    zipFile(source, f'login_screen/logo/{data["logo_on_form"]}')

                if data.get("set_favicon_login") == "True" and "login_favicon_file" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/login_screen/favicon/{data["login_favicon_file"]}'
                    )
                    zipFile(source, f'login_screen/favicon/{data["login_favicon_file"]}')

                if (
                    data.get("customize_appdrawer_bg") == "True"
                    and data.get("change_appdrawer_bg_file") == "True"
                    and data.get("appdrawer_bg_image") == "True"
                    and "appdrawer_bg_image_name" in data
                ):
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/appdrawer/background_images/{data["appdrawer_bg_image_name"]}'
                    zipFile(source, f'appdrawer/background_images/{data["appdrawer_bg_image_name"]}')

                if data.get("add_logo_appdrawer") == "True" and "logo-file-appdrawer" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/appdrawer/logo/{data["logo-file-appdrawer"]}'
                    zipFile(source, f'appdrawer/logo/{data["logo-file-appdrawer"]}')

                if data.get("add_logo_topnavbar") == "True" and "logo-file-topnavbar" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/appdrawer/logo/{data["logo-file-topnavbar"]}'
                    zipFile(source, f'appdrawer/logo/{data["logo-file-topnavbar"]}')

                if data.get("set_favicon_appdrawer") == "True" and "appdrawer_favicon_file" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/appdrawer/favicon/{data["appdrawer_favicon_file"]}'
                    zipFile(source, f'appdrawer/favicon/{data["appdrawer_favicon_file"]}')

                if data.get("add_logo_error") == "True" and "logo_file_error_page" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/logo/{data["logo_file_error_page"]}'
                    zipFile(source, f'custom_error_pages/logo/{data["logo_file_error_page"]}')

                if data.get("add_bg_error_subprocess") == "True" and "subprocess_bg" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["subprocess_bg"]}'
                    zipFile(source, f'custom_error_pages/background/{data["subprocess_bg"]}')

                if data.get("add_favicon_error_subprocess") == "True" and "subprocess_favicon" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["subprocess_favicon"]}'
                    zipFile(source, f'custom_error_pages/favicon/{data["subprocess_favicon"]}')

                if data.get("add_bg_error404") == "True" and "404bg" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["404bg"]}'
                    )
                    zipFile(source, f'custom_error_pages/background/{data["404bg"]}')

                if data.get("add_favicon_error404") == "True" and "404favicon" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["404favicon"]}'
                    )
                    zipFile(source, f'custom_error_pages/favicon/{data["404favicon"]}')

                if data.get("add_bg_error500") == "True" and "500bg" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["500bg"]}'
                    )
                    zipFile(source, f'custom_error_pages/background/{data["500bg"]}')

                if data.get("add_favicon_error500") == "True" and "500favicon" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["500favicon"]}'
                    )
                    zipFile(source, f'custom_error_pages/favicon/{data["500favicon"]}')

                if data.get("add_bg_error502") == "True" and "502bg" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["502bg"]}'
                    )
                    zipFile(source, f'custom_error_pages/background/{data["502bg"]}')

                if data.get("add_favicon_error502") == "True" and "502favicon" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["502favicon"]}'
                    )
                    zipFile(source, f'custom_error_pages/favicon/{data["502favicon"]}')

                if data.get("add_bg_error403") == "True" and "403bg" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["403bg"]}'
                    )
                    zipFile(source, f'custom_error_pages/background/{data["403bg"]}')

                if data.get("add_favicon_error403") == "True" and "403favicon" in data:
                    source = (
                        f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["403favicon"]}'
                    )
                    zipFile(source, f'custom_error_pages/favicon/{data["403favicon"]}')

                if data.get("add_bg_error_permission") == "True" and "permission_bg" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/background/{data["permission_bg"]}'
                    zipFile(source, f'custom_error_pages/background/{data["permission_bg"]}')

                if data.get("add_favicon_error_permission") == "True" and "permission_favicon" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/custom_error_pages/favicon/{data["permission_favicon"]}'
                    zipFile(source, f'custom_error_pages/favicon/{data["permission_favicon"]}')

                if data.get("add_logo_tenant") == "True" and "logo_on_tenant" in data:
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/tenant_admin/logo/{data["logo_on_tenant"]}'
                    zipFile(source, f'tenant_admin/logo/{data["logo_on_tenant"]}')

                if (
                    data.get("add_bg_tenant_admin") == "True"
                    and data.get("tenant_static_image") == "True"
                    and "tenant_static_image_file" in data
                ):
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/tenant_admin/background_images/{data["tenant_static_image_file"]}'
                    zipFile(source, f'tenant_admin/background_images/{data["tenant_static_image_file"]}')

                if data.get("tenant_image_slider") == "True" and "tenant_totalimage" in data:
                    for i in range(1, int(data["tenant_totalimage"]) + 1):
                        image = "tenant_image_slider_file" + str(i)
                        source = f"{MEDIA_ROOT}/{tenant}/TenantTheme/tenant_admin/slider_images/{data[image]}"
                        zipFile(source, f"tenant_admin/slider_images/{data[image]}")

                if (
                    data.get("tenant_video_on_loop") == "True"
                    and data.get("video_File_tenant") == "True"
                    and "video_file_bg_tenant" in data
                ):
                    source = f'{MEDIA_ROOT}/{tenant}/TenantTheme/tenant_admin/background_video/{data["video_file_bg_tenant"]}'
                    zipFile(source, f'login_screen/background_video/{data["video_file_bg_tenant"]}')

            preview_file = f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html"
            if os.path.exists(preview_file):
                with zipfile.ZipFile(f"{temp_file_path}/{tenant} Tenant Theme Package.zip", "a") as zipped_f:
                    zipped_f.write(preview_file, "preview.html")
                    zipped_f.close()

            with open(f"{temp_file_path}/{tenant} Tenant Theme Package.zip", "rb") as zip_file:
                response = HttpResponse(zip_file, content_type="application/zip")
                response["Content-Length"] = str(
                    os.stat(f"{temp_file_path}/{tenant} Tenant Theme Package.zip").st_size
                )

                response["Content-Disposition"] = "attachment; filename={}".format(
                    f"{tenant} Tenant Theme Package.zip"
                )
                zip_file.close()

                return response

        if request.POST["operation"] == "delete_theme":
            temp_file_path = f"{MEDIA_ROOT}/{tenant}"
            os.remove(f"{temp_file_path}/{tenant} Tenant Theme Package.zip")

        if request.POST["operation"] == "import_theme":
            if "uploadZip" in request.FILES:
                uploadZip = request.FILES["uploadZip"]
                uploadZip_filename = request.FILES["uploadZip"].name

                if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme"):
                    os.makedirs(f"kore_investment/media/{tenant}/TenantTheme")
                with open(
                    f"kore_investment/media/{tenant}/TenantTheme/" + uploadZip_filename, "wb+"
                ) as destination:
                    for chunk in uploadZip.chunks():
                        destination.write(chunk)
                    destination.close()

                shutil.unpack_archive(
                    f"kore_investment/media/{tenant}/TenantTheme/" + uploadZip_filename,
                    f"kore_investment/media/{tenant}/TenantTheme/",
                )

                os.remove(f"kore_investment/media/{tenant}/TenantTheme/" + uploadZip_filename)

                if os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/preview.html"):
                    destination = f"kore_investment/templates/user_defined_template/{tenant}/login/"
                    if not os.path.exists(destination):
                        os.makedirs(destination)
                    shutil.copy2(f"kore_investment/media/{tenant}/TenantTheme/preview.html", destination)
                    os.remove(f"kore_investment/media/{tenant}/TenantTheme/preview.html")

                if os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/export_json.json"):
                    with open(f"kore_investment/media/{tenant}/TenantTheme/export_json.json") as import_file:
                        imported_data = json.load(import_file)
                        import_file.close()

                    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                        data = {}
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                            data = json.load(json_file)
                            data[tenant].update(imported_data)
                            json_file.close()

                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as old_file:
                            json.dump(data, old_file, indent=4)
                            old_file.close()

            return JsonResponse({"response": "Theme imported successfully!", "icon": "success"})

        if request.POST["operation"] == "export_app_theme":
            app_code = request.POST["app_code"]
            path = [f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles"]
            temp_file_path = f"{MEDIA_ROOT}/{tenant}"
            zip_name = f"{temp_file_path}/{tenant} {app_code} App Theme Package.zip"

            def zipdir(path, ziph):
                # ziph is zipfile handle
                for root, dirs, files in os.walk(path):
                    for file in files:
                        ziph.write(
                            os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
                        )

            def zipit(path, zip_name):
                zipf = zipfile.ZipFile(zip_name, "w")
                for dir in path:
                    zipdir(dir, zipf)
                zipf.close()

            zipit(path, zip_name)

            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = database_engine_dict[db_connection_name]

            check_app_code = read_data_func(
                request="",
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "application_theme",
                        "Columns": [
                            "app_code",
                            "theme_type",
                            "theme_name",
                            "theme_config",
                            "created_by",
                            "created_date",
                            "modified_by",
                            "modified_date",
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "",
                        }
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )

            with zipfile.ZipFile(zip_name, "a") as zipped_f:
                zipped_f.writestr(
                    "theme_config.json", json.dumps(check_app_code.to_dict("records"), default=str)
                )
                zipped_f.close()

            with open(zip_name, "rb") as zip_file:
                response = HttpResponse(zip_file, content_type="application/zip")
                response["Content-Length"] = str(os.stat(zip_name).st_size)

                response["Content-Disposition"] = "attachment; filename={}".format(
                    f"{tenant} {app_code} App Theme Package.zip"
                )
                zip_file.close()

                return response

        if request.POST["operation"] == "delete_app_theme":
            app_code = request.POST["app_code"]
            temp_file_path = f"{MEDIA_ROOT}/{tenant}"
            os.remove(f"{temp_file_path}/{tenant} {app_code} App Theme Package.zip")

        if request.POST["operation"] == "import_app_theme":
            if "uploadAppZip" in request.FILES:
                uploadAppZip = request.FILES["uploadAppZip"]
                uploadAppZip_filename = request.FILES["uploadAppZip"].name

                app_code = request.POST["app_code"]

                if not os.path.exists(f"{MEDIA_ROOT}/{tenant}/{app_code}"):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}")
                with open(f"{MEDIA_ROOT}/{tenant}/{app_code}/" + uploadAppZip_filename, "wb+") as destination:
                    for chunk in uploadAppZip.chunks():
                        destination.write(chunk)
                    destination.close()

                shutil.unpack_archive(
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/" + uploadAppZip_filename,
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/",
                )

                os.remove(f"{MEDIA_ROOT}/{tenant}/{app_code}/" + uploadAppZip_filename)

                if os.path.exists(f"{MEDIA_ROOT}/{tenant}/{app_code}/theme_config.json"):
                    with open(f"{MEDIA_ROOT}/{tenant}/{app_code}/theme_config.json") as import_file:
                        imported_data = json.load(import_file)
                        import_file.close()

                db_type = ""
                db_connection_name = None
                schema = tenant + "_" + app_code
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        db_connection_name = json.load(json_file).get(schema)
                        json_file.close()
                user_db_engine, db_type = db_engine_extractor(db_connection_name)

                for theme in imported_data:
                    condition_list = [
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "theme_type",
                            "condition": "Equal to",
                            "input_value": theme["theme_type"],
                            "and_or": "",
                        },
                    ]
                    if theme["theme_type"] != "Global" and theme["theme_name"]:
                        condition_list[-1]["and_or"] = "and"
                        condition_list.append(
                            {
                                "column_name": "theme_name",
                                "condition": "Equal to",
                                "input_value": theme["theme_name"],
                                "and_or": "",
                            }
                        )
                    else:
                        pass
                    check_app_code = read_data_func(
                        request="",
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "application_theme",
                                "Columns": ["app_code"],
                            },
                            "condition": condition_list,
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

                    if len(check_app_code) > 0:
                        update_data_func(
                            request="",
                            config_dict={
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "application_theme",
                                    "Columns": [
                                        {
                                            "column_name": "theme_config",
                                            "input_value": theme["theme_config"],
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "theme_name",
                                            "input_value": theme["theme_name"],
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "modified_by",
                                            "input_value": request.user.username,
                                            "separator": ",",
                                        },
                                        {
                                            "column_name": "modified_date",
                                            "input_value": datetime.now(),
                                            "separator": "",
                                        },
                                    ],
                                },
                                "condition": condition_list,
                            },
                            engine2=user_db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )
                    else:
                        theme_df = pd.DataFrame(
                            [
                                {
                                    "app_code": app_code,
                                    "theme_type": theme["theme_type"],
                                    "theme_name": theme["theme_name"],
                                    "theme_config": theme["theme_config"],
                                    "created_date": datetime.now(),
                                    "created_by": request.user.username,
                                }
                            ]
                        )
                        data_handling(
                            request,
                            theme_df,
                            "application_theme",
                            con=user_db_engine,
                            db_type=db_type,
                            engine_override=True,
                        )

                    theme_type = "Global"
                    showNavbar = True
                    showSidebar = True
                    showFooter = True
                    theme_config = json.loads(theme["theme_config"])
                    source = "kore_investment/templates/Themes/Default/base_all.html"
                    dest = f"kore_investment/templates/user_defined_template/{tenant}/{app_code}/theme/{theme_type}/"
                    if not os.path.exists(dest):
                        os.makedirs(dest)
                    dest += "base_all.html"
                    shutil.copyfile(source, dest)
                    footer_sticky = ""
                    navbar_sticky = ""
                    for i in ["footer", "navbar", "sidebar"]:
                        if "name" not in theme_config[i]["template_config"]:
                            ijson_name = "Default"
                            ijson = {}
                        else:
                            ijson_name = theme_config[i]["template_config"]["name"]
                            ijson = theme_config[i]["template_config"]["vars"]
                        theme_file = f"kore_investment/templates/Themes/{ijson_name}/{i}.html"
                        with open(theme_file) as rfile:
                            data = rfile.read()
                            if len(ijson.keys()):
                                for var in ijson.keys():
                                    var_tag = "<<" + var + ">>"
                                    if var == "sidebaricon":
                                        var_value = f"/media/{tenant}/{app_code}/{ijson[var]}"
                                    else:
                                        var_value = ijson[var]
                                    data = data.replace(var_tag, var_value)
                            else:
                                data = data.replace("<<sidebaricon>>", "")
                                data = data.replace(
                                    "<<footertext>>",
                                    "ACIES, Acies Consulting, Acies TechWorks, Acies Ventures, Acies LightHouse, Kepler, Kore, Callisto, Carpo, Revolutio and Antares are registered trademarks of Acies LLP, Acies Consulting Pte Ltd. and its subsidiaries in different countries and territories. Unauthorized use, misrepresentation or misuse of trademarks is strictly prohibited and subject to legal action under various laws.",
                                )
                            with open(dest) as rwfile:
                                rwdata = rwfile.read()
                                if i == "footer":
                                    if theme_config["footer"]["footerCheck"] is False:
                                        data = ""
                                    if showFooter is False:
                                        data = ""
                                if theme_config["footer"]["position"] == "Sticky":
                                    footer_sticky = ".footer-sticky { position: inherit !important; }\n"
                                    data = data.replace("<<footerSticky>>", "true")
                                else:
                                    data = data.replace("<<footerSticky>>", "false")
                                if i == "navbar":
                                    if theme_config["navbar"]["navbarCheck"] is False:
                                        data = ""
                                    if showNavbar is False:
                                        data = ""
                                if theme_config["navbar"]["position"] == "Floating":
                                    navbar_sticky = ".navbar-sticky { position: fixed !important;width: -webkit-fill-available; }\n"
                                    data = data.replace("<<navbarSticky>>", "false")
                                else:
                                    data = data.replace("<<navbarSticky>>", "true")
                                if i == "sidebar":
                                    if theme_config["sidebar"]["sidebarCheck"] is False:
                                        data = ""
                                        theme_config["sidebar"]["template_config"]["sidebarSize"] = "0rem"
                                    if showSidebar is False:
                                        data = ""
                                        theme_config["sidebar"]["template_config"]["sidebarSize"] = "0rem"
                                if theme_config["sidebar"]["position"] == "Right":
                                    data = data.replace("<<sidebarPosition>>", "right")
                                else:
                                    data = data.replace("<<sidebarPosition>>", "left")

                                new_data = rwdata.replace("<!--<<" + i + "html>>-->", data)

                                if theme_config["breadcrumbs"]["breadcrumbsCheck"] is False:
                                    new_data = new_data.replace("<<breadcrumnbs-css>>", "none")
                                else:
                                    new_data = new_data.replace("<<breadcrumnbs-css>>", "flex")

                                if theme_config["tabconfig"]["tabconfigCheck"] is False:
                                    new_data = new_data.replace("<<tabconfig-css>>", "none")
                                else:
                                    new_data = new_data.replace("<<tabconfig-css>>", "flex")

                                if theme_config["root"].get("favicon"):
                                    favicon = theme_config["root"]["favicon"]
                                    favicon_extension = favicon.split(".")[-1]
                                    check_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/favicon.{favicon_extension}"
                                    if os.path.isfile(check_path):
                                        new_data = new_data.replace(
                                            "<<baseFavicon>>",
                                            f"{{{{MEDIA_URL}}}}{tenant}/{app_code}/Themefiles/{theme_type}/favicon.{favicon_extension}",
                                        )
                                    else:
                                        new_data = new_data.replace(
                                            "<<baseFavicon>>", "/static/images/favicons/favicon1.ico"
                                        )
                                else:
                                    new_data = new_data.replace(
                                        "<<baseFavicon>>", "/static/images/favicons/favicon1.ico"
                                    )
                                if i == "sidebar":
                                    root_css = f"""\n:root {{\n--primary-color: {theme_config["root"]["primaryColor"]};\n--secondary-color: {theme_config["root"]["secondaryColor"]};\n--font-color: {theme_config["root"]["fontColor"]};\n--font-family: {theme_config["root"]["fontStyle"]};\n--font-size:{theme_config["root"]["fontSize"]+"px"};\n--font-hover-color: {theme_config["root"]["font-hover-color"]};\n--navbar-bg: {theme_config["navbar"]["bgColor"]};\n--navbar-font: {theme_config["navbar"]["fontColorNavbar"]};\n--sidebar-bg: {theme_config["sidebar"]["bgColor"]};\n--sidebar-font: {theme_config["sidebar"]["fontColorSidebar"]};\n--modal-fontColor: {theme_config["modals"]["modalFontColor"]};\n--modal-fontSize: {theme_config["modals"]["fontSize"]+"px;"};\n--modal-fontStyle:{theme_config["modals"]["fontStyle"]};\n--modal-bgColor: {theme_config["modals"]["modalBgColor"]};\n--footer-bg: {theme_config["footer"]["bgColor"]};\n--footer-font: {theme_config["footer"]["fontColorFooter"]};\n--sidebar-size: {theme_config["sidebar"]["template_config"]["sidebarSize"]};"""
                                    if "buttons" in theme_config:
                                        root_css += f"""\n--buttonBgColor: {theme_config["buttons"]["buttonBgColor"]};\n--buttonFontColor: {theme_config["buttons"]["buttonFontColor"]};\n--buttonShadowColor: {theme_config["buttons"]["buttonShadowColor"]};\n--button_shadow_x: {theme_config["buttons"]["button_shadow_x"]+"px"};\n--button_shadow_y: {theme_config["buttons"]["button_shadow_y"]+"px"};\n--button_blur_radius: {theme_config["buttons"]["button_blur_radius"]+"px"};\n--button_shadow_thickness: {theme_config["buttons"]["button_shadow_thickness"]+"px"};\n--buttonBorderColor: {theme_config["buttons"]["buttonBorderColor"]};\n--buttonBorderThickness: {theme_config["buttons"]["buttonBorderThickness"]+"px"};\n--buttonBorderStyle: {theme_config["buttons"]["buttonBorderStyle"]};\n--buttonBgHoverColor: {theme_config["buttons"]["buttonBgHoverColor"]};\n--buttonFontHoverColor: {theme_config["buttons"]["buttonFontHoverColor"]};"""

                                    root_css += f"""}}\n"""
                                    new_data = new_data.replace(
                                        "<<root_vars>>",
                                        f"<style>{root_css}{navbar_sticky}{footer_sticky}</style>",
                                    )
                                    new_data = new_data.replace(
                                        "<<webpage-title>>", theme_config["root"]["webpage-title"]
                                    )

                                with open(dest, "w") as wfile:
                                    wfile.write(new_data)

            os.remove(f"{MEDIA_ROOT}/{tenant}/{app_code}/theme_config.json")

            return JsonResponse(
                {
                    "response": "Theme imported successfully!",
                    "icon": "success",
                    "imported_data": imported_data,
                    "import_app_code": app_code,
                }
            )

        if request.POST["operation"] == "reset_tenant_admin_theme":
            media_path = f"{MEDIA_ROOT}/{tenant}/TenantTheme/"
            if os.path.exists(media_path):
                if os.path.exists(f"{media_path}/tenant_admin"):
                    shutil.rmtree(f"{media_path}/tenant_admin")

            tenant_admin_theme_data = {}

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_admin_theme_data = json.load(json_file)
                    json_file.close()

                if tenant_admin_theme_data.get(tenant):

                    tenant_theme_keys = [
                        "add_logo_tenant",
                        "logo_on_tenant",
                        "set_tenant_admin_theme",
                        "tenant_primary_bgcolor",
                        "tenant_secondary_bgcolor",
                        "tenant_font_bgcolor",
                        "tenant_hover_bgcolor",
                        "font_family_tenant",
                        "set_tenantbg_bgcolor",
                        "tenantbg_bgcolor",
                        "add_bg_tenant_admin",
                        "tenantloginBg",
                        "tenant_static_image_file",
                        "tenant_static_image",
                        "tenant_image_slider",
                        "tenant_counter",
                        "transition_default_speed",
                        "loop_default",
                        "animation_name",
                        "tenant_play_on_loop",
                        "tenant_slider_play_on_loop",
                        "tenant_last_image",
                        "tenant_transition_speed_enable",
                        "tenant_transition_speed",
                        "tenant_totalimage",
                        "tenant_slider_style",
                        "tenant_video_on_loop",
                        "add_videobg_tenant",
                        "video_File_tenant",
                        "video_URL_tenant",
                        "video_file_bg_tenant",
                        "video_url_bg_tenant",
                        "tenant_video_on_loop",
                    ]
                    for key in tenant_theme_keys:
                        if key in tenant_admin_theme_data[tenant]:
                            del tenant_admin_theme_data[tenant][key]

                    for key in list(tenant_admin_theme_data[tenant].keys()):
                        if key.startswith("tenant_image_slider_file"):
                            del tenant_admin_theme_data[tenant][key]

                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_admin_theme_data, json_file, indent=4)
                        json_file.close()

            return JsonResponse({"message": "Theme reset to default."})

        if request.POST["operation"] == "login_customization":

            destination = f"kore_investment/templates/user_defined_template/{tenant}/login/"
            if not os.path.exists(destination):
                os.makedirs(destination)

            with open(f"kore_investment/templates/accounts_base/preview_base.html") as preview_base_file:
                preview_base_data = preview_base_file.read()
                preview_base_file.close()

            with open(
                f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
            ) as to_file:
                to_file.write(preview_base_data)
                to_file.close()

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config_data = t_config
                    json_file.close()

            data = request.POST
            tenant_data = {}

            if "loginBg" in data.keys():
                if request.POST["loginBg"] == "static_image":
                    if "static_image_file" in request.FILES:
                        static_image_file = request.FILES["static_image_file"]
                        static_image_file_name = request.FILES["static_image_file"].name
                        tenant_data["static_image_file"] = static_image_file_name
                        tenant_data["static_image"] = "True"
                        tenant_data["image_slider"] = "False"
                        tenant_data["video_on_loop"] = "False"

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_images"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_images"
                            )
                        with open(
                            f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_images/"
                            + static_image_file_name,
                            "wb+",
                        ) as destination:
                            for chunk in static_image_file.chunks():
                                destination.write(chunk)
                            destination.close()

                        style = f"<img id='bg_image_static' src='/media/{tenant}/TenantTheme/login_screen/background_images/{static_image_file_name}' />"
                        preview_base_data = preview_base_data.replace("<styleBodyBgPreview>", style)
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    elif "static_image_file" in t_config_data:
                        image_path = f'/media/{tenant}/TenantTheme/login_screen/background_images/{t_config_data["static_image_file"]}'

                        style = f"<img id='bg_image_static' src='/media/{tenant}/TenantTheme/login_screen/background_images/{t_config_data['''static_image_file''']}' />"

                        preview_base_data = preview_base_data.replace("<styleBodyBgPreview>", style)
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    else:
                        tenant_data["static_image"] = "False"

                elif request.POST["loginBg"] == "image_slider":
                    if "image_slider_file1" in request.FILES:

                        tenant_data["static_image"] = "False"
                        tenant_data["image_slider"] = "True"
                        tenant_data["video_on_loop"] = "False"
                        counter = int(request.POST["counter"])
                        tenant_data["counter"] = counter
                        animation_fill = ""
                        transition_default_speed = 6
                        loop_default = "infinite"
                        animation_name = "imageAnimationSlow"
                        tenant_data["transition_default_speed"] = transition_default_speed
                        tenant_data["loop_default"] = loop_default
                        tenant_data["animation_name"] = animation_name
                        last_image = ""
                        if "play_on_loop" in data.keys():
                            tenant_data["play_on_loop"] = "True"
                            tenant_data["slider_play_on_loop"] = "True"
                        else:
                            loop_default = "1"
                            tenant_data["play_on_loop"] = "False"
                            tenant_data["slider_play_on_loop"] = "False"
                            animation_fill = "animation-fill-mode: forwards;"
                            animation_name = "imageAnimationNoLoop"
                            last_image = request.FILES[f"image_slider_file{1}"].name
                            tenant_data["last_image"] = last_image

                        if "transition_speed" in data.keys():
                            tenant_data["transition_speed_enable"] = "True"
                            tenant_data["transition_speed"] = request.POST["transition_speed"]
                            if tenant_data["transition_speed"] == "slow_transition":
                                transition_default_speed = 8
                            elif tenant_data["transition_speed"] == "fast_transition":
                                transition_default_speed = 4
                            else:
                                transition_default_speed = 6
                        else:
                            tenant_data["transition_speed_enable"] = "False"

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/login_screen/slider_images"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/login_screen/slider_images"
                            )

                        totalImages = int(request.POST["totalimage"])
                        tenant_data["totalImages"] = totalImages
                        list_of_images = []

                        slider_style = '<ul class="cb-slideshow"  id="cb-slideshow">'
                        for i in range(1, totalImages + 1):

                            if f"image_slider_file{i}" in request.FILES:
                                list_of_images.append(f"image_slider_file{i}")
                                index = len(list_of_images)
                                slider_file = request.FILES[f"image_slider_file{i}"]
                                tenant_data[f"image_slider_file{i}"] = slider_file.name

                                image_name = slider_file.name
                                slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index-1)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/TenantTheme/login_screen/slider_images/{image_name}" /></span></li>'
                                with open(
                                    f"kore_investment/media/{tenant}/TenantTheme/login_screen/slider_images/"
                                    + image_name,
                                    "wb+",
                                ) as destination:
                                    for chunk in slider_file.chunks():
                                        destination.write(chunk)
                                    destination.close()

                        if last_image:
                            slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/login_screen/slider_images/{last_image}" /></span></li>'
                        slider_style += "</ul>"
                        tenant_data["login_slider_style"] = slider_style

                        preview_base_data = preview_base_data.replace(
                            "<backgroundStyleForLoginPreview>", slider_style
                        )
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    elif "image_slider_file1" in t_config_data:
                        tenant_data["static_image"] = "False"
                        tenant_data["image_slider"] = "True"
                        tenant_data["video_on_loop"] = "False"

                        counter = t_config_data["counter"]
                        animation_name = "imageAnimationSlow"
                        animation_fill = ""
                        last_image = ""
                        if t_config_data["play_on_loop"] == "True":
                            loop_default = "infinite"
                        else:
                            loop_default = "1"
                            last_image = t_config_data["last_image"]
                            animation_fill = "animation-fill-mode: forwards;"
                            animation_name = "imageAnimationNoLoop"

                        if t_config_data["transition_speed_enable"] == "True":
                            if t_config_data["transition_speed"] == "slow_transition":
                                transition_default_speed = 8
                            elif t_config_data["transition_speed"] == "fast_transition":
                                transition_default_speed = 4
                            else:
                                transition_default_speed = 6
                        else:
                            transition_default_speed = 6

                        totalImages = t_config_data["totalImages"]
                        list_of_images = []

                        slider_style = '<ul class="cb-slideshow"  id="cb-slideshow">'
                        for i in range(1, totalImages + 1):

                            if f"image_slider_file{i}" in t_config_data:
                                list_of_images.append(f"image_slider_file{i}")
                                index = len(list_of_images)
                                image_name = t_config_data[f"image_slider_file{i}"]

                                slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index-1)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/TenantTheme/login_screen/slider_images/{image_name}" /></span></li>'

                        if last_image:
                            slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/login_screen/slider_images/{last_image}" /></span></li>'
                        slider_style += "</ul>"
                        tenant_data["login_slider_style"] = slider_style

                        preview_base_data = preview_base_data.replace(
                            "<backgroundStyleForLoginPreview>", slider_style
                        )
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    else:
                        tenant_data["static_image"] = "False"
                        tenant_data["image_slider"] = "False"
                        tenant_data["video_on_loop"] = "False"

                elif request.POST["loginBg"] == "video_on_loop":
                    if "add_videobg" in data.keys():
                        tenant_data["static_image"] = "False"
                        tenant_data["image_slider"] = "False"
                        tenant_data["video_on_loop"] = "True"
                        tenant_data["add_videobg"] = request.POST["add_videobg"]

                        if request.POST["add_videobg"] == "video_URL":
                            tenant_data["video_URL"] = "True"
                            tenant_data["video_File"] = "False"

                            if "video_url_bg" in data.keys():
                                bg_video_url = request.POST["video_url_bg"]
                                tenant_data["video_url_bg"] = bg_video_url

                                video_style = f'<div id="ytbg" data-ytbg-fade-in="true" data-youtube="{bg_video_url}"></div>'

                                preview_base_data = preview_base_data.replace(
                                    "<backgroundStyleForLoginPreview>", video_style
                                )
                                with open(
                                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                    "w",
                                ) as to_file:
                                    to_file.write(preview_base_data)
                                    to_file.close()
                            elif "video_url_bg" in t_config_data:

                                video_style = f'<div id="ytbg" data-ytbg-fade-in="true" data-youtube="{t_config_data["video_url_bg"]}"></div>'

                                preview_base_data = preview_base_data.replace(
                                    "<backgroundStyleForLoginPreview>", video_style
                                )
                                with open(
                                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                    "w",
                                ) as to_file:
                                    to_file.write(preview_base_data)
                                    to_file.close()
                            else:
                                tenant_data["video_URL"] = "False"

                        elif request.POST["add_videobg"] == "video_File":
                            tenant_data["video_URL"] = "False"
                            tenant_data["video_File"] = "True"

                            if "video_file_bg" in request.FILES:
                                bg_video_file = request.FILES["video_file_bg"]
                                bg_video_name = request.FILES["video_file_bg"].name
                                tenant_data["video_file_bg"] = bg_video_name

                                if not os.path.exists(
                                    f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_video"
                                ):
                                    os.makedirs(
                                        f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_video"
                                    )
                                with open(
                                    f"kore_investment/media/{tenant}/TenantTheme/login_screen/background_video/"
                                    + bg_video_name,
                                    "wb+",
                                ) as destination:
                                    for chunk in bg_video_file.chunks():
                                        destination.write(chunk)
                                    destination.close()

                                video_style = f'<div id="ytbg-1" data-vbg="/media/{tenant}/TenantTheme/login_screen/background_video/{bg_video_name}"></div>'

                                preview_base_data = preview_base_data.replace(
                                    "<backgroundStyleForLoginPreview>", video_style
                                )
                                with open(
                                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                    "w",
                                ) as to_file:
                                    to_file.write(preview_base_data)
                                    to_file.close()

                            elif "video_file_bg" in t_config_data:

                                video_style = f'<div id="ytbg-1" data-vbg="/media/{tenant}/TenantTheme/login_screen/background_video/{t_config_data["video_file_bg"]}"></div>'

                                preview_base_data = preview_base_data.replace(
                                    "<backgroundStyleForLoginPreview>", video_style
                                )
                                with open(
                                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                    "w",
                                ) as to_file:
                                    to_file.write(preview_base_data)
                                    to_file.close()

                            else:
                                tenant_data["video_File"] = "False"

                else:
                    tenant_data["static_image"] = "False"
                    tenant_data["image_slider"] = "False"
                    tenant_data["video_on_loop"] = "False"

            else:
                default_slider = """
                <ul class="cb-slideshow" style="<styleSlider>" >
                    <li>
                        <span style="animation: imageAnimationSlow 30s linear infinite;animation-delay: 0s;"><img class="lazyload" data-src="{%static 'images/login_slider/Screen-1.jpg'%}" /></span>
                    </li>
                    <li>
                        <span style="animation: imageAnimationSlow 30s linear infinite;animation-delay: 6s;"><img class="lazyload" data-src="{%static 'images/login_slider/Screen-2.jpg'%}" /></span>
                    </li>
                    <li>
                        <span style="animation: imageAnimationSlow 30s linear infinite;animation-delay: 12s;"><img class="lazyload" data-src="{%static 'images/login_slider/Screen-3.jpg'%}" /></span>
                    </li>
                    <li>
                        <span style="animation: imageAnimationSlow 30s linear infinite;animation-delay: 18s;"><img class="lazyload" data-src="{%static 'images/login_slider/Screen-4.jpg'%}" /></span>
                    </li>
                    <li>
                        <span style="animation: imageAnimationSlow 30s linear infinite;animation-delay: 24s;"><img class="lazyload" data-src="{%static 'images/login_slider/Screen-5.jpg'%}" /></span>
                    </li>
                </ul>
                """

                preview_base_data = preview_base_data.replace(
                    "<backgroundStyleForLoginPreview>", default_slider
                )
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "add_logo" in data.keys():

                tenant_data["add_logo_screen"] = "True"
                if "logo_on_screen" in request.FILES:
                    tenant_data["logo_on_screen"] = request.FILES["logo_on_screen"].name
                    image_path = (
                        f"/media/{tenant}/TenantTheme/login_screen/logo/"
                        + request.FILES["logo_on_screen"].name
                    )

                    if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/login_screen/logo"):
                        os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/login_screen/logo")
                    with open(f"kore_investment{image_path}", "wb+") as destination:
                        for chunk in request.FILES["logo_on_screen"].chunks():
                            destination.write(chunk)
                        destination.close()
                    preview_base_data = preview_base_data.replace(
                        "<logo_on_screen_dynamic_preview>", image_path
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                elif "add_logo_screen" in t_config_data:
                    if t_config_data["add_logo_screen"] == "True":
                        if "logo_on_screen" in t_config_data:
                            image_path = (
                                f"/media/{tenant}/TenantTheme/login_screen/logo/"
                                + t_config_data["logo_on_screen"]
                            )

                            preview_base_data = preview_base_data.replace(
                                "<logo_on_screen_dynamic_preview>", image_path
                            )
                            with open(
                                f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                "w",
                            ) as to_file:
                                to_file.write(preview_base_data)
                                to_file.close()

                        else:
                            tenant_data["add_logo_screen"] = "False"
                else:
                    tenant_data["add_logo_screen"] = "False"

            else:
                tenant_data["add_logo_screen"] = "False"

                preview_base_data = preview_base_data.replace("<screen_logo_style_preview>", "display:none")
                preview_base_data = preview_base_data.replace("<logo_on_screen_dynamic_preview>", "")
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "add_logo_login" in data.keys():
                tenant_data["add_logo_login"] = "True"
                if "logo_on_form" in request.FILES:
                    tenant_data["logo_on_form"] = request.FILES["logo_on_form"].name
                    image_path = (
                        f"/media/{tenant}/TenantTheme/login_screen/logo/" + request.FILES["logo_on_form"].name
                    )

                    if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/login_screen/logo"):
                        os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/login_screen/logo")
                    with open(f"kore_investment{image_path}", "wb+") as destination:
                        for chunk in request.FILES["logo_on_form"].chunks():
                            destination.write(chunk)
                        destination.close()

                    preview_base_data = preview_base_data.replace(
                        "<logo_on_form_dynamic_preview>", image_path
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                elif "add_logo_login" in t_config_data:
                    if t_config_data["add_logo_login"] == "True":
                        if "logo_on_form" in t_config_data:
                            image_path = (
                                f"/media/{tenant}/TenantTheme/login_screen/logo/"
                                + t_config_data["logo_on_form"]
                            )

                            preview_base_data = preview_base_data.replace(
                                "<logo_on_form_dynamic_preview>", image_path
                            )
                            with open(
                                f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                                "w",
                            ) as to_file:
                                to_file.write(preview_base_data)
                                to_file.close()

                        else:
                            tenant_data["add_logo_login"] = "False"
                else:
                    tenant_data["add_logo_login"] = "False"

            else:
                tenant_data["add_logo_login"] = "False"
                preview_base_data = preview_base_data.replace("<form_logo_style_preview>", "")
                preview_base_data = preview_base_data.replace(
                    "<logo_on_form_dynamic_preview>", "{%static 'images/Base_theme/Acies_short_logo.png'%}"
                )
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "terms_conditions_mandatory" in data.keys():
                tenant_data["terms_conditions_mandatory"] = request.POST["terms_conditions_mandatory"]
                if request.POST["terms_conditions_mandatory"] == "terms_at_first_signin":
                    jsValue = """
                            $(document).ready(function() {
                                $("#terms_div").css("display","none")
                                $("#aciessigninbutton").removeAttr("disabled")
                            });"""

                    preview_base_data = preview_base_data.replace(
                        "<<termsAndConditionsEverytimePreview>>", jsValue
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    jsValue = """
                            $(document).ready(function() {
                                $("#terms_div").css("display","block")
                                $("#aciessigninbutton").prop("disabled",true)
                            });"""

                    preview_base_data = preview_base_data.replace(
                        "<<termsAndConditionsEverytimePreview>>", jsValue
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "addTermsAndCondition" in data.keys():
                if request.POST["addTermsAndCondition"] == "True":
                    tenant_data["addTermsAndCondition"] = "True"
                    tenant_data["termsAndConditions"] = request.POST["termsAndConditions"]

                    preview_base_data = preview_base_data.replace(
                        "<termsandconditionspreview>", request.POST["termsAndConditions"]
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()
                else:
                    tenant_data["addTermsAndCondition"] = "False"
                    with open(f"kore_investment/templates/accounts_base/terms.html") as terms_file:
                        terms_data = terms_file.read()

                    preview_base_data = preview_base_data.replace("<termsandconditionspreview>", terms_data)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "customize_footer" in data.keys():
                if data["customize_footer"] == "True":
                    tenant_data["customize_footer"] = "True"
                    if "footer-editor" in data.keys():
                        custom_footer = request.POST["footer-editor"]
                        tenant_data["footer_text"] = custom_footer

                        preview_base_data = preview_base_data.replace(
                            "<custom_footer_preview>", custom_footer
                        )
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    if "login-footer-size" in data.keys():
                        loginFooterSize = request.POST["login-footer-size"]
                        tenant_data["login-footer-size"] = loginFooterSize
                        csssize = """.copyright-footer{font-size: """ + loginFooterSize + """px}"""

                        preview_base_data = preview_base_data.replace("<<copyright-size-preview>>", csssize)
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    if "footer_placement" in data.keys():
                        footer_placement = request.POST["footer_placement"]
                        tenant_data["footer_placement"] = footer_placement

                        place_css = """.copyright-footer{text-align:""" + footer_placement + """}"""

                        preview_base_data = preview_base_data.replace(
                            "<<copyright-placement-preview>>", place_css
                        )
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                    if "login_footer_bgcolor" in data.keys():
                        login_footer_bgcolor = request.POST["login_footer_bgcolor"]
                        tenant_data["login_footer_bgcolor"] = login_footer_bgcolor
                        color_css = """.copyright-footer{color:""" + login_footer_bgcolor + """}"""

                        preview_base_data = preview_base_data.replace(
                            "<<copyright-color-preview>>", color_css
                        )
                        with open(
                            f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html",
                            "w",
                        ) as to_file:
                            to_file.write(preview_base_data)
                            to_file.close()

                else:
                    tenant_data["customize_footer"] = "False"
                    tenant_data["footer_text"] = "Copyright © 2023 Acies. All rights reserved."

                    preview_base_data = preview_base_data.replace(
                        "<custom_footer_preview>", "Copyright © 2023 Acies. All rights reserved."
                    )
                    preview_base_data = preview_base_data.replace("<<copyright-size-preview>>", "")
                    preview_base_data = preview_base_data.replace("<<copyright-placement-preview>>", "")
                    preview_base_data = preview_base_data.replace("<<copyright-color-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "signup_header" in data.keys():
                tenant_data["signup_header"] = request.POST["signup_header"]

                preview_base_data = preview_base_data.replace(
                    "<<signupheader>>", request.POST["signup_header"]
                )
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "signup_msg" in data.keys():
                tenant_data["signup_msg"] = request.POST["signup_msg"]

                preview_base_data = preview_base_data.replace("<<signupmsg>>", request.POST["signup_msg"])
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "rename_username" in data.keys():
                tenant_data["rename_username"] = request.POST["rename_username"]
                rename_script = (
                    '''$(document).ready(function () {
                                    $('#div_id_login label, #signup_username label').html("'''
                    + request.POST["rename_username"]
                    + """")
                                    });"""
                )

                preview_base_data = preview_base_data.replace("<<rename_username>>", rename_script)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "rename_email" in data.keys():
                tenant_data["rename_email"] = request.POST["rename_email"]
                rename_script = (
                    '''$(document).ready(function () {
                                    $('#signup_email label').html("'''
                    + request.POST["rename_email"]
                    + """")
                                    });"""
                )

                preview_base_data = preview_base_data.replace("<<rename_email>>", rename_script)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "rename_password" in data.keys():
                tenant_data["rename_password"] = request.POST["rename_password"]
                rename_script = (
                    '''$(document).ready(function () {
                                    $('#div_id_password label,#signup_password label').html("'''
                    + request.POST["rename_password"]
                    + """")
                                    });"""
                )

                preview_base_data = preview_base_data.replace("<<rename_password>>", rename_script)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "rename_confirm_password" in data.keys():
                tenant_data["rename_confirm_password"] = request.POST["rename_confirm_password"]
                rename_script = (
                    '''$(document).ready(function () {
                                    $('#signup_confirm_password label').html("'''
                    + request.POST["rename_confirm_password"]
                    + """")
                                    });"""
                )

                preview_base_data = preview_base_data.replace("<<rename_confirm_password>>", rename_script)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "remove_signup" in data.keys():
                tenant_data["remove_signup"] = request.POST["remove_signup"]
                if request.POST["remove_signup"] == "True":
                    css = """ .bluebg{
                        display: none !important;
                        }
                        .formBx,.forgot-password{
                        left: 0 !important;
                        right: 0 !important;
                        margin: 0 auto;
                        }
                        @media (max-width: 991px){
                        .formBx, .forgot-password {
                            width: 100%;
                            height: 480px;
                            top: 0;
                            bottom: 0;
                            margin: auto;
                        }
                    }"""

                    preview_base_data = preview_base_data.replace("<<no-signup-preview>>", css)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<no-signup-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_remember_me" in data.keys():
                tenant_data["remove_remember_me"] = request.POST["remove_remember_me"]
                if request.POST["remove_remember_me"] == "True":
                    css = """ #div_id_remember{
                        display: none !important;
                        }
                        """

                    preview_base_data = preview_base_data.replace("<<no-remember-me-preview>>", css)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<no-remember-me-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_admin_toggle" in data.keys():
                tenant_data["remove_admin_toggle"] = request.POST["remove_admin_toggle"]
                if request.POST["remove_admin_toggle"] == "True":
                    css = """.admin-check{
                        display: none !important;
                        }
                        """

                    preview_base_data = preview_base_data.replace("<<remove_admin_toggle>>", css)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<remove_admin_toggle>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "block_autocomplete_credentials" in data.keys():
                tenant_data["block_autocomplete_credentials"] = request.POST["block_autocomplete_credentials"]
                if request.POST["block_autocomplete_credentials"] == "True":
                    jsValue = """
                        $(document).ready(function() {
                            let input_username_signin = document.querySelector('#div_id_login input')
                            input_username_signin.setAttribute("autocomplete","off")
                            let input_loginpassword = document.querySelector('#div_id_password input')
                            input_loginpassword.setAttribute("autocomplete","off")
                            let input_username_signup = document.querySelector('#signup_username input')
                            input_username_signup.setAttribute("autocomplete","off")
                            let input_signup_email = document.querySelector('#signup_email input')
                            input_signup_email.setAttribute("autocomplete","__away")
                            let input_signup_password = document.querySelector('#signup_password input')
                            input_signup_password.setAttribute("autocomplete","off")
                            let input_signup_confirm_password = document.querySelector('#signup_confirm_password input')
                            input_signup_confirm_password.setAttribute("autocomplete","off")
                        });"""

                    preview_base_data = preview_base_data.replace(
                        "<<block_autocomplete_credentials>>", jsValue
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<block_autocomplete_credentials>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_terms" in data.keys():
                tenant_data["remove_terms"] = request.POST["remove_terms"]
                if request.POST["remove_terms"] == "True":
                    jsValue = """
                        $(document).ready(function() {
                            $("#terms_div").css("display","none")
                            $("#aciessigninbutton").removeAttr("disabled")
                        });"""

                    preview_base_data = preview_base_data.replace("<<no-terms-preview>>", jsValue)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    jsValue = """
                        $(document).ready(function() {
                            $("#terms_div").css("display","block")
                            $("#aciessigninbutton").prop("disabled",true)
                        });"""

                    preview_base_data = preview_base_data.replace("<<no-terms-preview>>", jsValue)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_labels" in data.keys():
                tenant_data["remove_labels"] = request.POST["remove_labels"]
                if request.POST["remove_labels"] == "True":
                    css = """ #div_id_login label, #div_id_password label{
                        display: none !important;
                        }
                        #div_id_login, #div_id_password{
                            margin: 2rem auto;
                        }
                        """

                    preview_base_data = preview_base_data.replace("<<no-labels-preview>>", css)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    preview_base_data = preview_base_data.replace("<<no-labels-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "allow_copy_paste_username" in data.keys():
                tenant_data["allow_copy_paste_username"] = request.POST["allow_copy_paste_username"]
                if request.POST["allow_copy_paste_username"] == "True":
                    userscript = """$(document).ready(function () {
                                    $('#div_id_login input').bind('cut copy paste', function (e) {
                                    e.preventDefault();
                                    });
                                });"""

                    preview_base_data = preview_base_data.replace("<<userscript-preview>>", userscript)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<userscript-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "allow_copy_paste_email" in data.keys():
                tenant_data["allow_copy_paste_email"] = request.POST["allow_copy_paste_email"]
                if request.POST["allow_copy_paste_email"] == "True":
                    emailscript = """$(document).ready(function () {
                                    $('#signup_email_input').bind('cut copy paste', function (e) {
                                    e.preventDefault();
                                    });
                                });"""

                    preview_base_data = preview_base_data.replace("<<emailscript-preview>>", emailscript)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<emailscript-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "allow_copy_paste_password" in data.keys():
                tenant_data["allow_copy_paste_password"] = request.POST["allow_copy_paste_password"]
                if request.POST["allow_copy_paste_password"] == "True":
                    passwordscript = """$(document).ready(function () {
                                    $('#div_id_password input').bind('cut copy paste', function (e) {
                                    e.preventDefault();
                                    });
                                });"""

                    preview_base_data = preview_base_data.replace(
                        "<<passwordscript-preview>>", passwordscript
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<passwordscript-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "add_icons" in data.keys():
                tenant_data["add_icons"] = request.POST["add_icons"]
                if request.POST["add_icons"] == "True":
                    icon_script = """
                    $("#div_id_login input").addClass("added_icons")
                    $("#div_id_login input").parent().prepend('<i class="fa fa-user" style="position:absolute; z-index:1;margin:9px;font-size:17px;"></i>')
                    $("#div_id_password input").addClass("added_icons")
                    $("#div_id_password input").parent().prepend('<i class="fa fa-lock" style="position:absolute; z-index:1;margin:9px;font-size:17px;"></i>')"""

                    preview_base_data = preview_base_data.replace("<<put-icons-preview>>", icon_script)
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:

                    preview_base_data = preview_base_data.replace("<<put-icons-preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "icon_bgcolor" in data.keys():
                icon_bgcolor = request.POST["icon_bgcolor"]
                tenant_data["icon_bgcolor"] = icon_bgcolor
                color_css = '''$(".added_icons").siblings("i").css("color","''' + icon_bgcolor + """")"""

                preview_base_data = preview_base_data.replace("<<icon-color>>", color_css)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            else:

                preview_base_data = preview_base_data.replace("<<icon-color>>", "")
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "sign_btn_bgcolor" in data.keys():
                sign_btn_bgcolor = request.POST["sign_btn_bgcolor"]
                tenant_data["sign_btn_bgcolor"] = sign_btn_bgcolor
                hover_css = (
                    """#aciessigninbutton:hover{background-color:""" + sign_btn_bgcolor + """ !important}"""
                )

                preview_base_data = preview_base_data.replace("<<button-hover-preview>>", hover_css)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            else:

                preview_base_data = preview_base_data.replace("<<button-hover-preview>>", "")
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "sign_font_bgcolor" in data.keys():
                sign_font_bgcolor = request.POST["sign_font_bgcolor"]
                tenant_data["sign_font_bgcolor"] = sign_font_bgcolor
                hover_css = """#aciessigninbutton:hover{color:""" + sign_font_bgcolor + """}"""

                preview_base_data = preview_base_data.replace("<<button-hover-font-preview>>", hover_css)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            else:

                preview_base_data = preview_base_data.replace("<<button-hover-font-preview>>", "")
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "login_card_bgcolor" in data.keys():
                login_card_bgcolor = request.POST["login_card_bgcolor"]
                tenant_data["login_card_bgcolor"] = login_card_bgcolor
                color_css = """.bluebg{background-color:""" + login_card_bgcolor + """}"""

                preview_base_data = preview_base_data.replace("<<login-bg-preview>>", color_css)
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            else:

                preview_base_data = preview_base_data.replace("<<login-bg-preview>>", "")
                with open(
                    f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                ) as to_file:
                    to_file.write(preview_base_data)
                    to_file.close()

            if "remove_all_social" in data.keys():
                if request.POST["remove_all_social"] == "True":
                    tenant_data["remove_all_social"] = "True"

                    removeall_css = """.ui.horizontal.divider, .social-container{display: none;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_all_social_preview>>", removeall_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_all_social"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_all_social_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_facebook" in data.keys():
                if request.POST["remove_facebook"] == "True":
                    tenant_data["remove_facebook"] = "True"

                    remove_facebook_css = """.facebookBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_facebook_preview>>", remove_facebook_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_facebook"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_facebook_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_google" in data.keys():
                if request.POST["remove_google"] == "True":
                    tenant_data["remove_google"] = "True"

                    remove_google_css = """.googleBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_google_preview>>", remove_google_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_google"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_google_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_microsoft" in data.keys():
                if request.POST["remove_microsoft"] == "True":
                    tenant_data["remove_microsoft"] = "True"

                    remove_microsoft_css = """.microsoftBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_microsoft_preview>>", remove_microsoft_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_microsoft"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_microsoft_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_twitter" in data.keys():
                if request.POST["remove_twitter"] == "True":
                    tenant_data["remove_twitter"] = "True"

                    remove_twitter_css = """.twitterBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_twitter_preview>>", remove_twitter_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_twitter"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_twitter_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_amazon" in data.keys():
                if request.POST["remove_amazon"] == "True":
                    tenant_data["remove_amazon"] = "True"

                    remove_amazon_css = """.amazonBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_amazon_preview>>", remove_amazon_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_amazon"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_amazon_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "remove_apple" in data.keys():
                if request.POST["remove_apple"] == "True":
                    tenant_data["remove_apple"] = "True"

                    remove_apple_css = """.appleBtn{display: none !important;}"""

                    preview_base_data = preview_base_data.replace(
                        "<<remove_apple_preview>>", remove_apple_css
                    )
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

                else:
                    tenant_data["remove_apple"] = "False"

                    preview_base_data = preview_base_data.replace("<<remove_apple_preview>>", "")
                    with open(
                        f"kore_investment/templates/user_defined_template/{tenant}/login/preview.html", "w"
                    ) as to_file:
                        to_file.write(preview_base_data)
                        to_file.close()

            if "set_title_login" in data.keys():
                if request.POST["set_title_login"] == "True":
                    tenant_data["set_title_login"] = "True"
                    if "login_title" in request.POST:
                        tenant_data["login_title"] = request.POST["login_title"]

                    else:
                        tenant_data["login_title"] = "Sign In"

                else:
                    tenant_data["set_title_login"] = "False"
                    tenant_data["login_title"] = "Sign In"

            if "set_favicon_login" in data.keys():
                if request.POST["set_favicon_login"] == "True":
                    tenant_data["set_favicon_login"] = "True"
                    if "login_favicon_file" in request.FILES:
                        tenant_data["login_favicon_file"] = request.FILES["login_favicon_file"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/login_screen/favicon/"
                            + request.FILES["login_favicon_file"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/login_screen/favicon"
                        ):
                            os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/login_screen/favicon")
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["login_favicon_file"].chunks():
                                destination.write(chunk)
                            destination.close()

                    elif "login_favicon_file" in t_config_data:
                        image_path = (
                            f"/media/{tenant}/TenantTheme/login_screen/favicon/"
                            + t_config_data["login_favicon_file"]
                        )
                        tenant_data["login_favicon_file"] = t_config_data["login_favicon_file"]

                    else:
                        tenant_data["set_favicon_login"] = "False"

                else:
                    tenant_data["set_favicon_login"] = "False"

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update(tenant_data)
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "appdrawer_customization":

            data = request.POST
            tenant_data = {}

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                cdata = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    cdata = json.load(json_file)
                    for t_name, t_config in cdata.items():
                        if t_name == tenant:
                            existing_data = t_config
                    json_file.close()

            if "customize_appdrawer_bg" in data.keys():
                if request.POST["customize_appdrawer_bg"] == "True":
                    tenant_data["customize_appdrawer_bg"] = "True"
                    if request.POST["change_appdrawer_bg_file"] == "True":
                        tenant_data["change_appdrawer_bg_file"] = "True"
                        if "appdrawer_bg_image" in request.FILES:
                            appdrawer_bg_image = request.FILES["appdrawer_bg_image"]
                            appdrawer_bg_image_name = appdrawer_bg_image.name
                            tenant_data["appdrawer_bg_image_name"] = appdrawer_bg_image_name

                            tenant_data["appdrawer_bg_image"] = "True"

                            if not os.path.exists(
                                f"kore_investment/media/{tenant}/TenantTheme/appdrawer/background_images"
                            ):
                                os.makedirs(
                                    f"kore_investment/media/{tenant}/TenantTheme/appdrawer/background_images"
                                )
                            with open(
                                f"kore_investment/media/{tenant}/TenantTheme/appdrawer/background_images/"
                                + appdrawer_bg_image_name,
                                "wb+",
                            ) as destination:
                                for chunk in appdrawer_bg_image.chunks():
                                    destination.write(chunk)
                                destination.close()

                        elif "appdrawer_bg_image_name" in existing_data:
                            appdrawer_bg_image_name = existing_data["appdrawer_bg_image_name"]

                        else:
                            tenant_data["change_appdrawer_bg_file"] = "False"

                    else:
                        tenant_data["change_appdrawer_bg_file"] = "False"
                        if "appdrawer_bgColor" in data.keys():
                            if request.POST["appdrawer_bgColor"] == "True":
                                tenant_data["appdrawer_bgColor"] = "True"

                                appdrawer_bgColorCode = request.POST["appdrawer_bgColorCode"]
                                tenant_data["appdrawer_bgColorCode"] = appdrawer_bgColorCode

                            elif "appdrawer_bgColorCode" in existing_data:
                                appdrawer_bgColorCode = existing_data["appdrawer_bgColorCode"]

                            else:
                                tenant_data["appdrawer_bgColor"] = "False"
                        else:
                            tenant_data["appdrawer_bgColor"] = "False"

                else:
                    tenant_data["customize_appdrawer_bg"] = "False"

            else:
                tenant_data["customize_appdrawer_bg"] = "False"

            if "set_app_drawer_theme" in data.keys():
                if request.POST["set_app_drawer_theme"] == "True":
                    tenant_data["set_app_drawer_theme"] = "True"

                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                        cdata = {}
                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                            cdata = json.load(json_file)
                            for t_name, t_config in cdata.items():
                                if t_name == tenant:
                                    json_data = t_config
                            json_file.close()

                    font_color = request.POST["font_bgcolor"]
                    font_hover_color = request.POST["font_hover_bgcolor"]
                    primary_bgcolor = request.POST["primary_bgcolor"]
                    secondary_color = request.POST["secondary_bgcolor"]
                    font_family = request.POST["font_style_app_drawer"]

                    json_data["font_color"] = font_color
                    json_data["font_hover_color"] = font_hover_color
                    json_data["primary_bgcolor"] = primary_bgcolor
                    json_data["secondary_color"] = secondary_color
                    json_data["font_family"] = font_family

                    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                        cdata = {}

                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                            cdata = json.load(json_file)
                            for t_name, t_config in cdata.items():
                                if t_name == tenant:
                                    t_config.update(json_data)
                            json_file.close()

                        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                            json.dump(cdata, json_file, indent=4)
                            json_file.close()
                else:
                    tenant_data["set_app_drawer_theme"] = "False"

            if "set_appdrawer_template" in data.keys():
                if request.POST["set_appdrawer_template"] == "True":

                    tenant_data["set_appdrawer_template"] = "True"
                    tenant_data["app_template"] = request.POST["app_template"]
                    print("1948")
                    print(request.POST["app_template"])
                    if request.POST["app_template"] == "template4":
                        tenant_data["widgets_template_value"] = request.POST["widgets_template_value"]

                else:
                    tenant_data["set_appdrawer_template"] = "False"

            if "add_logo_appdrawer" in data.keys():
                if request.POST["add_logo_appdrawer"] == "True":

                    tenant_data["add_logo_appdrawer"] = "True"

                    if "logo-file-appdrawer" in request.FILES:
                        tenant_data["logo-file-appdrawer"] = request.FILES["logo-file-appdrawer"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/appdrawer/logo/"
                            + request.FILES["logo-file-appdrawer"].name
                        )

                        if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/appdrawer/logo"):
                            os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/appdrawer/logo")
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["logo-file-appdrawer"].chunks():
                                destination.write(chunk)
                            destination.close()

                    elif "logo-file-appdrawer" in existing_data:
                        tenant_data["logo-file-appdrawer"] = existing_data["logo-file-appdrawer"]

                    else:
                        tenant_data["add_logo_appdrawer"] = "False"
                else:
                    tenant_data["add_logo_appdrawer"] = "False"

            if "add_logo_topnavbar" in data.keys():
                if request.POST["add_logo_topnavbar"] == "True":

                    tenant_data["add_logo_topnavbar"] = "True"

                    if "logo-file-topnavbar" in request.FILES:
                        tenant_data["logo-file-topnavbar"] = request.FILES["logo-file-topnavbar"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/appdrawer/logo/"
                            + request.FILES["logo-file-topnavbar"].name
                        )

                        if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/appdrawer/logo"):
                            os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/appdrawer/logo")
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["logo-file-topnavbar"].chunks():
                                destination.write(chunk)
                            destination.close()

                    elif "logo-file-topnavbar" in existing_data:
                        tenant_data["logo-file-topnavbar"] = existing_data["logo-file-topnavbar"]

                    else:
                        tenant_data["add_logo_topnavbar"] = "False"
                else:
                    tenant_data["add_logo_topnavbar"] = "False"

            if "customize_app_footer" in data.keys():
                if request.POST["customize_app_footer"] == "True":
                    tenant_data["customize_app_footer"] = "True"
                    if "app-footer-editor" in data.keys():
                        custom_footer = request.POST["app-footer-editor"]
                        tenant_data["app_footer_text"] = custom_footer

                    if "app_footer_size" in data.keys():
                        AppFooterSize = request.POST["app_footer_size"]
                        tenant_data["app_footer_size"] = AppFooterSize

                    if "app_footer_placement" in data.keys():
                        app_footer_placement = request.POST["app_footer_placement"]
                        tenant_data["app_footer_placement"] = app_footer_placement

                    if "app_footer_bgcolor" in data.keys():
                        app_footer_bgcolor = request.POST["app_footer_bgcolor"]
                        tenant_data["app_footer_bgcolor"] = app_footer_bgcolor

                else:
                    tenant_data["customize_app_footer"] = "False"
                    default_text = "ACIES, Acies Consulting, Acies TechWorks, Acies Ventures, Acies LightHouse, Kepler, Kore, Callisto, Carpo, Revolutio and Antares are registered trademarks of Acies LLP, Acies Consulting Pte Ltd. and its subsidiaries in different countries and territories. Unauthorized use, misrepresentation or misuse of trademarks is strictly prohibited and subject to legal action under various laws."
                    tenant_data["app_footer_text"] = default_text

            if "set_title_appdrawer" in data.keys():
                if request.POST["set_title_appdrawer"] == "True":
                    tenant_data["set_title_appdrawer"] = "True"
                    if "appdrawer_title" in request.POST:
                        tenant_data["appdrawer_title"] = request.POST["appdrawer_title"]
                    else:
                        tenant_data["appdrawer_title"] = "Revolutio"
                else:
                    tenant_data["set_title_appdrawer"] = "False"

            if "set_favicon_appdrawer" in data.keys():
                if request.POST["set_favicon_appdrawer"] == "True":
                    tenant_data["set_favicon_appdrawer"] = "True"
                    if "appdrawer_favicon_file" in request.FILES:
                        tenant_data["appdrawer_favicon_file"] = request.FILES["appdrawer_favicon_file"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/appdrawer/favicon/"
                            + request.FILES["appdrawer_favicon_file"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/appdrawer/favicon"
                        ):
                            os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/appdrawer/favicon")
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["appdrawer_favicon_file"].chunks():
                                destination.write(chunk)
                            destination.close()

                    elif "appdrawer_favicon_file" in existing_data:
                        tenant_data["appdrawer_favicon_file"] = existing_data["appdrawer_favicon_file"]

                    else:
                        tenant_data["set_favicon_appdrawer"] = "False"
                else:
                    tenant_data["set_favicon_appdrawer"] = "False"

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update(tenant_data)
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved"})

        if request.POST["operation"] == "error_page_customization":

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            existing_data = t_config
                    json_file.close()

                data = request.POST
                tenant_data = {}

                if "add_logo_error" in data.keys():
                    tenant_data["add_logo_error"] = "True"
                    if "logo_file_error_page" in request.FILES:
                        tenant_data["logo_file_error_page"] = request.FILES["logo_file_error_page"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/logo/"
                            + request.FILES["logo_file_error_page"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/logo"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/logo/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["logo_file_error_page"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_logo_error" in existing_data.keys() and existing_data["add_logo_error"] == "True"
                    ):
                        tenant_data["add_logo_error"] = "True"
                    else:
                        tenant_data["add_logo_error"] = "False"

                else:
                    tenant_data["add_logo_error"] = "False"

                if "add_bg_error_subprocess" in data.keys():
                    tenant_data["add_bg_error_subprocess"] = "True"
                    if "subprocess_bg" in request.FILES:
                        tenant_data["subprocess_bg"] = request.FILES["subprocess_bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["subprocess_bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["subprocess_bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error_subprocess" in existing_data.keys()
                        and existing_data["add_bg_error_subprocess"] == "True"
                    ):
                        tenant_data["add_bg_error_subprocess"] = "True"
                    else:
                        tenant_data["add_bg_error_subprocess"] = "False"

                else:
                    tenant_data["add_bg_error_subprocess"] = "False"

                    # favicon subprocess
                if "add_favicon_error_subprocess" in data.keys():
                    tenant_data["add_favicon_error_subprocess"] = "True"
                    if "subprocess_favicon" in request.FILES:
                        tenant_data["subprocess_favicon"] = request.FILES["subprocess_favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["subprocess_favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["subprocess_favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error_subprocess" in existing_data.keys()
                        and existing_data["add_favicon_error_subprocess"] == "True"
                    ):
                        tenant_data["add_favicon_error_subprocess"] = "True"
                    else:
                        tenant_data["add_favicon_error_subprocess"] = "False"

                else:
                    tenant_data["add_favicon_error_subprocess"] = "False"

                if "change_subprocess_text" in data.keys():
                    tenant_data["change_subprocess_text"] = "True"
                    if "subprocess_text" in data.keys() and data["subprocess_text"] != None:
                        tenant_data["subprocess_text"] = request.POST["subprocess_text"]
                    elif (
                        "subprocess_text" in existing_data.keys()
                        and existing_data["change_subprocess_text"] == "True"
                    ):
                        tenant_data["change_subprocess_text"] = "True"
                    else:
                        tenant_data["change_subprocess_text"] = "False"
                else:
                    tenant_data["change_subprocess_text"] = "False"

                if "change_subprocess_button" in data.keys():
                    tenant_data["change_subprocess_button"] = "True"
                    if "buttons_subprocess" in data.keys():
                        tenant_data["buttons_subprocess"] = {}
                        buttons_subprocess_json = data.get("buttons_subprocess", "")
                        buttons_subprocess_dict = json.loads(buttons_subprocess_json)
                        for key, value in buttons_subprocess_dict.items():
                            tenant_data["buttons_subprocess"][key] = value
                else:
                    tenant_data["change_subprocess_button"] = "False"
                    tenant_data["buttons_subprocess"] = "False"

                if "add_bg_error404" in data.keys():
                    tenant_data["add_bg_error404"] = "True"
                    if "404bg" in request.FILES:
                        tenant_data["404bg"] = request.FILES["404bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["404bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["404bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error404" in existing_data.keys()
                        and existing_data["add_bg_error404"] == "True"
                    ):
                        tenant_data["add_bg_error404"] = "True"
                    else:
                        tenant_data["add_bg_error404"] = "False"

                else:
                    tenant_data["add_bg_error404"] = "False"
                # favicon error 404
                if "add_favicon_error404" in data.keys():
                    tenant_data["add_favicon_error404"] = "True"
                    if "404favicon" in request.FILES:
                        tenant_data["404favicon"] = request.FILES["404favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["404favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["404favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error404" in existing_data.keys()
                        and existing_data["add_favicon_error404"] == "True"
                    ):
                        tenant_data["add_favicon_error404"] = "True"
                    else:
                        tenant_data["add_favicon_error404"] = "False"

                else:
                    tenant_data["add_favicon_error404"] = "False"

                if "change_404_text" in data.keys():
                    tenant_data["change_404_text"] = "True"
                    if "text_404" in data.keys() and data["text_404"] != None:
                        tenant_data["text_404"] = request.POST["text_404"]
                    elif "text_404" in existing_data.keys() and existing_data["change_404_text"] == "True":
                        tenant_data["change_404_text"] = "True"
                    else:
                        tenant_data["change_404_text"] = "False"
                else:
                    tenant_data["change_404_text"] = "False"

                if "change_404_button" in data.keys():
                    tenant_data["change_404_button"] = "True"
                    if "buttons_404" in data.keys():
                        tenant_data["buttons_404"] = {}
                        buttons_404_json = data.get("buttons_404", "")
                        buttons_404_dict = json.loads(buttons_404_json)
                        for key, value in buttons_404_dict.items():
                            tenant_data["buttons_404"][key] = value
                else:
                    tenant_data["change_404_button"] = "False"
                    tenant_data["buttons_404"] = "False"

                if "add_bg_error500" in data.keys():
                    tenant_data["add_bg_error500"] = "True"
                    if "500bg" in request.FILES:
                        tenant_data["500bg"] = request.FILES["500bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["500bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["500bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error500" in existing_data.keys()
                        and existing_data["add_bg_error500"] == "True"
                    ):
                        tenant_data["add_bg_error500"] = "True"
                    else:
                        tenant_data["add_bg_error500"] = "False"

                else:
                    tenant_data["add_bg_error500"] = "False"

                if "add_favicon_error500" in data.keys():
                    tenant_data["add_favicon_error500"] = "True"
                    if "500favicon" in request.FILES:
                        tenant_data["500favicon"] = request.FILES["500favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["500favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["500favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error500" in existing_data.keys()
                        and existing_data["add_favicon_error500"] == "True"
                    ):
                        tenant_data["add_favicon_error500"] = "True"
                    else:
                        tenant_data["add_favicon_error500"] = "False"

                else:
                    tenant_data["add_favicon_error500"] = "False"

                if "change_500_text" in data.keys():
                    tenant_data["change_500_text"] = "True"
                    if "text_500" in data.keys() and data["text_500"] != None:
                        tenant_data["text_500"] = request.POST["text_500"]
                    elif "text_500" in existing_data.keys() and existing_data["change_500_text"] == "True":
                        tenant_data["change_500_text"] = "True"
                    else:
                        tenant_data["change_500_text"] = "False"
                else:
                    tenant_data["change_500_text"] = "False"

                if "change_500_button" in data.keys():
                    tenant_data["change_500_button"] = "True"
                    if "buttons_500" in data.keys():
                        tenant_data["buttons_500"] = {}
                        buttons_500_json = data.get("buttons_500", "")
                        buttons_500_dict = json.loads(buttons_500_json)
                        for key, value in buttons_500_dict.items():
                            tenant_data["buttons_500"][key] = value
                else:
                    tenant_data["change_500_button"] = "False"
                    tenant_data["buttons_500"] = "False"

                if "add_bg_error403" in data.keys():
                    tenant_data["add_bg_error403"] = "True"
                    if "403bg" in request.FILES:
                        tenant_data["403bg"] = request.FILES["403bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["403bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["403bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error403" in existing_data.keys()
                        and existing_data["add_bg_error403"] == "True"
                    ):
                        tenant_data["add_bg_error403"] = "True"
                    else:
                        tenant_data["add_bg_error403"] = "False"

                else:
                    tenant_data["add_bg_error403"] = "False"
                # favicon error 403
                if "add_favicon_error403" in data.keys():
                    tenant_data["add_favicon_error403"] = "True"
                    if "403favicon" in request.FILES:
                        tenant_data["403favicon"] = request.FILES["403favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["403favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["403favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error403" in existing_data.keys()
                        and existing_data["add_favicon_error403"] == "True"
                    ):
                        tenant_data["add_favicon_error403"] = "True"
                    else:
                        tenant_data["add_favicon_error403"] = "False"

                else:
                    tenant_data["add_favicon_error403"] = "False"

                if "change_403_text" in data.keys():
                    tenant_data["change_403_text"] = "True"
                    if "text_403" in data.keys() and data["text_403"] != None:
                        tenant_data["text_403"] = request.POST["text_403"]
                    elif "text_403" in existing_data.keys() and existing_data["change_403_text"] == "True":
                        tenant_data["change_403_text"] = "True"
                    else:
                        tenant_data["change_403_text"] = "False"
                else:
                    tenant_data["change_403_text"] = "False"

                if "change_403_button" in data.keys():
                    tenant_data["change_403_button"] = "True"
                    if "buttons_403" in data.keys():
                        tenant_data["buttons_403"] = {}
                        buttons_403_json = data.get("buttons_403", "")
                        buttons_403_dict = json.loads(buttons_403_json)
                        for key, value in buttons_403_dict.items():
                            tenant_data["buttons_403"][key] = value
                else:
                    tenant_data["change_403_button"] = "False"
                    tenant_data["buttons_403"] = "False"

                if "add_bg_error502" in data.keys():
                    tenant_data["add_bg_error502"] = "True"
                    if "502bg" in request.FILES:
                        tenant_data["502bg"] = request.FILES["502bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["502bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["502bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error502" in existing_data.keys()
                        and existing_data["add_bg_error502"] == "True"
                    ):
                        tenant_data["add_bg_error502"] = "True"
                    else:
                        tenant_data["add_bg_error502"] = "False"

                else:
                    tenant_data["add_bg_error502"] = "False"

                if "add_favicon_error502" in data.keys():
                    tenant_data["add_favicon_error502"] = "True"
                    if "502favicon" in request.FILES:
                        tenant_data["502favicon"] = request.FILES["502favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["502favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["502favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error502" in existing_data.keys()
                        and existing_data["add_favicon_error502"] == "True"
                    ):
                        tenant_data["add_favicon_error502"] = "True"
                    else:
                        tenant_data["add_favicon_error502"] = "False"

                else:
                    tenant_data["add_favicon_error502"] = "False"

                if "change_502_text" in data.keys():
                    tenant_data["change_502_text"] = "True"
                    if "text_502" in data.keys() and data["text_502"] != None:
                        tenant_data["text_502"] = request.POST["text_502"]
                    elif "text_502" in existing_data.keys() and existing_data["change_502_text"] == "True":
                        tenant_data["change_502_text"] = "True"
                    else:
                        tenant_data["change_502_text"] = "False"
                else:
                    tenant_data["change_502_text"] = "False"

                if "change_502_button" in data.keys():
                    tenant_data["change_502_button"] = "True"
                    if "buttons_502" in data.keys():
                        tenant_data["buttons_502"] = {}
                        buttons_502_json = data.get("buttons_502", "")
                        buttons_502_dict = json.loads(buttons_502_json)
                        for key, value in buttons_502_dict.items():
                            tenant_data["buttons_502"][key] = value
                else:
                    tenant_data["change_502_button"] = "False"
                    tenant_data["buttons_502"] = "False"

                if "add_bg_error503" in data.keys():
                    tenant_data["add_bg_error503"] = "True"
                    if "503bg" in request.FILES:
                        tenant_data["503bg"] = request.FILES["503bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["503bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["503bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error503" in existing_data.keys()
                        and existing_data["add_bg_error503"] == "True"
                    ):
                        tenant_data["add_bg_error503"] = "True"
                    else:
                        tenant_data["add_bg_error503"] = "False"

                else:
                    tenant_data["add_bg_error503"] = "False"
                # favicon error 503
                if "add_favicon_error503" in data.keys():
                    tenant_data["add_favicon_error503"] = "True"
                    if "503favicon" in request.FILES:
                        tenant_data["503favicon"] = request.FILES["503favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["503favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["503favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error503" in existing_data.keys()
                        and existing_data["add_favicon_error503"] == "True"
                    ):
                        tenant_data["add_favicon_error503"] = "True"
                    else:
                        tenant_data["add_favicon_error503"] = "False"

                else:
                    tenant_data["add_favicon_error503"] = "False"

                if "change_503_text" in data.keys():
                    tenant_data["change_503_text"] = "True"
                    if "text_503" in data.keys() and data["text_503"] != None:
                        tenant_data["text_503"] = request.POST["text_503"]
                    elif "text_503" in existing_data.keys() and existing_data["change_503_text"] == "True":
                        tenant_data["change_503_text"] = "True"
                    else:
                        tenant_data["change_503_text"] = "False"
                else:
                    tenant_data["change_503_text"] = "False"

                if "change_503_button" in data.keys():
                    tenant_data["change_503_button"] = "True"
                    if "buttons_503" in data.keys():
                        tenant_data["buttons_503"] = {}
                        buttons_503_json = data.get("buttons_503", "")
                        buttons_503_dict = json.loads(buttons_503_json)
                        for key, value in buttons_503_dict.items():
                            tenant_data["buttons_503"][key] = value
                else:
                    tenant_data["change_503_button"] = "False"
                    tenant_data["buttons_503"] = "False"

                if "add_bg_error_permission" in data.keys():
                    tenant_data["add_bg_error_permission"] = "True"
                    if "permission_bg" in request.FILES:
                        tenant_data["permission_bg"] = request.FILES["permission_bg"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            + request.FILES["permission_bg"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/background/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["permission_bg"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_bg_error_permission" in existing_data.keys()
                        and existing_data["add_bg_error_permission"] == "True"
                    ):
                        tenant_data["add_bg_error_permission"] = "True"
                    else:
                        tenant_data["add_bg_error_permission"] = "False"
                else:
                    tenant_data["add_bg_error_permission"] = "False"

                if "add_favicon_error_permission" in data.keys():
                    tenant_data["add_favicon_error_permission"] = "True"
                    if "permission_favicon" in request.FILES:
                        tenant_data["permission_favicon"] = request.FILES["permission_favicon"].name
                        image_path = (
                            f"/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            + request.FILES["permission_favicon"].name
                        )

                        if not os.path.exists(
                            f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon"
                        ):
                            os.makedirs(
                                f"kore_investment/media/{tenant}/TenantTheme/custom_error_pages/favicon/"
                            )
                        with open(f"kore_investment{image_path}", "wb+") as destination:
                            for chunk in request.FILES["permission_favicon"].chunks():
                                destination.write(chunk)
                            destination.close()
                    elif (
                        "add_favicon_error_permission" in existing_data.keys()
                        and existing_data["add_favicon_error_permission"] == "True"
                    ):
                        tenant_data["add_favicon_error_permission"] = "True"
                    else:
                        tenant_data["add_favicon_error_permission"] = "False"
                else:
                    tenant_data["add_favicon_error_permission"] = "False"

                if "change_permission_text" in data.keys():
                    tenant_data["change_permission_text"] = "True"
                    if "permission_text" in data.keys():
                        tenant_data["permission_text"] = request.POST["permission_text"]
                    elif (
                        "permission_text" in existing_data.keys()
                        and existing_data["change_permission_text"] == "True"
                    ):
                        tenant_data["change_permission_text"] = "True"
                    else:
                        tenant_data["change_permission_text"] = "False"
                else:
                    tenant_data["change_permission_text"] = "False"

                if "change_permission_button" in data.keys():
                    tenant_data["change_permission_button"] = "True"
                    if "buttons_permission" in data.keys():
                        tenant_data["buttons_permission"] = {}
                        buttons_permission_json = data.get("buttons_permission", "")
                        buttons_permission_dict = json.loads(buttons_permission_json)
                        for key, value in buttons_permission_dict.items():
                            tenant_data["buttons_permission"][key] = value
                else:
                    tenant_data["change_permission_button"] = "False"
                    tenant_data["buttons_permission"] = "False"

                if "add_footer_error" in data.keys():
                    if request.POST["add_footer_error"] == "True":
                        tenant_data["add_footer_error"] = "True"
                        if "error_footer" in data.keys():
                            custom_footer = request.POST["error_footer"]
                            tenant_data["error_footer_text"] = custom_footer

                        if "error_footer_size" in data.keys():
                            ErrorFooterSize = request.POST["error_footer_size"]
                            tenant_data["error_footer_size"] = ErrorFooterSize

                        if "error_footer_placement" in data.keys():
                            error_footer_placement = request.POST["error_footer_placement"]
                            tenant_data["error_footer_placement"] = error_footer_placement

                        if "error_footer_bgcolor" in data.keys():
                            error_footer_bgcolor = request.POST["error_footer_bgcolor"]
                            tenant_data["error_footer_bgcolor"] = error_footer_bgcolor

                    else:
                        tenant_data["add_footer_error"] = "False"
                        default_text = "Copyright © 2023 Acies. All rights reserved."
                        tenant_data["error_footer_text"] = default_text

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update(tenant_data)
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveTenantAdminData":

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            existing_data = t_config
                    json_file.close()

            data = request.POST
            tenant_data = {}

            if "add_logo_tenant" in data.keys() and request.POST["add_logo_tenant"] == "True":
                tenant_data["add_logo_tenant"] = "True"
                if "logo_on_tenant" in request.FILES:
                    tenant_data["logo_on_tenant"] = request.FILES["logo_on_tenant"].name
                    image_path = (
                        f"/media/{tenant}/TenantTheme/tenant_admin/logo/"
                        + request.FILES["logo_on_tenant"].name
                    )

                    if not os.path.exists(f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/logo"):
                        os.makedirs(f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/logo/")
                    with open(f"kore_investment{image_path}", "wb+") as destination:
                        for chunk in request.FILES["logo_on_tenant"].chunks():
                            destination.write(chunk)
                        destination.close()
                elif "add_logo_tenant" in existing_data.keys() and existing_data["add_logo_tenant"] == "True":
                    tenant_data["add_logo_tenant"] = "True"
                else:
                    tenant_data["add_logo_tenant"] = "False"

            else:
                tenant_data["add_logo_tenant"] = "False"

            if "set_tenant_admin_theme" in data.keys():
                if request.POST["set_tenant_admin_theme"] == "True":
                    tenant_data["set_tenant_admin_theme"] = "True"

                    if "tenant_primary_bgcolor" in data.keys():
                        tenant_data["tenant_primary_bgcolor"] = request.POST["tenant_primary_bgcolor"]
                    if "tenant_secondary_bgcolor" in data.keys():
                        tenant_data["tenant_secondary_bgcolor"] = request.POST["tenant_secondary_bgcolor"]
                    if "tenant_font_bgcolor" in data.keys():
                        tenant_data["tenant_font_bgcolor"] = request.POST["tenant_font_bgcolor"]
                    if "tenant_hover_bgcolor" in data.keys():
                        tenant_data["tenant_hover_bgcolor"] = request.POST["tenant_hover_bgcolor"]
                    if "font_style_tenant_admin" in data.keys():
                        tenant_data["font_family_tenant"] = request.POST["font_style_tenant_admin"]

                else:
                    tenant_data["set_tenant_admin_theme"] = "False"

            if "tenantbg_bgcolor" in data.keys():
                tenant_data["set_tenantbg_bgcolor"] = "True"
                tenant_data["tenantbg_bgcolor"] = request.POST["tenantbg_bgcolor"]
            else:
                tenant_data["set_tenantbg_bgcolor"] = "False"

            if "add_bg_tenant_admin" in data.keys() and data["add_bg_tenant_admin"] == "True":
                tenant_data["add_bg_tenant_admin"] = "True"
                if "tenantloginBg" in data.keys():
                    if request.POST["tenantloginBg"] == "tenant_static_image":
                        if "tenant_static_image_file" in request.FILES:
                            tenant_static_image = request.FILES["tenant_static_image_file"]
                            tenant_static_image_file_name = request.FILES["tenant_static_image_file"].name
                            tenant_data["tenant_static_image_file"] = tenant_static_image_file_name
                            tenant_data["tenant_static_image"] = "True"
                            tenant_data["tenant_image_slider"] = "False"
                            tenant_data["tenant_video_on_loop"] = "False"

                            if not os.path.exists(
                                f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_images"
                            ):
                                os.makedirs(
                                    f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_images"
                                )
                            with open(
                                f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_images/"
                                + tenant_static_image_file_name,
                                "wb+",
                            ) as destination:
                                for chunk in tenant_static_image.chunks():
                                    destination.write(chunk)
                                destination.close()

                    elif request.POST["tenantloginBg"] == "tenant_image_slider":
                        if "tenant_image_slider_file1" in request.FILES:
                            tenant_data["tenant_static_image"] = "False"
                            tenant_data["tenant_image_slider"] = "True"
                            tenant_data["tenant_video_on_loop"] = "False"

                            counter = int(request.POST["tenant_counter"])
                            tenant_data["tenant_counter"] = counter

                            animation_fill = ""
                            transition_default_speed = 6
                            loop_default = "infinite"
                            animation_name = "imageAnimationSlow"
                            tenant_data["transition_default_speed"] = transition_default_speed
                            tenant_data["loop_default"] = loop_default
                            tenant_data["animation_name"] = animation_name
                            last_image = ""

                            if "tenant_play_on_loop" in data.keys():
                                tenant_data["tenant_play_on_loop"] = "True"
                                tenant_data["tenant_slider_play_on_loop"] = "True"
                            else:
                                loop_default = "1"
                                tenant_data["tenant_play_on_loop"] = "False"
                                tenant_data["tenant_slider_play_on_loop"] = "False"
                                animation_fill = "animation-fill-mode: forwards;"
                                animation_name = "imageAnimationNoLoop"
                                last_image = request.FILES[f"tenant_image_slider_file{1}"].name
                                tenant_data["tenant_last_image"] = last_image

                            if "tenant_transition_speed" in data.keys():
                                tenant_data["tenant_transition_speed_enable"] = "True"
                                tenant_data["tenant_transition_speed"] = request.POST[
                                    "tenant_transition_speed"
                                ]
                                if tenant_data["tenant_transition_speed"] == "tenant_slow_transition":
                                    transition_default_speed = 8
                                elif tenant_data["tenant_transition_speed"] == "tenant_fast_transition":
                                    transition_default_speed = 4
                                else:
                                    transition_default_speed = 6
                            else:
                                tenant_data["tenant_transition_speed_enable"] = "False"

                            if not os.path.exists(
                                f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/slider_images"
                            ):
                                os.makedirs(
                                    f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/slider_images"
                                )

                            totalImages = int(request.POST["tenant_totalimage"])
                            tenant_data["tenant_totalimage"] = totalImages
                            list_of_images = []

                            slider_style = '<ul class="cb-slideshow" style="<styleSlider>" >'
                            for i in range(1, totalImages + 1):

                                if f"tenant_image_slider_file{i}" in request.FILES:
                                    list_of_images.append(f"tenant_image_slider_file{i}")
                                    index = len(list_of_images)
                                    slider_file = request.FILES[f"tenant_image_slider_file{i}"]
                                    tenant_data[f"tenant_image_slider_file{i}"] = slider_file.name

                                    image_name = slider_file.name
                                    slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index-1)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/TenantTheme/tenant_admin/slider_images/{image_name}" /></span></li>'
                                    with open(
                                        f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/slider_images/"
                                        + image_name,
                                        "wb+",
                                    ) as destination:
                                        for chunk in slider_file.chunks():
                                            destination.write(chunk)
                                        destination.close()

                            if last_image:
                                slider_style += f'<li><span style="animation: {animation_name} {counter*transition_default_speed}s linear {loop_default};animation-delay: {(index)*transition_default_speed}s;{animation_fill}"><img class="lazyload" data-src="/media/{tenant}/TenantTheme/tenant_admin/slider_images/{last_image}" /></span></li>'

                            slider_style += "</ul>"

                            tenant_data["tenant_slider_style"] = slider_style

                    elif request.POST["tenantloginBg"] == "tenant_video_on_loop":
                        if "add_videobg_tenant" in data.keys():
                            tenant_data["tenant_static_image"] = "False"
                            tenant_data["tenant_image_slider"] = "False"
                            tenant_data["tenant_video_on_loop"] = "True"
                            tenant_data["add_videobg_tenant"] = request.POST["add_videobg_tenant"]

                            if request.POST["add_videobg_tenant"] == "video_File_tenant":
                                tenant_data["video_File_tenant"] = "True"
                                tenant_data["video_URL_tenant"] = "False"

                                if "video_file_bg_tenant" in request.FILES:
                                    bg_video_file = request.FILES["video_file_bg_tenant"]
                                    bg_video_name = request.FILES["video_file_bg_tenant"].name
                                    tenant_data["video_file_bg_tenant"] = bg_video_name

                                    if not os.path.exists(
                                        f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_video"
                                    ):
                                        os.makedirs(
                                            f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_video"
                                        )
                                    with open(
                                        f"kore_investment/media/{tenant}/TenantTheme/tenant_admin/background_video/"
                                        + bg_video_name,
                                        "wb+",
                                    ) as destination:
                                        for chunk in bg_video_file.chunks():
                                            destination.write(chunk)
                                        destination.close()

                            elif request.POST["add_videobg_tenant"] == "video_URL_tenant":
                                tenant_data["video_URL_tenant"] = "True"
                                tenant_data["video_File_tenant"] = "False"

                                if "video_url_bg_tenant" in data.keys():
                                    bg_video_url = request.POST["video_url_bg_tenant"]
                                    tenant_data["video_url_bg_tenant"] = bg_video_url

                            else:
                                tenant_data["tenant_video_on_loop"] = "False"

                    else:
                        tenant_data["tenant_static_image"] = "False"
                        tenant_data["tenant_image_slider"] = "False"
                        tenant_data["tenant_video_on_loop"] = "False"
                        tenant_data["add_bg_tenant_admin"] = "False"

                else:
                    tenant_data["tenant_static_image"] = "False"
                    tenant_data["tenant_image_slider"] = "False"
                    tenant_data["tenant_video_on_loop"] = "False"
                    tenant_data["add_bg_tenant_admin"] = "False"
            else:
                tenant_data["tenant_static_image"] = "False"
                tenant_data["tenant_image_slider"] = "False"
                tenant_data["tenant_video_on_loop"] = "False"
                tenant_data["add_bg_tenant_admin"] = "False"

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update(tenant_data)
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "developer_mode":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({"developer_mode": request.POST["developer_mode"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "allow_user_forum":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({"allow_user_forum": request.POST["allow_user_forum"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "allow_user_planner":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({"allow_user_planner": request.POST["allow_user_planner"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "allow_user_profile":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({"allow_user_profile": request.POST["allow_user_profile"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "allow_dashboard_portal":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update(
                                {"allow_dashboard_portal": request.POST["allow_dashboard_portal"]}
                            )
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "block_third_party":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({"block_third_party": request.POST["block_third_party"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "licenseConfig":
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            t_config.update({request.POST["key"]: request.POST["value"]})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveCustomLoginMessages":
            messageData = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            for key, value in request.POST.items():
                                if key == "operation":
                                    continue
                                messageData.update({key: value})
                            t_config.update({"customLoginMessages": messageData})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveRemembermeConfig":
            remembermeData = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    for t_name, t_config in data.items():
                        if t_name == tenant:
                            for key, value in request.POST.items():
                                if key == "operation":
                                    continue
                                remembermeData.update({key: value})
                            t_config.update({"remembermeConfig": remembermeData})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
                    json_file.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveLdapConfig":
            ldapData = {}
            dataFull = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
                with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
                    dataFull = json.load(json_file)
                    for l_name, l_config in dataFull.items():
                        if l_name == tenant:
                            ldapData = l_config
                    json_file.close()

            if request.POST["activate_ldap"]:
                if "ldap_server_uri" in request.POST and request.POST["ldap_server_uri"] != "":
                    ldapData["ldap_server_uri"] = request.POST["ldap_server_uri"]
                if "ldap_bind_dn" in request.POST and request.POST["ldap_bind_dn"] != "":
                    ldapData["ldap_bind_dn"] = request.POST["ldap_bind_dn"]
                if "ldap_bind_password" in request.POST and request.POST["ldap_bind_password"] != "":
                    ldapData["ldap_bind_password"] = request.POST["ldap_bind_password"]
                ldap_user_search_domain = []
                for key, value in request.POST.items():
                    if key.startswith("ldap_user_search_domain"):
                        ldap_user_search_domain.append(value)
                    else:
                        continue
                ldapData["ldap_user_search_domain"] = ldap_user_search_domain
                if (
                    "ldap_user_search_criteria" in request.POST
                    and request.POST["ldap_user_search_criteria"] != ""
                ):
                    ldapData["ldap_user_search_criteria"] = request.POST["ldap_user_search_criteria"]
                if (
                    "ldap_user_attribute_mapping" in request.POST
                    and request.POST["ldap_user_attribute_mapping"] != ""
                ):
                    ldapData["ldap_user_attribute_mapping"] = json.loads(
                        request.POST["ldap_user_attribute_mapping"].replace("'", '"')
                    )
                if (
                    "ldap_allow_user_creation" in request.POST
                    and request.POST["ldap_allow_user_creation"] != ""
                ):
                    ldapData["ldap_allow_user_creation"] = True
                else:
                    ldapData["ldap_allow_user_creation"] = False
                if (
                    "ldap_trigger_search_on_input" in request.POST
                    and request.POST["ldap_trigger_search_on_input"] != ""
                ):
                    ldapData["ldap_trigger_search_on_input"] = True
                else:
                    ldapData["ldap_trigger_search_on_input"] = False

            ldapData["activate_ldap"] = request.POST["activate_ldap"]
            ldapData["ldap_min_characters_for_search"] = request.POST["ldap_min_characters_for_search"]

            if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
                with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
                    dataFull = json.load(json_file)
                    json_file.close()

            dataFull[tenant] = ldapData

            with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json", "w") as outfile:
                json.dump(dataFull, outfile, indent=4)
                outfile.close()
            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "social_config":
            provider = request.POST["provider"].lower()
            name = request.POST["name"]
            clientId = request.POST["client_id"]
            secretId = request.POST["secret"]
            key = request.POST["key"]
            sites = Site.objects.get(pk=1)
            if SocialApp.objects.filter(provider=provider).exists():
                social_app = SocialApp.objects.get(provider=provider)
                social_app.client_id = clientId
                social_app.secret = secretId
                social_app.key = key
                social_app.save()
            else:
                obj = SocialApp.objects.create(
                    provider=provider, name=name, client_id=clientId, secret=secretId, key=key
                )
                social_app = SocialApp.objects.get(provider=provider)
                social_app.sites.add(sites)

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveOTPTypes":
            data = {
                "mfa_otp": {
                    "auth_type": request.POST["auth_type"],
                    "email_type": request.POST["email_type"],
                    "sms_type": request.POST["sms_type"],
                }
            }
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tdata = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tdata = json.load(json_file)
                    for t_name, t_config in tdata.items():
                        if t_name == tenant:
                            if "mfa_configs" in t_config:
                                t_config["mfa_configs"].update(data)
                            else:
                                t_config.update({"mfa_configs": data})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tdata, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "saveMFAConfigs":

            data = {
                "mfa_password": request.POST["mfa_password"],
            }

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tdata = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tdata = json.load(json_file)
                    for t_name, t_config in tdata.items():
                        if t_name == tenant:
                            if "mfa_configs" in t_config:
                                t_config["mfa_configs"].update(data)
                            else:
                                t_config.update({"mfa_configs": data})
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tdata, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "bootWorkers":
            boot_redis_worker()
            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "killWorkers":
            kill_redis_worker()
            return JsonResponse({"response": "success"})
        if request.POST["operation"] == "submitTenantConfig":
            post_tenant_config(request)
            return JsonResponse({"response": "success"})
        if request.POST["operation"] == "fetchTenantConfig":
            data_config = fetch_tenant_config(request)
            return JsonResponse(data_config)

        if request.POST["operation"] == "updateApplication":
            context = {}
            connected_database = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    connected_database = json.load(json_file)
                    connected_database = {
                        k: v for k, v in connected_database.items() if v.get("tenant") == tenant
                    }
                    json_file.close()
            system_model_json = {}
            if os.path.exists(f"{PLATFORM_DATA_PATH}app_config_tables.json"):
                with open(f"{PLATFORM_DATA_PATH}app_config_tables.json") as json_file:
                    system_model_json = json.load(json_file)
                    json_file.close()
            for db_connection_name, config in connected_database.items():
                try:
                    user_db_engine, db_type = db_engine_extractor(db_connection_name)
                    app_config_tables = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Tables",
                                "Columns": ["tablename", "fields"],
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
                    app_config_tables["version"] = ""
                    dynamic_model_create.migration_handler(
                        app_config_tables, system_model_json, request, db_connection_name
                    )
                    update_application.update_user_tables(
                        request, db_connection_name, user_db_engine, db_type
                    )
                    context["response"] = "Application database updated successfully."
                    context["icon"] = "success"
                except Exception as e:
                    logging.warning(f"Following exception occured while connecting to the database - {e}")
                    context["response"] = f"Error connecting to database - {db_connection_name}"
                    context["icon"] = "error"

            return JsonResponse(context)

        if request.POST["operation"] == "refreshTenantDBConnections":
            failed_list = []
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    db_data = json.load(json_file)
                    for db_cname, db_config in db_data.items():
                        if db_config.get("tenant") == tenant:
                            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                                db_config["server"],
                                db_config["port"],
                                db_config["db_name"],
                                db_config["username"],
                                db_config["password"],
                                db_config["connection_code"],
                            )
                            db_config["HOST"] = db_server
                            db_config["PORT"] = port
                            db_config["NAME"] = db_name
                            db_config["USER"] = username
                            db_config["PASSWORD"] = password
                            del db_config["server"]
                            del db_config["port"]
                            del db_config["db_name"]
                            del db_config["username"]
                            del db_config["password"]
                            if db_config["db_type"] == "MSSQL":
                                del db_config["db_type"]
                                try:
                                    quoted_temp = urllib.parse.quote_plus(
                                        "driver={ODBC Driver 18 for SQL Server};server="
                                        + db_config["HOST"]
                                        + ","
                                        + db_config["PORT"]
                                        + ";database="
                                        + db_config["NAME"]
                                        + ";Uid="
                                        + db_config["USER"]
                                        + ";Pwd="
                                        + db_config["PASSWORD"]
                                        + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                                    )
                                    engine_temp = create_engine(
                                        f"mssql+pyodbc:///?odbc_connect={quoted_temp}"
                                    )
                                    turbodbc_con = connect(
                                        driver="ODBC Driver 18 for SQL Server",
                                        server=db_config["HOST"] + "," + db_config["PORT"],
                                        database=db_config["NAME"],
                                        uid=db_config["USER"],
                                        pwd=db_config["PASSWORD"]
                                        + ";Encrypt=yes;TrustServerCertificate=yes;",
                                        turbodbc_options=make_options(
                                            prefer_unicode=True,
                                            use_async_io=True,
                                            varchar_max_character_limit=100000000,
                                            autocommit=True,
                                        ),
                                    )
                                    database_engine_dict[db_cname] = [engine_temp, turbodbc_con], "MSSQL"
                                except Exception as e:
                                    logging.warning(
                                        f"Following exception occured while connecting to the database - {e}"
                                    )
                                    failed_list.append(db_cname)
                                    continue
                            elif db_config["db_type"] == "PostgreSQL":
                                del db_config["db_type"]
                                try:
                                    engine_temp = create_engine(
                                        f"postgresql+psycopg2://{db_config['USER']}:{db_config['PASSWORD']}@{db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
                                    )
                                    database_engine_dict[db_cname] = [engine_temp, {}], "PostgreSQL"
                                except Exception as e:
                                    logging.warning(
                                        f"Following exception occured while connecting to the database - {e}"
                                    )
                                    failed_list.append(db_cname)
                                    continue
                    json_file.close()
            return JsonResponse({"response": "success", "failed_list": failed_list})

        if request.POST["operation"] == "submitSessionConfig":
            session_count = request.POST["session_count"]

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    for t_name, t_config in tenant_data.items():
                        if t_name == tenant:
                            t_config["session_count"] = int(session_count)
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tenant_data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "save_smtp_details":
            smtp_host = request.POST["smtp_host"]
            smtp_host_user = request.POST["smtp_host_user"]
            smtp_host_password = request.POST["smtp_host_password"]
            smtp_port = request.POST["smtp_port"]
            smtp_requires_auth = request.POST.get("smtp_requires_auth", "yes")
            smtp_allow_reset = request.POST["smtp_allow_reset"]
            smtp_default_message = request.POST["smtp_default_message"]
            smtp_msg_content = request.POST["smtp_msg_content"]

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()
                tenant_data[tenant]["smtp_host"] = smtp_host
                tenant_data[tenant]["smtp_host_user"] = smtp_host_user
                tenant_data[tenant]["smtp_host_password"] = smtp_host_password
                tenant_data[tenant]["smtp_port"] = smtp_port
                tenant_data[tenant]["smtp_requires_auth"] = smtp_requires_auth
                tenant_data[tenant]["smtp_allow_reset"] = smtp_allow_reset
                tenant_data[tenant]["smtp_default_message"] = smtp_default_message
                tenant_data[tenant]["smtp_msg_content"] = smtp_msg_content

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tenant_data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "save_approval_config":
            mail_provider = request.POST["mail_provider"]
            smtp_port = request.POST["smtp_port"]
            approval_password = request.POST["approval_password"]
            approval_email = request.POST["approval_email"]
            approval_msg_content = request.POST["approval_msg_content"]
            approval_smtp_requires_auth = request.POST.get("approval_smtp_requires_auth", "yes")

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()
                tenant_data[tenant]["mail_provider"] = mail_provider
                tenant_data[tenant]["approval_smtp_port"] = smtp_port
                tenant_data[tenant]["approval_password"] = approval_password
                tenant_data[tenant]["approval_email"] = approval_email
                tenant_data[tenant]["approval_msg_content"] = approval_msg_content
                tenant_data[tenant]["approval_smtp_requires_auth"] = approval_smtp_requires_auth

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tenant_data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "saveTenantDBConnectionCheckInterval":
            interval = request.POST["interval"]
            if interval:
                interval = int(interval)
            else:
                interval = 1
            failed_list = []
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    if tenant_data.get(tenant):
                        tenant_data[tenant]["db_connection_check_interval"] = interval
                    else:
                        tenant_data[tenant] = {
                            "password_validity": 180,
                            "min_length_of_password": 4,
                            "max_length_of_password": 32,
                            "alphanumeric": "false",
                            "capitalLetter": "false",
                            "lowercaseLetter": "false",
                            "symbols": "false",
                            "regex_pattern": "(^.{4,32}$)",
                            "password_history_length": 3,
                            "db_connection_check_interval": interval,
                        }
                    json_file.close()
            else:
                tenant_data = {}
                tenant_data[tenant] = {
                    "password_validity": 180,
                    "min_length_of_password": 4,
                    "max_length_of_password": 32,
                    "alphanumeric": "false",
                    "capitalLetter": "false",
                    "lowercaseLetter": "false",
                    "symbols": "false",
                    "regex_pattern": "(^.{4,32}$)",
                    "password_history_length": 3,
                    "db_connection_check_interval": interval,
                }
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w+") as outfile:
                json.dump(tenant_data, outfile, indent=4)
                outfile.close()
            func = "schedulercheck.db_con_checker"
            job_id = f"DB health check - {tenant}"
            schedulerfunc.add_db_health_scheduler(func, job_id, tenant, minutes=interval)
            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "check_username_validation":
            username = request.POST["username"]
            username = username.lower()
            User = get_user_model()
            if tenant != "public":
                username += f".{tenant}"
            try:
                user = User.objects.get(username=username)
                if user:
                    return JsonResponse({"response": "error"})
            except User.DoesNotExist:
                return JsonResponse({"response": "success"})

        if request.POST["operation"] == "check_password_validation":
            password = request.POST["password"]
            regex_pattern = ""
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
                    return JsonResponse({"response": "error"})
                else:
                    return JsonResponse({"response": "error"})

        if request.POST["operation"] == "check_email_validation":
            email = request.POST["email"]
            email_pattern = r"[^@]+@[^@]+\.[^@]+"

            if re.fullmatch(email_pattern, email):
                return JsonResponse({"response": "success"})
            else:
                return JsonResponse({"response": "error"})

        if request.POST["operation"] == "user_controls_licensing":
            control_data = request.POST.dict()
            del control_data["operation"]
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    data = json.load(json_file)
                    json_file.close()
                    if tenant in data:
                        data[tenant].update({key: value for key, value in control_data.items()})

                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(data, json_file, indent=4)
                        json_file.close()

            return JsonResponse({"response": "Successfully Saved", "icon": "success"})

        if request.POST["operation"] == "create_new_user":

            User = get_user_model()

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)

                    if tenant_data[tenant].get("set_user_limit") == "True" and tenant_data[tenant].get(
                        "user_limit_count"
                    ):
                        limit = int(tenant_data[tenant].get("user_limit_count"))

                        user_count = User.objects.filter(is_developer=False).count()
                        if user_count >= limit:
                            return JsonResponse(
                                {
                                    "response": "Maximum number of users allowed has been reached. Please contact the administrator.",
                                    "icon": "warning",
                                }
                            )
                    else:
                        pass
            username = request.POST["username"]
            username = username.lower()
            if tenant != "public":
                username += f".{tenant}"
            else:
                pass
            password = request.POST["password"]
            email = request.POST["email"]
            email_pattern = r"[^@]+@[^@]+\.[^@]+"
            regex_pattern = ""
            tenant_data = {}
            common_passwords = []

            try:
                user = User.objects.get(username=username)
                if user:
                    return JsonResponse(
                        {
                            "response": "User already exists! Please select another username.",
                            "icon": "warning",
                        }
                    )
            except User.DoesNotExist:
                pass

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

            if re.fullmatch(email_pattern, email):
                if check_password_complexity(regex_pattern, password, common_passwords):
                    instance = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "Instance",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "name",
                                    "condition": "Equal to",
                                    "input_value": tenant,
                                    "and_or": "",
                                }
                            ],
                        },
                        schema=tenant,
                    )
                    instance_id = str(instance.id.iloc[0])
                    User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=True,
                        is_active=True,
                        is_superuser=False,
                        mfa_hash=pyotp.random_base32(),
                        role="User",
                        instance_id=instance_id,
                    )
                else:
                    if password in common_passwords:
                        return JsonResponse(
                            {
                                "response": "Password entered is too common! Please select another password.",
                                "icon": "warning",
                            }
                        )
                    else:
                        return JsonResponse(
                            {
                                "response": "Password entered doesn't meet the password policy! Please select another password.",
                                "icon": "warning",
                            }
                        )
            else:
                return JsonResponse(
                    {
                        "response": "Invalid Email address format entered! Please enter a valid email.",
                        "icon": "warning",
                    }
                )
            return JsonResponse({"response": "User has been successfully created!", "icon": "success"})

        if request.POST["operation"] == "user_management_approvals":
            approvals_enabled = request.POST["enabled"]
            app_level = request.POST["app_level"]
            tenant_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()
            if app_level != "true":
                tenant_data[tenant]["tenant_user_management_approvals"] = approvals_enabled
            else:
                approvals_enabled = json.loads(approvals_enabled)
                app_selected = approvals_enabled["applicationSelected"]
                if not tenant_data[tenant].get("app_level_user_management_approvals"):
                    tenant_data[tenant]["app_level_user_management_approvals"] = {app_selected: {}}
                else:
                    pass
                app_level_settings = tenant_data[tenant]["app_level_user_management_approvals"].get(
                    app_selected
                )
                if not app_level_settings:
                    app_level_settings = {}
                else:
                    pass
                app_level_settings["newUserApproval"] = approvals_enabled["newUserApproval"]
                app_level_settings["userGroupApproval"] = approvals_enabled["userGroupApproval"]
                app_level_settings["groupPermissionApproval"] = approvals_enabled["groupPermissionApproval"]
                tenant_data[tenant]["app_level_user_management_approvals"][app_selected] = app_level_settings
            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as old_file:
                json.dump(tenant_data, old_file, indent=4)
                old_file.close()
            return JsonResponse({"response": "Success", "icon": "success"})

        if request.POST["operation"] == "createNewDB":
            connection_code = request.POST["password"][len(request.POST["password"]) - 16 :]
            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                request.POST["dbServer"],
                request.POST["port"],
                request.POST["db_name"],
                request.POST["username"],
                request.POST["password"][: len(request.POST["password"]) - 16],
                connection_code,
            )
            db_type = request.POST["db_type"]
            encrypted_db_name = request.POST["db_name"]
            db_connection_name = request.POST["db_connection_name"]
            encrypted_db_server = request.POST["dbServer"]
            encrypted_username = request.POST["username"]
            encrypted_password = request.POST["password"][: len(request.POST["password"]) - 16]
            encrypted_port = request.POST["port"]
            schema = request.POST["db_schema"]
            service_name = request.POST["db_service_name"]
            db_data_file_location = request.POST["db_data_file_location"]
            db_log_file_location = request.POST["db_log_file_location"]
            data = {}
            data["db_name"] = db_name
            data["db_connection_name"] = db_connection_name
            db_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    db_data = json.load(json_file)
                    json_file.close()
            if db_connection_name not in db_data.keys() and db_connection_name.lower() != "default":
                try:
                    if db_type == "MSSQL":
                        db_quoted_string = urllib.parse.quote_plus(
                            "driver={ODBC Driver 18 for SQL Server};server="
                            + db_server
                            + ","
                            + port
                            + ";database=master"
                            + ";Uid="
                            + username
                            + ";Pwd="
                            + password
                            + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                        )
                        engine_temp = create_engine(
                            f"mssql+pyodbc:///?odbc_connect={db_quoted_string}",
                            connect_args={"autocommit": True},
                        )
                    elif db_type == "PostgreSQL":
                        engine_temp = psycopg2.connect(
                            dbname=db_name,
                            user=username,
                            password=password,
                            host=db_server,
                            port=port,
                        )
                        engine_temp.autocommit = True
                    elif db_type == "Oracle":
                        engine_temp = create_engine(
                            "oracle+oracledb://:@",
                            thick_mode=False,
                            connect_args={
                                "user": username,
                                "password": password,
                                "host": db_server,
                                "port": port,
                                "service_name": service_name,
                            },
                        )
                    else:
                        raise Exception
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    data["response"] = "Error"
                    data["error"] = str(e)
                else:
                    if db_type == "MSSQL":
                        existing_databases = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "master.dbo.sysdatabases",
                                    "Columns": ["name"],
                                },
                                "condition": [],
                            },
                            engine2=[engine_temp, None],
                            db_type=db_type,
                            engine_override=True,
                        )
                        existing_databases = existing_databases.name.str.lower().tolist()
                    elif db_type == "PostgreSQL":
                        query = "SELECT schema_name FROM information_schema.schemata;"
                        cursor = engine_temp.cursor()
                        cursor.execute(query)
                        records = cursor.fetchall()
                        existing_databases = records[0]
                    elif db_type == "Oracle":
                        query = "SELECT name FROM v$database;"
                        existing_databases = non_standard_read_data_func(
                            query, [engine_temp, None], db_type=db_type
                        )
                        existing_databases = existing_databases.name.str.lower().tolist()
                    else:
                        existing_databases = []
                    if db_name.lower() not in existing_databases or (
                        db_type == "PostgreSQL" and schema not in existing_databases
                    ):
                        try:
                            if db_type == "MSSQL":
                                sql_query = f"CREATE DATABASE {db_name} ON ( NAME = {db_name}_dat, FILENAME = '{db_data_file_location}', SIZE = 1024MB, FILEGROWTH = 256MB ) LOG ON ( NAME = {db_name}_log, FILENAME = '{db_log_file_location}', SIZE = 512MB, FILEGROWTH = 125MB );"
                                with engine_temp.begin() as conn:
                                    conn.execute(text(sql_query))
                            elif db_type == "PostgreSQL":
                                cursor = engine_temp.cursor()
                                if schema not in existing_databases:
                                    schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema};"
                                cursor.execute(schema_query)
                                cursor.close()
                                engine_temp.close()
                            else:
                                pass
                        except Exception as e:
                            data["response"] = "Error"
                            data["error"] = str(e)
                        else:
                            if db_type == "MSSQL":
                                db_q_string = urllib.parse.quote_plus(
                                    "driver={ODBC Driver 18 for SQL Server};server="
                                    + db_server
                                    + ","
                                    + port
                                    + ";database="
                                    + db_name
                                    + ";Uid="
                                    + username
                                    + ";Pwd="
                                    + password
                                    + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                                )
                                db_engine_temp = create_engine(
                                    f"mssql+pyodbc:///?odbc_connect={db_q_string}",
                                    connect_args={"autocommit": True},
                                )
                                turb_con = connect(
                                    driver="ODBC Driver 18 for SQL Server",
                                    server=db_server + "," + port,
                                    database=db_name,
                                    uid=username,
                                    pwd=password + ";Encrypt=yes;TrustServerCertificate=yes;",
                                    turbodbc_options=make_options(
                                        prefer_unicode=True,
                                        use_async_io=True,
                                        varchar_max_character_limit=100000000,
                                        autocommit=True,
                                    ),
                                )
                            elif db_type == "PostgreSQL":
                                db_engine_temp = {
                                    "dbname": db_name,
                                    "user": username,
                                    "password": password,
                                    "host": db_server,
                                    "port": port,
                                    "schema": schema,
                                }
                                turb_con = None
                            elif db_type == "Oracle":
                                db_engine_temp = create_engine(
                                    "oracle+oracledb://:@",
                                    thick_mode=False,
                                    connect_args={
                                        "user": username,
                                        "password": password,
                                        "host": db_server,
                                        "port": port,
                                        "service_name": service_name,
                                    },
                                )
                                turb_con = None
                            else:
                                pass
                            database_engine_dict[db_connection_name] = [db_engine_temp, turb_con], db_type
                            db_info = {
                                "server": encrypted_db_server,
                                "db_name": encrypted_db_name,
                                "username": encrypted_username,
                                "password": encrypted_password,
                                "port": encrypted_port,
                                "db_type": db_type,
                                "tenant": tenant,
                                "schema": schema,
                                "service_name": service_name,
                                "connection_code": connection_code,
                            }
                            db_data[f"{db_connection_name}"] = db_info
                            with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
                                json.dump(db_data, outfile, indent=4)
                                outfile.close()
                            updated_database_list = []
                            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases_updation.json"):
                                with open(f"{PLATFORM_FILE_PATH}user_databases_updation.json") as json_file:
                                    updated_database_list = json.load(json_file)
                                    json_file.close()
                            updated_database_list.append(db_connection_name)
                            with open(f"{PLATFORM_FILE_PATH}user_databases_updation.json", "w") as outfile:
                                json.dump(updated_database_list, outfile, indent=4)
                                outfile.close()
                            data["response"] = "Database successfuly created."
                    else:
                        data["response"] = (
                            "Database already exists! Please use a different name to create the database."
                        )
            else:
                data["response"] = (
                    "Database connection name already exists! Please use a different name to define the database connection."
                )
            return JsonResponse(data)

        if request.POST["operation"] == "newDBSysTableMigration":
            db_connection_name = request.POST["db_connection_name"]
            data = {}
            try:
                dynamic_model_create.fresh_migration(request, db_connection_name)
            except Exception as e:
                logging.warning(f"Following exception occured - {e}")
                data["response"] = "Error"
                data["error"] = str(e)
            else:
                data["response"] = "System tables successfuly created."
            return JsonResponse(data)

        if request.POST["operation"] == "addNewDBConnection":
            connection_code = request.POST["password"][len(request.POST["password"]) - 16 :]
            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                request.POST["dbServer"],
                request.POST["port"],
                request.POST["db_name"],
                request.POST["username"],
                request.POST["password"][: len(request.POST["password"]) - 16],
                connection_code,
            )
            encrypted_db_name = request.POST["db_name"]
            db_connection_name = request.POST["db_connection_name"]
            encrypted_db_server = request.POST["dbServer"]
            encrypted_username = request.POST["username"]
            encrypted_password = request.POST["password"][: len(request.POST["password"]) - 16]
            encrypted_port = request.POST["port"]
            db_type = request.POST["db_type"]
            db_schema = request.POST["db_schema"]
            db_service_name = request.POST["db_service_name"]
            db_connection_mode = request.POST["db_connection_mode"]

            data = {}
            data["db_name"] = db_name
            data["db_connection_name"] = db_connection_name

            db_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    db_data = json.load(json_file)
                    json_file.close()

            if db_type == "":
                db_type = "MSSQL"
            else:
                pass
            if db_type == "PostgreSQL" and db_schema == "":
                db_schema = "public"
            else:
                pass

            if db_connection_name not in db_data.keys() and db_connection_name.lower() != "default":
                try:
                    if db_type == "MSSQL":
                        db_quoted_string = urllib.parse.quote_plus(
                            "driver={ODBC Driver 18 for SQL Server};server="
                            + db_server
                            + ","
                            + port
                            + ";database="
                            + db_name
                            + ";Uid="
                            + username
                            + ";Pwd="
                            + password
                            + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                        )
                        engine_temp = create_engine(
                            f"mssql+pyodbc:///?odbc_connect={db_quoted_string}",
                            connect_args={"autocommit": True},
                        )
                        turb_con = connect(
                            driver="ODBC Driver 18 for SQL Server",
                            server=db_server + "," + port,
                            database=db_name,
                            uid=username,
                            pwd=password + ";Encrypt=yes;TrustServerCertificate=yes;",
                            turbodbc_options=make_options(
                                prefer_unicode=True,
                                use_async_io=True,
                                varchar_max_character_limit=100000000,
                                autocommit=True,
                            ),
                        )
                        dummy_row = execute_read_query("SELECT 1", [engine_temp, turb_con], db_type)
                        if not len(dummy_row):
                            raise Exception
                        else:
                            pass
                    elif db_type == "PostgreSQL":
                        sql_engine = psycopg2.connect(
                            dbname=db_name,
                            user=username,
                            password=password,
                            host=db_server,
                            port=port,
                        )
                        engine_temp = {
                            "dbname": db_name,
                            "user": username,
                            "password": password,
                            "host": db_server,
                            "port": port,
                            "schema": db_schema,
                        }
                        cursor = sql_engine.cursor()
                        cursor.execute("SELECT 1;")
                        records = cursor.fetchall()
                        if not records[0]:
                            raise Exception
                        else:
                            pass
                    elif db_type == "Oracle":
                        if db_connection_mode == "thick":
                            oracledb.init_oracle_client()
                            thick_mode = True
                        else:
                            thick_mode = False
                        engine_temp = create_engine(
                            f"oracle+oracledb://:@",
                            thick_mode=thick_mode,
                            connect_args={
                                "user": username,
                                "password": password,
                                "host": db_server,
                                "port": port,
                                "service_name": db_service_name,
                            },
                            pool_pre_ping=True,
                            pool_size=70,
                            max_overflow=10,
                            pool_recycle=3600,
                        )
                        turb_con = None
                        dummy_row = execute_read_query(
                            "SELECT table_name from all_tables", [engine_temp, turb_con], db_type
                        )
                        if not len(dummy_row):
                            raise Exception
                        else:
                            pass
                    else:
                        raise Exception("Unrecognised Database type!")
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    data["response"] = "Error"
                    data["error"] = str(e)
                else:
                    if db_type == "MSSQL":
                        database_engine_dict[db_connection_name] = [engine_temp, turb_con], db_type
                        existing_app_list = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "information_schema.tables",
                                    "Columns": ["TABLE_NAME"],
                                },
                                "condition": [],
                            },
                            engine2=[engine_temp, turb_con],
                            db_type=db_type,
                            engine_override=True,
                        )["TABLE_NAME"].tolist()
                    elif db_type == "Oracle":
                        database_engine_dict[db_connection_name] = [engine_temp, turb_con], db_type
                        existing_app_list = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "all_tables",
                                        "Columns": ["table_name"],
                                    },
                                    "condition": [],
                                },
                                engine2=[engine_temp, turb_con],
                                db_type=db_type,
                                engine_override=True,
                            )["table_name"]
                            .str.lower()
                            .tolist()
                        )
                    else:
                        database_engine_dict[db_connection_name] = [engine_temp, None], db_type
                        existing_app_list = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "information_schema.tables",
                                    "Columns": ["table_name"],
                                },
                                "condition": [
                                    {
                                        "column_name": "table_schema",
                                        "condition": "Equal to",
                                        "input_value": db_schema,
                                        "and_or": "",
                                    }
                                ],
                            },
                            engine2=[engine_temp, None],
                            db_type=db_type,
                            engine_override=True,
                            schema=db_schema,
                        )["table_name"].tolist()
                    if "users_application" not in existing_app_list:
                        try:
                            dynamic_model_create.fresh_migration(request, db_connection_name)
                        except Exception as e:
                            logging.warning(
                                f"Following exception occured while running initial migration - {e}"
                            )
                            data["response"] = "Error"
                            data["error"] = str(e)
                        else:
                            db_info = {
                                "server": encrypted_db_server,
                                "db_name": encrypted_db_name,
                                "username": encrypted_username,
                                "password": encrypted_password,
                                "port": encrypted_port,
                                "db_type": db_type,
                                "schema": db_schema,
                                "tenant": tenant,
                                "service_name": db_service_name,
                                "db_connection_mode": db_connection_mode,
                                "connection_code": connection_code,
                            }

                            db_data[f"{db_connection_name}"] = db_info
                            with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
                                json.dump(db_data, outfile, indent=4)
                                outfile.close()
                            data["response"] = "Database successfuly added."
                    else:
                        db_info = {
                            "server": encrypted_db_server,
                            "db_name": encrypted_db_name,
                            "username": encrypted_username,
                            "password": encrypted_password,
                            "port": encrypted_port,
                            "db_type": db_type,
                            "schema": db_schema,
                            "tenant": tenant,
                            "service_name": db_service_name,
                            "db_connection_mode": db_connection_mode,
                            "connection_code": connection_code,
                        }
                        db_data[f"{db_connection_name}"] = db_info
                        with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
                            json.dump(db_data, outfile, indent=4)
                            outfile.close()
                        data["response"] = "Database successfuly added."
            else:
                data["response"] = "Error"
                data["error"] = (
                    "Database connection name already exists! Please use a different name to define the database connection."
                )
            return JsonResponse(data)

        if request.POST["operation"] == "loadExistingApps":
            db_connection_name = request.POST["db_connection_name"]
            context = {}
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            existing_app_list = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Application",
                        "Columns": ["application_code"],
                    },
                    "condition": [],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            ).application_code.tolist()
            # Update allotted application
            instance = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Instance",
                        "Columns": ["id"],
                    },
                    "condition": [
                        {
                            "column_name": "name",
                            "condition": "Equal to",
                            "input_value": tenant,
                            "and_or": "",
                        }
                    ],
                },
                schema=tenant,
            )
            instance_id = str(instance.id.iloc[0])

            allotted_apps = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "configuration_parameter",
                        "Columns": ["value"],
                    },
                    "condition": [
                        {
                            "column_name": "parameter",
                            "condition": "Equal to",
                            "input_value": "Allotted Applications",
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
                schema=tenant,
            )
            if not allotted_apps.empty:
                allotted_apps = allotted_apps.value
            if allotted_apps.iloc[0]:
                allotted_apps = json.loads(allotted_apps.iloc[0])
            else:
                allotted_apps = []
            allotted_apps += existing_app_list
            allotted_apps = list(set(allotted_apps))
            allotted_apps = json.dumps(allotted_apps)
            update_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "configuration_parameter",
                        "Columns": [
                            {
                                "column_name": "value",
                                "input_value": allotted_apps,
                                "separator": "",
                            }
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "parameter",
                            "condition": "Equal to",
                            "input_value": "Allotted Applications",
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
                schema=tenant,
            )
            app_db_mapping = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    app_db_mapping = json.load(json_file)
                    json_file.close()
            for i in existing_app_list:
                i = tenant + "_" + i
                app_db_mapping[i] = db_connection_name
            with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json", "w") as outfile:
                json.dump(app_db_mapping, outfile, indent=4)
                outfile.close()
            context["status"] = "success"
            return JsonResponse(context)

        if request.POST["operation"] == "edit_updated_db":
            connection_code = request.POST["password"][len(request.POST["password"]) - 16 :]
            db_server, port, db_name, username, password = decrypt_existing_db_credentials(
                request.POST["server"],
                request.POST["port"],
                request.POST["db_name"],
                request.POST["username"],
                request.POST["password"][: len(request.POST["password"]) - 16],
                connection_code,
            )
            service_name = request.POST["db_service_name"]

            db_connection_name = request.POST["db_connection_name"]
            edited_data = json.loads(json.dumps(request.POST))
            edited_data["password"] = edited_data["password"][: len(edited_data["password"]) - 16]
            edited_data["connection_code"] = connection_code
            db_type = request.POST["db_type"]

            del edited_data["db_connection_name"]
            del edited_data["operation"]

            if db_server and username and password and port and db_name:

                if db_type == "MSSQL":

                    db_quoted_string = urllib.parse.quote_plus(
                        "driver={ODBC Driver 18 for SQL Server};server="
                        + db_server
                        + ","
                        + port
                        + ";database="
                        + db_name
                        + ";Uid="
                        + username
                        + ";Pwd="
                        + password
                        + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                    )
                    engine_temp = create_engine(
                        f"mssql+pyodbc:///?odbc_connect={db_quoted_string}",
                        connect_args={"autocommit": True},
                    )
                    turb_con = connect(
                        driver="ODBC Driver 18 for SQL Server",
                        server=db_server + "," + port,
                        database=db_name,
                        uid=username,
                        pwd=password + ";Encrypt=yes;TrustServerCertificate=yes;",
                        turbodbc_options=make_options(
                            prefer_unicode=True,
                            use_async_io=True,
                            varchar_max_character_limit=100000000,
                            autocommit=True,
                        ),
                    )

                    database_engine_dict[db_connection_name] = [engine_temp, turb_con], db_type
                elif db_type == "Oracle":
                    engine_temp = create_engine(
                        "oracle+oracledb://:@",
                        thick_mode=False,
                        connect_args={
                            "user": username,
                            "password": password,
                            "host": db_server,
                            "port": port,
                            "service_name": service_name,
                        },
                    )
                    database_engine_dict[db_connection_name] = [engine_temp, None], db_type
                else:
                    db_schema = request.POST["schema"]
                    if db_schema == "":
                        db_schema = "public"

                    engine_temp = {
                        "dbname": db_name,
                        "user": username,
                        "password": password,
                        "host": db_server,
                        "port": port,
                        "schema": db_schema,
                    }

                    database_engine_dict[db_connection_name] = [engine_temp, None], db_type
                db_data = {}
                if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                    with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                        db_data = json.load(json_file)
                        json_file.close()

                for key, value in edited_data.items():
                    db_data[db_connection_name][key] = value

                with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
                    json.dump(db_data, outfile, indent=4)
                    outfile.close()

                return JsonResponse({"response": "Database configs updated successfully", "icon": "success"})

            return JsonResponse({"response": "Please fill all the fields", "icon": "warning"})

        if request.POST["operation"] == "delete_db":
            db_connection_name = request.POST["db_connection_name"]

            db_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    db_data = json.load(json_file)
                    json_file.close()

            if db_connection_name in db_data:
                del db_data[db_connection_name]

            with open(f"{PLATFORM_FILE_PATH}user_databases.json", "w") as outfile:
                json.dump(db_data, outfile, indent=4)
                outfile.close()

            if db_connection_name in database_engine_dict:
                del database_engine_dict[db_connection_name]

            return JsonResponse({"response": "Database configs deleted successfully"})

        if request.POST["operation"] == "loadConnectedDb":
            connected_database = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}user_databases.json"):
                with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
                    db_data = json.load(json_file)
                    connected_database = {k: v for k, v in db_data.items() if v.get("tenant") == tenant}
                    for k, v in connected_database.items():
                        logging.warning(connected_database[k]["password"])
                        connected_database[k]["password"] = (
                            connected_database[k]["password"] + connected_database[k]["connection_code"]
                        )
                        del connected_database[k]["connection_code"]
                        logging.warning(connected_database[k])

                    json_file.close()

            context = {"response": connected_database}

            return JsonResponse(context)

        if request.POST["operation"] == "save_tenant_smtp_config":

            allow_users_to_config_smtp = request.POST["allow_users_to_config_smtp"]
            smtp_server_count = int(request.POST["smtp_server_count"])

            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                tenant_data = {}
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    tenant_data[tenant]["smtp_server_count"] = smtp_server_count
                    tenant_data[tenant]["allow_users_to_config_smtp"] = allow_users_to_config_smtp
                    json_file.close()

                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                    json.dump(tenant_data, json_file, indent=4)
                    json_file.close()

            return JsonResponse({"response": "Data saved successfully."})

    context_data = {}

    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == tenant:
                    if "primary_bgcolor" not in t_config:
                        t_config.update({"primary_bgcolor": "#d4af37"})

                    if "secondary_color" not in t_config:
                        t_config.update({"secondary_color": "#a5780a"})

                    if "font_color" not in t_config:
                        t_config.update({"font_color": "#000000"})

                    if "font_hover_color" not in t_config:
                        t_config.update({"font_hover_color": "#ffffff"})

                    if "font_family" not in t_config:
                        t_config.update({"font_family": "Arial"})

                    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                        json.dump(tenant_data, json_file, indent=4)
                        json_file.close()

    context_data = {}
    getContextData(context_data, tenant)

    context_data.update(getAppList(request, context_data, tenant))

    social_queryset = SocialApp.objects.all()
    social_configs = {}
    for i in social_queryset.values():
        if i["provider"] == "google":
            social_configs["Google"] = i
        elif i["provider"] == "facebook":
            social_configs["Facebook"] = i
        elif i["provider"] == "microsoft":
            social_configs["Microsoft"] = i
        elif i["provider"] == "twitter":
            social_configs["Twitter"] = i
        elif i["provider"] == "amazon":
            social_configs["Amazon"] = i
        elif i["provider"] == "apple":
            social_configs["Apple"] = i
        else:
            pass

    context_data["social_configs"] = social_configs

    if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
        with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
            ldap_data = json.load(json_file)
            for l_name, l_config in ldap_data.items():
                if l_name == tenant:
                    if l_config.get("ldap_server_uri"):
                        context_data["ldap_server_uri"] = l_config["ldap_server_uri"]
                    if l_config.get("ldap_bind_dn"):
                        context_data["ldap_bind_dn"] = l_config["ldap_bind_dn"]
                    if l_config.get("ldap_bind_password"):
                        context_data["ldap_bind_password"] = l_config["ldap_bind_password"]
                    if l_config.get("ldap_user_search_domain"):
                        context_data["ldap_user_search_domain"] = l_config["ldap_user_search_domain"]
                    if l_config.get("ldap_user_search_criteria"):
                        context_data["ldap_user_search_criteria"] = l_config["ldap_user_search_criteria"]
                    if l_config.get("ldap_user_attribute_mapping"):
                        context_data["ldap_user_attribute_mapping"] = json.dumps(
                            l_config["ldap_user_attribute_mapping"]
                        )
                    if l_config.get("activate_ldap"):
                        context_data["activate_ldap"] = l_config["activate_ldap"]

    show_dashboard = "false"
    show_planner = "false"
    tenant_db = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_db = json.load(json_file)
            json_file.close()

    if tenant_db.get(tenant):
        if tenant_db[tenant].get("show_dashboard"):
            show_dashboard = tenant_db[tenant].get("show_dashboard")

        if tenant_db[tenant].get("show_planner"):
            show_planner = tenant_db[tenant].get("show_planner")

    app_db_mapping = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()

    system_apps = []

    dashboard_db_conn = ""
    dashboard_display = ""
    if show_dashboard == "true" and app_db_mapping.get(f"{tenant}_dashboard"):
        system_apps.append("dashboard")
        dashboard_db_conn = app_db_mapping[f"{tenant}_dashboard"]

        user_db_engine, db_type = db_engine_extractor(dashboard_db_conn)

        dashboard_config = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "system_application_master",
                    "Columns": ["display_config"],
                },
                "condition": [
                    {
                        "column_name": "app_name",
                        "condition": "Equal to",
                        "input_value": "dashboard",
                        "and_or": "",
                    }
                ],
            },
            engine2=user_db_engine,
            engine_override=True,
            db_type=db_type,
        ).display_config

        if dashboard_config.iloc[0]:
            dashboard_display = json.loads(dashboard_config.iloc[0])["display_position"]

    planner_display = ""
    planner_db_conn = ""
    if show_planner == "true" and app_db_mapping.get(f"{tenant}_planner"):
        system_apps.append("planner")
        planner_db_conn = app_db_mapping[f"{tenant}_planner"]

        db_type = ""
        user_db_engine, db_type = db_engine_extractor(planner_db_conn)

        planner_config = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "system_application_master",
                    "Columns": ["display_config"],
                },
                "condition": [
                    {
                        "column_name": "app_name",
                        "condition": "Equal to",
                        "input_value": "planner",
                        "and_or": "",
                    }
                ],
            },
            engine2=user_db_engine,
            engine_override=True,
            db_type=db_type,
        ).display_config

        if planner_config.iloc[0]:
            planner_display = json.loads(planner_config.iloc[0])["display_position"]

    context_data["show_dashboard"] = show_dashboard
    context_data["dashboard_display"] = dashboard_display
    context_data["show_planner"] = show_planner
    context_data["planner_display"] = planner_display
    context_data["planner_db_conn"] = planner_db_conn
    context_data["dashboard_db_conn"] = dashboard_db_conn
    context_data["system_apps"] = system_apps

    return render(request, "tenant_admin/index.html", context_data, using="light")


@never_cache
def login_preview(request):
    tenant = tenant_schema_from_request(request, original=True)
    template = f"user_defined_template/{tenant}/login/preview.html"
    data = {}

    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
        t_config = tenant_data[tenant]

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

            data.update({"root_css": root_css})

    return render(request, template, data)


def boot_redis_worker(no_of_worker=4):
    workers = Worker.all(redis_instance)
    up_workers = [i for i in workers if i.get_state() != "suspended"]
    return True


def kill_redis_worker():
    environ.Path(__file__) - 3
    return True


def post_tenant_config(request):
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == tenant_schema_from_request(request, original=True):
                    t_config["password_validity"] = int(request.POST["password_validity_days"])
                    t_config["inactive_users_after_days"] = int(request.POST["inactive_criteria"])
                    t_config["delete_users_after_days"] = int(request.POST["inactive_deletion_criteria"])
                    t_config["min_length_of_password"] = int(request.POST["min_length_of_password"])
                    t_config["max_length_of_password"] = int(request.POST["max_length_of_password"])
                    t_config["password_history_length"] = int(request.POST["password_history_length"])
                    t_config["alphanumeric"] = request.POST["alphanumeric"]
                    t_config["capitalLetter"] = request.POST["capitalLetter"]
                    t_config["lowercaseLetter"] = request.POST["lowercaseLetter"]
                    t_config["symbols"] = request.POST["symbols"]
                    t_config["restricted_characters"] = request.POST["restricted_characters"]
                    t_config["restrict_characters"] = request.POST["restrict_characters"]
                    t_config["allowed_characters"] = request.POST["allowed_characters"]
                    t_config["regex_pattern"] = regex_generator(
                        int(request.POST["min_length_of_password"]),
                        int(request.POST["max_length_of_password"]),
                        request.POST["alphanumeric"],
                        request.POST["capitalLetter"],
                        request.POST["lowercaseLetter"],
                        request.POST["symbols"],
                        request.POST["restricted_characters"],
                        request.POST["allowed_characters"],
                        request.POST["restrict_characters"],
                    )
                    t_config["incorrect_password"] = int(request.POST["incorrect_password"])
                    t_config["common_passwords"] = request.POST["common_passwords"]
                    t_config["user_inactivity_days"] = request.POST["user_inactivity_days"]
                    t_config["user_inactivity_hours"] = request.POST["user_inactivity_hours"]
                    t_config["user_inactivity_minutes"] = request.POST["user_inactivity_minutes"]
                    t_config["user_failedlogins_days"] = request.POST["user_failedlogins_days"]
                    t_config["user_failedlogins_hours"] = request.POST["user_failedlogins_hours"]
                    t_config["user_failedlogins_minutes"] = request.POST["user_failedlogins_minutes"]

            json_file.close()

        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
            json.dump(tenant_data, json_file, indent=4)
            json_file.close()

    return True


def fetch_tenant_config(request):
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        tenant_data, data_config = {}, {}
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            for t_name, t_config in tenant_data.items():
                if t_name == tenant_schema_from_request(request, original=True):
                    if t_config.get("password_validity"):
                        data_config["password_validity_days"] = t_config["password_validity"]
                    else:
                        data_config["password_validity_days"] = 180
                    if t_config.get("min_length_of_password"):
                        data_config["min_length_of_password"] = t_config["min_length_of_password"]
                    else:
                        data_config["min_length_of_password"] = 4
                    if t_config.get("max_length_of_password"):
                        data_config["max_length_of_password"] = t_config["max_length_of_password"]
                    else:
                        data_config["max_length_of_password"] = 32
                    if t_config.get("alphanumeric"):
                        data_config["alphanumeric"] = t_config["alphanumeric"]
                    else:
                        data_config["alphanumeric"] = "false"
                    if t_config.get("capitalLetter"):
                        data_config["capitalLetter"] = t_config["capitalLetter"]
                    else:
                        data_config["capitalLetter"] = "false"
                    if t_config.get("lowercaseLetter"):
                        data_config["lowercaseLetter"] = t_config["lowercaseLetter"]
                    else:
                        data_config["lowercaseLetter"] = "false"

                    if t_config.get("restricted_characters"):
                        data_config["restricted_characters"] = t_config["restricted_characters"]
                    if t_config.get("allowed_characters"):
                        data_config["allowed_characters"] = t_config["allowed_characters"]
                    if t_config.get("symbols"):
                        data_config["symbols"] = t_config["symbols"]
                    else:
                        data_config["symbols"] = "false"
                    if t_config.get("restrict_characters"):
                        data_config["restrict_characters"] = t_config["restrict_characters"]
                    else:
                        data_config["restrict_characters"] = "false"
                    if t_config.get("password_history_length"):
                        data_config["password_history_length"] = t_config["password_history_length"]
                    else:
                        data_config["password_history_length"] = 3
                    if t_config.get("delete_users_after_days"):
                        data_config["inactive_deletion_criteria"] = t_config["delete_users_after_days"]
                    else:
                        data_config["inactive_deletion_criteria"] = 180
                    if t_config.get("inactive_users_after_days"):
                        data_config["inactive_criteria"] = t_config["inactive_users_after_days"]
                    else:
                        data_config["inactive_criteria"] = 60
                    if t_config.get("session_count"):
                        data_config["session_count"] = t_config["session_count"]
                    else:
                        data_config["session_count"] = 2
                    if t_config.get("db_connection_check_interval"):
                        data_config["db_connection_check_interval"] = t_config["db_connection_check_interval"]
                    else:
                        data_config["db_connection_check_interval"] = 1
                    if t_config.get("incorrect_password"):
                        data_config["incorrect_password"] = t_config["incorrect_password"]
                    else:
                        data_config["incorrect_password"] = 3
                    if t_config.get("common_passwords"):
                        data_config["common_passwords"] = t_config["common_passwords"]
                    if t_config.get("app_template"):
                        data_config["app_template"] = t_config["app_template"]
                    if t_config.get("widgets_template_value"):
                        data_config["widgets_template_value"] = t_config["widgets_template_value"]
                    if t_config.get("set_appdrawer_template"):
                        data_config["set_appdrawer_template"] = t_config["set_appdrawer_template"]
                    if t_config.get("smtp_host"):
                        data_config["smtp_host"] = t_config["smtp_host"]
                    if t_config.get("smtp_port"):
                        data_config["smtp_port"] = t_config["smtp_port"]
                    if t_config.get("smtp_host_user"):
                        data_config["smtp_host_user"] = t_config["smtp_host_user"]
                    if t_config.get("smtp_host_password"):
                        data_config["smtp_host_password"] = t_config["smtp_host_password"]
                    if t_config.get("smtp_host_user"):
                        data_config["smtp_host_user"] = t_config["smtp_host_user"]
                    if t_config.get("smtp_allow_reset"):
                        data_config["smtp_allow_reset"] = t_config["smtp_allow_reset"]
                    if t_config.get("smtp_default_message"):
                        data_config["smtp_default_message"] = t_config["smtp_default_message"]
                    if t_config.get("smtp_msg_content"):
                        data_config["smtp_msg_content"] = t_config["smtp_msg_content"]
                    if t_config.get("mail_provider"):
                        data_config["mail_provider"] = t_config["mail_provider"]
                    if t_config.get("approval_smtp_port"):
                        data_config["approval_smtp_port"] = t_config["approval_smtp_port"]
                    if t_config.get("approval_smtp_requires_auth"):
                        data_config["approval_smtp_requires_auth"] = t_config["approval_smtp_requires_auth"]
                    if t_config.get("approval_password"):
                        data_config["approval_password"] = t_config["approval_password"]
                    if t_config.get("approval_email"):
                        data_config["approval_email"] = t_config["approval_email"]
                    if t_config.get("approval_msg_content"):
                        data_config["approval_msg_content"] = t_config["approval_msg_content"]
                    if t_config.get("customize_footer"):
                        data_config["customize_footer"] = t_config["customize_footer"]
                        data_config["footer_text"] = t_config["footer_text"]
                    if t_config.get("signup_header"):
                        data_config["signup_header"] = t_config["signup_header"]
                    if t_config.get("signup_msg"):
                        data_config["signup_msg"] = t_config["signup_msg"]
                    if t_config.get("rename_username"):
                        data_config["rename_username"] = t_config["rename_username"]
                    if t_config.get("rename_email"):
                        data_config["rename_email"] = t_config["rename_email"]
                    if t_config.get("rename_password"):
                        data_config["rename_password"] = t_config["rename_password"]
                    if t_config.get("rename_confirm_password"):
                        data_config["rename_confirm_password"] = t_config["rename_confirm_password"]
                    if t_config.get("remove_signup"):
                        data_config["remove_signup"] = t_config["remove_signup"]
                    if t_config.get("remove_remember_me"):
                        data_config["remove_remember_me"] = t_config["remove_remember_me"]
                    if t_config.get("remove_terms"):
                        data_config["remove_terms"] = t_config["remove_terms"]
                    if t_config.get("add_icons"):
                        data_config["add_icons"] = t_config["add_icons"]
                    if t_config.get("remove_labels"):
                        data_config["remove_labels"] = t_config["remove_labels"]
                    if t_config.get("sign_btn_bgcolor"):
                        data_config["sign_btn_bgcolor"] = t_config["sign_btn_bgcolor"]
                    if t_config.get("terms_conditions_mandatory"):
                        data_config["terms_conditions_mandatory"] = t_config["terms_conditions_mandatory"]
                    if t_config.get("addTermsAndCondition"):
                        data_config["addTermsAndCondition"] = t_config["addTermsAndCondition"]
                    if t_config.get("termsAndConditions"):
                        data_config["termsAndConditions"] = t_config["termsAndConditions"]
                    if t_config.get("static_image"):
                        data_config["static_image"] = t_config["static_image"]
                    if t_config.get("static_image_file"):
                        data_config["static_image_file"] = t_config["static_image_file"]
                    if t_config.get("video_on_loop"):
                        data_config["video_on_loop"] = t_config["video_on_loop"]
                    if t_config.get("video_URL"):
                        data_config["video_URL"] = t_config["video_URL"]
                    if t_config.get("video_url_bg"):
                        data_config["video_url_bg"] = t_config["video_url_bg"]
                    if t_config.get("video_File"):
                        data_config["video_File"] = t_config["video_File"]
                    if t_config.get("video_file_bg"):
                        data_config["video_file_bg"] = t_config["video_file_bg"]
                    if t_config.get("image_slider"):
                        data_config["image_slider"] = t_config["image_slider"]
                    if t_config.get("totalImages"):
                        data_config["totalImages"] = t_config["totalImages"]
                        for i in range(1, int(t_config["totalImages"]) + 1):
                            image = "image_slider_file" + str(i)
                            if t_config.get(image):
                                data_config[image] = t_config[image]
                    if t_config.get("play_on_loop"):
                        data_config["play_on_loop"] = t_config["play_on_loop"]
                    if t_config.get("transition_speed"):
                        data_config["transition_speed"] = t_config["transition_speed"]
                    if t_config.get("add_logo_screen"):
                        data_config["add_logo_screen"] = t_config["add_logo_screen"]
                    if t_config.get("logo_on_screen"):
                        data_config["logo_on_screen"] = t_config["logo_on_screen"]
                    if t_config.get("add_logo_login"):
                        data_config["add_logo_login"] = t_config["add_logo_login"]
                    if t_config.get("logo_on_form"):
                        data_config["logo_on_form"] = t_config["logo_on_form"]
                    if t_config.get("login_card_bgcolor"):
                        data_config["login_card_bgcolor"] = t_config["login_card_bgcolor"]
                    if t_config.get("customize_appdrawer_bg"):
                        data_config["customize_appdrawer_bg"] = t_config["customize_appdrawer_bg"]
                    if t_config.get("change_appdrawer_bg_file"):
                        data_config["change_appdrawer_bg_file"] = t_config["change_appdrawer_bg_file"]
                    if t_config.get("add_logo_appdrawer"):
                        data_config["add_logo_appdrawer"] = t_config["add_logo_appdrawer"]
                    if t_config.get("logo-file-appdrawer"):
                        data_config["logo-file-appdrawer"] = t_config["logo-file-appdrawer"]
                    if t_config.get("add_logo_topnavbar"):
                        data_config["add_logo_topnavbar"] = t_config["add_logo_topnavbar"]
                    if t_config.get("logo-file-topnavbar"):
                        data_config["logo-file-topnavbar"] = t_config["logo-file-topnavbar"]
                    if t_config.get("appdrawer_bg_image"):
                        data_config["appdrawer_bg_image"] = t_config["appdrawer_bg_image"]
                    if t_config.get("appdrawer_bg_image_name"):
                        data_config["appdrawer_bg_image_name"] = t_config["appdrawer_bg_image_name"]
                    if t_config.get("appdrawer_bgColor"):
                        data_config["appdrawer_bgColor"] = t_config["appdrawer_bgColor"]
                    if t_config.get("appdrawer_bgColorCode"):
                        data_config["appdrawer_bgColorCode"] = t_config["appdrawer_bgColorCode"]
                    if t_config.get("login-footer-size"):
                        data_config["login-footer-size"] = t_config["login-footer-size"]
                    if t_config.get("footer_placement"):
                        data_config["footer_placement"] = t_config["footer_placement"]
                    if t_config.get("login_footer_bgcolor"):
                        data_config["login_footer_bgcolor"] = t_config["login_footer_bgcolor"]
                    if t_config.get("customize_app_footer"):
                        data_config["customize_app_footer"] = t_config["customize_app_footer"]
                    if t_config.get("app_footer_text"):
                        data_config["app_footer_text"] = t_config["app_footer_text"]
                    if t_config.get("app_footer_size"):
                        data_config["app_footer_size"] = t_config["app_footer_size"]
                    if t_config.get("app_footer_placement"):
                        data_config["app_footer_placement"] = t_config["app_footer_placement"]
                    if t_config.get("app_footer_bgcolor"):
                        data_config["app_footer_bgcolor"] = t_config["app_footer_bgcolor"]
                    if t_config.get("sign_font_bgcolor"):
                        data_config["sign_font_bgcolor"] = t_config["sign_font_bgcolor"]
                    if t_config.get("icon_bgcolor"):
                        data_config["icon_bgcolor"] = t_config["icon_bgcolor"]
                    if t_config.get("remove_all_social"):
                        data_config["remove_all_social"] = t_config["remove_all_social"]
                    if t_config.get("remove_facebook"):
                        data_config["remove_facebook"] = t_config["remove_facebook"]
                    if t_config.get("remove_google"):
                        data_config["remove_google"] = t_config["remove_google"]
                    if t_config.get("remove_microsoft"):
                        data_config["remove_microsoft"] = t_config["remove_microsoft"]
                    if t_config.get("remove_twitter"):
                        data_config["remove_twitter"] = t_config["remove_twitter"]
                    if t_config.get("remove_amazon"):
                        data_config["remove_amazon"] = t_config["remove_amazon"]
                    if t_config.get("remove_apple"):
                        data_config["remove_apple"] = t_config["remove_apple"]
                    if t_config.get("remove_admin_toggle"):
                        data_config["remove_admin_toggle"] = t_config["remove_admin_toggle"]
                    if t_config.get("developer_mode"):
                        data_config["developer_mode"] = t_config["developer_mode"]
                    if t_config.get("allow_user_forum"):
                        data_config["allow_user_forum"] = t_config["allow_user_forum"]
                    if t_config.get("allow_user_planner"):
                        data_config["allow_user_planner"] = t_config["allow_user_planner"]
                    if t_config.get("allow_user_profile"):
                        data_config["allow_user_profile"] = t_config["allow_user_profile"]
                    if t_config.get("allow_dashboard_portal"):
                        data_config["allow_dashboard_portal"] = t_config["allow_dashboard_portal"]
                    if t_config.get("block_third_party"):
                        data_config["block_third_party"] = t_config["block_third_party"]
                    if t_config.get("add_logo_error"):
                        data_config["add_logo_error"] = t_config["add_logo_error"]
                    if t_config.get("logo_file_error_page"):
                        data_config["logo_file_error_page"] = t_config["logo_file_error_page"]
                    if t_config.get("add_bg_error_subprocess"):
                        data_config["add_bg_error_subprocess"] = t_config["add_bg_error_subprocess"]
                    if t_config.get("subprocess_bg"):
                        data_config["subprocess_bg"] = t_config["subprocess_bg"]
                    if t_config.get("add_favicon_error_subprocess"):
                        data_config["add_favicon_error_subprocess"] = t_config["add_favicon_error_subprocess"]
                    if t_config.get("subprocess_favicon"):
                        data_config["subprocess_favicon"] = t_config["subprocess_favicon"]
                    if t_config.get("change_subprocess_text"):
                        data_config["change_subprocess_text"] = t_config["change_subprocess_text"]
                    if t_config.get("change_subprocess_button"):
                        data_config["change_subprocess_button"] = t_config["change_subprocess_button"]
                    if t_config.get("buttons_subprocess"):
                        data_config["buttons_subprocess"] = t_config["buttons_subprocess"]
                    if t_config.get("subprocess_text"):
                        data_config["subprocess_text"] = t_config["subprocess_text"]
                    if t_config.get("add_bg_error_permission"):
                        data_config["add_bg_error_permission"] = t_config["add_bg_error_permission"]
                    if t_config.get("permission_bg"):
                        data_config["permission_bg"] = t_config["permission_bg"]
                    if t_config.get("add_favicon_error_permission"):
                        data_config["add_favicon_error_permission"] = t_config["add_favicon_error_permission"]
                    if t_config.get("permission_favicon"):
                        data_config["permission_favicon"] = t_config["permission_favicon"]
                    if t_config.get("change_permission_text"):
                        data_config["change_permission_text"] = t_config["change_permission_text"]
                    if t_config.get("change_permission_button"):
                        data_config["change_permission_button"] = t_config["change_permission_button"]
                    if t_config.get("buttons_permission"):
                        data_config["buttons_permission"] = t_config["buttons_permission"]
                    if t_config.get("permission_text"):
                        data_config["permission_text"] = t_config["permission_text"]
                    if t_config.get("500bg"):
                        data_config["500bg"] = t_config["500bg"]
                    if t_config.get("add_bg_error500"):
                        data_config["add_bg_error500"] = t_config["add_bg_error500"]
                    if t_config.get("500favicon"):
                        data_config["500favicon"] = t_config["500favicon"]
                    if t_config.get("add_favicon_error500"):
                        data_config["add_favicon_error500"] = t_config["add_favicon_error500"]
                    if t_config.get("text_500"):
                        data_config["text_500"] = t_config["text_500"]
                    if t_config.get("change_500_text"):
                        data_config["change_500_text"] = t_config["change_500_text"]
                    if t_config.get("change_500_button"):
                        data_config["change_500_button"] = t_config["change_500_button"]
                    if t_config.get("buttons_500"):
                        data_config["buttons_500"] = t_config["buttons_500"]
                    if t_config.get("502bg"):
                        data_config["502bg"] = t_config["502bg"]
                    if t_config.get("add_bg_error502"):
                        data_config["add_bg_error502"] = t_config["add_bg_error502"]
                    if t_config.get("502favicon"):
                        data_config["502favicon"] = t_config["502favicon"]
                    if t_config.get("add_favicon_error502"):
                        data_config["add_favicon_error502"] = t_config["add_favicon_error502"]
                    if t_config.get("text_502"):
                        data_config["text_502"] = t_config["text_502"]
                    if t_config.get("change_502_text"):
                        data_config["change_502_text"] = t_config["change_502_text"]
                    if t_config.get("change_502_button"):
                        data_config["change_502_button"] = t_config["change_502_button"]
                    if t_config.get("buttons_502"):
                        data_config["buttons_502"] = t_config["buttons_502"]
                    if t_config.get("403bg"):
                        data_config["403bg"] = t_config["403bg"]
                    if t_config.get("add_bg_error403"):
                        data_config["add_bg_error403"] = t_config["add_bg_error403"]
                    if t_config.get("add_favicon_error403"):
                        data_config["add_favicon_error403"] = t_config["add_favicon_error403"]
                    if t_config.get("403favicon"):
                        data_config["403favicon"] = t_config["403favicon"]
                    if t_config.get("text_403"):
                        data_config["text_403"] = t_config["text_403"]
                    if t_config.get("change_403_text"):
                        data_config["change_403_text"] = t_config["change_403_text"]
                    if t_config.get("change_403_button"):
                        data_config["change_403_button"] = t_config["change_403_button"]
                    if t_config.get("buttons_403"):
                        data_config["buttons_403"] = t_config["buttons_403"]
                    if t_config.get("503bg"):
                        data_config["503bg"] = t_config["503bg"]
                    if t_config.get("add_bg_error503"):
                        data_config["add_bg_error503"] = t_config["add_bg_error503"]
                    if t_config.get("add_favicon_error503"):
                        data_config["add_favicon_error503"] = t_config["add_favicon_error503"]
                    if t_config.get("503favicon"):
                        data_config["503favicon"] = t_config["503favicon"]
                    if t_config.get("text_503"):
                        data_config["text_503"] = t_config["text_503"]
                    if t_config.get("change_503_text"):
                        data_config["change_503_text"] = t_config["change_503_text"]
                    if t_config.get("change_503_button"):
                        data_config["change_503_button"] = t_config["change_503_button"]
                    if t_config.get("buttons_503"):
                        data_config["buttons_503"] = t_config["buttons_503"]
                    if t_config.get("add_bg_error404"):
                        data_config["add_bg_error404"] = t_config["add_bg_error404"]
                    if t_config.get("404bg"):
                        data_config["404bg"] = t_config["404bg"]
                    if t_config.get("add_favicon_error404"):
                        data_config["add_favicon_error404"] = t_config["add_favicon_error404"]
                    if t_config.get("404favicon"):
                        data_config["404favicon"] = t_config["404favicon"]
                    if t_config.get("change_404_text"):
                        data_config["change_404_text"] = t_config["change_404_text"]
                    if t_config.get("change_404_button"):
                        data_config["change_404_button"] = t_config["change_404_button"]
                    if t_config.get("buttons_404"):
                        data_config["buttons_404"] = t_config["buttons_404"]
                    if t_config.get("text_404"):
                        data_config["text_404"] = t_config["text_404"]
                    if t_config.get("allow_copy_paste_password"):
                        data_config["allow_copy_paste_password"] = t_config["allow_copy_paste_password"]
                    if t_config.get("allow_copy_paste_username"):
                        data_config["allow_copy_paste_username"] = t_config["allow_copy_paste_username"]
                    if t_config.get("allow_copy_paste_email"):
                        data_config["allow_copy_paste_email"] = t_config["allow_copy_paste_email"]
                    if t_config.get("block_autocomplete_credentials"):
                        data_config["block_autocomplete_credentials"] = t_config[
                            "block_autocomplete_credentials"
                        ]
                    if t_config.get("primary_bgcolor"):
                        data_config["primary_bgcolor"] = t_config["primary_bgcolor"]
                    if t_config.get("secondary_color"):
                        data_config["secondary_color"] = t_config["secondary_color"]
                    if t_config.get("font_color"):
                        data_config["font_color"] = t_config["font_color"]
                    if t_config.get("font_hover_color"):
                        data_config["font_hover_color"] = t_config["font_hover_color"]
                    if t_config.get("font_family"):
                        data_config["font_family"] = t_config["font_family"]
                    if t_config.get("set_app_drawer_theme"):
                        data_config["set_app_drawer_theme"] = t_config["set_app_drawer_theme"]
                    if t_config.get("add_logo_tenant"):
                        data_config["add_logo_tenant"] = t_config["add_logo_tenant"]
                    if t_config.get("logo_on_tenant"):
                        data_config["logo_on_tenant"] = t_config["logo_on_tenant"]
                    if t_config.get("set_tenant_admin_theme"):
                        data_config["set_tenant_admin_theme"] = t_config["set_tenant_admin_theme"]
                    if t_config.get("tenant_primary_bgcolor"):
                        data_config["tenant_primary_bgcolor"] = t_config["tenant_primary_bgcolor"]
                    if t_config.get("tenant_secondary_bgcolor"):
                        data_config["tenant_secondary_bgcolor"] = t_config["tenant_secondary_bgcolor"]
                    if t_config.get("tenant_font_bgcolor"):
                        data_config["tenant_font_bgcolor"] = t_config["tenant_font_bgcolor"]
                    if t_config.get("tenant_hover_bgcolor"):
                        data_config["tenant_hover_bgcolor"] = t_config["tenant_hover_bgcolor"]
                    if t_config.get("font_family_tenant"):
                        data_config["font_family_tenant"] = t_config["font_family_tenant"]
                    if t_config.get("tenantbg_bgcolor"):
                        data_config["tenantbg_bgcolor"] = t_config["tenantbg_bgcolor"]
                    if t_config.get("set_tenantbg_bgcolor"):
                        data_config["set_tenantbg_bgcolor"] = t_config["set_tenantbg_bgcolor"]
                    if t_config.get("add_bg_tenant_admin"):
                        data_config["add_bg_tenant_admin"] = t_config["add_bg_tenant_admin"]
                    if t_config.get("tenant_static_image"):
                        data_config["tenant_static_image"] = t_config["tenant_static_image"]
                    if t_config.get("tenant_static_image_file"):
                        data_config["tenant_static_image_file"] = t_config["tenant_static_image_file"]
                    if t_config.get("tenant_video_on_loop"):
                        data_config["tenant_video_on_loop"] = t_config["tenant_video_on_loop"]
                    if t_config.get("video_URL_tenant"):
                        data_config["video_URL_tenant"] = t_config["video_URL_tenant"]
                    if t_config.get("video_url_bg_tenant"):
                        data_config["video_url_bg_tenant"] = t_config["video_url_bg_tenant"]
                    if t_config.get("video_File_tenant"):
                        data_config["video_File_tenant"] = t_config["video_File_tenant"]
                    if t_config.get("video_file_bg_tenant"):
                        data_config["video_file_bg_tenant"] = t_config["video_file_bg_tenant"]
                    if t_config.get("tenant_image_slider"):
                        data_config["tenant_image_slider"] = t_config["tenant_image_slider"]
                    if t_config.get("mfa_configs"):
                        data_config["mfa_configs"] = t_config["mfa_configs"]
                    if t_config.get("block_custom_homepage_dev"):
                        data_config["block_custom_homepage_dev"] = t_config["block_custom_homepage_dev"]
                    if t_config.get("block_custom_homepage_user"):
                        data_config["block_custom_homepage_user"] = t_config["block_custom_homepage_user"]
                    if t_config.get("block_add_navpoints_dev"):
                        data_config["block_add_navpoints_dev"] = t_config["block_add_navpoints_dev"]
                    if t_config.get("block_add_navpoints_user"):
                        data_config["block_add_navpoints_user"] = t_config["block_add_navpoints_user"]
                    if t_config.get("block_remove_navpoints_dev"):
                        data_config["block_remove_navpoints_dev"] = t_config["block_remove_navpoints_dev"]
                    if t_config.get("block_remove_navpoints_user"):
                        data_config["block_remove_navpoints_user"] = t_config["block_remove_navpoints_user"]
                    if t_config.get("remembermeConfig"):
                        data_config["remembermeConfig"] = t_config["remembermeConfig"]
                    if t_config.get("customLoginMessages"):
                        data_config["customLoginMessages"] = t_config["customLoginMessages"]
                    if t_config.get("set_title_appdrawer"):
                        data_config["set_title_appdrawer"] = t_config["set_title_appdrawer"]
                    if t_config.get("appdrawer_title"):
                        data_config["appdrawer_title"] = t_config["appdrawer_title"]
                    if t_config.get("set_favicon_appdrawer"):
                        data_config["set_favicon_appdrawer"] = t_config["set_favicon_appdrawer"]
                    if t_config.get("appdrawer_favicon_file"):
                        data_config["appdrawer_favicon_file"] = t_config["appdrawer_favicon_file"]
                    if t_config.get("set_title_login"):
                        data_config["set_title_login"] = t_config["set_title_login"]
                    if t_config.get("login_title"):
                        data_config["login_title"] = t_config["login_title"]
                    if t_config.get("set_favicon_login"):
                        data_config["set_favicon_login"] = t_config["set_favicon_login"]
                    if t_config.get("login_favicon_file"):
                        data_config["login_favicon_file"] = t_config["login_favicon_file"]
                    if t_config.get("tenant_slider_style"):
                        data_config["tenant_slider_style"] = t_config["tenant_slider_style"]
                    if t_config.get("tenant_totalimage"):
                        data_config["tenant_totalimage"] = t_config["tenant_totalimage"]
                        for i in range(1, int(t_config["tenant_totalimage"]) + 1):
                            image = "tenant_image_slider_file" + str(i)
                            if t_config.get(image):
                                data_config[image] = t_config[image]
                    if t_config.get("user_limit_count"):
                        data_config["user_limit_count"] = t_config["user_limit_count"]
                    if t_config.get("app_limit_count"):
                        data_config["app_limit_count"] = t_config["app_limit_count"]
                    if t_config.get("dev_limit_count"):
                        data_config["dev_limit_count"] = t_config["dev_limit_count"]
                    if t_config.get("set_user_limit"):
                        data_config["set_user_limit"] = t_config["set_user_limit"]
                    if t_config.get("set_app_limit"):
                        data_config["set_app_limit"] = t_config["set_app_limit"]
                    if t_config.get("set_dev_limit"):
                        data_config["set_dev_limit"] = t_config["set_dev_limit"]
                    if t_config.get("smtp_server_count"):
                        data_config["smtp_server_count"] = t_config["smtp_server_count"]
                    if t_config.get("allow_users_to_config_smtp"):
                        data_config["allow_users_to_config_smtp"] = t_config["allow_users_to_config_smtp"]
                    if t_config.get("add_footer_error"):
                        data_config["add_footer_error"] = t_config["add_footer_error"]
                    if t_config.get("error_footer_text"):
                        data_config["error_footer_text"] = t_config["error_footer_text"]
                    if t_config.get("error_footer_size"):
                        data_config["error_footer_size"] = t_config["error_footer_size"]
                    if t_config.get("error_footer_placement"):
                        data_config["error_footer_placement"] = t_config["error_footer_placement"]
                    if t_config.get("error_footer_bgcolor"):
                        data_config["error_footer_bgcolor"] = t_config["error_footer_bgcolor"]
                    if t_config.get("user_inactivity_days"):
                        data_config["user_inactivity_days"] = t_config["user_inactivity_days"]
                    if t_config.get("user_inactivity_hours"):
                        data_config["user_inactivity_hours"] = t_config["user_inactivity_hours"]
                    if t_config.get("user_inactivity_minutes"):
                        data_config["user_inactivity_minutes"] = t_config["user_inactivity_minutes"]
                    if t_config.get("user_failedlogins_days"):
                        data_config["user_failedlogins_days"] = t_config["user_failedlogins_days"]
                    if t_config.get("user_failedlogins_hours"):
                        data_config["user_failedlogins_hours"] = t_config["user_failedlogins_hours"]
                    if t_config.get("user_failedlogins_minutes"):
                        data_config["user_failedlogins_minutes"] = t_config["user_failedlogins_minutes"]

                    if t_config.get("remove_bell_icon"):
                        data_config["remove_bell_icon"] = t_config["remove_bell_icon"]
                    if t_config.get("limit_notification"):
                        data_config["limit_notification"] = t_config["limit_notification"]
                    if t_config.get("noti_expiry_days"):
                        data_config["noti_expiry_days"] = t_config["noti_expiry_days"]
                    if t_config.get("noti_expiry_hours"):
                        data_config["noti_expiry_hours"] = t_config["noti_expiry_hours"]
                    if t_config.get("noti_expiry_minutes"):
                        data_config["noti_expiry_minutes"] = t_config["noti_expiry_minutes"]

            json_file.close()

        return data_config


def redirect_index(request):
    return redirect("/tenant_admin/")


@never_cache
def customize_theme(request, app_mode):
    tenant = tenant_schema_from_request(request, original=True)
    if request.method == "POST":
        if request.POST["operation"] == "save_theme_data":
            theme_config = json.loads(request.POST["data"])
            app_code = request.POST["app_code"]
            theme_type = request.POST["theme_type"]
            theme_name = request.POST["theme_name"]

            app_type = request.POST["app_type"]

            if app_type == "user_apps":

                db_type = ""
                db_connection_name = None
                schema = tenant + "_" + app_code
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        db_connection_name = json.load(json_file).get(schema)
                        json_file.close()
                user_db_engine, db_type = db_engine_extractor(db_connection_name)
                condition_list = [
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": app_code,
                        "and_or": "and",
                    },
                    {
                        "column_name": "theme_type",
                        "condition": "Equal to",
                        "input_value": theme_type,
                        "and_or": "",
                    },
                ]
                if theme_type != "Global" and theme_name:
                    condition_list[-1]["and_or"] = "and"
                    condition_list.append(
                        {
                            "column_name": "theme_name",
                            "condition": "Equal to",
                            "input_value": theme_name,
                            "and_or": "",
                        }
                    )
                else:
                    pass
                check_app_code = read_data_func(
                    request="",
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "application_theme",
                            "Columns": ["app_code"],
                        },
                        "condition": condition_list,
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(check_app_code) > 0:
                    update_data_func(
                        request="",
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "application_theme",
                                "Columns": [
                                    {
                                        "column_name": "theme_config",
                                        "input_value": json.dumps(theme_config),
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "theme_name",
                                        "input_value": theme_name,
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "modified_by",
                                        "input_value": request.user.username,
                                        "separator": ",",
                                    },
                                    {
                                        "column_name": "modified_date",
                                        "input_value": datetime.now(),
                                        "separator": "",
                                    },
                                ],
                            },
                            "condition": condition_list,
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                else:
                    theme_df = pd.DataFrame(
                        [
                            {
                                "app_code": app_code,
                                "theme_type": theme_type,
                                "theme_name": theme_name,
                                "theme_config": json.dumps(theme_config),
                                "created_date": datetime.now(),
                                "created_by": request.user.username,
                            }
                        ]
                    )
                    data_handling(
                        request,
                        theme_df,
                        "application_theme",
                        con=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

            elif app_type == "sys_apps":

                db_type = ""
                db_connection_name = None
                schema = tenant + "_" + app_code
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        db_connection_name = json.load(json_file).get(schema)
                        json_file.close()
                user_db_engine, db_type = db_engine_extractor(db_connection_name)

                check_app_code = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "system_application_master",
                            "Columns": ["app_name"],
                        },
                        "condition": [
                            {
                                "column_name": "app_name",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )

                if len(check_app_code) > 0:
                    update_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "system_application_master",
                                "Columns": [
                                    {
                                        "column_name": "app_theme",
                                        "input_value": json.dumps(theme_config),
                                        "separator": "",
                                    }
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": "app_name",
                                    "condition": "Equal to",
                                    "input_value": app_code,
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                else:
                    display = {}
                    if app_code == "planner":
                        display = {"show_planner": "true", "display_position": "planner_app"}
                    elif app_code == "dashboard":
                        display = {"show_dashboard": "true", "display_position": "dashboard_app"}

                    dashboard_config_df = pd.DataFrame(
                        [
                            {
                                "app_name": app_code,
                                "display_config": json.dumps(display),
                                "app_theme": json.dumps(theme_config),
                            }
                        ]
                    )

                    data_handling(
                        request,
                        dashboard_config_df,
                        "system_application_master",
                        con=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
            else:
                pass

            return JsonResponse({"message": "Theme saved successfully!"})

        if request.POST["operation"] == "load_section_data":
            app_code = request.POST["app_code"]
            theme_type = request.POST["theme_type"]
            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            section_data = read_data_func(
                request=request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "application_theme",
                        "Columns": ["theme_name"],
                    },
                    "condition": [
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "theme_type",
                            "condition": "Equal to",
                            "input_value": theme_type,
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if len(section_data) > 0:
                section_data = section_data["theme_name"].tolist()
                for i, v in enumerate(section_data):
                    if v == "":
                        section_data[i] = "Global"
            else:
                return JsonResponse({})
            return JsonResponse({"section_data": section_data})

        if request.POST["operation"] == "save_process_section_data":
            app_code = request.POST["app_code"]
            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            theme_name = request.POST["theme_name"]
            process_code = request.POST["process_code"]
            sub_process_code = request.POST["sub_process_code"]
            update_data_func(
                request=request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "NavigationSideBar",
                        "Columns": [
                            {
                                "column_name": "theme_name",
                                "input_value": theme_name,
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "item_name",
                            "condition": "Equal to",
                            "input_value": sub_process_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "item_group_code",
                            "condition": "Equal to",
                            "input_value": process_code,
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            return JsonResponse({})

        if request.POST["operation"] == "load_process_section_data":
            process_code = request.POST["process_code"]
            sub_process_code = request.POST["sub_process_code"]
            app_code = request.POST["app_code"]
            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            theme_name = read_data_func(
                request=request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "NavigationSideBar",
                        "Columns": [
                            "theme_name",
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "item_name",
                            "condition": "Equal to",
                            "input_value": sub_process_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "item_group_code",
                            "condition": "Equal to",
                            "input_value": process_code,
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if len(theme_name) > 0:
                theme_name = theme_name.iloc[0]["theme_name"]
                if theme_name is not None:
                    return JsonResponse(json.loads(theme_name))
            return JsonResponse({})

        if request.POST["operation"] == "load_template_selection_data":
            app_code = request.POST["app_code"]
            template_type = request.POST["template_type"]
            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            template_data = read_data_func(
                request="",
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "template_theme",
                        "Columns": ["template_name"],
                    },
                    "condition": [
                        {
                            "column_name": "template_type",
                            "condition": "Equal to",
                            "input_value": template_type,
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if len(template_data) > 0:
                template_data = template_data["template_name"].tolist()
            else:
                check_default_exists = read_data_func(
                    request="",
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "template_theme",
                            "Columns": ["*"],
                        },
                        "condition": [],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(check_default_exists) < 3:
                    default_df = pd.DataFrame(
                        {
                            "template_name": ["Default", "Default", "Default"],
                            "template_type": ["navbar", "sidebar", "footer"],
                            "template_config": [
                                '{"name":"default_theme","vars":{}}',
                                '{"name":"default_theme","sidebarSize":"4.6rem","vars":{"sidebaricon":{"label":"Sidebar icon","type":"file"}}}',
                                '{"name":"default_theme","vars":{"footertext":{"label":"Footer text","type":"text"}}}',
                            ],
                        }
                    )
                    data_handling(
                        request,
                        default_df,
                        "template_theme",
                        con=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                return JsonResponse({}, safe=False)
            return JsonResponse({"template_selection": template_data})

        if request.POST["operation"] == "load_theme_data":
            app_code = request.POST["app_code"]
            theme_type = request.POST["theme_type"]
            theme_name = request.POST["theme_name"]
            app_type = request.POST["app_type"]

            theme_data = {}
            if app_type == "user_apps":

                db_type = ""
                db_connection_name = None
                schema = tenant + "_" + app_code
                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        db_connection_name = json.load(json_file).get(schema)
                        json_file.close()
                user_db_engine, db_type = db_engine_extractor(db_connection_name)
                condition_list = [
                    {
                        "column_name": "app_code",
                        "condition": "Equal to",
                        "input_value": app_code,
                        "and_or": "and",
                    },
                    {
                        "column_name": "theme_type",
                        "condition": "Equal to",
                        "input_value": theme_type,
                        "and_or": "",
                    },
                ]
                if theme_type != "Global" and theme_name:
                    condition_list[-1]["and_or"] = "and"
                    condition_list.append(
                        {
                            "column_name": "theme_name",
                            "condition": "Equal to",
                            "input_value": theme_name,
                            "and_or": "",
                        }
                    )
                else:
                    pass
                theme_config = read_data_func(
                    request="",
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "application_theme",
                            "Columns": ["theme_config", "theme_name"],
                        },
                        "condition": condition_list,
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(theme_config) > 0:
                    theme_data = {}
                    theme_data["theme_config"] = json.loads(theme_config.iloc[0]["theme_config"])
                    theme_data["theme_name"] = theme_config.iloc[0]["theme_name"]
                else:
                    return JsonResponse({})

            elif app_type == "sys_apps":

                db_type = ""
                db_connection_name = None
                schema = tenant + "_" + app_code

                if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                        db_connection_name = json.load(json_file).get(schema)
                        json_file.close()
                user_db_engine, db_type = db_engine_extractor(db_connection_name)

                theme_config = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "system_application_master",
                            "Columns": ["app_theme"],
                        },
                        "condition": [
                            {
                                "column_name": "app_name",
                                "condition": "Equal to",
                                "input_value": app_code,
                                "and_or": "",
                            }
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(theme_config) > 0:
                    theme_data["theme_config"] = theme_config.to_dict("records")[0]["app_theme"]
                else:
                    return JsonResponse({})

            else:
                pass

            return JsonResponse(theme_data)

        if request.POST["operation"] == "load_template_data":
            app_code = request.POST["app_code"]
            template_name = request.POST["template_name"]
            template_type = request.POST["template_type"]
            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)
            template_data = read_data_func(
                request="",
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "template_theme",
                        "Columns": ["template_config"],
                    },
                    "condition": [
                        {
                            "column_name": "template_name",
                            "condition": "Equal to",
                            "input_value": template_name,
                            "and_or": "and",
                        },
                        {
                            "column_name": "template_type",
                            "condition": "Equal to",
                            "input_value": template_type,
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )
            if len(template_data) > 0:
                template_data = json.loads(template_data.iloc[0]["template_config"])
                if os.path.exists(
                    "kore_investment/"
                    + "/templates/Themes/"
                    + template_name
                    + "/theme_preview/"
                    + template_type
                    + ".png"
                ):
                    file_path = (
                        "kore_investment/"
                        + "/templates/Themes/"
                        + template_name
                        + "/theme_preview/"
                        + template_type
                        + ".png"
                    )
                    try:
                        with open(file_path, "rb") as f:
                            template_data["preview_image"] = b64encode(f.read()).decode("utf-8")
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
            return JsonResponse(template_data)

        if request.POST["operation"] == "upload_theme_image":
            app_code = request.POST["app_code"]
            theme_type = request.POST["theme_type"]
            if theme_type == "Section":
                theme_name = request.POST["theme_name"]
            if "image" in request.FILES:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]
                img_name = request.POST["image_name"]
                if theme_type == "Section":
                    img_save_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/{theme_name}/{img_name}{img_extension}"
                else:
                    img_save_path = (
                        f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/{img_name}{img_extension}"
                    )
                if not os.path.exists(f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/"):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/")
                if theme_type == "Section" and not os.path.exists(
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/{theme_name}/"
                ):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/{theme_name}/")
                with open(img_save_path, "wb+") as f:
                    for chunk in img.chunks():
                        f.write(chunk)
            return JsonResponse({})

        if request.POST["operation"] == "upload_bg":
            app_code = request.POST["app_code"]
            error_code = request.POST["error_code"]
            if "image" in request.FILES:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]
                img_name = request.POST["image_name"]

                img_save_path = (
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/background/{error_code}/{img_name}"
                )

                if not os.path.exists(
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/background/{error_code}"
                ):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/background/{error_code}")
                with open(img_save_path, "wb+") as f:
                    for chunk in img.chunks():
                        f.write(chunk)
            return JsonResponse({})

        if request.POST["operation"] == "upload_favicon":
            app_code = request.POST["app_code"]
            error_code = request.POST["error_code"]
            if "image" in request.FILES:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]
                img_name = request.POST["image_name"]

                img_save_path = (
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/favicon/{error_code}/{img_name}"
                )

                if not os.path.exists(
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/favicon/{error_code}"
                ):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/favicon/{error_code}")
                with open(img_save_path, "wb+") as f:
                    for chunk in img.chunks():
                        f.write(chunk)
            return JsonResponse({})

        if request.POST["operation"] == "upload_logo":
            app_code = request.POST["app_code"]
            error_code = request.POST["error_code"]
            if "image" in request.FILES:
                img = request.FILES["image"]
                img_extension = os.path.splitext(img.name)[1]
                img_name = request.POST["image_name"]

                img_save_path = (
                    f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/logo/{error_code}/{img_name}"
                )

                if not os.path.exists(f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/logo/{error_code}"):
                    os.makedirs(f"{MEDIA_ROOT}/{tenant}/{app_code}/ErrorConfigfiles/logo/{error_code}")
                with open(img_save_path, "wb+") as f:
                    for chunk in img.chunks():
                        f.write(chunk)
            return JsonResponse({})

        if request.POST["operation"] == "apply_theme_data":
            preview = False
            app_code = request.POST["app_code"]
            theme_type = request.POST["theme_type"]
            theme_name = request.POST["theme_name"]
            app_type = request.POST["app_type"]

            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = db_engine_extractor(db_connection_name)

            processGlobal = False
            if theme_name == "" and theme_type == "Section":
                processGlobal = True
            showNavbar = True
            showSidebar = True
            showFooter = True
            if "process_config" in request.POST:
                process_config = json.loads(request.POST["process_config"])
                showNavbar = process_config["showNavbar"]
                showSidebar = process_config["showSidebar"]
                showFooter = process_config["showFooter"]
                process_code = process_config["process_code"]
                sub_process_code = process_config["sub_process_code"]
                item_code = read_data_func(
                    request=request,
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "navigationsidebar",
                            "Columns": [
                                "item_code",
                            ],
                        },
                        "condition": [
                            {
                                "column_name": "item_name",
                                "condition": "Equal to",
                                "input_value": sub_process_code,
                                "and_or": "and",
                            },
                            {
                                "column_name": "item_group_code",
                                "condition": "Equal to",
                                "input_value": process_code,
                                "and_or": "",
                            },
                        ],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                if len(item_code) > 0:
                    item_code = item_code.iloc[0]["item_code"]
            if "preview" in request.POST:
                preview = True
            if preview is False:
                if processGlobal:
                    theme_type = "Global"
                    theme_name = ""

                if app_type == "user_apps":
                    condition_list = [
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "theme_type",
                            "condition": "Equal to",
                            "input_value": theme_type,
                            "and_or": "",
                        },
                    ]
                    if theme_type != "Global" and theme_name:
                        condition_list[-1]["and_or"] = "and"
                        condition_list.append(
                            {
                                "column_name": "theme_name",
                                "condition": "Equal to",
                                "input_value": theme_name,
                                "and_or": "",
                            }
                        )
                    else:
                        pass

                    theme_config = read_data_func(
                        request="",
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "application_theme",
                                "Columns": ["theme_config"],
                            },
                            "condition": condition_list,
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                    theme_config = json.loads(theme_config.iloc[0]["theme_config"])

                elif app_type == "sys_apps":

                    theme_config = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "system_application_master",
                                "Columns": ["app_theme"],
                            },
                            "condition": [
                                {
                                    "column_name": "app_name",
                                    "condition": "Equal to",
                                    "input_value": app_code,
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )
                    theme_config = json.loads(theme_config.iloc[0]["app_theme"])
                else:
                    pass

                if processGlobal:
                    theme_type = "Section"
                    theme_name = "Global"
                if theme_type == "Section":
                    theme_type = f"Section/{theme_name}"
                if len(theme_config) > 0:

                    source = "kore_investment/templates/Themes/Default/base_all.html"
                    dest = f"kore_investment/templates/user_defined_template/{tenant}/{app_code}/theme/{theme_type}/"
                    if not os.path.exists(dest):
                        os.makedirs(dest)
                    if "process_config" in request.POST:
                        dest += f"{item_code}/"
                        if not os.path.exists(dest):
                            os.makedirs(dest)
                    dest += "base_all.html"
                    shutil.copyfile(source, dest)
                else:
                    return JsonResponse({"message": "Save theme to apply it."})
            else:
                source = "kore_investment/templates/Themes/Default/preview_customize.html"
                dest = (
                    f"kore_investment/templates/user_defined_template/{tenant}/{app_code}/theme/{theme_type}/"
                )
                theme_config = json.loads(request.POST["theme_config"])
                if not os.path.exists(dest):
                    os.makedirs(dest)
                dest += "preview_tenant.html"
                shutil.copyfile(source, dest)

            footer_sticky = ""
            navbar_sticky = ""
            if preview is True:
                theme_file = f"kore_investment/templates/user_defined_template/{tenant}/{app_code}/theme/{theme_type}/preview_tenant.html"
            else:
                pass

            for i in ["footer", "navbar", "sidebar"]:
                if "name" not in theme_config[i]["template_config"]:
                    ijson_name = "Default"
                    ijson = {}
                else:
                    ijson_name = theme_config[i]["template_config"]["name"]
                    ijson = theme_config[i]["template_config"]["vars"]
                if preview is False:
                    theme_file = f"kore_investment/templates/Themes/{ijson_name}/{i}.html"
                with open(theme_file) as rfile:
                    data = rfile.read()
                    if len(ijson.keys()):
                        for var in ijson.keys():
                            var_tag = "<<" + var + ">>"
                            if var == "sidebaricon":
                                var_value = f"/media/{tenant}/{app_code}/{ijson[var]}"
                            else:
                                var_value = ijson[var]
                            data = data.replace(var_tag, var_value)
                    else:
                        data = data.replace("<<sidebaricon>>", "")
                        data = data.replace(
                            "<<footertext>>",
                            "ACIES, Acies Consulting, Acies TechWorks, Acies Ventures, Acies LightHouse, Kepler, Kore, Callisto, Carpo, Revolutio and Antares are registered trademarks of Acies LLP, Acies Consulting Pte Ltd. and its subsidiaries in different countries and territories. Unauthorized use, misrepresentation or misuse of trademarks is strictly prohibited and subject to legal action under various laws.",
                        )
                    with open(dest) as rwfile:
                        rwdata = rwfile.read()
                        if i == "footer":
                            if theme_config["footer"]["footerCheck"] is False:
                                data = ""
                            if showFooter is False:
                                data = ""
                        if theme_config["footer"]["position"] == "Sticky":
                            footer_sticky = ".footer-sticky { position: inherit !important; }\n"
                            data = data.replace("<<footerSticky>>", "true")
                        else:
                            data = data.replace("<<footerSticky>>", "false")
                        if i == "navbar":
                            if theme_config["navbar"]["navbarCheck"] is False:
                                data = ""
                            if showNavbar is False:
                                data = ""
                        if theme_config["navbar"]["position"] == "Floating":
                            navbar_sticky = ".navbar-sticky { position: fixed !important;width: -webkit-fill-available; }\n"
                            data = data.replace("<<navbarSticky>>", "false")
                        else:
                            data = data.replace("<<navbarSticky>>", "true")
                        if i == "sidebar":
                            if theme_config["sidebar"]["sidebarCheck"] is False:
                                data = ""
                                theme_config["sidebar"]["template_config"]["sidebarSize"] = "0rem"
                            if showSidebar is False:
                                data = ""
                                theme_config["sidebar"]["template_config"]["sidebarSize"] = "0rem"
                        if theme_config["sidebar"]["position"] == "Right":
                            data = data.replace("<<sidebarPosition>>", "right")
                        else:
                            data = data.replace("<<sidebarPosition>>", "left")

                        if preview is True:
                            new_data = data
                        else:
                            new_data = rwdata.replace("<!--<<" + i + "html>>-->", data)

                        if theme_config["breadcrumbs"]["breadcrumbsCheck"] is False:
                            new_data = new_data.replace("<<breadcrumnbs-css>>", "none")
                        else:
                            new_data = new_data.replace("<<breadcrumnbs-css>>", "flex")

                        if theme_config["tabconfig"]["tabconfigCheck"] is False:
                            new_data = new_data.replace("<<tabconfig-css>>", "none")
                        else:
                            new_data = new_data.replace("<<tabconfig-css>>", "flex")

                        if theme_type == "Section":
                            theme_type = f"Section/{theme_name}"

                        if theme_config["root"].get("favicon"):
                            favicon = theme_config["root"]["favicon"]
                            favicon_extension = favicon.split(".")[-1]
                            check_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/{theme_type}/favicon.{favicon_extension}"
                            if os.path.isfile(check_path):
                                new_data = new_data.replace(
                                    "<<baseFavicon>>",
                                    f"{{{{MEDIA_URL}}}}{tenant}/{app_code}/Themefiles/{theme_type}/favicon.{favicon_extension}",
                                )
                            else:
                                new_data = new_data.replace(
                                    "<<baseFavicon>>", "/static/images/favicons/favicon1.ico"
                                )
                        else:
                            new_data = new_data.replace(
                                "<<baseFavicon>>", "/static/images/favicons/favicon1.ico"
                            )
                        if i == "sidebar":
                            if preview is True:
                                new_data += '<script>$(document).ready(function () { $("body").css("pointer-events", "none");  $("a").css("pointer-events", "none") });</script>'

                            userfield_hover_bg = theme_config["root"]["primaryColor"] + "bf"
                            root_css = f"""\n:root {{\n--primary-color: {theme_config["root"]["primaryColor"]};\n--secondary-color: {theme_config["root"]["secondaryColor"]};\n--userfield-hover-bg: {userfield_hover_bg};\n--font-color: {theme_config["root"]["fontColor"]};\n--font-family: {theme_config["root"]["fontStyle"]};\n--font-size:{theme_config["root"]["fontSize"]+"px"};\n--font-hover-color: {theme_config["root"]["font-hover-color"]};\n--navbar-bg: {theme_config["navbar"]["bgColor"]};\n--navbar-font: {theme_config["navbar"]["fontColorNavbar"]};\n--sidebar-bg: {theme_config["sidebar"]["bgColor"]};\n--sidebar-font: {theme_config["sidebar"]["fontColorSidebar"]};\n--modal-fontColor: {theme_config["modals"]["modalFontColor"]};\n--modal-fontSize: {theme_config["modals"]["fontSize"]+"px;"};\n--modal-fontStyle:{theme_config["modals"]["fontStyle"]};\n--modal-bgColor: {theme_config["modals"]["modalBgColor"]};\n--footer-bg: {theme_config["footer"]["bgColor"]};\n--footer-font: {theme_config["footer"]["fontColorFooter"]};\n--sidebar-size: {theme_config["sidebar"]["template_config"]["sidebarSize"]};"""
                            if "buttons" in theme_config:
                                root_css += f"""\n--buttonBgColor: {theme_config["buttons"]["buttonBgColor"]};\n--buttonFontColor: {theme_config["buttons"]["buttonFontColor"]};\n--buttonShadowColor: {theme_config["buttons"]["buttonShadowColor"]};\n--button_shadow_x: {theme_config["buttons"]["button_shadow_x"]+"px"};\n--button_shadow_y: {theme_config["buttons"]["button_shadow_y"]+"px"};\n--button_blur_radius: {theme_config["buttons"]["button_blur_radius"]+"px"};\n--button_shadow_thickness: {theme_config["buttons"]["button_shadow_thickness"]+"px"};\n--buttonBorderColor: {theme_config["buttons"]["buttonBorderColor"]};\n--buttonBorderThickness: {theme_config["buttons"]["buttonBorderThickness"]+"px"};\n--buttonBorderStyle: {theme_config["buttons"]["buttonBorderStyle"]};\n--buttonBgHoverColor: {theme_config["buttons"]["buttonBgHoverColor"]};\n--buttonFontHoverColor: {theme_config["buttons"]["buttonFontHoverColor"]};"""

                            root_css += f"""}}\n"""
                            new_data = new_data.replace(
                                "<<root_vars>>", f"<style>{root_css}{navbar_sticky}{footer_sticky}</style>"
                            )
                            new_data = new_data.replace(
                                "<<webpage-title>>", theme_config["root"]["webpage-title"]
                            )

                        with open(dest, "w") as wfile:
                            wfile.write(new_data)
            return JsonResponse({"message": "Theme applied successfully!"})

        if request.POST["operation"] == "reset_to_default_theme":
            app_code = request.POST["app_code"]

            base_path = f"{APPS_DIR}/templates/user_defined_template/{tenant}/{app_code}/theme/Global"
            if os.path.exists(base_path):
                shutil.rmtree(base_path)

            media_path = f"{MEDIA_ROOT}/{tenant}/{app_code}/Themefiles/Global"
            if os.path.exists(media_path):
                shutil.rmtree(media_path)

            db_type = ""
            db_connection_name = None
            schema = tenant + "_" + app_code
            if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
                    db_connection_name = json.load(json_file).get(schema)
                    json_file.close()
            user_db_engine, db_type = database_engine_dict[db_connection_name]

            delete_data_func(
                request="",
                config_dict={
                    "inputs": {"Data_source": "Database", "Table": "application_theme"},
                    "condition": [
                        {
                            "column_name": "app_code",
                            "condition": "Equal to",
                            "input_value": app_code,
                            "and_or": "and",
                        },
                        {
                            "column_name": "theme_type",
                            "condition": "Equal to",
                            "input_value": "Global",
                            "and_or": "",
                        },
                    ],
                },
                engine2=user_db_engine,
                db_type=db_type,
                engine_override=True,
            )

            return JsonResponse({"message": "Theme reset to default."})

    context_data = {}
    context_data = getContextData(context_data, tenant)
    context_data.update(getAppList(request, context_data, tenant))

    show_dashboard = "false"
    show_planner = "false"
    tenant_db = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_db = json.load(json_file)
            json_file.close()

    if tenant_db.get(tenant):
        if tenant_db[tenant].get("show_dashboard"):
            show_dashboard = tenant_db[tenant].get("show_dashboard")

        if tenant_db[tenant].get("show_planner"):
            show_planner = tenant_db[tenant].get("show_planner")

    app_db_mapping = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
            app_db_mapping = json.load(json_file)
            json_file.close()

    system_apps = []

    if show_dashboard == "true" and app_db_mapping.get(f"{tenant}_dashboard"):
        system_apps.append("dashboard")
    if show_planner == "true" and app_db_mapping.get(f"{tenant}_planner"):
        system_apps.append("planner")

    context_data["system_apps"] = system_apps

    return render(request, "tenant_admin/customizeTheme.html", context_data, using="light")


@never_cache
def preview_theme(request, app_code, theme_type):
    tenant = tenant_schema_from_request(request, original=True)
    template_name = f"user_defined_template/{tenant}/{app_code}/theme/{theme_type}/preview_tenant.html"
    return render(
        request,
        template_name,
        context={"themesheet_css": "css/Themesheet/" + app_code + "/Global/themesheet.css"},
    )


def fetch_user_server_side(request):
    tenant = tenant_schema_from_request(request, original=True)
    length = int(request.GET["length"])
    if length != -1:
        start = int(request.GET["start"])
    instance = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Instance",
                "Columns": ["id"],
            },
            "condition": [
                {
                    "column_name": "name",
                    "condition": "Equal to",
                    "input_value": tenant,
                    "and_or": "",
                }
            ],
        },
        schema=tenant,
    )
    instance_id = str(instance.id.iloc[0])
    tenant_user_group_details = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "group_details",
                "Columns": ["name"],
            },
            "condition": [
                {
                    "column_name": "instance_id",
                    "condition": "Equal to",
                    "input_value": instance_id,
                    "and_or": "",
                },
            ],
        },
    )

    if not tenant_user_group_details.empty:
        user_group_details_final = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "auth_group",
                    "Columns": ["id", "name"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "IN",
                        "input_value": str(tuple(tenant_user_group_details.name.tolist())).replace(",)", ")"),
                        "and_or": "",
                    }
                ],
            },
        )
    else:
        user_group_details_final = pd.DataFrame(columns=["id", "name"])

    user_group_details_final = pd.merge(user_group_details_final, tenant_user_group_details, how="left")
    User = get_user_model()
    if request.GET["columns[0][search][value]"]:
        users_having_access_to_app = list(
            User.objects.filter(
                djangoQuerySet(instance_id=instance_id)
                & djangoQuerySet(username__icontains=request.GET["columns[0][search][value]"])
            ).values(
                "groups", "id", "username", "first_name", "last_name", "email", "is_active", "is_superuser"
            )
        )
    else:
        users_having_access_to_app = list(
            User.objects.filter(djangoQuerySet(instance_id=instance.id)).values(
                "groups", "id", "username", "first_name", "last_name", "is_active", "email", "is_superuser"
            )
        )

    total_count = len(users_having_access_to_app)
    if total_count:
        if length != -1:
            users_having_access_to_app = users_having_access_to_app[start : start + length]
        else:
            pass

        users_having_access_to_app = pd.DataFrame(users_having_access_to_app)

        if not user_group_details_final.empty:
            user_to_group_mapping = users_having_access_to_app[["groups", "username"]].copy()
            user_to_group_mapping["groups"] = user_to_group_mapping["groups"].map(
                lambda x: user_group_details_final.loc[user_group_details_final["id"] == x, "name"].values[0],
                na_action="ignore",
            )
            user_to_group_mapping = user_to_group_mapping.groupby(["username"]).agg(
                lambda x: [i for i in x.tolist() if not pd.isna(i)]
            )
            user_to_group_mapping = user_to_group_mapping["groups"].to_dict()
        else:
            user_to_group_mapping = {i: [] for i in users_having_access_to_app["username"]}

        users_having_access_to_app.drop_duplicates(subset=["username"], keep="first", inplace=True)

        if not user_group_details_final.empty:
            rawDatanew = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "UserPermission_Master",
                        "Columns": [
                            "usergroup",
                            "app_code",
                            "app_name",
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "usergroup",
                            "condition": "IN",
                            "input_value": user_group_details_final["name"].tolist(),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
            )
        else:
            rawDatanew = pd.DataFrame(columns=["usergroup", "app_code", "app_name"])
        users_having_access_to_app["apps_assigned"] = ""

        def user_role_identifier(user, user_to_group_mapper, admin_perms):
            if user_to_group_mapper.get(user):
                user_groups = user_to_group_mapper[user]
                all_perms = admin_perms[admin_perms["usergroup"].isin(user_groups)]
                if not all_perms.empty:
                    apps_assigned = ", ".join(all_perms["app_name"].unique().tolist())
                else:
                    apps_assigned = "No Apps Assigned"
            else:
                apps_assigned = "No Apps Assigned"
            return apps_assigned

        users_having_access_to_app["apps_assigned"] = users_having_access_to_app["username"].apply(
            lambda x: user_role_identifier(x, user_to_group_mapping, rawDatanew)
        )
        users_having_access_to_app["action"] = ""
        users_having_access_to_app.fillna("", inplace=True)
        user_profile = (
            read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Profile",
                        "Columns": ["user_id", "profile_pic"],
                    },
                    "condition": [
                        {
                            "column_name": "user_id",
                            "condition": "IN",
                            "input_value": users_having_access_to_app["id"].tolist(),
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
            )
            .set_index("user_id")["profile_pic"]
            .to_dict()
        )
        users_having_access_to_app["profile_pic"] = users_having_access_to_app["id"].map(user_profile)
        users_having_access_to_app["profile_pic"].fillna("", inplace=True)
        users_having_access_to_app = users_having_access_to_app.to_dict("records")
    else:
        users_having_access_to_app = []
    context = {
        "draw": request.GET["draw"],
        "recordsTotal": total_count,
        "recordsFiltered": len(users_having_access_to_app),
        "data": users_having_access_to_app,
    }
    return HttpResponse(json.dumps(context), content_type="application/json")


def user_management(request):
    tenant = tenant_schema_from_request(request, original=True)
    instance = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Instance",
                "Columns": ["id"],
            },
            "condition": [
                {
                    "column_name": "name",
                    "condition": "Equal to",
                    "input_value": tenant,
                    "and_or": "",
                }
            ],
        },
        schema=tenant,
    )
    instance_id = str(instance.id.iloc[0])
    if request.method == "POST":
        if request.POST["operation"] == "remove_user_from_tenant":
            User = get_user_model()
            user_id = request.POST["user_id"]
            user = User.objects.get(id=int(user_id), instance_id=instance_id)
            user.delete()
            delete_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "Profile"},
                    "condition": [
                        {
                            "column_name": "user_id",
                            "condition": "Equal to",
                            "input_value": user_id,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
            )
            delete_data_func(
                request,
                {
                    "inputs": {"Data_source": "Database", "Table": "User"},
                    "condition": [
                        {
                            "column_name": "id",
                            "condition": "Equal to",
                            "input_value": user_id,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
            )
            return JsonResponse({"response": "success"})
        if request.POST["operation"] == "user_activation":
            User = get_user_model()
            username = request.POST["username"]
            is_active = request.POST["is_active"]
            if is_active == "true":
                is_active = "t"
            else:
                is_active = "f"
            update_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "User",
                        "Columns": [{"column_name": "is_active", "input_value": is_active, "separator": ""}],
                    },
                    "condition": [
                        {
                            "column_name": "username",
                            "condition": "Equal to",
                            "input_value": username,
                            "and_or": "AND",
                        },
                        {
                            "column_name": "instance_id",
                            "condition": "Equal to",
                            "input_value": instance_id,
                            "and_or": "",
                        },
                    ],
                },
            )
            return JsonResponse({"response": "success"})
        else:
            pass
    else:
        pass


def user_logout(request, id):
    flag = force_logout_user(id, request)
    tenant = tenant_schema_from_request(request, original=True)
    if flag:
        redis_instance.set(tenant + "force_logout" + str(id), "True")
        messages.success(request, "User logged out")
    else:
        messages.add_message(request, messages.INFO, "User isn't logged in")
    return redirect(reverse("tenant_admin:index"))


def force_logout_user(id, request):
    found_delete = False
    for s in Session.objects.filter(expire_date__gte=timezone.now()):
        if str(s.get_decoded().get("_auth_user_id")) == str(id):
            found_delete = True
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
                                "input_value": "Admin",
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "session_id",
                            "condition": "Equal to",
                            "input_value": str(s),
                            "and_or": "",
                        }
                    ],
                },
            )
            s.delete()
    return found_delete
