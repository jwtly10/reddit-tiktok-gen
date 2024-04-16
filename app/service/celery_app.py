from celery import Celery

celery_app = Celery("worker", broker="redis://127.0.0.1:6379/0")

import app.service.task
