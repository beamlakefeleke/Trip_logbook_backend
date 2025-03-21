from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Django Admin Panel
    path("api/", include("api.urls")),  # ✅ Include API endpoints
]
