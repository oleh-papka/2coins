from drf_spectacular.utils import extend_schema
from rest_framework import generics

from budget.api.serializers import CategorySimpleSerializer
from budget.models import Category


@extend_schema(
    summary='Create a new Category',
)
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySimpleSerializer


class CategoryRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySimpleSerializer

    @extend_schema(
        summary='Get Category by id',
    )
    def get(self, request, *args, **kwargs):
        return super(CategoryRetrieveDestroyView, self).get(request, *args, **kwargs)

    @extend_schema(
        summary='Delete specified Category by id',
    )
    def delete(self, request, *args, **kwargs):
        return super(CategoryRetrieveDestroyView, self).delete(request, *args, **kwargs)
