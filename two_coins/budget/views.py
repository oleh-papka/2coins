import operator

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.db.models import Sum, F, FloatField, Q
from django.db.models.functions import TruncDate, Coalesce, Cast
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from misc.models import StyleFormUpdateMixin
from profiles.models import Profile
from . import forms, models
from .models import Transaction, Style, Transfer


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

        transactions_queryset = models.Transaction.objects.filter(account=self.object).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))
        transfers_queryset = models.Transfer.objects.filter(
            Q(account_to=self.object) | Q(account_from=self.object)).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        transfers_list = list(transfers_queryset)
        transactions_list = list(transactions_queryset)

        combined_list = transactions_list + transfers_list

        combined_list.sort(key=operator.attrgetter('date'), reverse=True)

        combined_actions = []

        if not combined_list:
            return context

        temp_date = combined_list[0].truncated_date
        temp_total = 0
        temp_actions = []

        for action in combined_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'

            if action.truncated_date != temp_date:
                combined_actions.append({
                    'date': temp_date,
                    'total': temp_total,
                    'txns': temp_actions
                })

                temp_date = action.truncated_date
                temp_total = 0
                temp_actions = [{"action_type": action_type,
                                 "action": action}]
            else:
                temp_actions.append({"action_type": action_type,
                                     "action": action})

            if action_type == 'txn':
                amount = action.amount_converted if action.amount_converted else action.amount
                temp_total += amount
            else:
                if action.account_from == self.object:
                    temp_total -= action.amount_from
                elif action.account_to == self.object:
                    if action.amount_to:
                        temp_total += action.amount_to
                    else:
                        temp_total += action.amount_from
        else:
            combined_actions.append({
                'date': temp_date,
                'total': temp_total,
                'actions': temp_actions
            })

        context["combined_actions"] = combined_actions

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
        account.style = Style.create_style(color=form.cleaned_data.get('color'),
                                           icon=form.cleaned_data.get('icon'))

        if not account.initial_balance:
            account.initial_balance = account.balance

        account.save()
        messages.success(self.request, f"Account '{account.name}' created!")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_list'] = models.Currency.objects.all()
        return context


class AccountUpdateView(LoginRequiredMixin, StyleFormUpdateMixin):
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
        context['currency_list'] = models.Currency.objects.all()
        return context


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Account
    template_name = 'budget/account/account_delete.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        style = self.object.style

        self.object.delete()
        style.delete()

        messages.success(self.request, f"Account '{self.object.name}' deleted!")
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

        transactions_queryset = models.Transaction.objects.filter(category=self.object,
                                                                  account__profile__user=self.request.user).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        transactions_list = list(transactions_queryset)
        transactions = []

        if not transactions_list:
            return context

        temp_date = transactions_list[0].truncated_date
        temp_total = 0
        temp_transactions = []

        for transaction in transactions_list:
            if transaction.truncated_date != temp_date:
                transactions.append({
                    'date': temp_date,
                    'total': temp_total,
                    'txns': temp_transactions
                })

                temp_date = transaction.truncated_date
                temp_total = 0
                temp_transactions = [transaction]
            else:
                temp_transactions.append(transaction)

            amount = transaction.amount_converted if transaction.amount_converted else transaction.amount
            temp_total += amount

        else:
            transactions.append({
                'date': temp_date,
                'total': temp_total,
                'transactions': temp_transactions
            })

        context["transactions"] = transactions

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
            initial['category_type'] = '-' if category_type == '-' else '+'

        return initial

    def form_valid(self, form):
        category = form.save(commit=False)
        category.profile = Profile.objects.get(user=self.request.user)
        category.style = Style.create_style(color=form.cleaned_data.get('color'),
                                            icon=form.cleaned_data.get('icon'))
        category.save()
        messages.success(self.request, f"Category '{category.name}' created!")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, StyleFormUpdateMixin):
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
        style = self.object.style

        self.object.delete()
        style.delete()

        messages.success(self.request, f"Category '{self.object.name}' deleted!")
        return HttpResponseRedirect(success_url)


# Transactions

class TransactionList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = models.Transaction
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        transactions_queryset = models.Transaction.objects.filter(account__profile__user=user).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))
        transfers_queryset = models.Transfer.objects.filter(account_from__profile__user=user).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        total_none_flag = True if len(transactions_queryset.values('currency')) > 2 else False

        transfers_list = list(transfers_queryset)
        transactions_list = list(transactions_queryset)

        combined_list = transactions_list + transfers_list

        combined_list.sort(key=operator.attrgetter('date'), reverse=True)

        combined_actions = []

        if not combined_list:
            return context

        temp_date = combined_list[0].truncated_date
        temp_total = 0
        temp_actions = []

        for action in combined_list:
            action_type = 'txn' if isinstance(action, models.Transaction) else 'trf'

            if action.truncated_date != temp_date:
                combined_actions.append({
                    'date': temp_date,
                    'total': None if total_none_flag else temp_total,
                    'actions': temp_actions
                })

                temp_date = action.truncated_date
                temp_total = 0
                temp_actions = [{"action_type": action_type,
                                 "action": action}]
            else:
                temp_actions.append({"action_type": action_type,
                                     "action": action})

            if action_type == 'txn':
                amount = action.amount_converted if action.amount_converted else action.amount
                temp_total += amount
        else:
            combined_actions.append({
                'date': temp_date,
                'total': None if total_none_flag else temp_total,
                'actions': temp_actions
            })

        context["combined_actions"] = combined_actions

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
        amount = form.cleaned_data.get('amount') if account.currency == form.cleaned_data.get(
            'currency') else form.cleaned_data.get('amount_converted')

        account.balance += abs(amount) if form.cleaned_data.get('transaction_type') == Transaction.INCOME else -abs(
            amount)
        account.save()

        messages.success(self.request, f"Transaction '{form.cleaned_data.get('amount')}' created!")
        messages.info(self.request, f'Updated balance of account!\nYour new balance is {account.balance}')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
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
            prev_transaction.account.balance += prev_transaction_amount
        else:
            prev_transaction.account.balance -= prev_transaction_amount
        prev_transaction.account.save()

        # Updating account balance
        new_transaction.account.refresh_from_db()
        new_transaction_amount = abs(new_transaction.amount_converted or new_transaction.amount)
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

        messages.success(self.request, f"Transaction '{self.object.amount}' deleted!")
        messages.info(self.request,
                      f'Updated balance of account!\nYour new balance is {transaction.account.balance}')

        return super().form_valid(form)


# Transfers

class TransferCreateView(LoginRequiredMixin, CreateView):
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

            messages.success(self.request, f"Transfer '{account_from.name}->{account_to.name}' done!")
            messages.info(self.request,
                          f"Updated balance of '{account_from.name}' account!\nYour new balance is {account_from.balance}")

            messages.info(self.request,
                          f"Updated balance of '{account_to.name}' account!\nYour new balance is {account_to.balance}")

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


class TransferUpdateView(LoginRequiredMixin, UpdateView):
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

            messages.success(self.request, f"Transfer '{account_from.name}->{account_to.name}' updated!")
            messages.info(self.request,
                          f"Updated balance of '{account_from.name}' account!\nYour new balance is {account_from.balance}")

            messages.info(self.request,
                          f"Updated balance of '{account_to.name}' account!\nYour new balance is {account_to.balance}")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)


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
                      f"Updated balance of '{transfer.account_from.name}' account!\nYour new balance is {transfer.account_from.balance}")

        messages.info(self.request,
                      f"Updated balance of '{transfer.account_to.name}' account!\nYour new balance is {transfer.account_to.balance}")

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
