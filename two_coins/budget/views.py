from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
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
    context_object_name = 'account_list'
    template_name = "budget/account/account_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Accounts'
        return context

    def get_queryset(self):
        profile = models.Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class AccountDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = models.Account
    template_name = 'budget/account/account.html'


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


class CategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Category
    form_class = forms.CategoryForm
    template_name = 'budget/category/category_create.html'
    success_url = reverse_lazy('category_list')

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
    context_object_name = 'transaction_list'
    template_name = "budget/transaction/transaction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["instance_name"] = 'Transactions'
        return context

    def get_queryset(self):
        profile = models.Profile.objects.get(user=self.request.user)
        return super().get_queryset().filter(profile=profile)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    form_class = forms.TransactionForm
    template_name = 'budget/transaction/transaction_create.html'
    success_url = reverse_lazy('transaction_list')

    def get_initial(self):
        initial = super().get_initial()
        initial['txn_type'] = self.kwargs.get('txn_type')
        initial['category'] = self.kwargs.get('category')
        return initial

    def form_valid(self, form):
        messages.success(self.request, f"Transaction '{form.cleaned_data.get('amount')}' created!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong!")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = [(cat.id, cat.name) for cat in models.Category.objects.all()]
        context['accounts'] = [(acct.id, acct.name) for acct in models.Account.objects.all()]
        context['txn_types'] = models.Transaction.TRANSACTION_TYPES_CHOICES

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

        context['categories'] = [(cat.id, cat.name) for cat in models.Category.objects.all()]
        context['accounts'] = [(acct.id, acct.name) for acct in models.Account.objects.all()]
        context['txn_types'] = models.Transaction.TRANSACTION_TYPES_CHOICES

        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = models.Transaction
    template_name = 'budget/transaction/transaction_delete.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        messages.success(self.request, f"Transaction '{self.object.name}' deleted!")
        return super().form_valid(form)


# Dashboard

class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'budget/dashboard.html'

    data_acct = {
        'data': [acct.balance for acct in models.Account.objects.all()],
        'labels': [acct.name for acct in models.Account.objects.all()],
        'colors': [acct.color for acct in models.Account.objects.all()]
    }

    transactions_by_category = models.Transaction.objects.values('category__name').annotate(
        total_amount=Sum('amount'))

    data_cat = {
        'data': [item['total_amount'] for item in transactions_by_category],
        'labels': [item['category__name'] for item in transactions_by_category],
        'colors': [cat.color for cat in models.Category.objects.all()]
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_acct'] = self.data_acct
        context['data_cat'] = self.data_cat

        return context
