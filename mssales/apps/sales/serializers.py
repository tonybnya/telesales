"""
Script Name : serializers.py
Description : Serializers for the Sales app
Author      : @tonybnya
"""


from rest_framework import serializers

from .models import SalesOrderLine


class SalesOrderLine(serializers.ModelSerializer):
    """
    Serializer of the SalesOrderLine Model.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_reference = serializers.CharField(source='product.internal_reference', read_only=True)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = SalesOrderLine
        fields = [
            'id', 'product', 'product_name', 'product_reference',
            'qty', 'unit_price', 'discount_pct', 'line_total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'line_total', 'created_at', 'updated_at']

    def validate_qty(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price must be positive.")
        return value

    def validate_discount_pct(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount must be between 0 and 100.")
        return value

    def validate(self, data):
        """
        Check product availability when creating/updating order lines
        """
        product = data.get('product')
        qty = data.get('qty')

        if product and qty:
            current_reserved = 0
            if self.instance and self.instance.order.status == 'confirmed':
                current_reserved = self.instance.qty

            available = product.available_quantity + current_reserved
            if qty > available:
                raise serializers.ValidationError(f"Insufficient stock. Available: {available}, Requested: {qty}")
        return data


class SalesOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    order_lines = SalesOrderLineSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    grand_total = serializers.ReadOnlyField()

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'number', 'customer', 'customer_name', 'customer_email',
            'status', 'notes', 'order_lines', 'total_amount', 'grand_total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'number', 'total_amount', 'grand_total', 'created_at', 'updated_at']

    def validate_status(self, value):
        if self.instance:
            current_status = self.instance.status
            allowed_transitions = {
                'draft': ['confirmed', 'cancelled'],
                'confirmed': ['cancelled'],
                'cancelled': []
            }

            if value != current_status and value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(f"Cannot change status from {current_status} to {value}")

        return value


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    """
    Special serializer for creating orders with lines
    """
    order_lines = SalesOrderLineSerializer(many=True)

    class Meta:
        model = SalesOrder
        fields = ['customer', 'notes', 'order_lines']

    def create(self, validated_data):
        order_lines_data = validated_data.pop('order_lines')
        order = SalesOrder.objects.create(**validated_data)

        for line_data in order_lines_data:
            if 'unit_price' not in line_data or line_data['unit_price'] is None:
                line_data['unit_price'] = line_data['product'].sales_price

            SalesOrderLine.objects.create(order=order, **line_data)
        return order


class SalesOrderSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for lists.
    """
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = SalesOrder
        fields = ['id', 'number', 'customer_name', 'status', 'total_amount']
