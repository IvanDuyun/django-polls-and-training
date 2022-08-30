from time import sleep
from celery import Celery
from django.conf import settings


app = Celery('tasks', backend=settings.CELERY_RESULT_BACKEND, broker=settings.CELERY_BROKER_URL)


@app.task
def simulate_background_task(x, y):
    sleep(5)
    return x + y
