from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, AccountViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'transaction', TransactionViewSet, basename='transaction')
router.register(r'account', AccountViewSet, basename='account')
router.register(r'category', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'budget-api'
