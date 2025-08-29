"""
Script Name : urls.py
Description : Define and register routes related to authentication
Author      : @tonybnya
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomeTokenObtainPairView, user_profile, verify_token

urlpatterns = [
    path('login/', CustomeTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', user_profile, name='user_profile'),
    path('verify/', verify_token, name='verify_token')
]
