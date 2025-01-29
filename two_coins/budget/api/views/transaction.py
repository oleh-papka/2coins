from django.db.models.functions import TruncDate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.response import Response

from budget.api.serializers import TransactionSerializer, TransactionSimpleSerializer
from budget.models import Transaction


@extend_schema(
    summary='Create a new Transaction',
)
class TransactionCreateView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSimpleSerializer


class TransactionRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSimpleSerializer

    @extend_schema(
        summary='Get Transaction by id',
    )
    def get(self, request, *args, **kwargs):
        return super(TransactionRetrieveDestroyView, self).get(request, *args, **kwargs)

    @extend_schema(
        summary='Delete specified Transaction by id',
    )
    def delete(self, request, *args, **kwargs):
        return super(TransactionRetrieveDestroyView, self).delete(request, *args, **kwargs)


class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID to sort by'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, description='Category ID to sort by'),
        ],
        description='Get transactions within a specified date range '
                    '(if not provided defaults to current month), '
                    'optionally sorted by account or category.',
        summary='Retrieves Transactions only',
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        account_id = request.query_params.get('account_id', None)
        category_id = request.query_params.get('category_id', None)

        txn_filter_kwargs = {
            'account__profile__user': user
        }

        if start_date:
            txn_filter_kwargs['date__gte'] = start_date
        if end_date:
            txn_filter_kwargs['date__lte'] = end_date
        if account_id:
            txn_filter_kwargs['account__id'] = account_id
        if category_id:
            txn_filter_kwargs['category__id'] = category_id

        txn_data = Transaction.objects.filter(**txn_filter_kwargs).order_by('-date').annotate(
            truncated_date=TruncDate('date')).order_by('-date')

        return Response(self.get_serializer(txn_data, many=True).data)
