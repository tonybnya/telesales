"""
Script Name : models.py
Description : Inventory/Revervation Model
Author      : @tonybnya
"""
from django.core.validators import MinValueValidator
from django.db import models


class Reservation(models.Model):
    """
    Modelisation of a Reservation.
    Lightweight to track reserved stock.
    """
    order = models.ForeignKey('sales.SalesOrder', on_delete=models.CASCADE, related_name='reservations')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reservations')

    qty = models.IntegerField(validators=[MinValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservations'
        unique_together = ['order', 'product']

    def __str__(self):
        return f"Reserved: {self.qty} x {self. product.name} for {self.order.number}"
