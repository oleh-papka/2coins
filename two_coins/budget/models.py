import datetime

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

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Account name")
    currency = models.ForeignKey(Currency,
                                 null=True,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    balance = models.FloatField(null=False,
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
    goal_balance = models.FloatField(null=True,
                                     blank=True,
                                     default=None,
                                     verbose_name="Goal balance")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name="Icon",
                            help_text="Icon name from FontAwesome")
    profile = models.ForeignKey('profiles.Profile',
                                on_delete=models.CASCADE)
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")

    def save(self, *args, **kwargs):
        if not self.initial_date:
            self.initial_date = timezone.now()
        if not self.balance:
            self.balance = 0

        Category.objects.get_or_create(name='Other',
                                       cat_type=Category.OTHER,
                                       profile=self.profile,
                                       icon="fa-solid fa-ellipsis",
                                       color="#787878")

        super(Account, self).save(*args, **kwargs)


class Category(TimeStampMixin):
    """
    Model for storing transaction category.
    """

    INCOME = "+"
    EXPENSE = "-"
    OTHER = ":"
    CATEGORY_TYPES_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
    ]

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Name")
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
    profile = models.ForeignKey('profiles.Profile',
                                on_delete=models.CASCADE)
    cat_type = models.CharField(null=False,
                                blank=False,
                                max_length=1,
                                choices=CATEGORY_TYPES_CHOICES,
                                default=EXPENSE,
                                verbose_name="Category type")

    def get_transactions_by_category(self, user):
        return Transaction.objects.filter(category=self, account__profile__user=user).order_by('-date')


class Transaction(TimeStampMixin):
    """
    Model for storing one transaction within an account
    """

    INCOME = "+"
    EXPENSE = "-"
    # TRANSFER = ">"
    TRANSACTION_TYPES_CHOICES = [
        (EXPENSE, "Expense"),
        (INCOME, "Income"),
        # (TRANSFER, "Transfer"), # TODO: money transfer between accounts
    ]

    txn_type = models.CharField(null=False,
                                blank=True,
                                max_length=2,
                                choices=TRANSACTION_TYPES_CHOICES,
                                default=EXPENSE,
                                verbose_name="Transaction type")
    amount = models.FloatField(null=False,
                               blank=False,
                               verbose_name="Amount")
    currency = models.ForeignKey(Currency,
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    amount_default_currency = models.FloatField(null=True,
                                                blank=True,
                                                verbose_name="Amount in default currency")
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

        if self.category and self.category.cat_type != Category.OTHER:
            self.txn_type = self.category.cat_type

        self.amount = abs(self.amount) if self.txn_type == self.INCOME else - abs(self.amount)
        if self.amount_default_currency:
            self.amount_default_currency = abs(self.amount_default_currency) if self.txn_type == self.INCOME else - abs(
                self.amount_default_currency)

        super(Transaction, self).save(*args, **kwargs)
