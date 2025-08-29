"""
Script Name : urls.py
Description : Define and register routes for Reservation
Author      : @tonybnya
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReservationViewSet

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls))
]
