from itertools import chain
from operator import attrgetter

from django.db.models.functions import TruncDate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, generics
from rest_framework.response import Response

from .serializers import TransactionDetailedSerializer, CombinedTxnTrfSerializer, TransactionSerializer
from ..models import Transaction, Transfer


class TransactionCreateListView(mixins.ListModelMixin,
                                generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionDetailedSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        responses={200: None},
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        txn_filter_kwargs = {
            'account__profile__user': user
        }

        if start_date:
            txn_filter_kwargs['date__gte'] = start_date
        if end_date:
            txn_filter_kwargs['date__lte'] = end_date

        txn_data = Transaction.objects.filter(**txn_filter_kwargs).order_by('-date').annotate(
            truncated_date=TruncDate('date')).order_by('-date')

        serializer = TransactionDetailedSerializer(txn_data, many=True)

        return Response(serializer.data)


class TransactionDeleteView(generics.DestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class CombinedActionListView(generics.GenericAPIView):
    serializer_class = CombinedTxnTrfSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        responses={200: None},
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        txn_filter_kwargs = {
            'account__profile__user': user
        }
        trf_filter_kwargs = {
            'account_from__profile__user': user
        }

        if start_date:
            txn_filter_kwargs['date__gte'] = start_date
            trf_filter_kwargs['date__gte'] = start_date
        if end_date:
            txn_filter_kwargs['date__lte'] = end_date
            trf_filter_kwargs['date__lte'] = end_date

        txn_data = Transaction.objects.filter(**txn_filter_kwargs).order_by('-date').annotate(
            truncated_date=TruncDate('date'))
        trf_data = Transfer.objects.filter(**trf_filter_kwargs).order_by(
            '-date').annotate(truncated_date=TruncDate('date'))

        txn_data = list(txn_data)
        for item in txn_data:
            item.action_type = "txn"

        trf_data = list(trf_data)
        for item in trf_data:
            item.action_type = "trf"

        combined_data = sorted(
            chain(txn_data, trf_data),
            key=attrgetter('date'),
            reverse=True
        )

        serializer = CombinedTxnTrfSerializer(combined_data, many=True)

        return Response(serializer.data)
