from django.urls import path

from budget.api.views import *

urlpatterns = [
    path('combined_actions/', CombinedActionListView.as_view(), name='combined_actions'),

    path('transfers/', TransferListView.as_view(), name='transfer'),

    path('transactions/', TransactionListView.as_view(), name='transaction'),
    path('transactions/', TransactionCreateView.as_view(), name='transaction_add'),
    path('transactions/<int:id>/', TransactionRetrieveDestroyView.as_view(), name='transaction_get_delete'),
    path('categories/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:id>/', CategoryRetrieveDestroyView.as_view(), name='category_get_delete'),
    path('accounts/', AccountCreateView.as_view(), name='account_add'),
    path('accounts/<int:id>/', AccountRetrieveDestroyView.as_view(), name='account_get_delete'),

    path('charts/transactions/', TransactionsForSingleCategoryBarChart.as_view(), name='charts_transaction'),
    path('charts/account/transactions/', TransactionsForSingleAccountBarChart.as_view(),
         name='charts_account_transaction'),
    path('charts/transaction/group_by_category/', TransactionsByCategoryChartDataView.as_view(),
         name='charts_transaction_category'),
    path('charts/transaction/group_by_account/', TransactionsByAccountBarChart.as_view(),
         name='charts_transaction_account'),
    path('charts/doughnut/', BalanceByTypeDoughnutChart.as_view(), name='dashboard_doughnut_chart'),
    path('charts/balance/', BalanceByPeriodBarChart.as_view(), name='dashboard_balance_chart'),
]

app_name = 'budget-api'
