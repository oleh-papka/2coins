from django.urls import path

from .views import TransactionCreateListView, CombinedActionListView, TransactionDeleteView, TransactionChartDataView

urlpatterns = [
    path('combined-actions/', CombinedActionListView.as_view(), name='combined_actions'),
    path('transaction/', TransactionCreateListView.as_view(), name='transaction'),
    path('transaction/<int:pk>', TransactionDeleteView.as_view(), name='transaction'),


    path('charts/transaction/', TransactionChartDataView.as_view(), name='charts_transaction')
]

app_name = 'budget-api'
