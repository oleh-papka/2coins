from rest_framework import serializers

from ..models import Transaction, Account, Transfer, Category, Currency


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'icon', 'color']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer()

    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'currency', 'icon', 'color', 'description']


class TransactionSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    category = CategorySerializer()
    currency = CurrencySerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'amount_converted', 'account', 'category', 'currency', 'description', 'date']


class TransactionCombinedSerializer(TransactionSerializer):
    action_type = serializers.CharField()

    class Meta(TransactionSerializer.Meta):
        fields = TransactionSerializer.Meta.fields + ['action_type']


class TransferSerializer(serializers.ModelSerializer):
    account_from = AccountSerializer()
    account_to = AccountSerializer()

    class Meta:
        model = Transfer
        fields = ['id', 'amount_from', 'amount_to', 'account_from', 'account_to', 'date', 'description']


class TransferCombinedSerializer(TransferSerializer):
    action_type = serializers.CharField()

    class Meta(TransferSerializer.Meta):
        fields = TransferSerializer.Meta.fields + ['action_type']


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
    datasets = serializers.ListField()
