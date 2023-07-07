from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Currencies
    path('currency/', views.CurrencyList.as_view(), name='currency_list'),
    path('currency/add/', views.CurrencyCreateView.as_view(), name='currency_add'),
    path('currency/<int:pk>/edit/', views.CurrencyUpdateView.as_view(), name='currency_edit'),
    path('currency/<int:pk>/delete/', views.CurrencyDeleteView.as_view(), name='currency_delete'),

    # Accounts
    path('account/', views.AccountListView.as_view(), name='account_list'),
    path('account/add/', views.AccountCreateView.as_view(), name='account_add'),
    path('account/<int:pk>/', views.AccountDetailView.as_view(), name='account'),
    path('account/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_edit'),
    path('account/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),

    # Categories
    path('category/', views.CategoryList.as_view(), name='category_list'),
    path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('category/add/<cat_type>/', views.CategoryCreateView.as_view(), name='category_add'),
    path('category/<int:pk>/', views.CategoryDetailView.as_view(), name='category'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Transactions
    path('transaction/', views.TransactionList.as_view(), name='transaction_list'),
    path('transaction/add/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transaction/add/<txn_type>/<category>/', views.TransactionCreateView.as_view(), name='transaction_add'),
    path('transaction/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
]
