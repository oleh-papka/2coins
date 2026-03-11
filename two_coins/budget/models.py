from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F
from django.utils import timezone

from misc.models import TimeStampMixin, StyleMixin


class Currency(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Name")
    symbol = models.CharField(max_length=5, unique=True, verbose_name="Symbol")
    abbr = models.CharField(max_length=5, unique=True, verbose_name="Abbreviation")

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"Currency {self.name} ({self.abbr})"


class Account(TimeStampMixin, StyleMixin):
    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Name")
    balance = models.DecimalField(null=False,
                                  blank=False,
                                  default=Decimal("0"),
                                  max_digits=10,
                                  decimal_places=2,
                                  verbose_name="Balance")
    profile = models.ForeignKey('profiles.Profile',
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE,
                                related_name='+')
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return f"Account {self.name}"

    def withdraw(self, amount: Decimal):
        amount = abs(amount)

        with db_transaction.atomic():
            account = Account.objects.select_for_update().get(pk=self.pk)

            if account.balance < amount:
                raise ValidationError("Insufficient funds")

            account.balance = F("balance") - amount
            account.save(update_fields=["balance"])
            account.refresh_from_db(fields=["balance"])
            self.balance = account.balance

    def deposit(self, amount: Decimal):
        amount = abs(amount)
        Account.objects.filter(pk=self.pk).update(balance=F("balance") + amount)
        self.refresh_from_db(fields=["balance"])


class Category(TimeStampMixin, StyleMixin):
    class CategoryType(models.TextChoices):
        INCOME = "+", "Income"
        EXPENSE = "-", "Expense"

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Category name")
    category_type = models.CharField(null=False,
                                     blank=False,
                                     max_length=1,
                                     choices=CategoryType,
                                     default=CategoryType.EXPENSE,
                                     verbose_name="Category type")
    profile = models.ForeignKey('profiles.Profile',
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"Category {self.name}"


class Transaction(TimeStampMixin):
    account = models.ForeignKey(null=False,
                                blank=False,
                                to=Account,
                                on_delete=models.CASCADE,
                                verbose_name="Account")
    category = models.ForeignKey(null=False,
                                 blank=False,
                                 to=Category,
                                 on_delete=models.CASCADE,
                                 verbose_name="Category")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    amount = models.DecimalField(null=False,
                                 blank=False,
                                 default=Decimal("0"),
                                 max_digits=10,
                                 decimal_places=2,
                                 verbose_name="Amount")
    amount_converted = models.DecimalField(null=True,
                                           blank=True,
                                           default=None,
                                           max_digits=10,
                                           decimal_places=2,
                                           verbose_name="Amount in account's currency")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    performed_date = models.DateField(default=timezone.localdate, verbose_name="Date")

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction of {self.account.name}"


class Transfer(TimeStampMixin):
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')
    txn_from = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='+')

    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='+')
    txn_to = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='+')

    class Meta:
        verbose_name = "Transfer"
        verbose_name_plural = "Transfers"

    def __str__(self):
        return f"Transfer {self.from_account.name} -> {self.to_account.name}"
