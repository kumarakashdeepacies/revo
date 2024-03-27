import random
import string

from rq import Queue, Worker

from config.settings.base import redis_instance

comp_queue = Queue("computation_queue_1", connection=redis_instance)

# Start a worker with a custom name
worker_code = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
worker = Worker([comp_queue], connection=redis_instance, name=f"Computation 1 worker - {worker_code}")
worker.work()
