from .celery import app as celery_app

__all__ = ('celery_app',)
REDIRECT_FIELD_NAME = "next"