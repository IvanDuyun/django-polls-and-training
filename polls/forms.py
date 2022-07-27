from django.forms import FloatField, IntegerField, ChoiceField, inlineformset_factory
from . import models
from django import forms
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from .custom_layout_object import *


class AuthorBalanceForm(forms.ModelForm):
    balance = FloatField(disabled=True)
    author = IntegerField(disabled=True)
    WITHDRAW = 2
    REPLENISH = 1
    action = forms.ChoiceField(choices=((REPLENISH, "Пополнить"), (WITHDRAW, "Списать")))
    change = FloatField(min_value=0)

    class Meta:
        model = models.AuthorBalance
        fields = ['author', 'balance']

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        change = cleaned_data.get("change")
        balance = cleaned_data.get("balance")
        if action == '2' and change > balance:
            self.add_error('change', 'Списываемая сумма не может быть меньше баланса')
        return cleaned_data


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = models.Choice
        fields = ['choice_text', 'votes']


class QuestionForm(forms.ModelForm):

    class Meta:
        model = models.Question
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('author'),
                Field('question_text'),
                Field('pub_date'),
                Fieldset('Add choices',
                Formset('choices')),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'Save')),
                )
            )


ChoiceInlineFormset = inlineformset_factory(models.Question, models.Choice, extra=3, form=ChoiceForm)



