from django.db.models import Sum
from django.db.models.functions import TruncDate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, generics
from rest_framework.response import Response

from misc.utils import get_date_range, get_combined_actions
from .serializers import TransactionSerializer, TransferSerializer, ChartDataSerializer, \
    CombinedActionQueryParamsSerializer, CombinedActionSerializer, TransactionCombinedSerializer, \
    TransferCombinedSerializer
from ..models import Transaction, Transfer


class TransactionCreateListView(mixins.ListModelMixin,
                                generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, description='Category ID'),
        ],
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


class TransactionDeleteView(generics.DestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransferListView(generics.ListAPIView):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer


class CombinedActionListView(generics.GenericAPIView):
    serializer_class = CombinedActionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, description='Category ID'),
            OpenApiParameter(name='all_transfers', type=OpenApiTypes.BOOL, description='Include all transfers'),
        ],
    )
    def get(self, request, *args, **kwargs):
        serializer = CombinedActionQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data.get('start_date', None)
        end_date = serializer.validated_data.get('end_date', None)
        account_id = serializer.validated_data.get('account_id', None)
        category_id = serializer.validated_data.get('category_id', None)
        all_transfers = serializer.validated_data.get('all_transfers', False)

        start_date, end_date = get_date_range(start_date, end_date)
        combined_actions = get_combined_actions(user_id=self.request.user.id,
                                                start_date=start_date,
                                                end_date=end_date,
                                                account_id=account_id,
                                                category_id=category_id,
                                                all_transfers=all_transfers)
        combined_actions_serialized = []
        if combined_actions:
            for action in combined_actions:
                if action.action_type == 'txn':
                    combined_actions_serialized.append(TransactionCombinedSerializer(action).data)
                else:
                    combined_actions_serialized.append(TransferCombinedSerializer(action).data)

        response_data = {'combined_actions': combined_actions_serialized}

        return Response(self.get_serializer(response_data).data)


class TransactionChartDataView(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    def get(self, request, *args, **kwargs):
        txn_data = (
            Transaction.objects.annotate(date_only=TruncDate('date'))
            .values('date_only')
            .annotate(amount_total=Sum('amount'))
            .order_by('date_only')
        )

        labels = []
        data = []

        for txn_group in txn_data:
            labels.append(txn_group['date_only'].strftime('%d/%m'))
            data.append(float(txn_group['amount_total']))

        response_data = {
            'labels': labels,
            'data': data,
        }

        return Response(response_data)
