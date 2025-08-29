"""
Script Name : urls.py
Description : Define and register routes for Sales
Author      : @tonybnya
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SalesOrderLineViewSet, SalesOrderViewSet

router = DefaultRouter()
router.register(r'sales-orders', SalesOrderViewSet)
router.register(r'sales-order-lines', SalesOrderLineViewSet)

urlpatterns = [
    path('', include(router.urls))
]
