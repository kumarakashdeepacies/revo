from datetime import datetime
import json
import logging
import os

from dateutil.relativedelta import relativedelta
from rq_scheduler import Scheduler

from config.settings.base import PLATFORM_FILE_PATH, redis_instance_scheduler
from kore_investment.users.schedulingjobs import schedulercheck

# Create scheduler to run in a thread inside the application process
scheduler = Scheduler(connection=redis_instance_scheduler)


def start():
    start_date = datetime.utcnow() + relativedelta(minutes=5)
    db_health_start_date = datetime.utcnow() + relativedelta(minutes=6)
    tenant_data = {}
    if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
        with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
            tenant_data = json.load(json_file)
            json_file.close()
    else:
        pass
    for tenant, config in tenant_data.items():
        db_check_interval = 10
        if config.get("db_connection_check_interval"):
            db_check_interval = config["db_connection_check_interval"]
        job_id = f"DB_health_check_{tenant}"
        tenant_inactive_user_scheduler_job = str(tenant) + "_inactive_user_scheduler_job"
        tenant_delete_user_scheduler_job = str(tenant) + "_delete_user_scheduler_job"
        func = "schedulercheck.db_con_checker"
        add_db_health_scheduler(
            func, job_id, tenant, minutes=db_check_interval, start_date=db_health_start_date
        )
        func = "schedulercheck.mark_users_inactive"
        scheduled_time = datetime.utcnow().replace(hour=23, minute=30)
        add_db_health_scheduler(
            func, tenant_inactive_user_scheduler_job, tenant, start_date=scheduled_time, days=1
        )
        func = "schedulercheck.delete_inactive_users"
        scheduled_time = datetime.utcnow().replace(hour=23, minute=45)
        add_db_health_scheduler(
            func, tenant_delete_user_scheduler_job, tenant, start_date=scheduled_time, days=1
        )
    scheduled_time = datetime.utcnow().replace(hour=18, minute=30)
    add_db_health_scheduler(
        "schedulercheck.delete_expired_notifications",
        "Purge_Notifications",
        None,
        start_date=scheduled_time,
        days=1,
        timeout=300,
    )
    add_db_health_scheduler(
        "schedulercheck.migration_checker",
        "Migration_checker",
        None,
        minutes=1,
        start_date=start_date,
        interval=False,
        timeout=600,
    )


def add_schedule_flow(
    func, job_id, request, month, day_of_week, day, hour, minute, start_date, repeat, request2={}
):
    def request_to_dict(request):
        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
        return request2

    try:
        request = request_to_dict(request)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        request = request2
    scheduler.cancel(job_id)
    scheduler.schedule(
        scheduled_time=start_date,
        func=eval(func),
        id=job_id,
        args=[request, f"{job_id}"],
        interval=repeat,
        repeat=repeat,
    )
    return None


def add_scheduler_process(
    func, job_id, request, month, day_of_week, day, hour, minute, start_date, end_date, data
):
    def request_to_dict(request):
        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
        return request2

    request = request_to_dict(request)
    scheduler.cancel(job_id)
    scheduler.cron(
        f"{minute} {hour} {day} {month} {day_of_week}",
        func=eval(func),
        id=f"{job_id}",
        args=[request, f"{job_id}", data["src_element_id"], data["element_id"], data["pr_code"], ""],
        repeat=None,
    )
    return None


def add_scheduler(func, job_id, request, month, day_of_week, day, hour, minute, start_date, end_date):
    def request_to_dict(request):
        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
        return request2

    request = request_to_dict(request)
    scheduler.cancel(job_id)
    if type(func) == str:
        func = eval(func)
    else:
        pass
    scheduler.cron(
        f"{minute} {hour} {day} {month} {day_of_week}",
        func=func,
        id=f"{job_id}",
        args=[request, f"{job_id}"],
        repeat=None,
    )
    return None


def add_db_health_scheduler(
    func, job_id, schema, minutes=1, start_date=None, days=None, interval=True, timeout=180
):
    if not start_date:
        start_date = datetime.utcnow() + relativedelta(minutes=5)
    jobs = scheduler.get_jobs()
    jobids = []
    for job in jobs:
        jobids.append(job.id)
    if interval:
        if job_id in jobids:
            scheduler.cancel(job_id)
        if days:
            interval = days * 24 * 60 * 60
            scheduler.schedule(
                scheduled_time=start_date,
                func=eval(func),
                id=job_id,
                args=[f"{job_id}", schema],
                interval=interval,
                repeat=None,
                result_ttl=interval + 1,
                timeout=timeout,
                queue_name="system_scheduled_job_queue",
            )
        else:
            interval = minutes * 60
            scheduler.schedule(
                scheduled_time=start_date,
                func=eval(func),
                id=job_id,
                args=[f"{job_id}", schema],
                interval=interval,
                repeat=None,
                result_ttl=interval + 1,
                timeout=timeout,
                queue_name="system_scheduled_job_queue",
            )
    else:
        if job_id in jobids:
            scheduler.cancel(job_id)
        scheduler.schedule(
            scheduled_time=start_date,
            func=eval(func),
            id=job_id,
            args=[f"{job_id}", schema],
            interval=1,
            repeat=None,
            result_ttl=5,
            timeout=timeout,
            queue_name="system_scheduled_job_queue",
        )
    return None


def process_flow_scheduler(
    func,
    job_id,
    request,
    month,
    day_of_week,
    day,
    hour,
    minute,
    retries,
    interval_between_retries,
    start_date,
    end_date,
    block_config={},
):
    def request_to_dict(request):
        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
        return request2

    request = request_to_dict(request)
    scheduler.cancel(job_id)
    if func == "schedulercheck.execute_flow":
        args_list = [request, job_id, retries, interval_between_retries]
    else:
        args_list = [request, job_id, block_config, retries, interval_between_retries]
    scheduler.cron(
        f"{minute} {hour} {day} {month} {day_of_week}",
        func=eval(func),
        id=f"{job_id}",
        args=args_list,
        repeat=None,
        timeout=3600,
    )
    return None


def delete_scheduler(job_id):
    scheduler.cancel(f"{job_id}")
    return None
