"""
Script Name : models.py
Description : Sales Order Models
Author      : @tonybnya
"""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction


class SalesOrder(models.Model):
    """
    Modelisation of a SalesOrder.
    """
    STATUS_CHOICES = [
        ('draft', 'DRAFT'),
        ('confirmed', 'CONFIRMED'),
        ('cancelled', 'CANCELLED')
    ]

    number = models.CharField(max_length=50, unique=True, editable=False)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='sales_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_orders'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.number:
            # generate a unique order number
            self.number = f"SO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number} - {self.customer.name}"

    @property
    def total_amount(self):
        """
        Calculate amount of total order.
        """
        return sum(line.line_total for line in self.order_lines.all())

    @property
    def grand_total(self):
        """
        Calculate grand total with VAT (20%)
        """
        return float(self.total_amount) * 1.20

    def confirm_order(self):
        """
        Confirm order and create reservations.
        """
        if self.status != 'draft':
            raise ValueError("Only draft orders can be confirmed")

        with transaction.atomic():
            # create reservations for all order lines
            for line in self.order_lines_all():
                if line.product.available_quantity < line.qty:
                    raise ValueError(f"Insufficient stock for {line.product.name}")

                from apps.inventory.models import Reservation
                Reservation.objects.create(
                    order=self,
                    product=line.product,
                    qty=line.qty
                )

            self.status = 'confirmed'
            self.save()

    def cancel_order(self):
        """
        Cancel order and release reservations
        """
        if self.status != 'confirmed':
            raise ValueError("Only confirmed orders can be cancelled")

        with transaction.atomic():
            # Delete all reservations
            from apps.inventory.models import Reservation
            Reservation.objects.filter(order=self).delete()

            self.status = 'cancelled'
            self.save()


class SalesOrderLine(models.Model):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='order_lines')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)

    qty = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_order_lines'
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.order.number} - {self.product.name} (x{self.qty})"

    @property
    def line_total(self):
        """
        Calculate line total: qty * unit_price * (1 - discount_pct)
        """
        discount_factor = 1 - (self.discount_pct / 100)
        return self.qty * self.unit_price * discount_factor

    def clean(self):
        super().clean()
        # set unit_price to product's sales_price if not provided
        if not self.unit_price and self.product:
            self.unit_price = self.product.sales_price
