from rest_framework import serializers

from ..models import Transaction, Account


class NestedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'currency']


class TransactionDetailSerializer(serializers.ModelSerializer):
    account = NestedAccountSerializer()

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
