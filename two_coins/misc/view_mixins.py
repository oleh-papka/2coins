from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View

from budget.forms import TransferForm
from budget.models import Transfer, Account, Currency
from profiles.models import Profile


class FormInvalidMixin:
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")

        return super().form_invalid(form)


class TransferMixin(View):
    login_url = reverse_lazy('login')
    model = Transfer
    form_class = TransferForm
    success_url = reverse_lazy('transaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if account_id := self.request.GET.get('account'):
            context['account_from'] = Account.objects.get(id=account_id)

        context['account_list'] = list(Account.objects.filter(
            profile__user=self.request.user).all().values('id', 'name', 'currency_id',
                                                          'currency__abbr', 'currency__symbol'))

        context['currency_list'] = Currency.objects.all()
        context['profile'] = Profile.objects.get(user=self.request.user)

        return context
