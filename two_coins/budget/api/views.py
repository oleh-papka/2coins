from collections import defaultdict

from django.db.models import Q, Case, When, F, Sum
from django.db.models.functions import TruncDate, Round, ExtractWeek, TruncWeek, TruncMonth, ExtractMonth
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from misc.utils import get_date_range, get_combined_actions, get_current_month_dates
from .serializers import TransactionSerializer, TransferSerializer, ChartDataSerializer, \
    CombinedActionQueryParamsSerializer, CombinedActionSerializer, TransactionCombinedSerializer, \
    TransferCombinedSerializer, StackedChartDataSerializer
from ..models import Transaction, Transfer


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
                    '(if not provided defaults to current month), '
                    'optionally sorted by account.',
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


class TransactionChartDataView(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
            OpenApiParameter(name='account_id', type=OpenApiTypes.INT, description='Account ID'),
            OpenApiParameter(name='category_id', type=OpenApiTypes.INT, description='Category ID'),
            OpenApiParameter(name='absolute_values', type=OpenApiTypes.BOOL,
                             description='Override values to absolute values'),
        ],
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        absolute_values = request.query_params.get('absolute_values', None)
        account_id = request.query_params.get('account_id', None)
        category_id = request.query_params.get('category_id', None)

        values_args = ['date_only']
        extra_data = []

        txn_filter_kwargs = {
            'account__profile__user': request.user,
            'date__range': (start_date, end_date),
        }

        if account_id:
            txn_filter_kwargs['account__id'] = account_id
            values_args.extend(['category__name', 'category__color'])

            trf_data = (
                Transfer.objects
                .filter(Q(account_to=account_id) | Q(account_from=account_id),
                        date__range=(start_date, end_date))
                .annotate(date_only=TruncDate('date'))
                .order_by('date_only')
            )

            for trf in trf_data:
                if trf.account_from.currency == trf.account_to.currency:
                    total_amount = -trf.amount_from if trf.account_to.id != int(account_id) else trf.amount_from
                else:
                    total_amount = -trf.amount_to if trf.account_to.id != int(account_id) else trf.amount_to

                extra_data.append({
                    'date_only': trf.date_only,
                    'category__name': 'Transfer',
                    'category__color': '0ccaf0',
                    'total_amount': total_amount,
                })

        if category_id:
            txn_filter_kwargs['category__id'] = category_id
            values_args.extend(['account__name', 'account__color'])

        txn_data = (
            Transaction.objects
            .filter(**txn_filter_kwargs)
            .annotate(date_only=TruncDate('date'))
            .values(*values_args)
            .annotate(
                total_amount=Round(
                    Sum(
                        Case(
                            When(amount_converted__isnull=False, then=F('amount_converted')),
                            default=F('amount'),
                        )
                    ),
                    2
                )
            )
            .order_by('date_only')
        )

        if extra_data:
            txn_data = list(txn_data) + extra_data
            txn_data.sort(key=lambda x: x['date_only'])

        labels = []
        dataset_dict = defaultdict(lambda: {'backgroundColor': None, 'data': defaultdict(float)})

        group_name = values_args[-1].split('__')[0]

        for txn in txn_data:
            date = txn['date_only'].strftime('%d/%m')
            if date not in labels:
                labels.append(date)

            label_name = txn[f'{group_name}__name']
            label_color = txn[f'{group_name}__color']
            total_amount = float(txn['total_amount'])

            if absolute_values:
                total_amount = abs(total_amount)

            label = dataset_dict[label_name]
            label['backgroundColor'] = label_color
            label['data'][date] += total_amount

        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": label_name,
                    "data": [label["data"][date] for date in labels],
                    "backgroundColor": f'#{label["backgroundColor"]}6A',
                    "borderColor": f'#{label["backgroundColor"]}',
                    "borderRadius": {
                        "topLeft": 5,
                        "topRight": 5,
                        "bottomLeft": 5,
                        "bottomRight": 5
                    }
                }
                for label_name, label in dataset_dict.items()
            ]
        }

        return Response(data)


class TransactionsByCategoryChartDataView(generics.GenericAPIView):
    serializer_class = StackedChartDataSerializer

    def get(self, request, *args, **kwargs):
        category_type = request.query_params.get('category_type', None)
        absolute_values = request.query_params.get('absolute_values', None)

        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        txn_filter_kwargs = {
            'account__profile__user': request.user,
            'date__range': (start_date, end_date),
        }

        if category_type:
            txn_filter_kwargs['category__category_type'] = category_type

        txn_data = (
            Transaction.objects
            .filter(**txn_filter_kwargs)
            .annotate(date_only=TruncDate('date'))
            .values('date_only', 'category__name', 'category__color')
            .annotate(
                total_amount=Round(
                    Sum(
                        Case(
                            When(amount_converted__isnull=False, then=F('amount_converted')),
                            default=F('amount'),
                        )
                    ),
                    2
                )
            )
            .order_by('date_only')
        )

        labels = []
        dataset_dict = defaultdict(lambda: {'backgroundColor': None, 'data': defaultdict(float)})

        for txn in txn_data:
            date = txn['date_only'].strftime('%d/%m')
            if date not in labels:
                labels.append(date)

            category_name = txn['category__name']
            category_color = txn['category__color']
            total_amount = float(txn['total_amount'])

            if absolute_values:
                total_amount = abs(total_amount)

            category = dataset_dict[category_name]
            category['backgroundColor'] = category_color
            category['data'][date] += total_amount

        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": category_name,
                    "data": [category["data"][date] for date in labels],
                    "backgroundColor": f'#{category["backgroundColor"]}6A',
                    "borderColor": f'#{category["backgroundColor"]}',
                    "borderRadius": {
                        "topLeft": 5,
                        "topRight": 5,
                        "bottomLeft": 5,
                        "bottomRight": 5
                    }
                }
                for category_name, category in dataset_dict.items()
            ]
        }

        return Response(data)


class TransactionsByAccountChartDataView(generics.GenericAPIView):
    serializer_class = StackedChartDataSerializer

    def get(self, request, *args, **kwargs):
        absolute_values = request.query_params.get('absolute_values', None)

        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        txn_filter_kwargs = {
            'account__profile__user': request.user,
            'date__range': (start_date, end_date),
        }

        txn_data = (
            Transaction.objects
            .filter(**txn_filter_kwargs)
            .annotate(date_only=TruncDate('date'))
            .values('date_only', 'account__name', 'account__color')
            .annotate(
                total_amount=Round(
                    Sum(
                        Case(
                            When(amount_converted__isnull=False, then=F('amount_converted')),
                            default=F('amount'),
                        )
                    ),
                    2
                )
            )
            .order_by('date_only')
        )

        labels = []
        dataset_dict = defaultdict(lambda: {'backgroundColor': None, 'data': defaultdict(float)})

        for txn in txn_data:
            date = txn['date_only'].strftime('%d/%m')
            if date not in labels:
                labels.append(date)

            account_name = txn['account__name']
            account_color = txn['account__color']
            total_amount = float(txn['total_amount'])

            if absolute_values:
                total_amount = abs(total_amount)

            account = dataset_dict[account_name]
            account['backgroundColor'] = account_color
            account['data'][date] += total_amount

        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": account_name,
                    "data": [account["data"][date] for date in labels],
                    "backgroundColor": f'#{account["backgroundColor"]}6A',
                    "borderColor": f'#{account["backgroundColor"]}',
                    "borderRadius": {
                        "topLeft": 5,
                        "topRight": 5,
                        "bottomLeft": 5,
                        "bottomRight": 5
                    }
                }
                for account_name, account in dataset_dict.items()
            ]
        }

        return Response(data)


class DashboardDoughnutChartView(generics.GenericAPIView):
    serializer_class = StackedChartDataSerializer

    def get(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', 'category').lower()
        valid_groupings = {
            'category': {
                'name_field': 'category__name',
                'color_field': 'category__color',
                'label': 'Total by Category'
            },
            'account': {
                'name_field': 'account__name',
                'color_field': 'account__color',
                'label': 'Total by Account'
            }
        }

        grouping = valid_groupings.get(group_by)
        if not grouping:
            raise ValidationError({
                'group_by': 'Invalid value. Expected "category" or "account".'
            })

        name_field = grouping['name_field']
        color_field = grouping['color_field']
        label = grouping['label']

        txn_data = (
            Transaction.objects
            .filter(account__profile__user=request.user)
            .values(name_field, color_field)
            .annotate(
                total=Round(
                    Sum(
                        Case(
                            When(amount_converted__isnull=False, then=F('amount_converted')),
                            default=F('amount'),
                        )
                    ), 2
                )
            )
        )

        colors = [f"#{item[color_field]}" for item in txn_data]

        data = {
            'labels': [item[name_field] for item in txn_data],
            'datasets': [
                {
                    'label': label,
                    'data': [item['total'] for item in txn_data],
                    'backgroundColor': [f"{color}6A" for color in colors],
                    'borderColor': colors,
                    'borderWidth': 1
                }
            ]
        }

        return Response(data)


class DashboardBalanceChartView(generics.GenericAPIView):
    serializer_class = StackedChartDataSerializer

    def get(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', 'week').lower()

        grouping_configs = {
            'week': {
                'trunc_func': TruncWeek(F('date')),
                'extract_func': ExtractWeek(F('date')),
                'label': 'Total by Week',
                'label_template': lambda item: f"Week {item['period_num']:02d}",
            },
            'month': {
                'trunc_func': TruncMonth(F('date')),
                'extract_func': ExtractMonth(F('date')),
                'label': 'Total by Month',
                'label_template': lambda item: f"Month {item['period_num']:02d}",
            }
        }

        config = grouping_configs.get(group_by)
        if not config:
            raise ValidationError({
                'group_by': 'Invalid value. Expected "week" or "month".'
            })

        queryset = (
            Transaction.objects
            .filter(account__profile__user=request.user)
            .values(period=config['trunc_func'])
            .annotate(period_num=config['extract_func'])
            .annotate(
                total=Sum(
                    Case(
                        When(amount_converted__isnull=False, then=F('amount_converted')),
                        default=F('amount'),
                    )
                )
            )
            .order_by('period')[:12]
        )

        data = {
            'labels': [config['label_template'](item) for item in queryset],
            'datasets': [
                {
                    'label': config['label'],
                    'data': [round(item['total'] or 0, 2) for item in queryset],
                }
            ]
        }

        return Response(data)
