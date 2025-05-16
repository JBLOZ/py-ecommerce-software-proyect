import os
from celery import Celery
import requests

from models import SqueezeNet

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND_WEBHOOK = os.getenv("BACKEND_WEBHOOK_URL", "http://backend:8000/webhook/task_completed")

celery_app = Celery("inference", broker=REDIS_URL)
celery_app.conf.task_routes = {
    "app.tasks.process_image_task": {"queue": "image"}
}

@celery_app.task
def process_image_task(image_data: bytes, task_id: str):
    try:
        model = SqueezeNet("...") # TODO: Use os to get the model path
        predictions = model(image_data)

        requests.post(BACKEND_WEBHOOK, json={
            "task_id": task_id,
            "state": "completed",
            "category": predictions
        }, timeout=10)
    except Exception as e:
        requests.post(BACKEND_WEBHOOK, json={
            "task_id": task_id,
            "state": "failed",
            "error": str(e)
        }, timeout=10)
