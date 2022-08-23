from time import sleep
from celery import shared_task


@shared_task
def simulate_background_task():
    sleep(10)
    value = 2 + 2
    return value
