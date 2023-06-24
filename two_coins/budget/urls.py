from django.urls import path
from . import views

urlpatterns = [
    # Currencies
    path('currency/', views.CurrencyList.as_view(), name='currency_list'),
    path('currency/add/', views.currency_add, name='currency_add'),
    path('currency/<int:pk>/edit/', views.currency_edit, name='currency_edit'),
    path('currency/<int:pk>/delete/', views.currency_delete, name='currency_delete'),

    # Accounts
    path('account/', views.AccountList.as_view(), name='account_list'),
    path('account/add/', views.account_add, name='account_add'),
    path('account/<int:pk>/', views.account, name='account'),
    path('account/<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('account/<int:pk>/delete/', views.account_delete, name='account_delete'),

    # Categories
    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('category/add/', views.category_add, name='category_add'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
