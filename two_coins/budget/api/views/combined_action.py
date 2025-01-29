from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.response import Response

from budget.api.serializers import CombinedActionQueryParamsSerializer, CombinedActionSerializer, \
    TransactionCombinedSerializer, \
    TransferCombinedSerializer
from misc.utils import get_date_range, get_combined_actions


class CombinedActionListView(generics.GenericAPIView):
    serializer_class = CombinedActionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID to sort by'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, description='Category ID to sort by'),
            OpenApiParameter(name='all_transfers', type=OpenApiTypes.BOOL, description='Include all transfers'),
        ],
        description='Get transactions and transfers within a specified date range '
                    '(if not provided defaults to current month), '
                    'optionally sorted by account.',
        summary='Retrieves Transactions and Transfers',
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
