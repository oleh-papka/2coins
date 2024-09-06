import re
from datetime import datetime, time

from django import forms
from django.utils import timezone
from django.utils.timezone import make_aware

from . import models
from .models import Style, Account


class BaseTransactionForm(forms.ModelForm):
    """
    Abstract form class that provides shared validation logic for positive values.
    """

    class Meta:
        abstract = True

    def clean_positive_value(self, field_name):
        data = self.cleaned_data.get(field_name)
        return abs(data) if data else data


class BaseStyleForm(forms.ModelForm):
    """
    Abstract form class that provides shared styling logic for models.
    """

    icon = forms.CharField(max_length=30, required=False)
    color = forms.CharField(max_length=7, required=False)

    class Meta:
        abstract = True
        fields = '__all__'
        exclude = ('profile',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_name = self._meta.model._meta.verbose_name.capitalize()

        self.fields['icon'].label = f'{model_name} icon'
        self.fields['color'].label = f'{model_name} color'

    def clean_color(self):
        data = self.cleaned_data.get("color")
        color_regex = re.compile(r'^#?[0-9a-fA-F]{6}$')

        if not color_regex.match(data):
            self.add_error('color', f"Wrong color field format provided '{data}'! Expected #RRGGBB HEX format.")
            return data

        if data.startswith('#'):
            data = data[1:]

        return data.lower()


class AccountForm(BaseStyleForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Account

    def clean_deadline(self):
        data = self.cleaned_data.get("deadline")

        if data:
            # Convert the date to a datetime at the start of the day (midnight)
            data_datetime = make_aware(datetime.combine(data, time.min))

            if data_datetime <= timezone.now():
                self.add_error("deadline", "The deadline date must be in the future!")

        return data

    def clean(self):
        cleaned_data = super().clean()
        balance = cleaned_data.get("balance")
        allow_negative_balance = cleaned_data.get("allow_negative_balance")
        account_type = cleaned_data.get("account_type")
        color = self.cleaned_data.get('color')
        icon = self.cleaned_data.get('icon')
        initial_balance = cleaned_data.get("initial_balance")

        if not initial_balance:
            cleaned_data["initial_balance"] = balance

        if account_type == Account.SAVINGS_ACCOUNT:
            if allow_negative_balance or balance < 0:
                self.add_error("allow_negative_balance", "Savings account balance cannot be negative!")
                return cleaned_data

        cleaned_data["style"] = Style.create_style(color=color, icon=icon)

        return cleaned_data


class AccountUpdateForm(AccountForm):
    class Meta:
        model = Account
        exclude = ('currency',)

    def clean_currency(self):
        data = self.cleaned_data.get("currency")
        return self.instance.currency if not data else data


class CategoryForm(BaseStyleForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Category


class TransactionForm(BaseTransactionForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'

    def clean_amount(self):
        return self.clean_positive_value("amount")

    def clean_amount_converted(self):
        return self.clean_positive_value("amount_converted")

    def clean_date(self):
        data = self.cleaned_data.get("date")
        return timezone.now() if not data else data

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('transaction_type') == models.Transaction.EXPENSE:
            amount = cleaned_data.get('amount')
            amount_converted = cleaned_data.get('amount_converted')
            account = cleaned_data.get('account')

            amount_to_check = amount if not amount_converted else amount_converted
            field_name = 'amount_converted' if amount_converted else 'amount'

            if amount_to_check > account.balance and not account.allow_negative_balance:
                self.add_error(field_name, 'Insufficient funds in the account!')

        return cleaned_data


class TransferForm(BaseTransactionForm):
    def clean_amount_from(self):
        return self.clean_positive_value("amount_from")

    def clean_amount_to(self):
        return self.clean_positive_value("amount_to")

    def clean(self):
        cleaned_data = super().clean()
        amount_from = cleaned_data.get("amount_from")
        amount_to = cleaned_data.get("amount_to")
        account_from = cleaned_data.get("account_from")
        account_to = cleaned_data.get("account_to")

        if amount_from and account_from.currency == account_to.currency:
            cleaned_data['amount_to'] = 0

        if account_from and account_to and account_from == account_to:
            msg = "You cannot transfer to the same account."
            self.add_error("account_from", msg)
            self.add_error("account_to", msg)

        if amount_from > account_from.balance and not account_from.allow_negative_balance:
            self.add_error('amount_from', 'Insufficient funds in the source account!')

        return cleaned_data

    class Meta:
        model = models.Transfer
        fields = '__all__'
