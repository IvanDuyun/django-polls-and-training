import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_for_polls.settings")
app = Celery("polls")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

