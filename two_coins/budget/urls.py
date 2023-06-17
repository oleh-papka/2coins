from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.accounts, name='accounts'),
    path('account/add/', views.account_add, name='account_add'),
    path('account/<int:pk>/', views.account, name='account'),
    path('account/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('account/<int:pk>/delete/', views.account_delete, name='accounts_delete'),
]
