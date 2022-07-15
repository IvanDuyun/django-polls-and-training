from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import transaction
import time

from .models import Choice, Question, Donator, DonatorBalance


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def donator_list(request):
    donators = Donator.objects.all()
    return render(request, 'polls/donator_list.html', {'donators': donators})

def change_balance(request, donator, action):
    value = int(request.POST.get(action))
    try:
        with transaction.atomic():
            if action == 'replenish':
                donator.balance.money += value
                donator.balance.save()
            elif action == 'withdraw':
                if donator.balance.money < value:
                    donator.balance.save()
                else:
                    donator.balance.money -= value
                    donator.balance.save()
    except:
        change_balance(request, donator, action)

def donator_detail(request, pk):
    donator = get_object_or_404(Donator, pk=pk)
    if request.method == "POST":
        if request.POST.get('b_replenish'):
            change_balance(request, donator, 'replenish')
        elif request.POST.get('b_withdraw'):
            change_balance(request, donator, 'withdraw')
        return HttpResponseRedirect(reverse('polls:donator_detail', args=(donator.id,)))
    return render(request, 'polls/donator_detail.html', {'donator': donator})