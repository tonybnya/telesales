"""
Script Name : serializers.py
Description : Serializers for the Products app
Author      : @tonybnya
"""

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'internal_reference', 'barcode', 'product_category',
            'product_type', 'favorite', 'responsible', 'sales_price', 'cost',
            'quantity_on_hand', 'forecasted_quantity', 'available_quantity',
            'activity', 'exception', 'decoration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'available_quantity']

    def validate_sales_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Sales price must be positive.")
        return value

    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost must be positive.")
        return value

    def validate_internal_reference(self, value):
        if self.instance:
            if Product.objects.exclude(pk=self.instance.pk).filter(internal_reference=value).exists():
                raise serializers.ValidationError("Internal reference must be unique.")
        else:
            if Product.objects.filter(internal_reference=value).exists():
                raise serializers.ValidationError("Internal reference must be unique.")
        return value


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for dropdown lists and references.
    """
    available_quantity = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'internal_reference', 'sales_price', 'available_quantity']
