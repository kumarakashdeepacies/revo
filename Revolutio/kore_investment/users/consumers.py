import asyncio
from datetime import datetime
import json
import os
import pickle

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.utils import timezone
import pandas as pd
from rq.command import send_shutdown_command
from rq.job import Job
from rq.registry import StartedJobRegistry
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from config.settings.base import PLATFORM_FILE_PATH, redis_instance
from kore_investment.users.computations.db_centralised_function import (
    current_app_db_extractor_url,
    read_data_func,
)
from kore_investment.users.computations.file_storage import (
    file_storage_checker,
    flush_diskstorage,
    read_computation_from_storage,
)


def tenant_extractor_from_host(hostname):
    tenants_map = {}
    with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
        tenants_map = json.load(json_file)
        json_file.close()
    if tenants_map.get(hostname):
        schema = tenants_map.get(hostname)
    else:
        schema = "public"
    return schema


def origin_validator(origin):
    if origin not in ["http://127.0.0.1:8080", "http://localhost:8080"]:
        allowed_origins = []
        with open(f"{PLATFORM_FILE_PATH}allowed_domains.json") as json_file:
            allowed_origins = json.load(json_file)
            json_file.close()
        if origin in allowed_origins:
            return True
        else:
            return False
    else:
        return True


@sync_to_async
def get_user_from_session(session_id, hostname):
    User = get_user_model()
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_object = ""
    for session in sessions:  # iterate over sessions
        if session_id == session.session_key:
            user_id = session.get_decoded().get("_auth_user_id")
            user_object = User.objects.get(id=int(user_id))
            break
        else:
            continue
    if user_object == "":
        return AnonymousUser()
    return user_object


class run_process_multi_run(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()

    async def receive_json(self, content):
        url_string = content["path"]
        session_id = self.scope["cookies"]["sessionid"]
        headers = {"host": str(v, "utf-8") for i, v in self.scope["headers"] if i == b"host"}
        hostname = headers["host"]
        hostname = hostname.split(":")[0].lower()
        user_object = await get_user_from_session(session_id, hostname)
        if user_object.username != "AnonymousUser":
            tenant = tenant_extractor_from_host(hostname)
            curr_app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
            model_name = self.scope["url_route"]["kwargs"]["model_name"]
            run_check = True
            while run_check:
                await asyncio.sleep(0.3)
                ind_output = read_computation_from_storage(db_connection_name + f"run_process_{model_name}")
                if type(ind_output) != type(None):
                    ind_output = json.loads(ind_output)
                    main_comp_per = ind_output["main_comp_per"]
                    if main_comp_per == 100:
                        run_check = False
                    flush_diskstorage(db_connection_name + f"run_process_{model_name}")
                    await self.send_json(ind_output)
                else:
                    continue
        else:
            await self.close()


class run_process_multi_run_inter(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()

    async def receive_json(self, content):
        url_string = content["path"]
        session_id = self.scope["cookies"]["sessionid"]
        headers = {"host": str(v, "utf-8") for i, v in self.scope["headers"] if i == b"host"}
        hostname = headers["host"]
        hostname = hostname.split(":")[0].lower()
        user_object = await get_user_from_session(session_id, hostname)
        if user_object.username != "AnonymousUser":
            tenant = tenant_extractor_from_host(hostname)
            curr_app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
            model_name = self.scope["url_route"]["kwargs"]["model_name"]
            multi_run_config = pickle.loads(
                redis_instance.get(db_connection_name + f"multi_run_config_{model_name}")
            )
            global_dict = multi_run_config["global_dict"]
            multi_run_vars = global_dict["inputs"].get("multi_run_vars")
            multi_run_vars_length = [
                len(var["defaultValue"])
                for var in global_dict["inputs"]["variables"]
                if var["varName"] in multi_run_vars
            ]
            len_multi_runs = max(multi_run_vars_length)
            check = True
            while check:
                await asyncio.sleep(0.2)
                intermediate_run_config = read_computation_from_storage(
                    db_connection_name + f"intermediate_multi_run_process_{model_name}"
                )
                if type(intermediate_run_config) != type(None):
                    current_element_name = intermediate_run_config["current_element"]
                    next_element_name = intermediate_run_config["next_element"]
                    completed_percent = intermediate_run_config["inter_comp_per"]
                    inter_message = intermediate_run_config["element_message"]
                    run_inter = intermediate_run_config["run"]
                    inter_output_export_message_list = intermediate_run_config[
                        "inter_output_export_message_list"
                    ]
                    if inter_message == "Success":
                        message = (
                            "Iteration "
                            + str(run_inter + 1)
                            + " - Successfully ran "
                            + current_element_name
                            + ", now running "
                            + next_element_name
                            + "..."
                        )
                    else:
                        message = (
                            "Error" + current_element_name + ", now running " + next_element_name + "..."
                        )
                    comp_per = 100 * (run_inter) / len_multi_runs
                    inter_comp_per = 100 / len_multi_runs
                    req_comp_per = (inter_comp_per * completed_percent) + comp_per
                    inter_output = {
                        "message": message,
                        "comp_per": req_comp_per,
                        "inter_output_export_message_list": inter_output_export_message_list,
                    }
                    await self.send_json(inter_output)
                    if comp_per == 100:
                        check = False
                        await self.close()
                    flush_diskstorage(db_connection_name + f"intermediate_multi_run_process_{model_name}")
            else:
                await self.close()
        else:
            await self.close()


class run_model_multi_run(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()

    async def receive_json(self, content):
        url_string = content["path"]
        session_id = self.scope["cookies"]["sessionid"]
        headers = {"host": str(v, "utf-8") for i, v in self.scope["headers"] if i == b"host"}
        hostname = headers["host"]
        hostname = hostname.split(":")[0].lower()
        user_object = await get_user_from_session(session_id, hostname)
        if user_object.username != "AnonymousUser":
            tenant = tenant_extractor_from_host(hostname)
            curr_app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
            model_name = self.scope["url_route"]["kwargs"]["model_name"]
            run_check = True
            while run_check:
                await asyncio.sleep(0.3)
                ind_output = read_computation_from_storage(db_connection_name + f"run_model_{model_name}")
                if type(ind_output) != type(None):
                    ind_output = json.loads(ind_output)
                    main_comp_per = ind_output["main_comp_per"]
                    if main_comp_per == 100:
                        run_check = False
                    flush_diskstorage(db_connection_name + f"run_model_{model_name}")
                    await self.send_json(ind_output)
                else:
                    continue
        else:
            await self.close()


class run_model_multi_run_inter(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()

    async def receive_json(self, content):
        url_string = content["path"]
        session_id = self.scope["cookies"]["sessionid"]
        headers = {"host": str(v, "utf-8") for i, v in self.scope["headers"] if i == b"host"}
        hostname = headers["host"]
        hostname = hostname.split(":")[0].lower()
        user_object = await get_user_from_session(session_id, hostname)
        if user_object.username != "AnonymousUser":
            tenant = tenant_extractor_from_host(hostname)
            curr_app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
            model_name = self.scope["url_route"]["kwargs"]["model_name"]
            multi_run_config = pickle.loads(
                redis_instance.get(db_connection_name + f"multi_run_config_run_model_{model_name}")
            )
            global_dict = multi_run_config["global_dict"]
            multi_run_vars = global_dict["inputs"].get("multi_run_vars")
            multi_run_vars_length = [
                len(var["defaultValue"])
                for var in global_dict["inputs"]["variables"]
                if var["varName"] in multi_run_vars
            ]
            len_multi_runs = max(multi_run_vars_length)
            check = True
            while check:
                await asyncio.sleep(0.2)
                intermediate_run_config = read_computation_from_storage(
                    db_connection_name + f"intermediate_multi_run_model_{model_name}"
                )
                if type(intermediate_run_config) != type(None):
                    current_element_name = intermediate_run_config["current_element"]
                    next_element_name = intermediate_run_config["next_element"]
                    completed_percent = intermediate_run_config["inter_comp_per"]
                    inter_message = intermediate_run_config["element_message"]
                    inter_output_export_message_list = intermediate_run_config[
                        "inter_output_export_message_list"
                    ]
                    run_inter = intermediate_run_config["run"]
                    if inter_message == "Success":
                        message = (
                            "Iteration "
                            + str(run_inter + 1)
                            + " - Successfully ran "
                            + current_element_name
                            + ", now running "
                            + next_element_name
                            + "..."
                        )
                    else:
                        message = (
                            "Error" + current_element_name + ", now running " + next_element_name + "..."
                        )
                    comp_per = 100 * (run_inter) / len_multi_runs
                    inter_comp_per = 100 / len_multi_runs
                    req_comp_per = (inter_comp_per * completed_percent) + comp_per
                    inter_output = {
                        "message": message,
                        "comp_per": req_comp_per,
                        "inter_output_export_message_list": inter_output_export_message_list,
                    }
                    if comp_per == 100:
                        check = False
                    flush_diskstorage(db_connection_name + f"intermediate_multi_run_model_{model_name}")
                    await self.send_json(inter_output)
        else:
            await self.close()


class queued_job_output(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()
            rounding_conv = 4
            job_id = self.scope["url_route"]["kwargs"]["job_id"]
            job = Job.fetch(job_id, connection=redis_instance)
            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                await asyncio.sleep(0.1)
            else:
                context = {}
                context["status"] = job.get_status()
                if job.get_status() == "finished":
                    if not job_id.startswith("Run_Process_") and not job_id.startswith("Run_Model_"):
                        output, message, result_save_list, data_error = job.result
                        context["message"] = message
                        context["result_save"] = result_save_list
                        if job.kwargs.get("multi_import"):
                            multi_import = job.kwargs["multi_import"]
                        else:
                            multi_import = False
                        if message != "If Then Else" and data_error != "If Then Else":
                            context["elementid"] = job.kwargs["elementid"]
                            if len(data_error) == 0:
                                if (
                                    type(output) == str
                                    and output == context["elementid"]
                                    and file_storage_checker(output)
                                    and not multi_import
                                ):
                                    output = read_computation_from_storage(output, num_rows=100)
                                elif multi_import:
                                    eleId_list = job.kwargs["data"]
                                    op_list = {}
                                    for ele_k in eleId_list:
                                        df_remote = read_computation_from_storage(ele_k, num_rows=100)
                                        if isinstance(df_remote, pd.DataFrame):
                                            df_remote = df_remote.iloc[:, :150]
                                            for col in df_remote.columns:
                                                if df_remote[col].dtypes.name == "datetime64[ns]":
                                                    df_remote[col] = df_remote[col].dt.strftime(
                                                        "%Y-%m-%d %H:%M:%S"
                                                    )
                                                else:
                                                    if df_remote[col].dtypes.name in [
                                                        "float",
                                                        "float64",
                                                        "float32",
                                                    ]:
                                                        df_remote[col] = df_remote[col].round(rounding_conv)
                                            df_remote = df_remote.fillna("-").astype("str").to_dict("records")
                                        op_list[ele_k] = df_remote
                                    output = op_list
                                    context["multi_import"] = True
                                else:
                                    pass
                                if isinstance(output, pd.DataFrame):
                                    output = output.iloc[:, :150]
                                    for col in output.columns:
                                        if output[col].dtypes.name == "datetime64[ns]":
                                            output[col] = output[col].dt.strftime("%Y-%m-%d %H:%M:%S")
                                        else:
                                            if output[col].dtypes.name in ["float", "float64", "float32"]:
                                                output[col] = output[col].round(rounding_conv)
                                    output = output.fillna("-").astype("str").to_dict("records")
                                elif isinstance(output, dict):
                                    for key, value in output.items():
                                        if isinstance(value, pd.DataFrame):
                                            value = value.iloc[:, :150].head(100)
                                            for col in value.columns:
                                                if value[col].dtypes.name == "datetime64[ns]":
                                                    value[col] = value[col].dt.strftime("%Y-%m-%d %H:%M:%S")
                                                else:
                                                    if value[col].dtypes.name in [
                                                        "float",
                                                        "float64",
                                                        "float32",
                                                    ]:
                                                        value[col] = value[col].round(rounding_conv)
                                            output[key] = value.fillna("-").astype("str").to_dict("records")
                                        elif isinstance(value, datetime):
                                            output[key] = str(value)

                                context["content"] = output
                            else:
                                if isinstance(data_error, list):
                                    context["result_save"] = data_error
                                else:
                                    context["result_save"] = [data_error]
                        else:
                            for key, value in output.items():
                                value["data"] = value["data"].iloc[:, :150].head(100)
                                for col in value["data"].columns:
                                    if value["data"][col].dtypes.name == "datetime64[ns]":
                                        value["data"][col] = value["data"][col].dt.strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        )
                                    else:
                                        if value["data"][col].dtypes.name in ["float", "float64", "float32"]:
                                            value["data"][col] = value["data"][col].round(rounding_conv)
                                output[key]["data"] = (
                                    value["data"].fillna("-").astype("str").to_dict("records")
                                )
                            context["content"] = output
                    else:
                        context = job.result
                        if job_id.startswith("Run_Process_"):
                            if "output_display_type" in context:
                                if context["output_display_type"] == "individual":
                                    if "content" in context.keys():
                                        if isinstance(context["content"], pd.DataFrame):
                                            context["content"] = context["content"].iloc[:, :150].head(100)
                                            for col in context["content"].columns:
                                                if context["content"][col].dtypes.name == "datetime64[ns]":
                                                    context["content"][col] = context["content"][
                                                        col
                                                    ].dt.strftime("%Y-%m-%d %H:%M:%S")
                                                else:
                                                    if context["content"][col].dtypes.name in [
                                                        "float",
                                                        "float64",
                                                        "float32",
                                                    ]:
                                                        context["content"][col] = context["content"][
                                                            col
                                                        ].round(rounding_conv)
                                            context["content"] = (
                                                context["content"]
                                                .fillna("-")
                                                .astype("str")
                                                .to_dict("records")
                                            )
                                else:
                                    for con_ele in range(len(context["output_elements"])):
                                        if isinstance(
                                            context["output_elements"][con_ele]["content"], pd.DataFrame
                                        ):
                                            context["output_elements"][con_ele]["content"] = (
                                                context["output_elements"][con_ele]["content"]
                                                .iloc[:, :150]
                                                .head(100)
                                            )
                                            for col in context["output_elements"][con_ele]["content"].columns:
                                                if (
                                                    context["output_elements"][con_ele]["content"][
                                                        col
                                                    ].dtypes.name
                                                    == "datetime64[ns]"
                                                ):
                                                    context["output_elements"][con_ele]["content"][
                                                        col
                                                    ] = context["output_elements"][con_ele]["content"][
                                                        col
                                                    ].dt.strftime(
                                                        "%Y-%m-%d %H:%M:%S"
                                                    )
                                                else:
                                                    if context["output_elements"][con_ele]["content"][
                                                        col
                                                    ].dtypes.name in ["float", "float64", "float32"]:
                                                        context["output_elements"][con_ele]["content"][
                                                            col
                                                        ] = context["output_elements"][con_ele]["content"][
                                                            col
                                                        ].round(
                                                            rounding_conv
                                                        )
                                            context["output_elements"][con_ele]["content"] = (
                                                context["output_elements"][con_ele]["content"]
                                                .fillna("-")
                                                .astype("str")
                                                .to_dict("records")
                                            )
                else:
                    pass
                await self.send_json(context)


class queued_upload_output(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()
            job_id = self.scope["url_route"]["kwargs"]["job_id"]
            job = Job.fetch(job_id, connection=redis_instance)
            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                await asyncio.sleep(0.1)
            else:
                context = {}
                context["status"] = job.get_status()
                if job.get_status() == "finished":
                    context["message"] = "done"
                else:
                    pass
                await self.send_json(context)


class queued_audit_filter_output(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()
            job_id = self.scope["url_route"]["kwargs"]["job_id"]
            job = Job.fetch(job_id, connection=redis_instance)
            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                await asyncio.sleep(0.1)
            else:
                context = {}
                context["status"] = job.get_status()
                if job.get_status() == "finished":
                    output = job.result
                    if output is not None:
                        context["content"] = output
                        context["message"] = "done"
                    else:
                        context["message"] = "error"
                else:
                    context["message"] = "error"
                await self.send_json(context)


class queued_navbar_job_output(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()

    async def receive_json(self, content):
        url_string = content["path"]
        session_id = self.scope["cookies"]["sessionid"]
        headers = {"host": str(v, "utf-8") for i, v in self.scope["headers"] if i == b"host"}
        hostname = headers["host"]
        hostname = hostname.split(":")[0].lower()
        user_object = await get_user_from_session(session_id, hostname)
        if user_object.username != "AnonymousUser":
            tenant = tenant_extractor_from_host(hostname)
            count = 0
            connection_open = True
            current_user = user_object.username
            request_user_group = await get_user_groups(user_object)
            new_session_id = self.scope["cookies"]["sessionid"]
            notification_sent = []
            notification_list = read_data_func(
                "",
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "notification_management",
                        "Order_Type": "ORDER BY created_date DESC",
                        "Columns": ["id", "notification_message", "created_date", "status"],
                    },
                    "condition": [
                        {
                            "column_name": "user_name",
                            "condition": "Equal to",
                            "input_value": current_user,
                            "and_or": "and",
                        },
                        {
                            "column_name": "status",
                            "condition": "Equal to",
                            "input_value": "unread",
                            "and_or": "",
                        },
                    ],
                },
                schema=tenant,
            )

            notification_list = notification_list.to_dict("records")

            limit_notification = 5
            tenant_data = {}
            context = {}
            if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
                with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
                    tenant_data = json.load(json_file)
                    json_file.close()

                if tenant in tenant_data:
                    if "limit_notification" in tenant_data[tenant]:
                        limit_notification = tenant_data[tenant]["limit_notification"]
                else:
                    pass

            show_notifications = notification_list
            other_notifications = []

            if len(notification_list) > int(limit_notification):
                show_notifications = notification_list[: int(limit_notification)]
                other_notifications = notification_list[int(limit_notification) :]

            context["show_notifications"] = json.dumps(show_notifications, default=str)
            context["other_notifications"] = json.dumps(other_notifications, default=str)

            try:
                await self.send_json(context)
            except (ConnectionClosedOK, ConnectionClosedError):
                connection_open = False
                await self.close()
            while connection_open:
                registry = StartedJobRegistry("default", connection=redis_instance)
                navbar_registry = StartedJobRegistry("navbar_queue", connection=redis_instance)
                running_job_ids = registry.get_job_ids()  # Jobs which are exactly running.
                running_navbar_job_ids = navbar_registry.get_job_ids()  # Jobs which are exactly running.
                all_jobs = [*list(running_job_ids), *list(running_navbar_job_ids)]
                if len(all_jobs) > 0:
                    for job_id in all_jobs:
                        if job_id.startswith("nav_update_"):
                            job = Job.fetch(job_id, connection=redis_instance)
                            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                                await asyncio.sleep(0.1)
                            else:
                                if job.get_status() == "finished":
                                    stats, user_name, requested_user_name, tenant_name, notification_id = (
                                        job.result
                                    )
                                    if (
                                        current_user == requested_user_name or current_user == user_name
                                    ) and (tenant == tenant_name):
                                        context = {}
                                        context["status"] = job.get_status()
                                        context["username"] = user_name
                                        context["operation"] = "navbar_message"
                                        context["notification_id"] = notification_id
                                        context["stats"] = stats
                                        try:
                                            if connection_open:
                                                await self.send_json(context)
                                        except (ConnectionClosedOK, ConnectionClosedError):
                                            connection_open = False
                                            await self.close()
                                            break
                                    else:
                                        pass
                                else:
                                    pass

                        elif job_id.startswith("htmlGenerateAll"):
                            job = Job.fetch(job_id, connection=redis_instance)
                            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                                await asyncio.sleep(0.1)
                            else:
                                if job.get_status() == "finished":
                                    stats, curr_user, subprocess_name, tenant_name, notification_id = (
                                        job.result
                                    )
                                    if (curr_user == current_user) and (tenant == tenant_name):
                                        context = {"status": "finished"}
                                        context["notification_id"] = notification_id
                                        context["operation"] = "html"
                                        context["username"] = current_user
                                        context["subprocess_name"] = subprocess_name
                                        context["stats"] = stats
                                        try:
                                            if connection_open:
                                                await self.send_json(context)
                                        except (ConnectionClosedOK, ConnectionClosedError):
                                            connection_open = False
                                            await self.close()
                                            break
                                    else:
                                        pass
                                else:
                                    pass
                        else:
                            continue
                else:
                    pass

                alerts_registry = StartedJobRegistry("alerts_queue", connection=redis_instance)
                running_alert_job_ids = alerts_registry.get_job_ids()  # Jobs which are exactly running.
                if len(running_alert_job_ids) > 0:
                    for job_id in running_job_ids:
                        if job_id not in notification_sent:
                            job = Job.fetch(job_id, connection=redis_instance)
                            if job.get_status() == "finished":
                                alert_data = job.result
                                (
                                    user_name,
                                    group_list,
                                    tenant_name,
                                    alert_message,
                                    alert_owner,
                                    alert_exclude_user,
                                ) = alert_data
                                request_user_group = [x for x in request_user_group if x in group_list]
                                if request_user_group and alert_message != "":
                                    if alert_owner != "admin":
                                        if (
                                            current_user == alert_owner
                                            and set(request_user_group).issubset(group_list)
                                            and (tenant == tenant_name)
                                        ):
                                            context = {}
                                            context["status"] = job.get_status()
                                            context["username"] = user_name
                                            context["alert_message"] = alert_message
                                            context["operation"] = "alert_message"
                                            try:
                                                if connection_open:
                                                    notification_sent.append(job_id)
                                                    await self.send_json(context)
                                            except (ConnectionClosedOK, ConnectionClosedError):
                                                connection_open = False
                                                await self.close()
                                                break
                                        else:
                                            continue
                                    else:
                                        if (
                                            set(request_user_group).issubset(group_list)
                                            and (tenant == tenant_name)
                                            and current_user not in alert_exclude_user
                                        ):
                                            context = {}
                                            context["status"] = job.get_status()
                                            context["username"] = user_name
                                            context["alert_message"] = alert_message
                                            context["operation"] = "alert_message"
                                            try:
                                                if connection_open:
                                                    notification_sent.append(job_id)
                                                    await self.send_json(context)
                                            except (ConnectionClosedOK, ConnectionClosedError):
                                                connection_open = False
                                                await self.close()
                                                break
                                        else:
                                            continue
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                else:
                    pass

                if redis_instance.exists(f"DB_health_check_{tenant}") == 1:
                    if count:
                        await asyncio.sleep(10)
                    con_db_status = redis_instance.get(f"DB_health_check_{tenant}")
                    con_db_status = pickle.loads(con_db_status)
                    curr_app_code, db_connection_name = current_app_db_extractor_url(url_string, tenant)
                    current_db = "No application selected"
                    if curr_app_code and db_connection_name:
                        if con_db_status.get(db_connection_name):
                            current_db = con_db_status[db_connection_name]
                    un_healthy_count = [k for k, v in con_db_status.items() if v != "Healthy"]
                    db_status = {}
                    db_status["operation"] = "db_health"
                    db_status["con_db_status"] = con_db_status
                    db_status["current_db"] = current_db
                    db_status["un_healthy_count"] = un_healthy_count
                    count += 1
                    try:
                        if connection_open:
                            await self.send_json(db_status)
                    except (ConnectionClosedOK, ConnectionClosedError):
                        connection_open = False
                        await self.close()
                        break
                else:
                    pass

                if redis_instance.exists(f"Unapplied_migration_checker-{tenant}") == 1:
                    Unapplied_migration_list = redis_instance.get(f"Unapplied_migration_checker-{tenant}")
                    Unapplied_migration_list = pickle.loads(Unapplied_migration_list)
                    if Unapplied_migration_list:
                        try:
                            if connection_open:
                                context = {"unapplied_migration": "true", "operation": "migration_checker"}
                                await self.send_json(context)
                        except (ConnectionClosedOK, ConnectionClosedError):
                            connection_open = False
                            await self.close()
                            break
                    else:
                        pass
                else:
                    pass

                if redis_instance.exists(tenant + "mulsession" + user_object.username) == 1:
                    user_login_info = pickle.loads(
                        redis_instance.get(tenant + "mulsession" + user_object.username)
                    )
                    old_session_id = user_login_info["session_key"]
                    if old_session_id == new_session_id:
                        context = {"operation": "concurrent_session_breach"}
                        context["delete"] = "yes"
                        context["ip"] = user_login_info["ip"]
                        try:
                            if connection_open:
                                await self.send_json(context)
                            else:
                                break
                        except (ConnectionClosedOK, ConnectionClosedError):
                            connection_open = False
                            await self.close()
                            break
                    else:
                        pass
                else:
                    pass

                if redis_instance.exists(tenant + "force_logout" + str(self.scope["user"].id)) == 1:
                    context = {"operation": "force_logout_user"}
                    context["logout"] = "yes"
                    try:
                        if connection_open:
                            await self.send_json(context)
                        else:
                            break
                    except (ConnectionClosedOK, ConnectionClosedError):
                        connection_open = False
                        await self.close()
                        break
                else:
                    pass

                if redis_instance.exists(tenant + "deactivate_user" + str(user_object.id)) == 1:
                    context = {"operation": "deactivate_logout_user"}
                    context["logout"] = "yes"
                    redis_instance.delete(tenant + "deactivate_user" + str(user_object.id))
                    try:
                        if connection_open:
                            await self.send_json(context)
                        else:
                            break
                    except (ConnectionClosedOK, ConnectionClosedError):
                        connection_open = False
                        await self.close()
                        break
                else:
                    pass

                await asyncio.sleep(10)
        else:
            await self.close()


class queued_tenant_deletion(AsyncJsonWebsocketConsumer):
    async def connect(self):
        origin = "".join(str(v, "utf-8") for i, v in self.scope["headers"] if i == b"origin")
        if not origin_validator(origin):
            await self.close(code=1002)
        else:
            await self.accept()
            job_id = self.scope["url_route"]["kwargs"]["job_id"]
            job = Job.fetch(job_id, connection=redis_instance)
            while job.get_status() not in ["finished", "stopped", "canceled", "failed"]:
                await asyncio.sleep(0.1)
                job.refresh()
                if job.worker_name:
                    worker_name = job.worker_name
            else:
                context = {}
                context["status"] = job.get_status()
                job.refresh()
                send_shutdown_command(redis_instance, worker_name)
                if job_id.startswith("tenant_deletion_"):
                    if job.get_status() == "finished":
                        deleted_host, deleted_csrf_origin = job.result
                        global CSRF_TRUSTED_ORIGINS
                        if deleted_csrf_origin in CSRF_TRUSTED_ORIGINS:
                            CSRF_TRUSTED_ORIGINS.remove(deleted_csrf_origin)
                        global ALLOWED_HOSTS
                        if deleted_host in ALLOWED_HOSTS:
                            ALLOWED_HOSTS.remove(deleted_host)

                await self.send_json(context)


@database_sync_to_async
def get_user_groups(user_object):
    return list(user_object.groups.all().values_list("id", flat=True))
