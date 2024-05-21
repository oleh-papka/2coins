from rest_framework import viewsets

from .serializers import TransactionSerializer, TransactionDetailSerializer
from ..models import Transaction


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TransactionDetailSerializer
        return TransactionSerializer
