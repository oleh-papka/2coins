from django.urls import path, include

from budget.api.views import *

urlpatterns = [
    path('transfers', TransferListView.as_view(), name='transfer'),
    path('combined-actions', CombinedActionListView.as_view(), name='combined_actions'),
    path('transactions', TransactionListView.as_view(), name='transaction'),
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
