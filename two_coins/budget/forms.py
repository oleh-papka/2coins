from django import forms

from . import models


class AccountForm(forms.ModelForm):
    icon = forms.CharField(max_length=30,
                           label='Account icon',
                           required=False)
    color = forms.CharField(max_length=7,
                            label='Account color',
                            required=False)

    class Meta:
        model = models.Account
        fields = '__all__'
        exclude = ('profile', 'styling')


class CategoryForm(forms.ModelForm):
    icon = forms.CharField(max_length=30,
                           label='Category icon',
                           required=False)
    color = forms.CharField(max_length=7,
                            label='Category color',
                            required=False)

    class Meta:
        model = models.Category
        fields = '__all__'
        exclude = ('profile', 'styling')


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['account', 'transaction_type', 'category',
                  'amount', 'amount_account_currency',
                  'date', 'description', 'currency']
