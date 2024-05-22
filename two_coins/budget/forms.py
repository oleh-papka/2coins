from django import forms

from . import models


class AccountForm(forms.ModelForm):
    icon = forms.CharField(max_length=30,
                           label='Category icon',
                           required=False)
    color = forms.CharField(max_length=7,
                            label='Category color',
                            required=False)

    class Meta:
        model = models.Account
        fields = '__all__'
        exclude = ('profile',)


class AccountUpdateForm(forms.ModelForm):
    icon = forms.CharField(max_length=30,
                           label='Category icon',
                           required=False)
    color = forms.CharField(max_length=7,
                            label='Category color',
                            required=False)

    class Meta:
        model = models.Account
        fields = ['name', 'balance', 'initial_balance', 'target_balance', 'deadline', 'description']


class CategoryForm(forms.ModelForm):
    icon = forms.CharField(max_length=30,
                           label='Category icon',
                           required=False)
    color = forms.CharField(max_length=7,
                            label='Category color',
                            required=False)

    class Meta:
        model = models.Category
        fields = ['category_type', 'name', 'icon', 'color']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'
