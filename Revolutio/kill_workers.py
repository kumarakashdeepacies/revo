from rq.command import send_shutdown_command
from rq.worker import Worker

from config.settings.base import redis_instance

# Start a worker with a custom name
workers = workers = Worker.all(redis_instance)
for work in workers:
    send_shutdown_command(redis_instance, work.name)
