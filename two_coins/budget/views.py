from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.views.generic import ListView

from . import forms, models


# Currencies

class CurrencyList(ListView):
    model = models.Currency
    context_object_name = 'currency_list'
    template_name = "budget/currency_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Currencies'
        return context


def currency_add(request):
    if request.method == "POST":
        form = forms.CurrencyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('currency_list')
        else:
            print('NO')

    return render(request, 'budget/currency_create.html',
                  {'form': forms.CurrencyForm,
                   'acct_types': models.Currency.MONEY_TYPES_CHOICES,
                   'instance_name': 'Currencies'})


def currency_edit(request, pk):
    curr = models.Currency.objects.get(pk=pk)

    if request.method == "POST":
        form = forms.CurrencyForm(request.POST, instance=curr)

        if form.is_valid():
            form.save()
            return redirect('currency_list')
        else:
            print('NO')

    return render(request, 'budget/currency_edit.html',
                  {'form': forms.CurrencyForm(instance=curr),
                   'object': curr,
                   'acct_types': models.Currency.MONEY_TYPES_CHOICES,
                   'instance_name': 'Currencies'})


def currency_delete(request, pk):
    curr = models.Currency.objects.get(pk=pk)

    if request.method == "POST":
        curr.delete()
        return redirect('currency_list')

    return render(request, 'budget/currency_delete.html',
                  {'object': curr,
                   'instance_name': 'Currencies'})


# Accounts

class AccountList(ListView):
    model = models.Account
    context_object_name = 'account_list'
    template_name = "budget/account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Accounts'
        return context


def account(request, pk):
    template_name = "budget/account.html"
    acct = models.Account.objects.get(pk=pk)

    return render(request, template_name,
                  {'object': acct,
                   'instance_name': 'Accounts'})


def account_add(request):
    if request.method == "POST":
        form = forms.AccountForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('account_list')
        else:
            print('NO no no')
        # return render(request, 'budget/account_list.html')

    currencies = [(curr.id, curr.abbr) for curr in models.Currency.objects.all()]

    return render(request, 'budget/account_create.html',
                  {'form': forms.AccountForm,
                   'currencies': currencies,
                   'instance_name': 'Accounts'})


def account_edit(request, pk):
    acct = models.Account.objects.get(pk=pk)

    if request.method == "POST":
        form = forms.AccountForm(request.POST, instance=acct)
        print(form.data)

        if form.is_valid():
            form.save()
            return redirect('account_list')
        else:
            print('NO no no')

    currencies = [(curr.id, curr.abbr) for curr in models.Currency.objects.all()]

    return render(request, 'budget/account_edit.html',
                  {'form': forms.AccountForm(instance=acct),
                   'object': acct,
                   'currencies': currencies,
                   'instance_name': 'Accounts'})


def account_delete(request, pk):
    acct = models.Account.objects.get(pk=pk)

    if request.method == "POST":
        acct.delete()
        return redirect('account_list')

    return render(request, 'budget/account_delete.html',
                  {'object': acct,
                   'instance_name': 'Accounts'})
