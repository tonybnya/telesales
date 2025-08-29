"""
Script Name : serializers.py
Description : Serializers of the Reservations
Author      : @tonybnya
"""
from rest_framework import serializers

from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer of the Reservation.
    """
    order_number = serializers.CharField(source='order.number', read_only=True)
    customer_name = serializers.CharField(source='order.customer.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_reference = serializers.CharField(source='product.internal_reference', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'order', 'order_number', 'customer_name',
            'product', 'product_name', 'product_reference',
            'qty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventoryStatusSerializer(serializers.Serializer):
    """
    Serializer for inventory status reports
    """
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    internal_reference = serializers.CharField()
    quantity_on_hand = serializers.IntegerField()
    total_reserved = serializers.IntegerField()
    available_quantity = serializers.IntegerField()
    reservations_count = serializers.IntegerField()
