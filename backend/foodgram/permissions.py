from rest_framework import permissions
from rest_framework.reverse import reverse


class AdminAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class UserViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.path != reverse('user-me')
            or request.user.is_authenticated
        )
