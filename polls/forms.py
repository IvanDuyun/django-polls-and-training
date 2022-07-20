from django import forms
from django.forms import FloatField, IntegerField, ChoiceField
from . import models


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



