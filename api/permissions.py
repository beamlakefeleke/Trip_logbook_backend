from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to allow only admins to access certain endpoints.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "admin"


class IsDriver(permissions.BasePermission):
    """
    Custom permission to allow only drivers to access their own data.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "driver"


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission: Drivers can only access their own trips/logs, Admins can access everything.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True  # Admins can access any object
        return obj.driver == request.user  # Drivers can only access their own records


class ReadOnly(permissions.BasePermission):
    """
    Grants read-only access to all users.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthenticatedAndOwner(permissions.BasePermission):
    """
    Custom permission to ensure that only the authenticated owner of an object can modify it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.driver == request.user  # Ensure the driver is the owner


class AdminOrReadOnly(permissions.BasePermission):
    """
    Admins have full access; other users have read-only access.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS requests
        return request.user and request.user.is_authenticated and request.user.role == "admin"
