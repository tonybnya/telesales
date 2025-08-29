"""
Script Name : views.py
Description : Views of the Sales Model
Author      : @tonybnya
"""

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SalesOrder, SalesOrderLine
from .serializers import (SalesOrderCreateSerializer, SalesOrderLineSerializer,
                          SalesOrderSerializer, SalesOrderSummarySerializer)


class SalesOrderViewSet(viewsets.ModelViewSet):
    """
    Sales Order View.
    """
    queryset = SalesOrder.objects.all().select_related('customer').prefetch_related('order_lines__product')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'created_at']
    search_fields = ['number', 'customer__name', 'customer__email', 'notes']
    ordering_fields = ['created_at', 'number', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return SalesOrderCreateSerializer
        elif self.action == 'list':
            return SalesOrderSummarySerializer
        return SalesOrderSerializer

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a draft order"""
        order = self.get_object()
        
        try:
            with transaction.atomic():
                order.confirm_order()
                serializer = SalesOrderSerializer(order)
                return Response({
                    'message': 'Order confirmed successfully',
                    'order': serializer.data
                })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {'error': 'Failed to confirm order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a confirmed order"""
        order = self.get_object()
        
        try:
            with transaction.atomic():
                order.cancel_order()
                serializer = SalesOrderSerializer(order)
                return Response({
                    'message': 'Order cancelled successfully',
                    'order': serializer.data
                })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {'error': 'Failed to cancel order'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        orders = self.get_queryset()
        
        stats = {
            'total_orders': orders.count(),
            'draft_orders': orders.filter(status='draft').count(),
            'confirmed_orders': orders.filter(status='confirmed').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'total_revenue': sum(order.total_amount for order in orders.filter(status='confirmed')),
            'pending_revenue': sum(order.total_amount for order in orders.filter(status='draft')),
        }
        
        return Response(stats)

    @action(detail=True, methods=['get'])
    def lines(self, request, pk=None):
        """Get order lines for a specific order"""
        order = self.get_object()
        lines = order.order_lines.all()
        serializer = SalesOrderLineSerializer(lines, many=True)
        return Response(serializer.data)


class SalesOrderLineViewSet(viewsets.ModelViewSet):
    """
    Sales Order Line View
    """
    queryset = SalesOrderLine.objects.all().select_related('order', 'product')
    serializer_class = SalesOrderLineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order', 'product', 'order__status']
    search_fields = ['product__name', 'order__number']
    ordering = ['id']

    def perform_create(self, serializer):
        """Set unit_price to product's sales_price if not provided"""
        unit_price = serializer.validated_data.get('unit_price')
        if not unit_price:
            product = serializer.validated_data['product']
            serializer.save(unit_price=product.sales_price)
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Ensure order is still modifiable"""
        order = serializer.instance.order
        if order.status not in ['draft']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot modify lines of non-draft orders")
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure order is still modifiable"""
        if instance.order.status not in ['draft']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Cannot delete lines from non-draft orders")
        instance.delete()
