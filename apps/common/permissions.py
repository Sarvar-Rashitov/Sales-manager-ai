"""
Role-based permission helpers used across DRF views and Django views.
"""
from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "owner"


class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("owner", "admin")


class IsSalesManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "owner", "admin", "sales_manager"
        )


class IsOperator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "owner", "admin", "sales_manager", "operator"
        )


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated  # all authenticated users can view
