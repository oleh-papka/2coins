from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone

from misc.models import TimeStampMixin, StyleMixin


class Currency(models.Model):
    """
    Currencies for an account supports both fiat money and cryptocurrencies.
    """

    CRYPTO = "C"
    FIAT = "F"
    MONEY_TYPES_CHOICES = [
        (FIAT, "Fiat money"),
        (CRYPTO, "Crypto currency"),
    ]

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Currency name",
                            unique=True)
    currency_type = models.CharField(max_length=1,
                                     choices=MONEY_TYPES_CHOICES,
                                     default=FIAT,
                                     verbose_name="Currency type")
    symbol = models.CharField(null=False,
                              blank=False,
                              max_length=5,
                              verbose_name="Symbol",
                              unique=True)
    abbr = models.CharField(null=False,
                            blank=False,
                            max_length=5,
                            verbose_name="Abbreviation",
                            unique=True)


class Account(TimeStampMixin, StyleMixin):
    """
       Base model representing accounts of the user.
    """

    DEFAULT_ACCOUNT = 'd'
    SAVINGS_ACCOUNT = 's'

    ACCOUNT_TYPE_CHOICES = (
        (DEFAULT_ACCOUNT, "Default account"),
        (SAVINGS_ACCOUNT, "Savings account")
    )

    account_type = models.CharField(null=False,
                                    blank=False,
                                    max_length=1,
                                    choices=ACCOUNT_TYPE_CHOICES,
                                    default=DEFAULT_ACCOUNT,
                                    verbose_name="Account type")
    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Account name")
    balance = models.DecimalField(null=False,
                                  blank=True,
                                  default=0.00,
                                  max_digits=10,
                                  decimal_places=2,
                                  verbose_name="Account balance")
    profile = models.ForeignKey('profiles.Profile',
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE,
                                related_name='accounts')
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")
    allow_negative_balance = models.BooleanField(null=False,
                                                 blank=True,
                                                 default=False,
                                                 verbose_name="Allow negative balance")

    # Fields for savings account only
    initial_balance = models.DecimalField(null=True,
                                          blank=True,
                                          default=0.00,
                                          max_digits=10,
                                          decimal_places=2,
                                          verbose_name="Initial balance")
    target_balance = models.DecimalField(null=True,
                                         blank=True,
                                         default=0.00,
                                         max_digits=10,
                                         decimal_places=2,
                                         verbose_name="Target balance")
    deadline = models.DateField(null=True,
                                blank=True,
                                default=None,
                                verbose_name="Deadline date")

    def withdraw(self, amount):
        with db_transaction.atomic():
            self.balance -= abs(amount)
            self.save()

    def deposit(self, amount):
        with db_transaction.atomic():
            self.balance += abs(amount)
            self.save()

    def transfer(self, amount, amount_converted, to_account):
        with db_transaction.atomic():
            self.withdraw(amount)
            to_account.deposit(amount_converted)


class Category(TimeStampMixin, StyleMixin):
    """
    Model for storing transaction category.
    """

    INCOME = "+"
    EXPENSE = "-"

    CATEGORY_TYPES = (INCOME, EXPENSE)
    CATEGORY_TYPES_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
    ]

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Category name")
    category_type = models.CharField(null=False,
                                     blank=False,
                                     max_length=1,
                                     choices=CATEGORY_TYPES_CHOICES,
                                     default=EXPENSE,
                                     verbose_name="Category type")
    profile = models.ForeignKey('profiles.Profile',
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE)


class Transaction(models.Model):
    """
    Model for storing one transaction within an account
    """

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
                                 max_digits=10,
                                 decimal_places=2,
                                 verbose_name="Amount")
    amount_converted = models.DecimalField(null=True,
                                           blank=True,
                                           max_digits=10,
                                           decimal_places=2,
                                           verbose_name="Amount in account's currency")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                default=timezone.now,
                                verbose_name="Date/time")


class Transfer(models.Model):
    amount_from = models.DecimalField(null=False,
                                      blank=False,
                                      max_digits=10,
                                      decimal_places=2,
                                      verbose_name="Amount transferring from account")
    amount_to = models.DecimalField(null=False,
                                    blank=True,
                                    max_digits=10,
                                    decimal_places=2,
                                    verbose_name="Amount transferring to account")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                default=timezone.now,
                                verbose_name="Date/time")
    account_from = models.ForeignKey(Account,
                                     null=False,
                                     blank=False,
                                     on_delete=models.CASCADE,
                                     related_name="transfers_out",
                                     verbose_name="From Account")
    account_to = models.ForeignKey(Account,
                                   null=False,
                                   blank=False,
                                   on_delete=models.CASCADE,
                                   related_name="transfers_in",
                                   verbose_name="To Account")
