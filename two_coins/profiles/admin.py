from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('email', 'date_joined', 'last_login')
    list_display = ['email', 'last_login', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    ordering = ('id',)
    show_facets = admin.ShowFacets.ALWAYS
