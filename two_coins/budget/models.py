from django.db import models
from django.utils import timezone

from misc.models import TimeStampMixin


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


class Styling(models.Model):
    color = models.CharField(null=False,
                             blank=True,
                             max_length=7,
                             default="#fcba03",
                             verbose_name="Color")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name="Icon",
                            help_text="Icon name from FontAwesome")


class Currency(models.Model):
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
                              max_length=2,
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

    GENERIC_ACCOUNT = 'g'
    SAVINGS_ACCOUNT = 's'

    ACCOUNT_TYPE_CHOICES = (
        (GENERIC_ACCOUNT, "Default account"),
        (SAVINGS_ACCOUNT, "Savings account")
    )

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Account name")
    account_type = models.CharField(null=False,
                                    blank=False,
                                    max_length=1,
                                    choices=ACCOUNT_TYPE_CHOICES,
                                    default=GENERIC_ACCOUNT,
                                    verbose_name="Account type")
    balance = models.FloatField(null=False,
                                blank=True,
                                default=0,
                                verbose_name="Account balance")
    initial_balance = models.FloatField(null=False,
                                        blank=True,
                                        default=0,
                                        verbose_name="Initial account balance")
    target_balance = models.FloatField(null=False,
                                       blank=True,
                                       default=0,
                                       verbose_name="Target account balance")
    deadline = models.DateField(null=True,
                                blank=True,
                                verbose_name="Deadline date")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")
    styling = models.ForeignKey(Styling,
                                null=False,
                                blank=True,
                                default=1,
                                on_delete=models.DO_NOTHING)
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


class Category(TimeStampMixin):
    """
    Model for storing transaction category.
    """

    INCOME = "+"
    EXPENSE = "-"

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
    styling = models.ForeignKey(Styling,
                                null=False,
                                blank=False,
                                default=1,
                                on_delete=models.DO_NOTHING)
    profile = models.ForeignKey('profiles.Profile',
                                null=False,
                                blank=False,
                                on_delete=models.CASCADE)


class Transaction(TimeStampMixin):
    """
    Model for storing one transaction within an account
    """

    INCOME = "+"
    EXPENSE = "-"

    TRANSACTION_TYPE_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
    ]

    transaction_type = models.CharField(null=False,
                                        blank=False,
                                        max_length=1,
                                        choices=TRANSACTION_TYPE_CHOICES,
                                        default=EXPENSE,
                                        verbose_name="Transaction type")
    amount = models.FloatField(null=False,
                               blank=False,
                               verbose_name="Amount")
    amount_account_currency = models.FloatField(null=True,
                                                blank=True,
                                                verbose_name="Amount in account's currency")
    exchange_rate = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name="Exchange rate for transaction")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                default=timezone.now,
                                verbose_name="Transaction date/time")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    category = models.ForeignKey(null=True,
                                 blank=False,
                                 to=Category,
                                 on_delete=models.CASCADE,
                                 verbose_name="Category")
    account = models.ForeignKey(null=False,
                                blank=False,
                                to=Account,
                                on_delete=models.CASCADE,
                                verbose_name="Account")

    def save(self, *args, **kwargs):
        self.amount = abs(self.amount) if self.transaction_type == self.INCOME else - abs(self.amount)

        if self.amount_account_currency:
            self.amount_default_currency = abs(
                self.amount_account_currency) if self.transaction_type == self.INCOME else - abs(
                self.amount_account_currency)

        super(Transaction, self).save(*args, **kwargs)


class Transfer(TimeStampMixin):
    amount = models.FloatField(null=False,
                               blank=False,
                               verbose_name="Amount")
    amount_to = models.FloatField(null=False,
                                  blank=False,
                                  verbose_name="Amount transferring to")
    exchange_rate = models.FloatField(null=True,
                                      blank=True,
                                      default=1,
                                      verbose_name="Exchange rate for transfer")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                default=timezone.now,
                                verbose_name="Transaction date/time")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    from_account = models.ForeignKey(Account,
                                     null=False,
                                     blank=False,
                                     on_delete=models.CASCADE,
                                     related_name="transfers_out",
                                     verbose_name="From Account")
    to_account = models.ForeignKey(Account,
                                   null=False,
                                   blank=False,
                                   on_delete=models.CASCADE,
                                   related_name="transfers_in",
                                   verbose_name="To Account")

    def save(self, *args, **kwargs):
        self.amount = abs(self.amount)
        self.amount_to = abs(self.amount_to)

        super(Transfer, self).save(*args, **kwargs)
