from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'abbr', 'currency_type']
    search_fields = ['name', 'symbol', 'abbr']
    list_filter = ['currency_type']
    ordering = ('id',)
    show_facets = admin.ShowFacets.ALWAYS
