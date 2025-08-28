"""
Script Name : models.py
Description : Product Model
Author      : @tonybnya
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Product(models.Model):
    """
    Modelisation of a Product.
    """
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]

    PRODUCT_TYPE_CHOICES = [
        ('storable_product', 'Storable Product'),
        ('consumable', 'Consumable'),
        ('service', 'Service')
    ]

    name = models.CharField(max_length=255)
    internal_reference = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    product_category = models.CharField(max_length=255, default="All / Saleable / Office Furniture")
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPE_CHOICES, default='storable_product')
    favorite = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="normal")

    responsible = models.CharField(max_length=255, blank=True, null=True)

    sales_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    quantity_on_hand = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    forecasted_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    activity_exception_decoration = models.CharField(max_length=255, blank=True, null=True)
    # activity = models.CharField(max_length=255, blank=True, null=True)
    # exception = models.CharField(max_length=255, blank=True, null=True)
    # decoration = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.internal_reference})'

    @property
    def available_quantity(self):
        """
        Calculate available quantity (on_hand - reserved)
        """
        from apps.inventory.models import Reservation
        reserved = Reservation.objects.filter(product=self).aggregate(
            total_reserved=models.Sum('qty')
        )['total_reserved'] or 0
        return self.quantity_on_hand - reserved
