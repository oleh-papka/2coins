from drf_spectacular.utils import extend_schema
from rest_framework import generics

from budget.api.serializers import AccountSimpleSerializer
from budget.models import Account


@extend_schema(
    summary='Create a new Account',
)
class AccountCreateView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSimpleSerializer


class AccountRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSimpleSerializer

    @extend_schema(
        summary='Get Account by id',
    )
    def get(self, request, *args, **kwargs):
        return super(AccountRetrieveDestroyView, self).get(request, *args, **kwargs)

    @extend_schema(
        summary='Delete specified Account by id',
    )
    def delete(self, request, *args, **kwargs):
        return super(AccountRetrieveDestroyView, self).delete(request, *args, **kwargs)
