import glob
import json
import logging
import os

import pandas as pd
import psycopg2

from config.settings.base import PLATFORM_FILE_PATH, central_database_config, env, get_tenants_map

if env("DJANGO_SETTINGS_MODULE", default="local") == "local":
    from config.settings.local import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
else:
    from config.settings.local_http import ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import execute_from_command_line

from .db_centralised_function import postgres_push, read_data_func


def create_new_tenant(request, tenant_name):
    # Add tenant name to the instance model
    instance_data = pd.DataFrame([{"name": tenant_name}, {"name": f"{tenant_name}_admin"}])
    postgres_push(instance_data, "users_instance", "public")
    instance = (
        read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Instance",
                    "Columns": ["name", "id"],
                },
                "condition": [
                    {
                        "column_name": "name",
                        "condition": "IN",
                        "input_value": f"('{tenant_name}', '{tenant_name}_admin')",
                        "and_or": "",
                    }
                ],
            },
            schema="public",
        )
        .set_index("name")
        .to_dict()["id"]
    )
    instance_id = str(instance[tenant_name])
    tenant_instance_id = str(instance[f"{tenant_name}_admin"])

    # Create Tenant admins and default dev users
    default_user_name_1 = f'{env("DJANGO_SUPERUSER_USERNAME", default="revolutio_admin")}.{tenant_name}'
    default_user_name_2 = f"revolutio_admin2.{tenant_name}"
    default_email_id = env("DJANGO_SUPERUSER_EMAIL", default="contact@acies.holdings")
    tenant_admin_user_1 = f"tenant_admin1.{tenant_name}_admin"
    tenant_admin_user_2 = f"tenant_admin2.{tenant_name}_admin"
    default_password = env("DJANGO_SUPERUSER_PASSWORD", default="Revadmin@2023")
    User = get_user_model()
    User.objects.bulk_create(
        [
            User(
                username=tenant_admin_user_1,
                email=default_email_id,
                password=make_password(default_password),
                is_staff=True,
                is_active=True,
                is_superuser=True,
                role="Tenant Admin",
                instance_id=tenant_instance_id,
            ),
            User(
                username=tenant_admin_user_2,
                email=default_email_id,
                password=make_password(default_password),
                is_staff=True,
                is_active=True,
                is_superuser=True,
                role="Tenant Admin",
                instance_id=tenant_instance_id,
            ),
            User(
                username=default_user_name_1,
                email=default_email_id,
                password=make_password(default_password),
                is_staff=True,
                is_active=True,
                is_superuser=True,
                role="Developer",
                instance_id=instance_id,
            ),
            User(
                username=default_user_name_2,
                email=default_email_id,
                password=make_password(default_password),
                is_staff=True,
                is_active=True,
                is_superuser=True,
                role="Developer",
                instance_id=instance_id,
            ),
        ]
    )

    # Add the identifiers & host in the config files
    added_host, added_csrf_origin = add_tenant_info(tenant_name)
    return added_host, added_csrf_origin


def add_tenant_info(tenant):
    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json1_file:
            tenant_data = json.load(json1_file)
            json1_file.close()
    domain_name = env("PLATFORM_DOMAIN_NAME", default="revolutio.digital")
    environment = env("KUBERNETES_ENV", default="true")
    if environment == "true":
        scheme = "https://"
    else:
        scheme = "http://"

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
            "lowercaseLetter": "false",
            "symbols": "false",
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

    allowed_domains = []
    if os.path.exists(f"{PLATFORM_FILE_PATH}allowed_domains.json"):
        with open(f"{PLATFORM_FILE_PATH}allowed_domains.json") as json_file:
            allowed_domains = json.load(json_file)
            json_file.close()
    allowed_domains.append(f"{scheme}{tenant}.{domain_name}")
    with open(f"{PLATFORM_FILE_PATH}allowed_domains.json", "w") as outfile:
        json.dump(allowed_domains, outfile)
        outfile.close()

    global ALLOWED_HOSTS
    ALLOWED_HOSTS += [f"{tenant}.{domain_name}"]
    global CSRF_TRUSTED_ORIGINS
    CSRF_TRUSTED_ORIGINS += [f"{scheme}{tenant}.{domain_name}"]
    return (f"{tenant}.{domain_name}", f"{scheme}{tenant}.{domain_name}")


def migrate_tenant(schema):
    migration_arguements = ["manage.py", "migrate"]
    execute_from_command_line(migration_arguements)
    return True


def migrate_all_tenants():
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


def run_custom_command(command, mode="user", role="User"):
    if command:
        from kore_investment.users.models import Instance

        tenant_object = Instance.objects.get(name=command)
        User = get_user_model()
        is_developer = False

        if command not in ["public", "platform_admin"]:
            if mode == "user":
                first_username = f'{env("DJANGO_SUPERUSER_USERNAME", default="revolutio_admin")}.{command}'
                second_username = f"revolutio_admin2.{command}"
                is_developer = True
            elif mode == "tenant_admin":
                first_username = f"tenant_admin1.{command}"
                second_username = f"tenant_admin2.{command}"
            else:
                first_username = f"platform_admin1"
                second_username = f"platform_admin2"
        else:
            if mode == "user":
                first_username = f'{env("DJANGO_SUPERUSER_USERNAME", default="revolutio_admin")}'
                second_username = f"revolutio_admin2"
                is_developer = True
            elif mode == "tenant_admin":
                first_username = f"tenant_admin1"
                second_username = f"tenant_admin2"
            else:
                first_username = f"platform_admin1"
                second_username = f"platform_admin2"

        User.objects.create_user(
            username=first_username,
            email=env("DJANGO_SUPERUSER_EMAIL", default="contact@acies.holdings"),
            password=env("DJANGO_SUPERUSER_PASSWORD", default="Revadmin@2023"),
            is_staff=True,
            is_active=True,
            is_superuser=True,
            is_developer=is_developer,
            instance=tenant_object,
            role=role,
        )
        User.objects.create_user(
            username=second_username,
            email=env("DJANGO_SUPERUSER_EMAIL", default="contact@acies.holdings"),
            password=env("DJANGO_SUPERUSER_PASSWORD", default="Revadmin@2023"),
            is_staff=True,
            is_active=True,
            is_superuser=True,
            is_developer=is_developer,
            instance=tenant_object,
            role=role,
        )
    else:
        logging.error("No Custom Command Passed")
    return True
