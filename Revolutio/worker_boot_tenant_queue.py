import random
import string

from rq import Queue, Worker

from config.settings.base import redis_instance

tenant_queue = Queue("tenant_queue", connection=redis_instance)

# Start a worker with a custom name
worker_code = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
worker = Worker([tenant_queue], connection=redis_instance, name=f"Tenant Creation - {worker_code}")
worker.work()
