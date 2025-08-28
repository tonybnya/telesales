"""
Script Name : views.py
Description : Views of the Product Model
Author      : @tonybnya
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, ProductSummarySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product View.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product_type', 'favorite', 'responsible']
    search_fields = ['name', 'internal_reference', 'barcode', 'product_category']
    ordering_fields = ['name', 'sales_price', 'cost', 'quantity_on_hand', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'summary':
            return ProductSummarySerializer
        return ProductSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get a simplified product list for dropdowns.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ProductSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get products with low stock (available_quantity < 10).
        """
        low_stock_products = []
        for product in self.get_queryset():
            if product.available_quantity < 10:
                low_stock_products.append(product)

        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Get detailed availability infos for a product.
        """
        product = self.get_object()
        data = {
            'product_id': product.id,
            'product_name': product.name,
            'quantity_on_hand': product.quantity_on_hand,
            'available_quantity': product.available_quantity,
            'reserved_quantity': product.quantity_on_hand - product.available_quantity,
            'forecasted_quantity': product.forecasted_quantity
        }
        return Response(data)
