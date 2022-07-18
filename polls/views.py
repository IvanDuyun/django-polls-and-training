from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import transaction
from .forms import AuthorBalanceForm
import time

from .models import Choice, Question, AuthorBalance


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


def author_balance_list(request):
    author_balance_all = AuthorBalance.objects.all()
    return render(request, 'polls/author_balance_list.html', {'author_balance_all': author_balance_all})


def author_balance_detail(request, pk):
    author_balance = get_object_or_404(AuthorBalance, pk=pk)
    if request.method == "POST":
        form = AuthorBalanceForm(request.POST, instance=author_balance)
        try:
            with transaction.atomic():
                if form.is_valid():
                    if form.cleaned_data['replenish']:
                        author_balance.balance += form.cleaned_data['change']
                    elif form.cleaned_data['withdraw']:
                        author_balance.balance -= form.cleaned_data['change']
                    author_balance.save()
                    return HttpResponseRedirect(reverse('polls:author_balance_detail',
                                                        args=(author_balance.id,)))
        except:
            author_balance_detail(request, pk)
    else:
        form = AuthorBalanceForm(instance=author_balance)
    return render(request, 'polls/author_balance_detail.html', {'form': form})
