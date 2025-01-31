from django.db.models import Q
from django.db.models.functions import TruncDate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.response import Response

from budget.api.serializers import TransferSerializer
from budget.models import Transfer
from misc.utils import get_current_month_dates


class TransferListView(generics.ListAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID to sort by'),
        ],
        description='Get transfers within a specified date range '
                    '(if not provided defaults to current month), optionally sorted by account',
        summary='Retrieves Transfers only',
    )
    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        account_id = request.query_params.get('account_id', None)

        if not start_date or not end_date:
            start_date, end_date = get_current_month_dates()

        if account_id:
            transfer_filters = Q(account_to=account_id) | Q(account_from=account_id)
        else:
            transfer_filters = Q(account_to__profile__user_id=user_id) | Q(account_from__profile__user_id=user_id)

        txn_data = Transfer.objects.filter(transfer_filters, date__range=(start_date, end_date)).order_by(
            '-date').annotate(
            truncated_date=TruncDate('date')).order_by('-date')

        return Response(self.get_serializer(txn_data, many=True).data)
