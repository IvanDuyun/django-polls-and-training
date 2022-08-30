from time import sleep
from polls.celery import app


@app.task
def simulate_background_task(x, y):
    sleep(5)
    return x + y
