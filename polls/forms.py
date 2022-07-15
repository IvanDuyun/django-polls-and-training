from django import forms
from django.conf import settings
from . import models


class DonatorForm(forms.ModelForm):
    class Meta:
        model = models.Donator
        fields = ['name', 'balance']
