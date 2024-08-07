from django import forms

from . import models


class BaseStyleForm(forms.ModelForm):
    icon = forms.CharField(max_length=30, required=False)
    color = forms.CharField(max_length=7, required=False)

    class Meta:
        abstract = True
        fields = '__all__'
        exclude = ('profile', 'style')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_name = self._meta.model._meta.verbose_name.capitalize()

        self.fields['icon'].label = f'{model_name} icon'
        self.fields['color'].label = f'{model_name} color'


# Todo: add validations to all of the forms
class AccountForm(BaseStyleForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Account


class CategoryForm(BaseStyleForm):
    class Meta(BaseStyleForm.Meta):
        model = models.Category


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'


class TransferForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        amount_from = cleaned_data.get("amount_from")
        amount_to = cleaned_data.get("amount_to")
        account_from = cleaned_data.get("account_from")
        account_to = cleaned_data.get("account_to")

        if amount_to and account_from.currency == account_to.currency:
            cleaned_data['amount_to'] = 0

        if account_from and account_to and account_from == account_to:
            msg = "You cannot transfer to the same account."
            self.add_error("account_from", msg)
            self.add_error("account_to", msg)

        if account_from.balance < amount_from:
            self.add_error('amount_from', 'Insufficient funds in the source account!')

        print(f"Final Cleaned Data: {cleaned_data}")
        return cleaned_data

    class Meta:
        model = models.Transfer
        fields = '__all__'
