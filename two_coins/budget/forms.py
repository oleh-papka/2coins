import random
import re
from datetime import datetime, time

from django import forms
from django.utils import timezone
from django.utils.timezone import make_aware

from misc.models import IconChoices
from . import models


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

    icon = forms.CharField(max_length=50, required=False)
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

        style_fields = ['icon', 'color']
        custom_fields_order = [field for field in self.fields if field not in style_fields] + style_fields

        self.fields = {key: self.fields[key] for key in custom_fields_order}

    def clean_color(self):
        color_data = self.cleaned_data.get("color")
        color_regex = re.compile(r'^#?[0-9a-fA-F]{6}$')

        if not color_regex.match(color_data):
            self.add_error('color', f"Wrong color field format provided '{color_data}'! Expected #RRGGBB HEX format.")
            return color_data

        if color_data.startswith('#'):
            color_data = color_data[1:]

        return color_data.lower()

    def clean_icon(self):
        icon_data = self.cleaned_data.get("icon")

        if not icon_data:
            return random.choice(IconChoices.CHOICES)[0]
        else:
            return icon_data


class AccountCreateForm(BaseStyleForm):
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
        initial_balance = cleaned_data.get("initial_balance")

        if not initial_balance:
            cleaned_data["initial_balance"] = balance

        if account_type == models.Account.SAVINGS_ACCOUNT:
            if allow_negative_balance or balance < 0:
                self.add_error("allow_negative_balance", "Savings account balance cannot be negative!")
                return cleaned_data

        return cleaned_data


class AccountUpdateForm(AccountCreateForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Account
        exclude = BaseStyleForm.Meta.exclude + ('currency',)

    def clean_currency(self):
        currency_data = self.cleaned_data.get("currency")
        return self.instance.currency if not currency_data else currency_data


class CategoryForm(BaseStyleForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Category


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'

    def clean_date(self):
        data = self.cleaned_data.get("date")
        return timezone.now() if not data else data

    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        category = cleaned_data.get('category')
        currency = cleaned_data.get('currency')
        amount_raw = cleaned_data.get('amount')
        amount_converted_raw = cleaned_data.get('amount_converted')

        # Set correct positive/negative values to both amount and amount_converted
        if category.category_type == '+':
            amount = abs(amount_raw)
            amount_converted = abs(amount_converted_raw) if amount_converted_raw is not None else None
        else:
            amount = -abs(amount_raw)
            amount_converted = -abs(amount_converted_raw) if amount_converted_raw is not None else None

        # Check if amount_converted has value when used not account's currency
        if account.currency != currency and not amount_converted:
            self.add_error('amount_converted', 'The transaction in different currency is not converted!.')

        # Check if account have enough funds for expense
        if category.category_type == '-':

            if not amount_converted:
                amount_to_check, field_name = amount, 'amount'
            else:
                amount_to_check, field_name = amount_converted, 'amount_converted'

            if abs(amount_to_check) > account.balance and not account.allow_negative_balance:
                self.add_error(field_name, 'Insufficient funds in the account!')

        cleaned_data['amount'] = amount
        cleaned_data['amount_converted'] = amount_converted

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
