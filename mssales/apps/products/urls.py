"""
Script Name : urls.py
Description : Define and register the routes for the products
Author      : @tonybnya
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls))
]
