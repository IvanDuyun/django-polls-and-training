from time import sleep
from celery import Celery
from django.conf import settings


app = Celery('tasks', broker=settings.CELERY_BROKER_URL)


@app.task
def simulate_background_task(x, y):
    sleep(10)
    return x + y
