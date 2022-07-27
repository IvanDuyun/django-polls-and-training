from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import transaction
from .forms import AuthorBalanceForm, ChoiceInlineFormset, QuestionForm
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
import time

from .models import Choice, Question, AuthorBalance


class QuestionCreateView(CreateView):
    model = Question
    template_name = 'polls/question_create.html'
    form_class = QuestionForm
    success_url = reverse_lazy('polls:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['choices'] = ChoiceInlineFormset(self.request.POST)
        else:
            context['choices'] = ChoiceInlineFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choices']
        with transaction.atomic():
            self.object = form.save()
            if choice_formset.is_valid():
                choice_formset.instance = self.object
                choice_formset.save()
        return super().form_valid(form)


class QuestionUpdateView(UpdateView):
    model = Question
    template_name = 'polls/question_create.html'
    form_class = QuestionForm
    success_url = reverse_lazy('polls:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['choices'] = ChoiceInlineFormset(self.request.POST, instance=self.object)
        else:
            context['choices'] = ChoiceInlineFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choices']
        with transaction.atomic():
            self.object = form.save()
            if choice_formset.is_valid():
                choice_formset.instance = self.object
                choice_formset.save()
        return super().form_valid(form)


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
        ).order_by('-pub_date')


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
    author_all = AuthorBalance.objects.all()
    return render(request, 'polls/author_balance_list.html', {'author_all': author_all})


def author_balance_detail(request, pk):
    if request.method == "POST":
        try:
            with transaction.atomic():
                author_balance = AuthorBalance.objects.select_for_update().filter(pk=pk).first()
                form = AuthorBalanceForm(request.POST, instance=author_balance)
                if form.is_valid():
                    change = form.cleaned_data['change']
                    if form.cleaned_data['action'] == '2':
                        change = -change
                    author_balance.balance += change
                    author_balance.save()
                    return HttpResponseRedirect(reverse('polls:author_balance_detail',
                                                        args=(author_balance.id,)))
        except:
            author_balance_detail(request, pk)
    else:
        form = AuthorBalanceForm(instance=get_object_or_404(AuthorBalance, pk=pk))
    return render(request, 'polls/author_balance_detail.html', {'form': form})
