import random
import string

from rq import Worker

from config.settings.base import redis_instance, redis_queue

# Start a worker with a custom name
worker_code = "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
worker = Worker([redis_queue], connection=redis_instance, name=f"Default worker - {worker_code}")
worker.work()
