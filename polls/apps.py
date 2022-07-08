from django.apps import AppConfig
from django.db.models.signals import post_save


class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'

    #def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        #from . import signals
        # Explicitly connect a signal handler.
        #post_save.connect(signals.post_save_question)
