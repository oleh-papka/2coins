from rest_framework import serializers

from ..models import Transaction, Account, Transfer, Category, Currency


class NestedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'currency']


class NestedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type']


class NestedCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'currency_type', 'symbol', 'abbr']


class TransactionDetailedSerializer(serializers.ModelSerializer):
    account = NestedAccountSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class CombinedActionSerializer(serializers.Serializer):
    combined_actions = serializers.ListField()


class CombinedActionQueryParamsSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    account_id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    all_transfers = serializers.BooleanField(required=False)


class ChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.DateTimeField())
    data = serializers.ListField(child=serializers.IntegerField())
