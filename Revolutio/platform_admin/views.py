from datetime import datetime, timedelta
import json
import os
import re

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from config.settings.base import PLATFORM_FILE_PATH, redis_instance
from kore_investment.users.queue_manager import enqueue_jobs
from platform_admin.db_centralised_function import read_data_func
from platform_admin.utilities import run_tenant_deletion_command, tenant_schema_from_request

from .Tenant_Management import create_new_tenant, migrate_all_tenants


# Create your views here.
@never_cache
def index(request):
    if request.method == "POST":
        if request.POST["operation"] == "create_tenant":
            tenant = request.POST["tenant_name"]
            if not re.fullmatch("^[a-z0-9][a-z0-9_-]*$", tenant) and "admin" not in tenant:
                return JsonResponse(
                    {
                        "response": "Failed",
                        "message": "Error! Special Characters or spaces are not allowed. Tenant name can only contain lower case letters and numbers.",
                    }
                )
            tenant_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json1_file:
                    tenant_data = json.load(json1_file)
                    json1_file.close()
            if tenant in tenant_data:
                return JsonResponse({"response": "Failed", "message": "Failed! Tenant already exists."})
            create_new_tenant(request, tenant)
            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "delete_tenant":
            tenant = request.POST["tenant_name"]
            tenant_job = "tenant_deletion_" + str(tenant)
            enqueue_jobs(
                run_tenant_deletion_command,
                tenant_job,
                args=(),
                kwargs={
                    "command": tenant,
                },
                job_type="tenant",
                retry=1,
                description=f"Delete tenant - {tenant}",
            )
            return JsonResponse({"response": "success", "job_id": tenant_job})

        if request.POST["operation"] == "migrateCentralDB":
            tenant = tenant_schema_from_request(request)
            job_id = "Tenant_DB_migration_" + str(tenant)
            enqueue_jobs(
                migrate_all_tenants,
                job_id,
                args=(),
                kwargs={},
                job_type="tenant",
                description=f"Central database migration for all schemas",
            )
            return JsonResponse({"response": "success", "job_id": job_id})

        if request.POST["operation"] == "create_su_user":
            username = request.POST["username"].lower()
            tenant = request.POST["tenant"] + "_admin"
            password = request.POST["password"]
            email = request.POST["email"]
            if tenant != "public":
                username += f".{tenant}"
            else:
                pass
            User = get_user_model()
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
                is_superuser=True,
                is_developer=False,
                role="Tenant Admin",
                instance_id=instance_id,
            )
            return JsonResponse({"response": "success"})

        if request.POST["operation"] == "reactivate_tenant":
            tenant_name = request.POST["tenant_name"]
            deactivated_tenant_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}deactivated_tenants.json"):
                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json") as json1_file:
                    deactivated_tenant_data = json.load(json1_file)
                    json1_file.close()

                if tenant_name in deactivated_tenant_data:
                    del deactivated_tenant_data[tenant_name]

                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json", "w") as json1_file:
                    json.dump(deactivated_tenant_data, json1_file, indent=4, default=str)
                    json1_file.close()

            return JsonResponse({"response": "Tenant reactivated successfully!"})

        if request.POST["operation"] == "deactivate_tenant":
            tenant_name = request.POST["tenant_name"]
            reactivate_option = request.POST["reactivate_option"]
            reactivation_days = request.POST["reactivation_days"]
            reactivation_hours = request.POST["reactivation_hours"]
            reactivation_minutes = request.POST["reactivation_minutes"]

            deactivated_tenant_data = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}deactivated_tenants.json"):
                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json") as json1_file:
                    deactivated_tenant_data = json.load(json1_file)
                    json1_file.close()

                if tenant_name in deactivated_tenant_data:
                    deactivated_tenant_data[tenant_name]["reactivate_option"] = reactivate_option
                    deactivated_tenant_data[tenant_name]["reactivation_days"] = reactivation_days
                    deactivated_tenant_data[tenant_name]["reactivation_hours"] = reactivation_hours
                    deactivated_tenant_data[tenant_name]["reactivation_minutes"] = reactivation_minutes
                    deactivated_tenant_data[tenant_name]["deactivated_time"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                else:
                    deactivated_tenant_data[tenant_name] = {
                        "reactivate_option": reactivate_option,
                        "reactivation_days": reactivation_days,
                        "reactivation_hours": reactivation_hours,
                        "reactivation_minutes": reactivation_minutes,
                        "deactivated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json", "w") as json1_file:
                    json.dump(deactivated_tenant_data, json1_file, indent=4, default=str)
                    json1_file.close()

            else:
                deactivated_tenant_data = {
                    tenant_name: {
                        "reactivate_option": reactivate_option,
                        "reactivation_days": reactivation_days,
                        "reactivation_hours": reactivation_hours,
                        "reactivation_minutes": reactivation_minutes,
                        "deactivated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                }
                with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json", "w") as json1_file:
                    json.dump(deactivated_tenant_data, json1_file, indent=4, default=str)
                    json1_file.close()

            for s in Session.objects.all():
                if s.get_decoded().get("_auth_user_id"):
                    redis_instance.set(
                        tenant_name + "deactivate_user" + str(s.get_decoded().get("_auth_user_id")), "True"
                    )
                    s.delete()

            return JsonResponse({"response": "Tenant deactivated successfully!"})

    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json1_file:
            tenant_data = json.load(json1_file)
            json1_file.close()
    tenant_names = [name for name in list(tenant_data.keys())]

    deactivated_tenants = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}deactivated_tenants.json"):
        with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json") as json1_file:
            deactivated_tenants = json.load(json1_file)
            json1_file.close()

    tenants_reactivate = {}
    temp = []
    for tenant, values in deactivated_tenants.items():
        reactivation_time = ""
        if values["reactivate_option"] == "custom":
            reactivation_days = values["reactivation_days"]
            reactivation_hours = values["reactivation_hours"]
            reactivation_minutes = values["reactivation_minutes"]
            deactivated_time = values["deactivated_time"]
            deactivated_time = datetime.strptime(deactivated_time, "%Y-%m-%d %H:%M:%S")

            reactivation_time = deactivated_time + timedelta(
                days=int(reactivation_days), hours=int(reactivation_hours), minutes=int(reactivation_minutes)
            )

            if datetime.now() >= reactivation_time:
                temp.append(tenant)
                tenants_reactivate[tenant] = ""
            else:
                tenants_reactivate[tenant] = reactivation_time.strftime("%Y-%m-%d %H:%M:%S")

        else:
            tenants_reactivate[tenant] = ""
    for name in temp:
        del deactivated_tenants[name]
        with open(f"{PLATFORM_FILE_PATH}deactivated_tenants.json", "w") as json1_file:
            json.dump(deactivated_tenants, json1_file, indent=4, default=str)
            json1_file.close()

    active_tenants = [name for name in tenant_data if name not in list(deactivated_tenants.keys())]

    return render(
        request,
        "platform_admin/index.html",
        {
            "tenant_names": tenant_names,
            "active_tenants": active_tenants,
            "deactivated_tenants": list(deactivated_tenants.keys()),
            "tenants_reactivate": tenants_reactivate,
        },
        using="light",
    )


def redirect_index(request):
    return redirect("/platform_admin/")
