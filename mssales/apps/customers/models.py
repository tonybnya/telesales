"""
Script Name : models.py
Description : Customer model
Author      : @tonybnya
"""


import re

from django.core.validators import EmailValidator
from django.db import models


class Customer(models.Model):
    """
    Modelisation of a Customer.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20)

    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    is_company = models.BooleanField(default=False)
    related_company = models.CharField(max_length=255, blank=True, null=True)

    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="United States")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # phone number format validation
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        if self.phone and not phone_pattern.match(self.phone.replace(' ', ' ').replace('-', '')):
            from django.core.exceptions import ValidationError
            raise ValidationError({'phone': 'Enter a valid phone number.'})

    @property
    def full_address(self):
        """
        Format full address.
        """
        address_parts = [
            self.street,
            f"{self.city}, {self.state} {self.zip_code}" if self.city and self.state else None, self.country
        ]
        return ', '.join(filter(None, address_parts))
