import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.conf import settings
from . import signals


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    __original_author = None

    def __str__(self):
        return self.question_text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_author = self.author

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.author != self.__original_author:
            print('Отправляю сигнал: автор изменился')
            signals.author_changed.send(sender=self)
        super().save(force_insert, force_update, *args, **kwargs)
        self.__original_name = self.author

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

