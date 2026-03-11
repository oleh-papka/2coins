from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'abbr']
    search_fields = ['name', 'symbol', 'abbr']
    ordering = ('id',)
    show_facets = admin.ShowFacets.ALWAYS
