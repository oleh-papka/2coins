from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

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


class CurrencyCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Currency
    form_class = forms.CurrencyForm
    template_name = 'budget/currency/currency_create.html'
    success_url = reverse_lazy('currency_list')

    def form_valid(self, form):
        messages.success(self.request, f"Currency '{form.cleaned_data.get('name')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acct_types'] = models.Currency.MONEY_TYPES_CHOICES
        return context


class CurrencyUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Currency
    form_class = forms.CurrencyForm
    template_name = 'budget/currency/currency_edit.html'
    success_url = reverse_lazy('currency_list')

    def form_valid(self, form):
        messages.success(self.request, f"Currency '{form.cleaned_data.get('name')}' updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acct_types'] = models.Currency.MONEY_TYPES_CHOICES
        return context


class CurrencyDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Currency
    template_name = 'budget/currency/currency_delete.html'
    success_url = reverse_lazy('currency_list')

    def form_valid(self, form):
        messages.success(self.request, f"Currency '{self.object.name}' deleted!")
        return super().form_valid(form)


# Accounts

class AccountListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Account
    template_name = "budget/account/account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Accounts'

        accounts = self.object_list
        for account in accounts:
            txn_sum = models.Transaction.objects.filter(account=account).aggregate(Sum('amount'))['amount__sum']
            txn_sum = 0 if txn_sum is None else txn_sum
            account.total = account.balance + txn_sum

        context['accounts_list'] = accounts

        return context

    def get_queryset(self):
        profile = models.Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class AccountDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = models.Account
    template_name = 'budget/account/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        txn_sum = models.Transaction.objects.filter(account=self.object).aggregate(Sum('amount'))['amount__sum']
        txn_sum = 0 if txn_sum is None else txn_sum
        self.object.total = self.object.balance + txn_sum

        transaction_dict = defaultdict(list)
        transactions = models.Transaction.objects.filter(account=self.object).order_by('-date').annotate(
            truncated_date=TruncDate('date'))

        for transaction in transactions:
            transaction_dict[transaction.truncated_date].append(transaction)

        res = dict()
        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount for i in v]), 'txns': v}

        context['transaction_dict'] = dict(res)

        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountForm
    template_name = 'budget/account/account_create.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = models.Profile.objects.get(user=self.request.user)
        self.object.save()
        messages.success(self.request, f"Account '{form.cleaned_data.get('name')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = [(curr.id, curr.abbr, curr.symbol) for curr in models.Currency.objects.all()]
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountForm
    template_name = 'budget/account/account_edit.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        messages.success(self.request, f"Account '{form.cleaned_data.get('name')}' updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = [(curr.id, curr.abbr, curr.symbol) for curr in models.Currency.objects.all()]
        return context


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Account
    template_name = 'budget/account/account_delete.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        messages.success(self.request, f"Account '{self.object.name}' deleted!")
        return super().form_valid(form)


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

    def get_queryset(self):
        profile = models.Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class CategoryDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = models.Category
    template_name = "budget/category/category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_dict = defaultdict(list)
        transactions = self.get_object().get_transactions_by_category(self.request.user).annotate(
            truncated_date=TruncDate('date'))

        for transaction in transactions:
            transaction_dict[transaction.truncated_date].append(transaction)

        res = dict()
        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount for i in v]), 'txns': v}

        context['transaction_dict'] = dict(res)

        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'budget/category/category_create.html'
    success_url = reverse_lazy('category_list')

    def get_initial(self):
        initial = super().get_initial()

        if cat_type := self.request.GET.get('cat_type'):
            initial['cat_type'] = '-' if cat_type == 'expense' else '+'

        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = models.Profile.objects.get(user=self.request.user)
        self.object.save()
        messages.success(self.request, f"Category '{form.cleaned_data.get('name')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'budget/category/category_edit.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f"Category '{form.cleaned_data.get('name')}' updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Category
    template_name = 'budget/category/category_delete.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, f"Category '{self.object.name}' deleted!")
        return super().form_valid(form)


# Transactions

class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Transaction
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_dict = defaultdict(list)
        transactions = models.Transaction.objects.filter(account__profile__user=self.request.user).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        for transaction in transactions:
            transaction_dict[transaction.truncated_date].append(transaction)

        res = dict()
        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount for i in v]), 'txns': v}

        context['transaction_dict'] = dict(res)
        return context

    def get_queryset(self):
        profile = models.Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(account__profile=profile)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_create.html'
    success_url = reverse_lazy('transaction_list')

    def get_initial(self):
        initial = super().get_initial()

        if cat_id := self.request.GET.get('category'):
            cat = models.Category.objects.get(id=cat_id)
            initial['category'] = cat.name

        if acct_id := self.request.GET.get('account'):
            acct = models.Account.objects.get(id=acct_id)
            initial['account'] = acct.name

        return initial

    def form_valid(self, form):
        messages.success(self.request, f"Transaction '{form.cleaned_data.get('amount')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if cat_id := self.request.GET.get('category'):
            cat = models.Category.objects.get(id=cat_id)
            context['category'] = cat

        if acct_id := self.request.GET.get('account'):
            acct = models.Account.objects.get(id=acct_id)
            context['account'] = acct

        context['categories'] = [(cat.id, cat.name) for cat in
                                 models.Category.objects.filter(profile__user=self.request.user).all()]
        context['accounts'] = [(acct.id, acct.name) for acct in
                               models.Account.objects.filter(profile__user=self.request.user).all()]

        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_edit.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        messages.success(self.request, f"Transaction '{form.cleaned_data.get('amount')}' updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = [(cat.id, cat.name) for cat in
                                 models.Category.objects.filter(profile__user=self.request.user).all()]
        context['accounts'] = [(acct.id, acct.name) for acct in
                               models.Account.objects.filter(profile__user=self.request.user).all()]
        context['txn_types'] = models.Transaction.TRANSACTION_TYPES_CHOICES

        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    template_name = 'budget/transaction/transaction_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        messages.success(self.request, f"Transaction '{self.object.amount}' deleted!")
        return super().form_valid(form)


# Dashboard

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'budget/dashboard.html'

    def get_context_data(self, **kwargs):
        data_acct = {
            'data': [acct.balance for acct in models.Account.objects.filter(profile__user=self.request.user).all()],
            'labels': [acct.name for acct in models.Account.objects.filter(profile__user=self.request.user).all()],
            'colors': [acct.color for acct in models.Account.objects.filter(profile__user=self.request.user).all()]
        }

        transactions_by_category = models.Transaction.objects.values('category__name').annotate(
            total_amount=Sum('amount'))

        data_cat = {
            'data': [item['total_amount'] for item in transactions_by_category],
            'labels': [item['category__name'] for item in transactions_by_category],
            'colors': [cat.color for cat in models.Category.objects.all()]
        }

        context = super().get_context_data(**kwargs)
        context['data_acct'] = data_acct
        context['data_cat'] = data_cat

        return context
