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


class CombinedTxnTrfSerializer(serializers.Serializer):
    account = NestedAccountSerializer(required=False)
    account_from = NestedAccountSerializer(required=False)
    account_to = NestedAccountSerializer(required=False)
    category = NestedCategorySerializer(required=False)
    currency = NestedCurrencySerializer(required=False)
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False)
    amount_from = serializers.DecimalField(max_digits=20, decimal_places=8, required=False)
    amount_to = serializers.DecimalField(max_digits=20, decimal_places=8, required=False)
    amount_converted = serializers.DecimalField(max_digits=20, decimal_places=8, required=False)
    description = serializers.CharField()
    date = serializers.DateTimeField()

    action_type = serializers.CharField()
