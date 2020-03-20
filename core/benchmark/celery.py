from celery import Celery

from core.config import config

mongodb_host_string = config["MONGODB_SETTINGS"]["host"].replace("?", "-celery?")

benchmark_tasks = Celery(
    __name__, broker=mongodb_host_string, backend=mongodb_host_string,
)

if __name__ == "__main__":
    benchmark_tasks.start()
