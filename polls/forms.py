from django import forms
from django.forms import FloatField, IntegerField, ChoiceField
from . import models


class AuthorBalanceForm(forms.ModelForm):
    balance = FloatField(disabled=True)
    author = IntegerField(disabled=True)
    replenish = forms.BooleanField(required=False)
    withdraw = forms.BooleanField(required=False)
    change = FloatField(min_value=0)

    class Meta:
        model = models.AuthorBalance
        fields = ['author', 'balance']

    def clean(self):
        cleaned_data = super().clean()

        withdraw = cleaned_data.get("withdraw")
        replenish = cleaned_data.get("replenish")
        change = cleaned_data.get("change")
        balance = cleaned_data.get("balance")

        if (withdraw and replenish) or (not withdraw and not replenish):
            self.add_error('replenish', 'Необходимо выбрать одно действие')
        elif withdraw and change > balance:
            self.add_error('change', 'Списываемая сумма не может быть меньше баланса')

        return cleaned_data



