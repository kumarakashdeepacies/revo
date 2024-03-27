from rq import Queue, Retry
from rq.worker import Worker

from config.settings.base import env, redis_instance

redis_queue = Queue(connection=redis_instance)
tenant_queue = Queue("tenant_queue", connection=redis_instance)
navbar_queue = Queue("navbar_queue", connection=redis_instance)
alerts_queue = Queue("alerts_queue", connection=redis_instance)


def start_queues():
    if env("KUBERNETES_ENV", default="true") != "true":
        boot_redis_worker(redis_queue, str(redis_queue.name))
        boot_redis_worker(tenant_queue, str(tenant_queue.name))
        boot_redis_worker(navbar_queue, str(navbar_queue.name))
        boot_redis_worker(alerts_queue, str(alerts_queue.name))
        for comp_queue_no in range(int(env("COMPUTATION_QUEUES", default="1"))):
            exec(
                f"global computation_queue_{comp_queue_no}; computation_queue_{comp_queue_no} = Queue('computation_queue_{comp_queue_no}', connection=redis_instance); boot_redis_worker(computation_queue_{comp_queue_no}, 'computation_queue_{comp_queue_no}')",
                globals(),
                globals(),
            )
        for upload_queue_no in range(int(env("DATA_UPLOAD_QUEUES", default="1"))):
            exec(
                f"global data_upload_queue_{upload_queue_no}; data_upload_queue_{upload_queue_no} = Queue('data_upload_queue_{upload_queue_no}', connection=redis_instance); boot_redis_worker(data_upload_queue_{upload_queue_no}, 'data_upload_queue_{upload_queue_no}')",
                globals(),
                globals(),
            )
    else:
        for comp_queue_no in range(int(env("COMPUTATION_QUEUES", default="2"))):
            exec(
                f"global computation_queue_{comp_queue_no}; computation_queue_{comp_queue_no} = Queue('computation_queue_{comp_queue_no}', connection=redis_instance)",
                globals(),
                globals(),
            )
        for upload_queue_no in range(int(env("DATA_UPLOAD_QUEUES", default="1"))):
            exec(
                f"global data_upload_queue_{upload_queue_no}; data_upload_queue_{upload_queue_no} = Queue('data_upload_queue_{upload_queue_no}', connection=redis_instance)",
                globals(),
                globals(),
            )
    return None


def return_queues(job_type="All"):
    queues = {}
    if job_type == "All":
        queues = {
            "redis_queue": redis_queue,
            "tenant_queue": tenant_queue,
            "navbar_queue": navbar_queue,
            "alerts_queue": alerts_queue,
        }
        for comp_queue_no in range(int(env("COMPUTATION_QUEUES", default="1"))):
            queues[f"computation_queue_{comp_queue_no}"] = eval(f"computation_queue_{comp_queue_no}")
        for upload_queue_no in range(int(env("DATA_UPLOAD_QUEUES", default="1"))):
            queues[f"data_upload_queue_{upload_queue_no}"] = eval(f"data_upload_queue_{upload_queue_no}")
    elif job_type == "computation":
        for comp_queue_no in range(int(env("COMPUTATION_QUEUES", default="2"))):
            queues[f"computation_queue_{comp_queue_no}"] = eval(f"computation_queue_{comp_queue_no}")
    elif job_type == "data_upload":
        for upload_queue_no in range(int(env("DATA_UPLOAD_QUEUES", default="1"))):
            queues[f"data_upload_queue_{upload_queue_no}"] = eval(f"data_upload_queue_{upload_queue_no}")
    elif job_type == "navbar_generation":
        queues["navbar_queue"] = navbar_queue
    elif job_type == "tenant":
        queues["tenant_queue"] = tenant_queue
    elif job_type == "alerts":
        queues["alerts_queue"] = alerts_queue
    else:
        queues["redis_queue"] = redis_queue
    return queues


def fetch_least_busy_queue(job_type="default"):
    if job_type == "computation":
        available_queues = return_queues(job_type="computation")
    elif job_type == "data_upload":
        available_queues = return_queues(job_type="data_upload")
    elif job_type == "tenant":
        available_queues = return_queues(job_type="tenant")
    elif job_type == "navbar_generation":
        available_queues = return_queues(job_type="navbar_generation")
    elif job_type == "html_generation":
        available_queues = return_queues(job_type="html_generation")
    elif job_type == "alerts":
        available_queues = return_queues(job_type="alerts")
    else:
        available_queues = return_queues(job_type="default")
    if len(available_queues) == 1:
        least_busy_queue = list(available_queues.values())[0]
    else:
        queue_traffic = {}
        for queue in available_queues.values():
            active_jobs = [
                i for i in queue.jobs if i.get_status() not in ["finished", "stopped", "canceled", "failed"]
            ]
            queue_traffic[queue] = len(active_jobs)
        least_busy_queue = min(queue_traffic, key=queue_traffic.get)
    return least_busy_queue


def enqueue_jobs(
    job_func,
    job_id,
    args=(),
    kwargs={},
    result_ttl=60,
    job_type="default",
    retry=1,
    job_timeout="3h",
    description=None,
):
    least_busy_queue = fetch_least_busy_queue(job_type=job_type)
    if env("KUBERNETES_ENV", default="true") != "true":
        boot_redis_worker(least_busy_queue, str(least_busy_queue.name))
    job = least_busy_queue.enqueue(
        job_func,
        job_id=job_id,
        result_ttl=result_ttl,
        job_timeout=job_timeout,
        failure_ttl=120,
        args=args,
        kwargs=kwargs,
        description=description,
    )
    job.save()
    return job_id


def boot_redis_worker(queue, queue_name, no_of_worker=1):
    workers = Worker.all(queue=queue)
    up_workers = [i for i in workers if i.get_state() != "suspended"]
    return True
