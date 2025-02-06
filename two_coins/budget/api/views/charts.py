import itertools
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Case, When, F, Sum
from django.db.models.functions import TruncDate, Round, ExtractWeek, TruncWeek, TruncMonth, ExtractMonth, Coalesce
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from budget.api.serializers import ChartDataSerializer
from budget.models import Transaction, Transfer, Currency, Account, Category
from misc.utils import get_date_range


def get_common_currencies(user, start_date, end_date, extra_filter_kwargs=None):
    """Fetch currencies that appear in every transaction."""

    base_filter_kwargs = {
        'account__profile__user': user,
        'date__range': (start_date, end_date),
    }

    filter_kwargs = base_filter_kwargs | extra_filter_kwargs if extra_filter_kwargs else base_filter_kwargs

    currency_pairs = list(
        Transaction.objects
        .filter(**filter_kwargs)
        .values_list('currency_id', 'account__currency_id')
        .distinct()
    )

    if not currency_pairs:
        return set()

    items = set()
    must_be_set = set()

    for x, y in currency_pairs:
        if x == y:
            must_be_set.add(x)
        items.add(x)
        items.add(y)

    # -- Early check: maybe must_be_set alone covers all pairs
    if all(must_be_set.intersection(pair) for pair in currency_pairs):
        return must_be_set

    # -- Remove the 'must be' items so we only combine the rest
    remaining_items = items - must_be_set
    for r in range(1, len(remaining_items) + 1):
        for combo in itertools.combinations(remaining_items, r):
            candidate_set = must_be_set.union(combo)
            # Check if candidate_set hits all pairs
            if all(candidate_set.intersection(pair) for pair in currency_pairs):
                return candidate_set
    return set()


class TransactionsByAccount(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    @extend_schema(
        operation_id='chart_transactions_by_account',
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        summary='Transactions by specified Account',
    )
    def get(self, request, account_id, *args, **kwargs):
        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))
        if not Account.objects.get(id=account_id):
            raise ValidationError(
                {'account_id': 'Invalid value. Value must be a valid Account ID'}
            )
        account_id = int(account_id)

        trf_data = []
        trf_queryset = (
            Transfer.objects
            .filter(
                Q(account_to=account_id) | Q(account_from=account_id),
                date__range=(start_date, end_date)
            )
            .annotate(
                date_only=TruncDate('date'),
                total_amount_from=Round(Sum(F('amount_from')), 2),
                total_amount_to=Round(Sum(F('amount_to')), 2),
            )
            .values(
                'date_only',
                'total_amount_from',
                'total_amount_to',
                'account_from_id',
                'account_from__currency',
                'account_to__currency',
            )
            .order_by('date_only')
        )

        for trf in trf_queryset:
            from_currency = trf['account_from__currency']
            to_currency = trf['account_to__currency']
            from_id = trf['account_from_id']
            total_amount_from = trf['total_amount_from']
            total_amount_to = trf['total_amount_to']

            if from_currency == to_currency:
                total_amount = -total_amount_from if from_id == account_id else total_amount_from
            else:
                total_amount = -total_amount_from if from_id == account_id else total_amount_to

            trf_data.append({
                'date_only': trf['date_only'],
                'category__name': 'Transfer',
                'category__color': '0ccaf0',
                'total_amount': total_amount,
            })

        # accounts data
        txn_queryset = (
            Transaction.objects
            .filter(
                account__profile__user=request.user,
                account_id=account_id,
                date__range=(start_date, end_date)
            )
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

        if trf_data:
            txn_queryset = list(txn_queryset) + trf_data
            txn_queryset.sort(key=lambda x: x['date_only'])

        labels = []
        dataset_dict = defaultdict(lambda: {'backgroundColor': None, 'data': defaultdict(float)})

        for txn in txn_queryset:
            date = txn['date_only'].strftime('%d/%m')
            if date not in labels:
                labels.append(date)

            label_name = txn['category__name']
            label_color = txn['category__color']
            total_amount = float(txn['total_amount'])

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
                }
                for label_name, label in dataset_dict.items()
            ]
        }

        return Response(data)


class TransactionsByCategory(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    def get_currency_transactions(self, currency_id, txn_filter_kwargs):
        return (
            Transaction.objects
            .filter(**txn_filter_kwargs)
            .annotate(date_only=TruncDate('date'))
            .values('date_only', 'account__name', 'account__color')
            .annotate(
                total=Sum(
                    Case(
                        When(Q(currency_id=currency_id), then=F('amount')),
                        When(Q(account__currency_id=currency_id), then=F('amount_converted')),
                        default=None,
                    )
                )
            )
            .order_by('date_only')
        )

    @extend_schema(
        operation_id='chart_transactions_by_category',
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        summary='Transactions by specified Category',
    )
    def get(self, request, category_id, *args, **kwargs):
        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        if not Category.objects.get(id=category_id):
            raise ValidationError(
                {'category_id': 'Invalid value. Value must be a valid Category ID'}
            )
        category_id = int(category_id)

        txn_filter_kwargs = {
            'account__profile__user': request.user,
            'date__range': (start_date, end_date),
            'category_id': category_id,
        }

        distinct_currencies = get_common_currencies(request.user, start_date, end_date, txn_filter_kwargs)

        datasets = []
        labels = []

        for currency in distinct_currencies:
            queryset = self.get_currency_transactions(currency, txn_filter_kwargs)
            currency_obj = Currency.objects.get(id=currency)

            dataset_dict = defaultdict(lambda: {'color': None, 'data': defaultdict(Decimal)})

            for txn in queryset:
                date = txn['date_only'].strftime('%d/%m')

                if not date in labels:
                    labels.append(date)

                account_name = txn['account__name']
                total_amount = round(txn['total'] or 0, 2)

                account = dataset_dict[account_name]
                account['color'] = txn['account__color']
                account['data'][date] += total_amount

            dataset = [{
                "label": account_name,
                "data": [account["data"][date] for date in labels],
                "backgroundColor": f'#{account["color"]}6A',
                "borderColor": f'#{account["color"]}',
                "stack": f"{currency_obj.symbol}"
            } for account_name, account in dataset_dict.items()
                if any(account["data"][date] for date in labels)
            ]

            datasets += dataset

        return Response({"labels": labels, "datasets": datasets, })


class TransactionsByCategories(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    def get_currency_transactions(self, user, start_date, end_date, currency_id, category_type=None):
        """Fetch transaction data for a specific currency."""

        filter_kwargs = {
            'account__profile__user': user,
            'date__range': (start_date, end_date),
        }

        if category_type:
            filter_kwargs |= {'category__category_type': category_type}

        return (
            Transaction.objects
            .filter(**filter_kwargs)
            .annotate(date_only=TruncDate('date'))
            .values('date_only', 'category__name', 'category__color')
            .annotate(
                total=Sum(
                    Case(
                        When(Q(account__currency_id=currency_id), then=Coalesce(F('amount_converted'), F('amount'))),
                        default=None,
                    )
                )
            )
            .order_by('date_only')
        )

    @extend_schema(
        operation_id='chart_transactions_by_categories',
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        summary='Transactions by Categories',
    )
    def get(self, request, *args, **kwargs):
        category_type = request.query_params.get('category_type', None)

        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        distinct_currencies = get_common_currencies(request.user, start_date, end_date)

        labels = []
        datasets = []

        for currency in distinct_currencies:
            queryset = self.get_currency_transactions(request.user, start_date, end_date, currency, category_type)
            currency_obj = Currency.objects.get(id=currency)

            dataset_dict = defaultdict(lambda: {'color': None, 'data': defaultdict(float)})

            for txn in queryset:
                date = txn['date_only'].strftime('%d/%m')

                if date not in labels:
                    labels.append(date)

                category_name = txn['category__name']
                total_amount = round(txn['total'] or 0, 2)

                category = dataset_dict[category_name]
                category['color'] = txn['category__color']
                category['data'][date] += float(total_amount)

            dataset = [{
                "label": f"{category_name} {currency_obj.symbol}",
                "data": [category["data"][date] for date in labels],
                "backgroundColor": f'#{category["color"]}6A',
                "borderColor": f'#{category["color"]}',
                "stack": f"{currency_obj.symbol}"
            } for category_name, category in dataset_dict.items()
                if any(category["data"][date] for date in labels)
            ]

            datasets += dataset

        return Response({"labels": labels, "datasets": datasets, })


class TransactionsByAccounts(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    def get_currency_transactions(self, user, start_date, end_date, currency_id):
        """Fetch transaction data for a specific currency."""

        return (
            Transaction.objects
            .filter(account__profile__user=user, date__range=(start_date, end_date))
            .annotate(date_only=TruncDate('date'))
            .values('date_only', 'account__name', 'account__color')
            .annotate(
                total=Sum(
                    Case(
                        When(Q(account__currency_id=currency_id), then=Coalesce(F('amount_converted'), F('amount'))),
                        default=None,
                    )
                )
            )
            .order_by('date_only')
        )

    @extend_schema(
        operation_id='chart_transactions_by_accounts',
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, description='Start date'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, description='End date'),
        ],
        summary='Transactions by Accounts',
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date = get_date_range(request.query_params.get('start_date', None),
                                              request.query_params.get('end_date', None))

        distinct_currencies = get_common_currencies(request.user, start_date, end_date)

        labels = []
        datasets = []

        for currency in distinct_currencies:
            queryset = self.get_currency_transactions(request.user, start_date, end_date, currency)
            currency_obj = Currency.objects.get(id=currency)

            dataset_dict = defaultdict(lambda: {'color': None, 'data': defaultdict(float)})

            for txn in queryset:
                date = txn['date_only'].strftime('%d/%m')

                if date not in labels:
                    labels.append(date)

                account_name = txn['account__name']
                total_amount = round(txn['total'] or 0, 2)

                account = dataset_dict[account_name]
                account['color'] = txn['account__color']
                account['data'][date] += float(total_amount)

            dataset = [{
                "label": account_name,
                "data": [account["data"][date] for date in labels],
                "backgroundColor": f'#{account["color"]}6A',
                "borderColor": f'#{account["color"]}',
                "stack": f"{currency_obj.symbol}"
            } for account_name, account in dataset_dict.items()
                if any(account["data"][date] for date in labels)
            ]

            datasets += dataset

        return Response({"labels": labels, "datasets": datasets, })


class BalanceByType(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    GROUPING_CONFIGS = {
        'category': {
            'name': 'category__name',
            'color': 'category__color',
            'label': 'Total by Category'
        },
        'account': {
            'name': 'account__name',
            'color': 'account__color',
            'label': 'Total by Account'
        }
    }

    def get_grouping_config(self, group_by):
        """Fetch grouping configuration based on the `group_by` parameter."""

        config = self.GROUPING_CONFIGS.get(group_by)

        if not config:
            raise ValidationError({
                'group_by': 'Invalid value. Expected "category" or "account"'
            })

        return config

    def get_currency_transactions(self, user, start_date, end_date, currency_id, config):
        """Fetch transaction data for a specific currency."""

        return (
            Transaction.objects
            .filter(
                account__profile__user=user,
                date__range=(start_date, end_date)
            )
            .filter(
                Q(currency_id=currency_id) | (Q(account__currency_id=currency_id) & Q(amount_converted__isnull=False))
            )
            .values(config['name'], config['color'])
            .annotate(
                total=Round(
                    Sum(
                        Case(
                            When(Q(currency_id=currency_id), then=F('amount')),
                            When(Q(account__currency_id=currency_id), then=F('amount_converted')),
                            default=None,
                        )
                    ), 2
                )
            )
            .order_by(config['name'])
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='group_by',
                type=OpenApiTypes.STR,
                description='Grouping type for transaction sums',
                enum=['category', 'account'],
            ),
        ],
        summary='Transactions sum by specified group type',
    )
    def get(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', 'category').lower()
        datasets = []
        labels = None

        config = self.get_grouping_config(group_by)
        name = config['name']
        color = config['color']

        start_date, end_date = get_date_range()

        distinct_currencies = get_common_currencies(request.user, start_date, end_date)

        for currency in distinct_currencies:
            queryset = self.get_currency_transactions(request.user, start_date, end_date, currency, config)
            colors = [f"#{item[color]}" for item in queryset]

            currency_obj = Currency.objects.get(id=currency)
            datasets.append({
                'label': f"{config['label']} {currency_obj.abbr}",
                'symbol': currency_obj.symbol,
                'data': [round(item['total'] or 0, 2) for item in queryset],
                'backgroundColor': [f"{color}6A" for color in colors],
                'borderColor': colors,
            })

            if not labels:
                labels = [item[name] for item in queryset]

        return Response({'labels': labels, 'datasets': datasets})


class BalanceByPeriod(generics.GenericAPIView):
    serializer_class = ChartDataSerializer

    GROUPING_CONFIGS = {
        'week': {
            'trunc_func': TruncWeek(F('date')),
            'extract_func': ExtractWeek(F('date')),
            'label_template': lambda item: f"Week {item['period_num']:02d}",
            'time_delta': timedelta(weeks=12),
        },
        'month': {
            'trunc_func': TruncMonth(F('date')),
            'extract_func': ExtractMonth(F('date')),
            'label_template': lambda item: f"Month {item['period_num']:02d}",
            'time_delta': timedelta(days=365),
        },
    }

    def get_grouping_config(self, group_by):
        """Fetch grouping configuration based on the `group_by` parameter."""

        config = self.GROUPING_CONFIGS.get(group_by)

        if not config:
            raise ValidationError({
                'group_by': 'Invalid value. Expected "week" or "month"'
            })

        return config

    def get_currency_transactions(self, user, start_date, end_date, currency_id, config):
        """Fetch transaction data for a specific currency."""

        return (
            Transaction.objects
            .filter(account__profile__user=user, date__range=(start_date, end_date))
            .values(period=config['trunc_func'])
            .annotate(
                period_num=config['extract_func'],
                total=Sum(
                    Case(
                        When(Q(account__currency_id=currency_id), then=Coalesce(F('amount_converted'), F('amount'))),
                        default=None,
                    )
                )
            )
            .order_by('period')[:12]
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='group_by',
                type=OpenApiTypes.STR,
                description='Grouping period for transaction sums',
                enum=['week', 'month'],
            ),
        ],
        summary='Transactions sum by specified group period',
    )
    def get(self, request, *args, **kwargs):
        group_by = request.query_params.get('group_by', 'week').lower()
        config = self.get_grouping_config(group_by)

        end_date = timezone.now()
        start_date = end_date - config['time_delta']

        datasets = []
        labels = None

        distinct_currencies = get_common_currencies(request.user, start_date, end_date)

        for currency in distinct_currencies:
            queryset = self.get_currency_transactions(request.user, start_date, end_date, currency, config)

            currency_obj = Currency.objects.get(id=currency)
            datasets.append({
                'label': currency_obj.abbr,
                'symbol': currency_obj.symbol,
                'data': [round(item['total'] or 0, 2) for item in queryset],
            })

            if not labels:
                labels = [config['label_template'](item) for item in queryset]

        return Response({'datasets': datasets, 'labels': labels or []})
