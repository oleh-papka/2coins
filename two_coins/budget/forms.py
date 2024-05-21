from django import forms

from . import models


class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields = '__all__'
        exclude = ('profile',)


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields = ['name', 'balance', 'initial_balance', 'target_balance', 'deadline', 'description', 'styling']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['category_type', 'name', 'styling']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'
