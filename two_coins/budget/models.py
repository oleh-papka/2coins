from django.db import models

from misc.models import TimeStampMixin

USUAL = "u"
SAVINGS = "s"
DEBT = "d"
CRYPTO = "c"
FOREIGN_CCY = "f"

ACCOUNT_TYPES_CHOICES = [
    (USUAL, "Usual account"),
    (SAVINGS, "Savings account"),
    (DEBT, "Debt account"),
    (CRYPTO, "Crypto wallet"),
    (FOREIGN_CCY, "Foreign currency wallet"),
]


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
                            verbose_name="Currency name")
    ccy_type = models.CharField(max_length=2,
                                choices=MONEY_TYPES_CHOICES,
                                default=FIAT,
                                verbose_name="Currency type"
                                )
    symbol = models.CharField(null=True,
                              blank=True,
                              max_length=1,
                              verbose_name="Currency symbol")
    abbr = models.CharField(null=False,
                            blank=False,
                            max_length=5,
                            verbose_name="Currency abbreviation")


class BaseAccount(TimeStampMixin):
    """
    Base model representing accounts of the user.
    """

    name = models.CharField(null=False,
                            blank=False,
                            max_length=30,
                            verbose_name="Account name")
    balance = models.IntegerField(null=False,
                                  blank=True,
                                  default=0,
                                  verbose_name="Account balance")
    currency = models.ForeignKey(Currency,
                                 null=False,
                                 blank=False,
                                 on_delete=models.DO_NOTHING,
                                 related_name="+")
    acct_type = models.CharField(max_length=1,
                                 choices=ACCOUNT_TYPES_CHOICES,
                                 default=USUAL,
                                 verbose_name="Account type")
    color = models.CharField(null=False,
                             blank=True,
                             max_length=6,
                             default="fcba03",
                             verbose_name="Account color")
    description = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name="Account description")


class UsualAccount(BaseAccount):
    """
    Usual account for the user.
    """
    pass


class SavingsAccount(BaseAccount):
    """
    Savings account for the user.
    """
    goal_balance = models.IntegerField(null=True,
                                       blank=True,
                                       default=None,
                                       verbose_name="Goal balance")


class DebtAccount(BaseAccount):
    """
    Debt account for the user.
    """
    debt = models.IntegerField(null=False,
                               blank=False,
                               verbose_name="Amount of debt")


class ForeignCurrencyAccount(BaseAccount):
    """
    Foreign currency account for the user.
    """
    initial_balance = models.IntegerField(null=False,
                                          blank=True,
                                          verbose_name="Initial balance")
    initial_price_main_ccy = models.IntegerField(null=False,
                                                 blank=False,
                                                 verbose_name="Initial price (main currency)")
    initial_date = models.DateTimeField(null=False,
                                        blank=True,
                                        verbose_name="Initial date")

    def save(self, *args, **kwargs):
        if not self.initial_balance:
            self.initial_balance = self.balance
        if not self.initial_date:
            self.initial_date = self.created_at

        super(ForeignCurrencyAccount, self).save(*args, **kwargs)


class CryptoAccount(ForeignCurrencyAccount):
    """
    Crypto account for the user.
    """
    initial_price_usd = models.IntegerField(null=False,
                                            blank=False,
                                            verbose_name="Initial price (USD)")
