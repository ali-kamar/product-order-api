import django_filters
from .models import Product, Order
from rest_framework import filters

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'price': ['lt', 'gt', 'exact', 'range'],
        }

#Create custom filter backend to filter products that are in stock
class InStockFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)
    
class OrderFilter(django_filters.FilterSet):
    #we override the created_at field to filter by date only, not datetime
    created_at = django_filters.DateFilter(field_name='created_at__date')
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['lt', 'gt', 'exact'],
        }