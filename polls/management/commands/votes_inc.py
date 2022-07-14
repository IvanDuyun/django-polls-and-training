from django.core.management.base import BaseCommand, CommandError
from polls.models import Choice
from django.db.models import F, Sum, Count, Q
from django.db import transaction

import time


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            nargs=2,
            type=int,
            dest='args'
        )

    @staticmethod
    def count_votes(id_choice):
        return Choice.objects.get(pk=id_choice).votes

    def go_sleep(self, time_sleep, id_choice):
        print('Количество голосов: %s' % self.count_votes(id_choice))
        print('ожидаю...')
        time.sleep(time_sleep)

    def print_results(self, id_choice):
        print('Работу закончила. Количество голосов: %s' % self.count_votes(id_choice))

    def votes_inc(self, id_choice):
        choice = Choice.objects.get(pk=id_choice)
        self.go_sleep(5, id_choice)
        choice.votes += 1
        choice.save()
        self.print_results(id_choice)

    def votes_inc_modified_with_f(self, id_choice):
        choice = Choice.objects.filter(pk=id_choice)
        self.go_sleep(5, id_choice)
        choice.update(votes=F('votes') + 1)
        self.print_results(id_choice)

    def votes_inc_modified_with_transaction(self, id_choice):
        choices = Choice.objects.select_for_update().filter(pk=id_choice)
        self.go_sleep(5, id_choice)
        with transaction.atomic():
            for choice in choices:
                choice.votes += 1
                choice.save()
        self.print_results(id_choice)

    def handle(self, way, id_choice, *args, **options):
        if way == 1:
            self.votes_inc(id_choice)
        elif way == 2:
            self.votes_inc_modified_with_f(id_choice)
        elif way == 3:
            self.votes_inc_modified_with_transaction(id_choice)
