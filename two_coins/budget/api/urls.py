from django.urls import path

from .views import TransactionChartDataView, TransferListView, \
    CombinedActionListView, TransactionsByCategoryChartDataView, TransactionsByAccountChartDataView, \
    TransactionListView, DashboardDoughnutChartView, DashboardBalanceChartView

urlpatterns = [
    path('combined_actions/', CombinedActionListView.as_view(), name='combined_actions'),

    path('transfers/', TransferListView.as_view(), name='transfer'),

    path('transactions/', TransactionListView.as_view(), name='transaction'),

    path('charts/transactions/', TransactionChartDataView.as_view(), name='charts_transaction'),
    path('charts/transaction/group_by_category/', TransactionsByCategoryChartDataView.as_view(),
         name='charts_transaction_category'),
    path('charts/transaction/group_by_account/', TransactionsByAccountChartDataView.as_view(),
         name='charts_transaction_account'),
    path('charts/doughnut/', DashboardDoughnutChartView.as_view(), name='dashboard_doughnut_chart'),
    path('charts/balance/', DashboardBalanceChartView.as_view(), name='dashboard_balance_chart'),
]

app_name = 'budget-api'
