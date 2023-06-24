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
        context["instance_name"] = 'Currency'
        return context


def currency(request, pk):
    return HttpResponse(f'Currency {pk}')


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
                   'instance_name': 'Currency'})


def currency_edit(request, pk):
    return HttpResponse(f"Form for editing your currency {pk}")


def currency_delete(request, pk):
    curr = models.Currency.objects.get(pk=pk)

    if request.method == "POST":
        curr.delete()
        return redirect('currency_list')

    return render(request, 'budget/currency_delete.html',
                  {'object': curr,
                   'instance_name': 'Currency'})


# Accounts

class AccountList(ListView):
    model = models.Account
    context_object_name = 'account_list'
    template_name = "budget/account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Account'
        return context


def account(request, pk):
    return HttpResponse(f"Account {pk}")


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
                   'instance_name': 'Account'})


def account_edit(request, pk):
    return HttpResponse(f"Form for editing your account {pk}")


def account_delete(request, pk):
    acct = models.Account.objects.get(pk=pk)

    if request.method == "POST":
        acct.delete()
        return redirect('account_list')

    return render(request, 'budget/account_delete.html',
                  {'object': acct,
                   'instance_name': 'Account'})
