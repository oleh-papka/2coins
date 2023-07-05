from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum

from django.shortcuts import render, redirect
from django.views.generic import ListView

from misc.views import AdminUserRequiredMixin
from . import forms, models


# Currencies

class CurrencyList(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    login_url = 'login'
    model = models.Currency
    context_object_name = 'currency_list'
    template_name = "budget/currency/currency_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Currencies'
        return context


def currency_add(request):
    if request.method == "POST":
        form = forms.CurrencyForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f"Currency '{form.cleaned_data.get('name')}' created!")
            return redirect('currency_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.CurrencyForm

    return render(request, 'budget/currency/currency_create.html',
                  {'form': form,
                   'acct_types': models.Currency.MONEY_TYPES_CHOICES,
                   'instance_name': 'Currencies'})


def currency_edit(request, pk):
    curr = models.Currency.objects.get(pk=pk)

    if request.method == "POST":
        form = forms.CurrencyForm(request.POST, instance=curr)

        if form.is_valid():
            form.save()
            messages.success(request, f"Currency '{form.cleaned_data.get('name')}' updated!")

            return redirect('currency_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.CurrencyForm(instance=curr)

    return render(request, 'budget/currency/currency_edit.html',
                  {'form': form,
                   'object': curr,
                   'acct_types': models.Currency.MONEY_TYPES_CHOICES,
                   'instance_name': 'Currencies'})


def currency_delete(request, pk):
    curr = models.Currency.objects.get(pk=pk)

    if request.method == "POST":
        curr.delete()
        messages.success(request, f"Currency '{curr.name}' deleted!")

        return redirect('currency_list')

    return render(request, 'budget/currency/currency_delete.html',
                  {'object': curr,
                   'instance_name': 'Currencies'})


# Accounts

class AccountList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Account
    context_object_name = 'account_list'
    template_name = "budget/account/account_list.html"

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
    currencies = [(curr.id, curr.abbr, curr.symbol) for curr in models.Currency.objects.all()]

    if request.method == "POST":
        form = forms.AccountForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f"Account '{form.cleaned_data.get('name')}' created!")
            return redirect('account_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.AccountForm

    return render(request, 'budget/account/account_create.html',
                  {'form': form,
                   'currencies': currencies,
                   'instance_name': 'Accounts'})


def account_edit(request, pk):
    acct = models.Account.objects.get(pk=pk)
    currencies = [(curr.id, curr.abbr) for curr in models.Currency.objects.all()]

    if request.method == "POST":
        form = forms.AccountForm(request.POST, instance=acct)

        if form.is_valid():
            form.save()
            messages.success(request, f"Account '{form.cleaned_data.get('name')}' updated!")
            return redirect('account_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.AccountForm(instance=acct)

    return render(request, 'budget/account/account_edit.html',
                  {'form': form,
                   'object': acct,
                   'currencies': currencies,
                   'instance_name': 'Accounts'})


def account_delete(request, pk):
    acct = models.Account.objects.get(pk=pk)

    if request.method == "POST":
        acct.delete()
        messages.success(request, f"Account '{acct.name}' deleted!")
        return redirect('account_list')

    return render(request, 'budget/account/account_delete.html',
                  {'object': acct,
                   'instance_name': 'Accounts'})


# Categories

class CategoryList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Category
    context_object_name = 'category_list'
    template_name = "budget/category/category_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Categories'
        return context


def category_add(request):
    if request.method == "POST":
        form = forms.CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('category_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.CategoryForm

    return render(request, 'budget/category/category_create.html',
                  {'form': form,
                   'instance_name': 'Categories'})


def category_edit(request, pk):
    cat = models.Category.objects.get(pk=pk)

    if request.method == "POST":
        form = forms.CategoryForm(request.POST, instance=cat)

        if form.is_valid():
            form.save()
            return redirect('category_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.CategoryForm(instance=cat)

    return render(request, 'budget/category/category_edit.html',
                  {'form': form,
                   'object': cat,
                   'instance_name': 'Categories'})


def category_delete(request, pk):
    cat = models.Category.objects.get(pk=pk)

    if request.method == "POST":
        cat.delete()
        return redirect('category_list')

    return render(request, 'budget/category/category_delete.html',
                  {'object': cat,
                   'instance_name': 'Categories'})


# Transactions

class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Transaction
    context_object_name = 'transaction_list'
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Transactions'
        return context


def transaction_add(request):
    categories = [(cat.id, cat.name) for cat in models.Category.objects.all()]
    accounts = [(acct.id, acct.name) for acct in models.Account.objects.all()]

    if request.method == "POST":
        form = forms.TransactionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('transaction_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.TransactionForm

    return render(request, 'budget/transaction/transaction_create.html',
                  {'form': form,
                   'txn_types': models.Transaction.TRANSACTION_TYPES_CHOICES,
                   'categories': categories,
                   'accounts': accounts,
                   'instance_name': 'Transactions'})


def transaction_edit(request, pk):
    txn = models.Transaction.objects.get(pk=pk)
    categories = [(cat.id, cat.name) for cat in models.Category.objects.all()]
    accounts = [(acct.id, acct.name) for acct in models.Account.objects.all()]

    if request.method == "POST":
        form = forms.TransactionForm(request.POST, instance=txn)

        if form.is_valid():
            form.save()
            return redirect('transaction_list')
        else:
            messages.warning(request, "Something went wrong!")
    else:
        form = forms.TransactionForm(instance=txn)

    return render(request, 'budget/transaction/transaction_edit.html',
                  {'form': form,
                   'object': txn,
                   'txn_types': models.Transaction.TRANSACTION_TYPES_CHOICES,
                   'categories': categories,
                   'accounts': accounts,
                   'instance_name': 'Transactions'})


def transaction_delete(request, pk):
    txn = models.Transaction.objects.get(pk=pk)

    if request.method == "POST":
        txn.delete()
        return redirect('transaction_list')

    return render(request, 'budget/transaction/transaction_delete.html',
                  {'object': txn,
                   'instance_name': 'Transactions'})


# Dashboard
def dashboard(request):
    class DataByAccount:
        data = [acct.balance for acct in models.Account.objects.all()]
        labels = [acct.name for acct in models.Account.objects.all()]
        colors = [acct.color for acct in models.Account.objects.all()]

    class DataByCategory:
        transactions_by_category = models.Transaction.objects.values('category__name').annotate(
            total_amount=Sum('amount'))

        data = [item['total_amount'] for item in transactions_by_category]
        labels = [item['category__name'] for item in transactions_by_category]
        colors = [cat.color for cat in models.Category.objects.all()]

    return render(request, 'budget/dashboard.html',
                  {'instance_name': 'Dashboard',
                   'data_acct': DataByAccount,
                   'data_cat': DataByCategory,
                   })
