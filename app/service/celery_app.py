from celery import Celery
import app.config
import os

redis_url = os.getenv("REDIS_URL", "127.0.0.0.1")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_db = os.getenv("REDIS_DB", "0")

celery_app = Celery("worker", broker=f"redis://{redis_url}:{redis_port}/{redis_db}")

import app.service.task
