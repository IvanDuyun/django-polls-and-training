import datetime
from django.db.models import F, Sum, Q
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.conf import settings
from abc import ABC, abstractmethod

from django.utils.timezone import now
from polymorphic.models import PolymorphicModel
import jwt
from . import signals


FIXED = '1'
VARIABLE = '2'


class UserProfile(models.Model):
    profile = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    agreement_accepted = models.BooleanField(default=False)

    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = now() + datetime.timedelta(days=1)
        token = jwt.encode({
            'id': self.id,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token


class CommonTariffTwo(PolymorphicModel):
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    @abstractmethod
    def get_current_price(self):
        pass


class TariffFixedTwo(CommonTariffTwo):
    price = models.FloatField(default=0)

    def get_current_price(self):
        return self.price


class TariffVariableTwo(CommonTariffTwo):
    price_the_question = models.FloatField(default=0)

    def get_current_price(self):
        return self.price_the_question * Question.manager.count_questions_from_current_author(self.author)


class CommonTariff(models.Model):
    TARIFF_CHOICES = (
        (FIXED, 'Fixed'),
        (VARIABLE, 'Variable'),
    )
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    category = models.CharField(choices=TARIFF_CHOICES, max_length=100, default=1)
    CATEGORY = None

    def get_current_tariff(self):
        if self.category == FIXED:
            return self.tarifffixed
        elif self.category == VARIABLE:
            return self.tariffvariable

    def save(self, *args, **kwargs):
        self.category = self.CATEGORY
        super().save(*args, **kwargs)

    @abstractmethod
    def get_current_price(self):
        pass


class TariffFixed(CommonTariff):
    price = models.FloatField(default=0)
    CATEGORY = FIXED

    def get_current_price(self):
        return self.price


class TariffVariable(CommonTariff):
    price_the_question = models.FloatField(default=0)
    CATEGORY = VARIABLE

    def get_current_price(self):
        return self.price_the_question * Question.manager.count_questions_from_current_author(self.author)


class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author')

    def count_questions(self):
        return self.get_queryset().count()

    def count_questions_from_current_author(self, author):
        return self.get_queryset().filter(author=author).count()

    def annotate_author(self):
        return self.get_queryset().annotate(votes_cnt=Sum('choice__votes'))

    def filter_ab(self):
        return self.get_queryset().filter(Q(question_text__startswith='A') | Q(question_text__startswith='B'))


class QuestionQuerySet(models.QuerySet):
    def count_questions(self):
        return self.count()

    def annotate_votes(self):
        return self.annotate(votes_cnt=Sum('choice__votes'))


class AuthorBalanceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('author')


class AuthorBalance(models.Model):
    balance = models.FloatField(default=0)
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    objects = AuthorBalanceManager()

    def __str__(self):
        return str(self.author)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    objects = models.Manager()
    manager = QuestionManager()
    manager_from_QS = models.Manager.from_queryset(QuestionQuerySet)()

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
        print('1. Количество вопросов: %s' % Question.manager_from_QS.count_questions())

        print('2. Количество голосов в каждом опросе:')
        votes_set = Question.manager_from_QS.annotate_votes()
        for votes in votes_set:
            print('%s: %s;' % (votes.question_text, votes.votes_cnt))

        print('То же самое, но менеджер на основе Queryset')
        print('3. Количество вопросов: %s' % Question.manager_from_QS.count_questions())

        print('4. Количество голосов в каждом опросе:')
        votes_set = Question.manager_from_QS.annotate_votes()
        for votes in votes_set:
            print('%s: %s;' % (votes.question_text, votes.votes_cnt))
        print('4. Всего голосов до вызова votes_inc: %s' % Choice.manager.count_all_votes())
        print('   Всего вариантов выбора: %s' % Choice.manager.count_choice())
        Choice.all_votes_inc()
        print('   Всего голосов после вызова votes_inc: %s' % Choice.manager.count_all_votes())

        print('   Голосов в Choice (pk=2) до вызова votes_inc: %s' % Choice.manager.count_votes(2))
        Choice.votes_inc(2)
        print('   Голосов в Choice (pk=2) после вызова votes_inc: %s' % Choice.manager.count_votes(2))

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
        #self.print_test()

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class ChoiceManager(models.Manager):
    def count_all_votes(self):
        return self.get_queryset().aggregate(Sum('votes'))

    def count_votes(self, id_choice):
        return self.get_queryset().filter(pk=id_choice).first().votes

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
    def votes_inc(id_choice):
        Choice.objects.filter(pk=id_choice).update(votes=F('votes') + 1)

    @staticmethod
    def all_votes_inc():
        Choice.objects.all().update(votes=F('votes') + 1)
