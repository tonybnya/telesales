"""
Script Name : views.py
Description : Views of the Customer Model
Author      : @tonybnya
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer, CustomerSummarySerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer View.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_company', 'city', 'state', 'country']
    search_fields = ['name', 'email', 'phone', 'city', 'state']
    ordering_fields = ['name', 'created_at', 'city', 'state']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'summary':
            return CustomerSummarySerializer
        return CustomerSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get simplified customer list for dropdowns
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = CustomerSummarySerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def companies(self, request):
        """
        Get company customers
        """
        companies = self.get_queryset().filter(is_company=True)
        serializer = CustomerSerializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """
        Get all orders for a customer.
        """
        customer = self.get_object()
        from apps.sales.serializers import SalesOrderSerializer
        orders = customer.sales_orders.all().order_by('-created_at')
        serializer = SalesOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get customer stats.
        """
        customer = self.get_object()
        orders = customer.sales_orders.all()

        stats = {
            'customer_id': customer.id,
            'customer_name': customer.name,
            'total_orders': orders.count(),
            'draft_orders': orders.filter(status='draft').count(),
            'confirmed_orders': orders.filter(status='confirmed').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'total_amount': sum(order.total_amount for order in orders)
        }
        return Response(stats)
