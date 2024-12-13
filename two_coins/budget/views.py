import operator
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.db.models import Sum, F, FloatField, Q
from django.db.models.functions import TruncDate, Coalesce, Cast
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from misc.models import FormInvalidMixin
from misc.utils import get_current_month_dates
from profiles.models import Profile
from . import forms, models
from .models import Transaction, Transfer
from .templatetags.number_filters import strip_trailing_zeros


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

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class AccountDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = models.Account
    template_name = 'budget/account/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if not start_date and not end_date:
            start_date, end_date = get_current_month_dates()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Include the full last day
            end_date = datetime.combine(end_date, datetime.max.time())

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'

        transactions_queryset = models.Transaction.objects.filter(account=self.object,
                                                                  date__range=(start_date, end_date)).order_by(
            '-date').annotate(
            truncated_date=TruncDate('date'))
        transfers_queryset = models.Transfer.objects.filter(
            Q(account_to=self.object) | Q(account_from=self.object),
            date__range=(start_date, end_date)).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        transfers_list = list(transfers_queryset)
        transactions_list = list(transactions_queryset)

        combined_list = transactions_list + transfers_list

        combined_list.sort(key=operator.attrgetter('date'), reverse=True)

        if not combined_list:
            return context

        for action in combined_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'
            action.action_type = action_type

        context["combined_actions"] = combined_list

        return context


class AccountCreateView(LoginRequiredMixin, FormInvalidMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountCreateForm
    template_name = 'budget/account/account_create.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        account = form.save(commit=False)
        account.profile = Profile.objects.get(user=self.request.user)
        account.save()
        messages.success(self.request, f"Account {account.name} created!")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_list'] = models.Currency.objects.all()
        return context


class AccountUpdateView(LoginRequiredMixin, FormInvalidMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Account
    form_class = forms.AccountUpdateForm
    template_name = 'budget/account/account_edit.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        messages.success(self.request, f"Account {form.cleaned_data.get('name')} updated!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_list'] = models.Currency.objects.all()
        return context


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Account
    template_name = 'budget/account/account_delete.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()

        messages.success(self.request, f"Account {self.object.name} deleted!")
        return HttpResponseRedirect(success_url)


# Categories

class CategoryList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Category
    context_object_name = 'category_list'
    template_name = "budget/category/category_list.html"

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class CategoryDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = models.Category
    template_name = "budget/category/category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if not start_date and not end_date:
            start_date, end_date = get_current_month_dates()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Include the full last day
            end_date = datetime.combine(end_date, datetime.max.time())

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'

        transactions_queryset = models.Transaction.objects.filter(category=self.object,
                                                                  account__profile__user=self.request.user,
                                                                  date__range=(start_date, end_date)).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        transactions_list = list(transactions_queryset)

        if not transactions_list:
            return context

        for action in transactions_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'
            action.action_type = action_type

        context["transactions"] = transactions_list

        return context


class CategoryCreateView(LoginRequiredMixin, FormInvalidMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'budget/category/category_create.html'
    success_url = reverse_lazy('category_list')

    def get_initial(self):
        initial = super().get_initial()

        if category_type := self.request.GET.get('category_type'):
            initial['category_type'] = '-' if category_type == '-' else '+'

        return initial

    def form_valid(self, form):
        category = form.save(commit=False)
        category.profile = Profile.objects.get(user=self.request.user)

        category.save()
        messages.success(self.request, f"Category {category.name} created!")

        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, FormInvalidMixin, UpdateView):
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
        success_url = self.get_success_url()
        self.object.delete()

        messages.success(self.request, f"Category {self.object.name} deleted!")
        return HttpResponseRedirect(success_url)


# Transactions

class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Transaction
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if not start_date and not end_date:
            start_date, end_date = get_current_month_dates()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Include the full last day
            end_date = datetime.combine(end_date, datetime.max.time())

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'

        transactions_queryset = models.Transaction.objects.filter(
            account__profile__user=user,
            date__range=(start_date, end_date)
        ).order_by('-date').annotate(truncated_date=TruncDate('date'))

        transfers_queryset = models.Transfer.objects.filter(
            account_from__profile__user=user,
            date__range=(start_date, end_date)
        ).order_by('-date').annotate(truncated_date=TruncDate('date'))

        transfers_list = list(transfers_queryset)
        transactions_list = list(transactions_queryset)

        combined_list = transactions_list + transfers_list

        combined_list.sort(key=operator.attrgetter('date'), reverse=True)

        if not combined_list:
            return context

        for action in combined_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'
            action.action_type = action_type

        context["combined_actions"] = combined_list

        return context

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(account__profile=profile)


class TransactionCreateView(LoginRequiredMixin, FormInvalidMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_create.html'
    success_url = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category_list'] = models.Category.objects.filter(profile__user=self.request.user).all()

        if category_id := self.request.GET.get('category'):
            category = models.Category.objects.get(id=category_id)
            context['category'] = category
            context[
                'transaction_type'] = models.Transaction.INCOME if category.category_type == models.Category.INCOME else models.Transaction.EXPENSE

        if account_id := self.request.GET.get('account'):
            account = models.Account.objects.get(id=account_id)
            context['account'] = account
            context['currency'] = account.currency

        context['profile'] = Profile.objects.get(user=self.request.user)
        context['account_list'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr',
                                                          'currency__symbol'))  # to pass values to JS
        context['currency_list'] = models.Currency.objects.all()
        context['transaction_type_list'] = models.Transaction.TRANSACTION_TYPE_CHOICES

        return context

    def form_valid(self, form):
        account = form.cleaned_data.get('account')
        currency = form.cleaned_data.get('currency')
        amount = form.cleaned_data.get('amount') if account.currency == currency else form.cleaned_data.get(
            'amount_converted')

        if form.cleaned_data.get('transaction_type') == Transaction.INCOME:
            account.deposit(amount)
        else:
            account.withdraw(amount)

        messages.success(self.request, f"Transaction {strip_trailing_zeros(amount)} {currency.symbol} created!")
        messages.info(self.request,
                      f'Updated balance of {account.name} account!\nYour balance is {strip_trailing_zeros(account.balance)} {account.currency.symbol}')

        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, FormInvalidMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_edit.html'
    success_url = reverse_lazy('transaction_list')

    def get_initial(self):
        initial = super().get_initial()

        initial['amount'] = abs(self.object.amount)
        if self.object.amount_converted:
            initial['amount_converted'] = abs(self.object.amount_converted)

        return initial

    def form_valid(self, form):
        prev_transaction = Transaction.objects.get(pk=form.instance.pk)
        new_transaction = form.instance

        # Reverting account balance
        prev_transaction_amount = abs(prev_transaction.amount_converted or prev_transaction.amount)
        if prev_transaction.transaction_type == Transaction.EXPENSE:
            prev_transaction.account.balance = prev_transaction.account.balance + prev_transaction_amount
        else:
            prev_transaction.account.balance = prev_transaction.account.balance - prev_transaction_amount
        prev_transaction.account.save()

        # Updating account balance
        new_transaction.account.refresh_from_db()
        new_transaction_amount = abs(new_transaction.amount_converted or new_transaction.amount)
        if new_transaction.transaction_type == Transaction.INCOME:
            new_transaction.account.balance = new_transaction.account.balance + new_transaction_amount
        else:
            new_transaction.account.balance = new_transaction.account.balance - new_transaction_amount
        new_transaction.account.save()

        messages.success(self.request, f"Transaction updated!")
        messages.info(self.request,
                      f'Updated balance of account!\nYour balance is {strip_trailing_zeros(new_transaction.account.balance)} {new_transaction.account.currency.symbol}')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category_list'] = models.Category.objects.filter(profile__user=self.request.user).all()
        context['account_list'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr',
                                                          'currency__symbol'))  # to pass values to JS

        context['profile'] = Profile.objects.get(user=self.request.user)
        context['currency_list'] = models.Currency.objects.all()
        context['transaction_type_list'] = models.Transaction.TRANSACTION_TYPE_CHOICES

        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    template_name = 'budget/transaction/transaction_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        transaction = self.get_object()

        # Reverting account balance
        transaction_amount = abs(transaction.amount_converted or transaction.amount)
        if transaction.transaction_type == Transaction.EXPENSE:
            transaction.account.balance += transaction_amount
        else:
            transaction.account.balance -= transaction_amount
        transaction.account.save()

        messages.success(self.request,
                         f"Transaction {strip_trailing_zeros(self.object.amount)} {self.object.currency.symbol} deleted!")
        messages.info(self.request,
                      f'Updated balance of account!\nYour new balance is {strip_trailing_zeros(transaction.account.balance)} {transaction.account.currency.symbol}')

        return super().form_valid(form)


# Transfers

class TransferCreateView(LoginRequiredMixin, FormInvalidMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Transfer
    form_class = forms.TransferForm
    template_name = 'budget/transfer/transfer_create.html'
    success_url = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if account_id := self.request.GET.get('account'):
            context['account_from'] = models.Account.objects.get(id=account_id)

        context['account_list'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr', 'currency__symbol'))

        context['currency_list'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

        return context

    def form_valid(self, form):
        account_from = form.cleaned_data.get('account_from')
        account_to = form.cleaned_data.get('account_to')
        amount_from = form.cleaned_data.get('amount_from')
        amount_to = form.cleaned_data.get('amount_to') or amount_from

        with db_transaction.atomic():
            self.object = form.save()

            account_from.balance -= amount_from
            account_from.save()

            account_to.balance += amount_to
            account_to.save()

            messages.success(self.request, f"Transfer {account_from.name}->{account_to.name} done!")
            messages.info(self.request,
                          f"Updated balance of {account_from.name} account!\nYour balance is {strip_trailing_zeros(account_from.balance)} {account_from.currency.symbol}")

            messages.info(self.request,
                          f"Updated balance of {account_to.name} account!\nYour balance is {strip_trailing_zeros(account_to.balance)} {account_to.currency.symbol}")

        return HttpResponseRedirect(self.get_success_url())


class TransferUpdateView(LoginRequiredMixin, FormInvalidMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = models.Transfer
    form_class = forms.TransferForm
    template_name = 'budget/transfer/transfer_edit.html'
    success_url = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if account_id := self.request.GET.get('account'):
            context['account_from'] = models.Account.objects.get(id=account_id)

        context['account_list'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr', 'currency__symbol'))

        context['currency_list'] = models.Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

        return context

    def form_valid(self, form):
        prev_transfer = Transfer.objects.get(pk=form.instance.pk)
        new_transfer = form.instance

        # Reverting account balance
        amount_to = prev_transfer.amount_to if prev_transfer.amount_to else prev_transfer.amount_from
        prev_transfer.account_from.balance += prev_transfer.amount_from
        prev_transfer.account_to.balance -= amount_to

        prev_transfer.account_from.save()
        prev_transfer.account_to.save()

        account_from = form.cleaned_data.get('account_from')
        account_to = form.cleaned_data.get('account_to')
        amount_from = form.cleaned_data.get('amount_from')
        amount_to = form.cleaned_data.get('amount_to') or amount_from

        # Updating account balance
        new_transfer.account_from.refresh_from_db()
        new_transfer.account_to.refresh_from_db()

        with db_transaction.atomic():
            new_transfer.account_from.balance -= amount_from
            new_transfer.account_from.save()

            new_transfer.account_to.balance += amount_to
            new_transfer.account_to.save()

            messages.success(self.request, f"Transfer {account_from.name}->{account_to.name} updated!")
            messages.info(self.request,
                          f"Updated balance of {account_from.name} account!\nYour balance is {strip_trailing_zeros(account_from.balance)} {account_from.currency.symbol}")

            messages.info(self.request,
                          f"Updated balance of {account_to.name} account!\nYour balance is {strip_trailing_zeros(account_to.balance)} {account_to.currency.symbol}")

        return super().form_valid(form)


class TransferDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Transfer
    template_name = 'budget/transfer/transfer_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        transfer = self.get_object()

        # Reverting account balance
        amount_to = transfer.amount_to if transfer.amount_to else transfer.amount_from
        transfer.account_from.balance += transfer.amount_from
        transfer.account_to.balance -= amount_to

        transfer.account_from.save()
        transfer.account_to.save()

        messages.success(self.request, f"Transfer deleted!")
        messages.info(self.request,
                      f"Updated balance of {transfer.account_from.name} account!\nYour balance is {strip_trailing_zeros(transfer.account_from.balance)} {transfer.account_from.currency.symbol}")

        messages.info(self.request,
                      f"Updated balance of {transfer.account_to.name} account!\nYour balance is {strip_trailing_zeros(transfer.account_to.balance)} {transfer.account_to.currency.symbol}")

        return super().form_valid(form)


# Dashboard

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'budget/dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        data_cat_query = (
            models.Category.objects
            .filter(profile__user=user)
            .annotate(data=Coalesce(Sum('transaction__amount'), 0.0))
            .annotate(labels=F('name'))
            .values('labels', 'data')
        )

        data_acct_query = (
            models.Account.objects
            .filter(profile__user=user)
            .annotate(
                data=Coalesce(Sum('transaction__amount'), 0.0) + Cast(F('balance'), output_field=FloatField())
            )
            .annotate(labels=F('name'))
            .values('data', 'labels')
        )

        transactions_list = list(models.Transaction.objects.filter(
            account__profile__user=user
        ).order_by('-date').annotate(truncated_date=TruncDate('date')))[:5]

        transfers_list = list(models.Transfer.objects.filter(
            account_from__profile__user=user
        ).order_by('-date').annotate(truncated_date=TruncDate('date')))[:5]

        combined_list = transactions_list + transfers_list

        combined_list.sort(key=operator.attrgetter('date'), reverse=True)
        combined_list = combined_list[:5]

        if not combined_list:
            return context

        for action in combined_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'
            action.action_type = action_type

        context["combined_actions"] = combined_list

        return context
