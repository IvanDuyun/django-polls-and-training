from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models


@receiver(post_save, sender=models.Question)
def post_save_question(sender, update_fields, **kwargs):
    pass
    #if 'author' in update_fields:
        #pass