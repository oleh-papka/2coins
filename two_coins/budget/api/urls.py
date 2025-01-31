from django.urls import path, include

from budget.api.views import *

# Categories
urlpatterns = [
    path('categories', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:category_id>', CategoryRetrieveDestroyView.as_view(), name='category_get_delete'),
]

# Accounts
urlpatterns += [
    path('accounts', AccountCreateView.as_view(), name='account_add'),
    path('accounts/<int:account_id>', AccountRetrieveDestroyView.as_view(), name='account_get_delete'),
]

# Transfers
urlpatterns += [
    path('transfers', TransferListView.as_view(), name='transfer'),
]

# Combined Transfers and Transactions
urlpatterns += [
    path('combined-actions', CombinedActionListView.as_view(), name='combined_actions'),
]

# Transactions
urlpatterns += [
    path('transactions', TransactionListView.as_view(), name='transaction'),
    path('transactions', TransactionCreateView.as_view(), name='transaction_add'),
    path('transactions/<int:transaction_id>', TransactionRetrieveDestroyView.as_view(), name='transaction_get_delete'),
]

# Charts
charts_urlpatterns = [
    path('categories/<int:category_id>', TransactionsByCategory.as_view(),
         name='chart_transactions_by_category'),
    path('categories/', TransactionsByCategories.as_view(), name='chart_transactions_by_categories'),

    path('accounts/<int:account_id>', TransactionsByAccount.as_view(),
         name='chart_transactions_by_account'),
    path('accounts', TransactionsByAccounts.as_view(), name='chart_transactions_by_accounts'),

    path('balance-by-group', BalanceByType.as_view(), name='chart_balance_by_group'),
    path('balance-by-period', BalanceByPeriod.as_view(), name='chart_balance_by_period'),
]

urlpatterns += [
    path('charts/', include(charts_urlpatterns)),
]

app_name = 'budget-api'
