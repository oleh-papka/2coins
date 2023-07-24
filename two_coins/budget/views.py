import json
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, FloatField
from django.db.models.functions import TruncDate, Coalesce, Cast
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from misc.views import AdminUserRequiredMixin
from . import forms, models
from profiles.models import Profile
from .utils import currency_converter


def get_template_chart_data(query_data):
    res = {'data': [], 'labels': [], 'colors': []}
    for dct in query_data:
        for k in dct.keys():
            res[k].append(dct[k])
    return res


# Currencies

class CurrencyList(LoginRequiredMixin, AdminUserRequiredMixin, ListView):
    login_url = 'login'
    model = models.Currency
    context_object_name = 'currency_list'
    template_name = "budget/currency/currency_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Currencies'
        context['currencies'] = models.Currency.objects.all()
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
        data_acct_query = (
            models.Account.objects
            .filter(profile__user=self.request.user)
            .annotate(
                data=Coalesce(Sum('transaction__amount'), 0.0) + Cast(F('balance'), output_field=FloatField())
            )
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )

        accounts = self.object_list

        for account in accounts:
            txn_sum = models.Transaction.objects.filter(account=account).aggregate(Sum('amount'))['amount__sum']
            account.total = account.balance + txn_sum if txn_sum else account.balance

        context = super().get_context_data(**kwargs)
        context['accounts_list'] = accounts
        context['data_acct'] = get_template_chart_data(data_acct_query)

        return context

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
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
            res[k] = {'total': sum([i.amount_default_currency if i.amount_default_currency else i.amount for i in v]),
                      'txns': v}

        data_acct_query = (
            models.Category.objects
            .filter(profile__user=self.request.user)
            .filter(transaction__account=self.object)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )

        context['transaction_dict'] = dict(res)
        context['data_acct'] = get_template_chart_data(data_acct_query)

        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountForm
    template_name = 'budget/account/account_create.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.profile = Profile.objects.get(user=self.request.user)
        self.object.save()
        messages.success(self.request, f"Account '{form.cleaned_data.get('name')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountUpdateForm
    template_name = 'budget/account/account_edit.html'
    success_url = reverse_lazy('account_list')

    def get_initial(self):
        initial = super().get_initial()

        initial['new_balance'] = (
            models.Account.objects
            .filter(profile__user=self.request.user, pk=self.object.id)
            .annotate(real_balance=Coalesce(Sum(F('transaction__amount')), 0.0) + Cast(F('balance'),
                                                                                       output_field=FloatField()))
            .values('real_balance')
        )[0]['real_balance']

        return initial

    def form_valid(self, form):
        messages.success(self.request, f"Account '{form.cleaned_data.get('name')}' updated!")

        new_balance = form.cleaned_data['new_balance']
        real_balance = (
            models.Account.objects
            .filter(profile__user=self.request.user, pk=self.object.id)
            .annotate(real_balance=Coalesce(Sum(F('transaction__amount')), 0.0) + Cast(F('balance'),
                                                                                       output_field=FloatField()))
            .values('real_balance')
        )[0]['real_balance']

        if new_balance != real_balance:
            txn_amount = new_balance - real_balance

            models.Transaction.objects.create(
                category=models.Category.objects.get(cat_type=models.Category.OTHER),
                account=self.object,
                txn_type=models.Transaction.INCOME if txn_amount > 0 else models.Transaction.EXPENSE,
                amount=txn_amount
            )

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

        income_categories_query = (
            models.Category.objects
            .filter(profile__user=self.request.user, cat_type=models.Category.INCOME)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )
        income_other_query = (
            models.Category.objects
            .filter(profile__user=self.request.user,
                    cat_type=models.Category.OTHER,
                    transaction__txn_type=models.Transaction.INCOME)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )
        expense_categories_query = (
            models.Category.objects
            .filter(profile__user=self.request.user, cat_type=models.Category.EXPENSE)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )
        expense_other_query = (
            models.Category.objects
            .filter(profile__user=self.request.user,
                    cat_type=models.Category.OTHER,
                    transaction__txn_type=models.Transaction.EXPENSE)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )
        data_income = income_categories_query | income_other_query
        data_expense = expense_categories_query | expense_other_query

        context['data_income'] = get_template_chart_data(data_income)
        context['data_expense'] = get_template_chart_data(data_expense)

        return context

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
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
        data_cat = {'data': [], 'labels': []}

        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount_default_currency if i.amount_default_currency else i.amount for i in v]),
                      'txns': v}
            data_cat['data'].append(abs(res[k]['total']))
            data_cat['labels'].append(res[k]['txns'][0].created_at.strftime("%m/%d"))

        data_cat['color'] = self.object.color

        context['transaction_dict'] = dict(res)
        context['data_cat'] = data_cat

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
        self.object.profile = Profile.objects.get(user=self.request.user)
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
        data_txn = {'data': [], 'labels': []}

        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount_default_currency if i.amount_default_currency else i.amount for i in v]),
                      'txns': v}
            data_txn['data'].append(abs(res[k]['total']))
            data_txn['labels'].append(res[k]['txns'][0].created_at.strftime("%m/%d"))

        context['transaction_dict'] = dict(res)
        context['data_txn'] = data_txn
        return context

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
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
            context['currency'] = acct.currency

        context['categories'] = [(cat.id, cat.name) for cat in
                                 models.Category.objects.filter(profile__user=self.request.user).all()]
        context['accounts'] = [(acct.id, acct.name) for acct in
                               models.Account.objects.filter(profile__user=self.request.user).all()]
        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

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
        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

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
        data_cat_query = (
            models.Category.objects
            .filter(profile__user=self.request.user)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('labels', 'colors', 'data')
        )

        data_acct_query = (
            models.Account.objects
            .filter(profile__user=self.request.user)
            .annotate(
                data=Coalesce(Sum('transaction__amount'), 0.0) + Cast(F('balance'), output_field=FloatField())
            )
            .annotate(labels=F('name'))
            .annotate(colors=F('color'))
            .values('data', 'labels', 'colors')
        )

        context = super().get_context_data(**kwargs)
        context['data_acct'] = get_template_chart_data(data_acct_query)
        context['data_cat'] = get_template_chart_data(data_cat_query)

        return context


# Currency converter
def currency_converter_req(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        res = currency_converter(float(data['amount']), data['from_ccy'], data['to_ccy'])

        response_data = {"result": res}
        return JsonResponse(response_data)
