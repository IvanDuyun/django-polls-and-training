import datetime

from django.db.models import F, Sum, Count,Q
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.conf import settings
from . import signals


class QuestionManager(models.Manager):
    def count_questions(self):
        return self.get_queryset().count()

    def annotate_votes(self):
        return self.get_queryset().annotate(votes_cnt=Sum('choice__votes'))

    def filter_ab(self):
        return self.get_queryset().filter(Q(question_text__startswith='A') | Q(question_text__startswith='B'))

class QuestionQuerySet(models.QuerySet):
    def count_questions(self):
        return Question.objects.count()

    def annotate_votes(self):
        return Question.objects.annotate(votes_cnt=Sum('choice__votes'))


class QuestionManagerFromQS(models.Manager):
    pass


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    objects = models.Manager()
    manager = QuestionManager()
    manager_from_QS = QuestionManagerFromQS.from_queryset(QuestionQuerySet)()

    __original_author = None

    def __str__(self):
        return self.question_text

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.__original_author = self.author
        except:
            pass

    @staticmethod
    def print_test():
        print('1. Количество вопросов: %s' % Question.manager.count_questions())

        print('2. Количество голосов в каждом опросе:')
        votes_set = Question.manager.annotate_votes()
        for votes in votes_set:
            print('%s: %s;' % (votes.question_text, votes.votes_cnt))

        print('То же самое, но менеджер на основе Queryset')
        print('3. Количество вопросов: %s' % Question.manager_from_QS.count_questions())

        print('4. Количество голосов в каждом опросе:')
        votes_set = Question.manager_from_QS.annotate_votes()
        for votes in votes_set:
            print('%s: %s;' % (votes.question_text, votes.votes_cnt))
        print('4. Всего голосов до вызова all_votes_inc: %s' % Choice.manager.count_questions())
        print('   Всего вариантов выбора: %s' % Choice.manager.count_choice())
        Choice.all_votes_inc()
        print('   Всего голосов после вызова all_votes_inc: %s' % Choice.manager.count_questions())

        filter_ab_question_set = Question.manager.filter_ab()
        print('5. Все вопросы с букв A,B:')
        for question in filter_ab_question_set:
            print('%s;' % question.question_text)

    def send_signal(self):
        if self.author != self.__original_author:
            print('Отправляю сигнал: автор изменился')
            signals.author_changed.send(sender=self)

        self.__original_name = self.author

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super().save(force_insert, force_update, *args, **kwargs)
        self.send_signal()
        self.print_test()

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class ChoiceManager(models.Manager):
    def count_questions(self):
        return self.get_queryset().aggregate(Sum('votes'))

    def count_choice(self):
        return self.get_queryset().count()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    objects = models.Manager()
    manager = ChoiceManager()

    def __str__(self):
        return self.choice_text

    @staticmethod
    def all_votes_inc():
        Choice.objects.all().update(votes=F('votes')+1)
