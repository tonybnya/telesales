"""
Script Name : views.py
Description : Views of the Reservation Model
Author      : @tonybnya
"""
from apps.products.models import Product
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Reservation
from .serializers import InventoryStatusSerializer, ReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """
    Reservation View.
    """
    queryset = Reservation.objects.all().select_related('order__customer', 'product')
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order', 'product', 'order__status', 'order__customer']
    search_fields = ['order__number', 'product__name', 'order__name']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """
        Get comprehensive inventory status report
        """
        products = Product.objects.all()
        inventory_data = []

        for product in products:
            reservations = Reservation.objects.filter(product=product)
            total_reserved = reservations.aggregate(Sum('qty'))['qty__sum'] or 0
            reservations_count = reservations.count()

            inventory_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'internal_reference': product.internal_reference,
                'quantity_on_hand': product.quantity_on_hand,
                'total_reserved': total_reserved,
                'available_quantity': product.quantity_on_hand - total_reserved,
                'reservations_count': reservations_count
            })

        # Sort by available quantity (lowest first)
        inventory_data.sort(key=lambda x: x['available_quantity'])
        
        serializer = InventoryStatusSerializer(inventory_data, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock_report(self, request):
        """Get products with low available stock"""
        threshold = int(request.query_params.get('threshold', 10))
        
        low_stock_products = []
        for product in Product.objects.all():
            if product.available_quantity < threshold:
                reservations = Reservation.objects.filter(product=product)
                total_reserved = reservations.aggregate(Sum('qty'))['qty__sum'] or 0
                
                low_stock_products.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'internal_reference': product.internal_reference,
                    'quantity_on_hand': product.quantity_on_hand,
                    'total_reserved': total_reserved,
                    'available_quantity': product.available_quantity,
                    'reservations_count': reservations.count()
                })
        
        serializer = InventoryStatusSerializer(low_stock_products, many=True)
        return Response(serializer.data)
