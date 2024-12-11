import re

from django import template

register = template.Library()


@register.filter
def strip_trailing_zeros(value):
    try:
        value = float(value)
        if value.is_integer():
            return int(value)
        return value
    except (ValueError, TypeError):
        return value


@register.filter
def int_space(value):
    orig = str(value)

    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1> \g<2>", orig)
    if orig == new:
        return new
    else:
        return int_space(new)
