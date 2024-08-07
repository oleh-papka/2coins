from rest_framework import viewsets

from .serializers import TransactionSerializer, TransactionDetailSerializer, AccountSerializer, CategorySerializer
from ..models import Transaction, Account, Category


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TransactionDetailSerializer
        return TransactionSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
