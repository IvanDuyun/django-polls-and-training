from django.apps import AppConfig
from django.db.models.signals import post_save


class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'

    def ready(self):
        from .import signals

