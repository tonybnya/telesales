"""
Script Name : urls.py
Description : Define and register the routes for the customers
Author      : @tonybnya
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls))
]
