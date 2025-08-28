"""
Script Name : serializers.py
Description : Serializers for the Customers app
Author      : @tonybnya
"""

import re

from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer of the Customer Model.
    """
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'billing_address', 'shipping_address',
            'is_company', 'related_company', 'street', 'city', 'state', 'zip_code',
            'country', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_address']

    def validate_phone(self, value):
        """
        Remove spaces and dashes to clean the phone number
        """
        clean_phone = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_pattern.match(clean_phone):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Customer with this email already exists.")
        return value


class CustomerSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for dropdown lists
    """
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'city', 'state']
