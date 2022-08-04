from django import dispatch
import polls.models as models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

author_changed = dispatch.Signal()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        models.UserProfile.objects.create(profile=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        models.UserProfile.objects.create(profile=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

