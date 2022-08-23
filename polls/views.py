from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import transaction
from .forms import AuthorBalanceForm, ChoiceInlineFormset, QuestionForm, QuestionFormM, UserProfileForm
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Choice, Question, AuthorBalance, UserProfile
from django.utils.http import url_has_allowed_host_and_scheme
from polls import REDIRECT_FIELD_NAME
from django.utils.encoding import iri_to_uri
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner
from .tasks import simulate_background_task
import time
import json


MAX_AGE = 1


def test_celery(request):
    simulate_background_task.delay()
    return HttpResponse('Вычисления начаты')


@csrf_exempt
def question_api(request, pk):
    """Task 11 (Json and Cryptographic signing)"""
    form_data = json.loads(request.body)
    signer = TimestampSigner()
    sign = form_data['pk']
    try:
        pk = signer.unsign(sign, MAX_AGE)
    except:
        return HttpResponse('No access')
    question = Question.objects.get(pk=pk)
    if request.method == "POST":
            form = QuestionFormM(form_data, instance=question)
            if form.is_valid():
                form.save()
                return HttpResponse('successfully')


def imitation_of_calculations():
    time.sleep(5)
    return 'ok'


def test_cache_manually(request):
    ok = cache.get('ok')
    if not ok:
        ok = imitation_of_calculations()
        cache.set('ok', ok, 60)
    return HttpResponse(ok)


@cache_page(60)
def test_cache_with_decorator(request):
    ok = imitation_of_calculations()
    return HttpResponse(ok)


def get_redirect(request):
    redirect_field_name = REDIRECT_FIELD_NAME
    if url_has_allowed_host_and_scheme(request.GET[redirect_field_name], None):
        return iri_to_uri(request.GET[redirect_field_name])
    else:
        raise


def set_agreement(request, profile_id):
    profile = UserProfile.objects.get(pk=profile_id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(get_redirect(request))
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'polls/agreement.html', {'form': form})


def question_create_view(request):
    if request.method == "POST":
        form = QuestionFormM(request.POST, request.FILES)
        formset = ChoiceInlineFormset(request.POST, request.FILES)
        with transaction.atomic():
            if form.is_valid():
                question_instance = form.save()
                if formset.is_valid():
                    choices = formset.save(commit=False)
                    for choice in choices:
                        choice.question = question_instance
                        choice.save()
                return HttpResponseRedirect(reverse('polls:index'))
    else:
        form = QuestionFormM()
        formset = ChoiceInlineFormset()
    return render(request, 'polls/question_create_m.html', {'formset': formset, 'form': form})


def question_update_view(request, pk):
    question = Question.objects.get(pk=pk)
    if request.method == "POST":
        form = QuestionFormM(request.POST, request.FILES, instance=question)
        formset = ChoiceInlineFormset(request.POST, request.FILES, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return HttpResponseRedirect(reverse('polls:index'))
    else:
        form = QuestionFormM(instance=question)
        formset = ChoiceInlineFormset(instance=question)
    return render(request, 'polls/question_create_m.html', {'formset': formset, 'form': form})


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


def latest_question(self):
    return Question.objects.latest("pub_date").pub_date


@condition(last_modified_func=latest_question)
def question_list(request):
    question_all = Question.objects.all()
    return render(request, 'polls/index.html', {'latest_question_list': question_all})


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
