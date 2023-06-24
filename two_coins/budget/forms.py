from django import forms
from . import models


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = models.Currency
        fields = '__all__'
        widgets = {
            'ccy_type': forms.Select
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields = '__all__'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = '__all__'
