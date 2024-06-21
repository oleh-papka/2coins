import random

from django.db import models
from django.utils import timezone

from misc.models import TimeStampMixin


class ColorChoices:
    COLOR_DARK_RED = '#aa1409'
    COLOR_RED = '#f44336'
    COLOR_PINK = '#e91e63'
    COLOR_ROSE = '#ffe4e1'
    COLOR_FUCHSIA = '#ff66ff'
    COLOR_PURPLE = '#9c27b0'
    COLOR_DARK_PURPLE = '#673ab7'
    COLOR_INDIGO = '#3f51b5'
    COLOR_BLUE = '#2196f3'
    COLOR_LIGHT_BLUE = '#03a9f4'
    COLOR_CYAN = '#00bcd4'
    COLOR_TEAL = '#009688'
    COLOR_AQUA = '#00ffff'
    COLOR_DARK_GREEN = '#2f6a31'
    COLOR_GREEN = '#4caf50'
    COLOR_LIGHT_GREEN = '#8bc34a'
    COLOR_LIME = '#cddc39'
    COLOR_YELLOW = '#ffeb3b'
    COLOR_AMBER = '#ffc107'
    COLOR_ORANGE = '#ff9800'
    COLOR_DARK_ORANGE = '#ff5722'
    COLOR_BROWN = '#795548'
    COLOR_LIGHT_GREY = '#c0c0c0'
    COLOR_GREY = '#9e9e9e'
    COLOR_DARK_GREY = '#607d8b'
    COLOR_BLACK = '#111111'
    COLOR_WHITE = '#ffffff'

    CHOICES = (
        (COLOR_DARK_RED, 'Dark Red'),
        (COLOR_RED, 'Red'),
        (COLOR_PINK, 'Pink'),
        (COLOR_ROSE, 'Rose'),
        (COLOR_FUCHSIA, 'Fuchsia'),
        (COLOR_PURPLE, 'Purple'),
        (COLOR_DARK_PURPLE, 'Dark Purple'),
        (COLOR_INDIGO, 'Indigo'),
        (COLOR_BLUE, 'Blue'),
        (COLOR_LIGHT_BLUE, 'Light Blue'),
        (COLOR_CYAN, 'Cyan'),
        (COLOR_TEAL, 'Teal'),
        (COLOR_AQUA, 'Aqua'),
        (COLOR_DARK_GREEN, 'Dark Green'),
        (COLOR_GREEN, 'Green'),
        (COLOR_LIGHT_GREEN, 'Light Green'),
        (COLOR_LIME, 'Lime'),
        (COLOR_YELLOW, 'Yellow'),
        (COLOR_AMBER, 'Amber'),
        (COLOR_ORANGE, 'Orange'),
        (COLOR_DARK_ORANGE, 'Dark Orange'),
        (COLOR_BROWN, 'Brown'),
        (COLOR_LIGHT_GREY, 'Light Grey'),
        (COLOR_GREY, 'Grey'),
        (COLOR_DARK_GREY, 'Dark Grey'),
        (COLOR_BLACK, 'Black'),
        (COLOR_WHITE, 'White'),
    )


class IconChoices:
    ICON_USER = "fa-regular fa-user"
    ICON_HOUSE = "fa-solid fa-house-chimney"
    ICON_IMAGE = "fa-regular fa-image"
    ICON_ENVELOPE = "fa-regular fa-envelope"
    ICON_STAR = "fa-regular fa-star"
    ICON_HEART = "fa-regular fa-heart"
    ICON_CART = "fa-solid fa-cart-shopping"
    ICON_CAR = "fa-solid fa-car"
    ICON_CARD = "fa-regular fa-credit-card"
    ICON_HAND_MONEY = "fa-solid fa-hand-holding-dollar"
    ICON_CALENDAR = "fa-solid fa-calendar-days"
    ICON_BUILDING_COLUMNS = "fa-solid fa-building-columns"

    CHOICES = (
        (ICON_USER, "User"),
        (ICON_HOUSE, "House"),
        (ICON_IMAGE, "Image"),
        (ICON_ENVELOPE, "Envelope"),
        (ICON_STAR, "Star"),
        (ICON_HEART, "Heart"),
        (ICON_CART, "Cart"),
        (ICON_CARD, "Card"),
        (ICON_CAR, "Car"),
        (ICON_HAND_MONEY, "Hand with money"),
        (ICON_CALENDAR, "Calendar"),
        (ICON_BUILDING_COLUMNS, "Building columns"),
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

    @classmethod
    def get_default_styling(cls):
        return Styling.objects.create(color=ColorChoices.COLOR_LIGHT_GREY, icon=IconChoices.ICON_CARD)

    @classmethod
    def get_or_create_styling(cls, color=None, icon=None):
        if not color:
            color = random.choice(ColorChoices.CHOICES)[0]
        if not icon:
            icon = random.choice(IconChoices.CHOICES)[0]

        return cls.objects.create(color=color, icon=icon)

    def update_styling(self, color=None, icon=None):
        if color and self.color != color:
            self.color = color

        if self.icon != icon:
            self.icon = icon

        return self.save()


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
                                        verbose_name="Initial balance")
    target_balance = models.FloatField(null=True,
                                       blank=True,
                                       default=0,
                                       verbose_name="Target balance")
    deadline = models.DateField(null=True,
                                blank=True,
                                default=None,
                                verbose_name="Deadline date")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name="Description")
    styling = models.OneToOneField(Styling,
                                   null=False,
                                   blank=True,
                                   default=Styling.get_default_styling,
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
    styling = models.OneToOneField(Styling,
                                   null=False,
                                   blank=True,
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

    TRANSACTION_TYPES = (INCOME, EXPENSE)
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
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Description")
    date = models.DateTimeField(null=False,
                                blank=True,
                                default=timezone.now,
                                verbose_name="Date/time")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name="+")
    category = models.ForeignKey(null=False,
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
        self.amount = abs(self.amount) if self.transaction_type == self.INCOME else -abs(self.amount)

        if self.amount_account_currency:
            self.amount_default_currency = abs(
                self.amount_account_currency) if self.transaction_type == self.INCOME else -abs(
                self.amount_account_currency)

        if not self.date:
            self.date = timezone.now()

        super(Transaction, self).save(*args, **kwargs)


class Transfer(TimeStampMixin):
    amount = models.FloatField(null=False,
                               blank=False,
                               verbose_name="Amount")
    amount_to = models.FloatField(null=False,
                                  blank=False,
                                  verbose_name="Amount transferring to")
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
