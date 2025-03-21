from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    DriverRegisterView,
    DriverLoginView,
    DriverListView,
    TripViewSet,
    LogEntryViewSet,
    TruckViewSet,
    ComplianceCheckView,
)

# 🚀 Create a router for ViewSets (Trips, Logs, Trucks)
router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'logs', LogEntryViewSet, basename='log')
router.register(r'trucks', TruckViewSet, basename='truck')

# 🛣️ URL Patterns
urlpatterns = [
    # Authentication Routes
    path('auth/register/', DriverRegisterView.as_view(), name='driver-register'),
    path('auth/login/', DriverLoginView.as_view(), name='driver-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Driver Management (Admin Only)
    path('drivers/', DriverListView.as_view(), name='driver-list'),

    # Compliance Check
    path('compliance/', ComplianceCheckView.as_view(), name='compliance-check'),

    # Include ViewSets (Trips, Logs, Trucks)
    path('', include(router.urls)),
]
