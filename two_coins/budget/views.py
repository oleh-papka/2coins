import operator

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.db.models.functions import TruncDate
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from misc.utils import get_date_range, get_combined_actions, add_transfer_messages
from misc.view_mixins import FormInvalidMixin, TransferMixin
from profiles.models import Profile
from . import forms, models
from .models import Transaction, Transfer, Category
from .templatetags.number_filters import strip_trailing_zeros


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

        start_date, end_date = get_date_range(self.request.GET.get('start_date'), self.request.GET.get('end_date'))

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'
        context["combined_actions"] = get_combined_actions(start_date=start_date,
                                                           end_date=end_date,
                                                           account_id=self.object.id)
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
        return redirect(success_url)


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

        start_date, end_date = get_date_range(self.request.GET.get('start_date'),
                                              self.request.GET.get('end_date'))

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'
        context["transactions"] = get_combined_actions(user_id=self.request.user.id,
                                                       start_date=start_date,
                                                       end_date=end_date,
                                                       category_id=self.object.id)

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
        return redirect(success_url)


# Transactions

class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Transaction
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date, end_date = get_date_range(self.request.GET.get('start_date'), self.request.GET.get('end_date'))

        context["date_range"] = f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'
        context["combined_actions"] = get_combined_actions(user_id=self.request.user.id,
                                                           start_date=start_date,
                                                           end_date=end_date,
                                                           all_transfers=True)
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

        context['category_list'] = list(
            models.Category.objects.filter(profile__user=self.request.user).all().values('id', 'name', 'category_type'))

        if category_id := self.request.GET.get('category'):
            category = models.Category.objects.get(id=category_id)
            context['category'] = category

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

        return context

    def form_valid(self, form):
        account = form.cleaned_data.get('account')
        currency = form.cleaned_data.get('currency')
        amount = form.cleaned_data.get('amount') if account.currency == currency else form.cleaned_data.get(
            'amount_converted')

        if form.cleaned_data.get("category").category_type == '+':
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
        if prev_transaction.category.category_type == Category.EXPENSE:
            prev_transaction.account.balance = prev_transaction.account.balance + prev_transaction_amount
        else:
            prev_transaction.account.balance = prev_transaction.account.balance - prev_transaction_amount

        prev_transaction.account.save()

        # Updating account balance
        new_transaction.account.refresh_from_db()
        new_transaction_amount = abs(new_transaction.amount_converted or new_transaction.amount)
        if new_transaction.category.category_type == Category.EXPENSE:
            new_transaction.account.balance = new_transaction.account.balance - new_transaction_amount
        else:
            new_transaction.account.balance = new_transaction.account.balance + new_transaction_amount

        new_transaction.account.save()

        messages.success(self.request,
                         f"Transaction {strip_trailing_zeros(new_transaction.amount)} {new_transaction.account.currency.symbol} updated!")
        if prev_transaction.account == new_transaction.account:
            messages.info(self.request,
                          f'Updated balance of {new_transaction.account.name} account!\nYour balance is {strip_trailing_zeros(new_transaction.account.balance)} {new_transaction.account.currency.symbol}')
        else:
            messages.info(self.request,
                          f'Updated balance of {prev_transaction.account.name} account ({strip_trailing_zeros(prev_transaction.account.balance)} {prev_transaction.account.currency.symbol});\n'
                          f'Updated balance of {new_transaction.account.name} account ({strip_trailing_zeros(new_transaction.account.balance)} {new_transaction.account.currency.symbol}) ')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['category_list'] = list(
            models.Category.objects.filter(profile__user=self.request.user).all().values('id', 'name', 'category_type'))
        context['account_list'] = list(models.Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr',
                                                          'currency__symbol'))  # to pass values to JS

        context['profile'] = Profile.objects.get(user=self.request.user)
        context['currency_list'] = models.Currency.objects.all()

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
        if transaction.category.category_type == Category.EXPENSE:
            transaction.account.balance += transaction_amount
        else:
            transaction.account.balance -= transaction_amount
        transaction.account.save()

        messages.success(self.request,
                         f"Transaction {strip_trailing_zeros(self.object.amount)} {self.object.currency.symbol} deleted!")
        messages.info(self.request,
                      f'Updated balance of {transaction.account.name} account!\nYour new balance is {strip_trailing_zeros(transaction.account.balance)} {transaction.account.currency.symbol}')

        return super().form_valid(form)


# Transfers


class TransferCreateView(LoginRequiredMixin, FormInvalidMixin, TransferMixin, CreateView):
    template_name = 'budget/transfer/transfer_create.html'

    def form_valid(self, form):
        account_from = form.cleaned_data.get('account_from')
        account_to = form.cleaned_data.get('account_to')
        amount_from = form.cleaned_data.get('amount_from')
        amount_to = form.cleaned_data.get('amount_to') or amount_from

        with db_transaction.atomic():
            self.object = form.save()

            account_from.balance -= amount_from
            account_from.save(update_fields=['balance'])

            account_to.balance += amount_to
            account_to.save(update_fields=['balance'])

            add_transfer_messages(self.request, account_from, account_to)

        return redirect(self.get_success_url())


class TransferUpdateView(LoginRequiredMixin, FormInvalidMixin, TransferMixin, UpdateView):
    template_name = 'budget/transfer/transfer_edit.html'

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

            add_transfer_messages(self.request, account_from, account_to)

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
