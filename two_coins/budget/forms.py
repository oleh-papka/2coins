from django import forms
from . import models


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = models.Currency
        fields = '__all__'


class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields = '__all__'
        exclude = ('profile',)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['cat_type', 'name', 'color', 'icon']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'
