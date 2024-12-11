import random

from django.contrib import messages
from django.db import models


class ColorChoices:
    COLOR_DARK_RED = 'aa1409'
    COLOR_RED = 'f44336'
    COLOR_PINK = 'e91e63'
    COLOR_ROSE = 'ffe4e1'
    COLOR_FUCHSIA = 'ff66ff'
    COLOR_PURPLE = '9c27b0'
    COLOR_DARK_PURPLE = '673ab7'
    COLOR_INDIGO = '3f51b5'
    COLOR_BLUE = '2196f3'
    COLOR_LIGHT_BLUE = '03a9f4'
    COLOR_CYAN = '00bcd4'
    COLOR_TEAL = '009688'
    COLOR_AQUA = '00ffff'
    COLOR_DARK_GREEN = '2f6a31'
    COLOR_GREEN = '4caf50'
    COLOR_LIGHT_GREEN = '8bc34a'
    COLOR_LIME = 'cddc39'
    COLOR_YELLOW = 'ffeb3b'
    COLOR_AMBER = 'ffc107'
    COLOR_ORANGE = 'ff9800'
    COLOR_DARK_ORANGE = 'ff5722'
    COLOR_BROWN = '795548'
    COLOR_LIGHT_GREY = 'c0c0c0'
    COLOR_GREY = '9e9e9e'
    COLOR_DARK_GREY = '607d8b'
    COLOR_BLACK = '111111'
    COLOR_WHITE = 'ffffff'

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


class TimeStampMixin(models.Model):
    """
    Mixin for ease adding created_at and updated_at to models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StyleMixin(models.Model):
    color = models.CharField(null=False,
                             blank=True,
                             max_length=6,
                             default=random.choice(ColorChoices.CHOICES)[0],
                             verbose_name="Color")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            default=random.choice(IconChoices.CHOICES)[0],
                            verbose_name="Icon",
                            help_text="Icon name from FontAwesome")

    class Meta:
        abstract = True


class FormInvalidMixin:
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")

        return super().form_invalid(form)
