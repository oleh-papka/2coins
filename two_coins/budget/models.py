import datetime

from django.db import models

from misc.models import TimeStampMixin
from profiles.models import Profile


class ColorChoices:
    COLOR_ROSE = '#ffe4e1'
    COLOR_BLUE = '#2196f3'
    COLOR_LIGHT_BLUE = '#03a9f4'
    COLOR_CYAN = '#00bcd4'
    COLOR_GREEN = '#4caf50'
    COLOR_LIGHT_GREEN = '#8bc34a'
    COLOR_LIME = '#cddc39'
    COLOR_YELLOW = '#ffeb3b'
    COLOR_AMBER = '#ffc107'
    COLOR_ORANGE = '#ff9800'
    COLOR_DARK_ORANGE = '#ff5722'
    COLOR_LIGHT_GREY = '#c0c0c0'

    CHOICES = (
        (COLOR_BLUE, 'Blue'),
        (COLOR_LIGHT_BLUE, 'Light Blue'),
        (COLOR_CYAN, 'Cyan'),
        (COLOR_GREEN, 'Green'),
        (COLOR_LIGHT_GREEN, 'Light Green'),
        (COLOR_LIME, 'Lime'),
        (COLOR_YELLOW, 'Yellow'),
        (COLOR_AMBER, 'Amber'),
        (COLOR_ORANGE, 'Orange'),
        (COLOR_DARK_ORANGE, 'Dark Orange'),
        (COLOR_ROSE, 'Rose'),
        (COLOR_LIGHT_GREY, 'Light Grey'),
    )


class Currency(TimeStampMixin):
    """
    Currencies for an account supports both fiat money and cryptocurrencies.
    """

    CRYPTO = "CX"
    FIAT = "FM"
    MONEY_TYPES_CHOICES = [
        (FIAT, "Fiat money"),
        (CRYPTO, "Crypto currency"),
    ]

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Currency name",
                            unique=True)
    ccy_type = models.CharField(max_length=2,
                                choices=MONEY_TYPES_CHOICES,
                                default=FIAT,
                                verbose_name="Currency type")
    symbol = models.CharField(null=False,
                              blank=False,
                              max_length=1,
                              verbose_name="Symbol",
                              unique=True)
    abbr = models.CharField(null=False,
                            blank=False,
                            max_length=5,
                            verbose_name="Abbreviation",
                            unique=True)


class Account(TimeStampMixin):
    """
    Base model representing accounts of the user.
    """

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Account name")
    currency = models.ForeignKey(Currency,
                                 null=True,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 default=0,
                                 related_name="+")
    balance = models.IntegerField(null=False,
                                  blank=True,
                                  default=0,
                                  verbose_name="Balance")
    initial_date = models.DateTimeField(null=False,
                                        blank=True,
                                        verbose_name="Initial date")
    color = models.CharField(null=False,
                             blank=True,
                             max_length=7,
                             default="#fcba03",
                             verbose_name="Account color")
    goal_balance = models.IntegerField(null=True,
                                       blank=True,
                                       default=None,
                                       verbose_name="Goal balance")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name="Icon",
                            help_text="Icon name from FontAwesome")
    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.initial_date:
            self.initial_date = datetime.datetime.now()
        if not self.balance:
            self.balance = 0

        super(Account, self).save(*args, **kwargs)


class Category(TimeStampMixin):
    """
    Model for storing transaction category.
    """

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Category name")
    color = models.CharField(null=False,
                             blank=True,
                             max_length=7,
                             default="#fcba03",
                             verbose_name="Category color")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name="Icon",
                            help_text="Icon name from FontAwesome")
    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE)


class Transaction(TimeStampMixin):
    """
    Model for storing one transaction with account
    """

    INCOME = "+"
    EXPENSE = "-"
    # TRANSFER = ">"
    TRANSACTION_TYPES_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
        # (TRANSFER, "Transfer"), # TODO: money transfer between accounts
    ]

    txn_type = models.CharField(max_length=2,
                                choices=TRANSACTION_TYPES_CHOICES,
                                default=EXPENSE,
                                verbose_name="Transaction type")
    amount = models.IntegerField(null=False,
                                 blank=False,
                                 verbose_name="Amount")
    category = models.ForeignKey(null=True,
                                 blank=False,
                                 to=Category,
                                 on_delete=models.CASCADE,
                                 verbose_name="Category")
    account = models.ForeignKey(null=True,
                                blank=False,
                                to=Account,
                                on_delete=models.CASCADE,
                                verbose_name="Account")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                verbose_name="Transaction date")

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = datetime.datetime.now()

        super(Transaction, self).save(*args, **kwargs)
