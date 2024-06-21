from collections import defaultdict
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, FloatField
from django.db.models.functions import TruncDate, Coalesce, Cast
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from misc.models import StylingFormUpdateMixin
from profiles.models import Profile
from . import forms, models
from .models import Styling, Transaction


def get_template_chart_data(query_data):
    res = {'data': [], 'labels': []}
    for dct in query_data:
        for k in dct.keys():
            res[k].append(dct[k])
    return res


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
            .values('data', 'labels')
        )

        context = super().get_context_data(**kwargs)
        context['accounts_list'] = self.object_list
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
        transactions_data = models.Transaction.objects.filter(account=self.object).order_by('-date').annotate(
            truncated_date=TruncDate('date'))
        category_ids = models.Category.objects.filter(profile__user=self.request.user).values_list('id', flat=True)
        categories_data = models.Category.objects.filter(profile__user=self.request.user).filter(id__in=category_ids)
        transactions = []

        temp_date = transactions_data[0].truncated_date if transactions_data else None
        temp_total = 0
        temp_txns = []

        categories = {}
        for cat in categories_data:
            categories[cat] = {
                "label": cat.name,
                "data": [0],
                "backgroundColor": str(cat.styling.color) + '2a',
                "borderColor": str(cat.styling.color),
                "borderWidth": 2,
                "borderRadius": 5,
            }

        for txn in transactions_data:
            if txn.truncated_date != temp_date:
                transactions.append({
                    'date': temp_date,
                    'total': temp_total,
                    'txns': temp_txns
                })

                temp_date = txn.truncated_date
                temp_total = 0
                temp_txns = [txn]

                for cat, data in categories.items():
                    if cat == txn.category:
                        data['data'].append(txn.amount_account_currency if txn.amount_account_currency else txn.amount)
                    else:
                        data['data'].append(0)
            else:
                temp_txns.append(txn)

                for cat, data in categories.items():
                    if cat == txn.category:
                        data['data'][-1] += txn.amount_account_currency if txn.amount_account_currency else txn.amount

            if txn.amount_account_currency:
                amount = txn.amount_account_currency
            else:
                amount = txn.amount

            temp_total += amount

        else:
            if transactions_data:
                transactions.append({
                    'date': temp_date,
                    'total': temp_total,
                    'txns': temp_txns
                })

        data_acct_query = (
            models.Category.objects
            .filter(profile__user=self.request.user)
            .filter(transaction__account=self.object)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .values('data', 'labels')
        )

        for i in categories.values():
            i["data"] = i["data"][::-1]

        context["data_txn"] = {
            "labels": [i['date'].strftime("%d/%m") for i in transactions][::-1],
            "datasets": [i for i in categories.values()]
        }

        context['data_acct'] = get_template_chart_data(data_acct_query)
        context["transactions"] = transactions

        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountForm
    template_name = 'budget/account/account_create.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        account = form.save(commit=False)
        account.profile = Profile.objects.get(user=self.request.user)
        account.styling = Styling.get_or_create_styling(color=form.cleaned_data.get('color'),
                                                        icon=form.cleaned_data.get('icon'))

        if not account.initial_balance:
            account.initial_balance = account.balance

        account.save()

        account_name = form.cleaned_data.get('name')
        messages.success(self.request, f"Account '{account_name}' created!")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

        return context


class AccountUpdateView(LoginRequiredMixin, StylingFormUpdateMixin):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountForm
    template_name = 'budget/account/account_edit.html'
    success_url = reverse_lazy('account_list')

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currencies'] = models.Currency.objects.all()

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

        income_data = (
            models.Category.objects
            .filter(profile__user=self.request.user, category_type=models.Category.INCOME)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .values('data', 'labels')
        )
        expense_data = (
            models.Category.objects
            .filter(profile__user=self.request.user, category_type=models.Category.EXPENSE)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .values('data', 'labels')
        )

        context['data_income'] = get_template_chart_data(income_data)
        context['data_expense'] = get_template_chart_data(expense_data)

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
        transactions = Transaction.objects.filter(category=self.object,
                                                  account__profile__user=self.request.user).order_by('-date').annotate(
            truncated_date=TruncDate('date'))

        for transaction in transactions:
            transaction_dict[transaction.truncated_date].append(transaction)

        res = dict()
        data_cat = {'data': [], 'labels': []}

        for k, v in dict(transaction_dict).items():
            res[k] = {'total': sum([i.amount_default_currency if i.amount_default_currency else i.amount for i in v]),
                      'txns': v}
            data_cat['data'].append(abs(res[k]['total']))
            data_cat['labels'].append(k.strftime("%d/%m"))

        data_cat['data'].reverse()
        data_cat['labels'].reverse()

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

        if category_type := self.request.GET.get('category_type'):
            initial['category_type'] = '-' if category_type == 'expense' else '+'

        return initial

    def form_valid(self, form):
        category = form.save(commit=False)
        category.profile = Profile.objects.get(user=self.request.user)
        category.styling = Styling.get_or_create_styling(color=form.cleaned_data.get('color'),
                                                         icon=form.cleaned_data.get('icon'))
        category.save()

        category_name = form.cleaned_data.get('name')
        messages.success(self.request, f"Category '{category_name}' created!")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, StylingFormUpdateMixin):
    login_url = reverse_lazy('login')
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'budget/category/category_edit.html'
    success_url = reverse_lazy('category_list')

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
        transactions_data = models.Transaction.objects.filter(account__profile__user=self.request.user).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))
        category_ids = models.Transaction.objects.filter(account__profile__user=self.request.user).values_list(
            'category', flat=True).distinct()
        categories_data = models.Category.objects.filter(profile__user=self.request.user).filter(id__in=category_ids)
        transactions = []

        temp_date = transactions_data[0].truncated_date if transactions_data else datetime.now()
        temp_total = 0
        temp_txns = []

        categories = {}
        for cat in categories_data:
            categories[cat] = {
                "label": cat.name,
                "data": [0],
                "backgroundColor": str(cat.styling.color) + '2a',
                "borderColor": str(cat.styling.color),
                "borderWidth": 2,
                "borderRadius": 5,
            }

        for txn in transactions_data:
            if txn.truncated_date != temp_date:
                transactions.append({
                    'date': temp_date,
                    'total': temp_total,
                    'txns': temp_txns
                })

                temp_date = txn.truncated_date
                temp_total = 0
                temp_txns = [txn]

                for cat, data in categories.items():
                    if cat == txn.category:
                        data['data'].append(txn.amount_account_currency if txn.amount_account_currency else txn.amount)
                    else:
                        data['data'].append(0)
            else:
                temp_txns.append(txn)

                for cat, data in categories.items():
                    if cat == txn.category:
                        data['data'][-1] += txn.amount_account_currency if txn.amount_account_currency else txn.amount

            if txn.amount_account_currency:
                amount = txn.amount_account_currency
            else:
                amount = txn.amount

            temp_total += amount
        else:
            transactions.append({
                'date': temp_date,
                'total': temp_total,
                'txns': temp_txns
            })

        for i in categories.values():
            i["data"] = i["data"][::-1]

        context["data_txn"] = {
            "labels": [i['date'].strftime("%d/%m") for i in transactions][::-1],
            "datasets": [i for i in categories.values()]
        }
        context["transactions"] = transactions

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
        account = form.cleaned_data.get('account')
        amount = form.cleaned_data.get('amount') if account.currency == form.cleaned_data.get(
            'currency') else form.cleaned_data.get('amount_account_currency')

        account.balance += abs(amount) if form.cleaned_data.get('transaction_type') == Transaction.INCOME else -abs(
            amount)
        account.save()

        messages.success(self.request, f"Transaction '{form.cleaned_data.get('amount')}' created!")
        messages.info(self.request, f'Updated balance of account!\nYour new balance is {account.balance}')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if cat_id := self.request.GET.get('category'):
            cat = models.Category.objects.get(id=cat_id)
            context['category'] = cat
        else:
            context['categories'] = [(cat.id, cat.name) for cat in
                                     models.Category.objects.filter(profile__user=self.request.user).all() if
                                     cat.category_type in models.Category.CATEGORY_TYPES]

        if acct_id := self.request.GET.get('account'):
            acct = models.Account.objects.get(id=acct_id)
            context['account'] = acct
            current_account_currency = acct.currency
            context['currency'] = current_account_currency

        context['accounts'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr', 'currency__symbol'))

        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)
        context['transaction_type'] = models.Transaction.TRANSACTION_TYPE_CHOICES

        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_edit.html'
    success_url = reverse_lazy('transaction_list')

    def get_initial(self):
        initial = super().get_initial()

        initial['amount'] = abs(self.object.amount)
        if self.object.amount_account_currency:
            initial['amount_account_currency'] = abs(self.object.amount_account_currency)

        return initial

    def form_valid(self, form):
        prev_transaction = Transaction.objects.get(pk=form.instance.pk)
        new_transaction = form.instance

        # Reverting account balance
        prev_transaction_amount = abs(prev_transaction.amount_account_currency or prev_transaction.amount)
        if prev_transaction.transaction_type == Transaction.EXPENSE:
            prev_transaction.account.balance += prev_transaction_amount
        else:
            prev_transaction.account.balance -= prev_transaction_amount
        prev_transaction.account.save()

        # Updating account balance
        new_transaction.account.refresh_from_db()
        new_transaction_amount = abs(new_transaction.amount_account_currency or new_transaction.amount)
        if new_transaction.transaction_type == Transaction.INCOME:
            new_transaction.account.balance += new_transaction_amount
        else:
            new_transaction.account.balance -= new_transaction_amount
        new_transaction.account.save()

        messages.success(self.request, f"Transaction updated!")
        messages.info(self.request,
                      f'Updated balance of account!\nYour new balance is {new_transaction.account.balance}')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = [(cat.id, cat.name) for cat in
                                 models.Category.objects.filter(profile__user=self.request.user).all()]
        context['accounts'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr', 'currency__symbol'))

        context['currencies'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)
        context['transaction_type'] = models.Transaction.TRANSACTION_TYPE_CHOICES

        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    template_name = 'budget/transaction/transaction_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        transaction = self.get_object()

        # Reverting account balance
        transaction_amount = abs(transaction.amount_account_currency or transaction.amount)
        if transaction.transaction_type == Transaction.EXPENSE:
            transaction.account.balance += transaction_amount
        else:
            transaction.account.balance -= transaction_amount
        transaction.account.save()

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
            .values('labels', 'data')
        )

        data_acct_query = (
            models.Account.objects
            .filter(profile__user=self.request.user)
            .annotate(
                data=Coalesce(Sum('transaction__amount'), 0.0) + Cast(F('balance'), output_field=FloatField())
            )
            .annotate(labels=F('name'))
            .values('data', 'labels')
        )

        last_txns = models.Transaction.objects.filter(account__profile__user=self.request.user).order_by('date')[:5]

        context = super().get_context_data(**kwargs)
        context['last_txns'] = last_txns
        context['data_acct'] = get_template_chart_data(data_acct_query)
        context['data_cat'] = get_template_chart_data(data_cat_query)

        return context
