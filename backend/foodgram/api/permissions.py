from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request


class CustomRecipePermissions(BasePermission):
    def has_permission(self, request: Request, view):
        if 'download_shopping_cart' in str(request.path):
            return request.user.is_authenticated
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if 'favorite' in str(request.path):
            return request.user.is_authenticated
        return (request.method in SAFE_METHODS or request.user == obj.author
                or request.user.is_superuser)


class CustomUserPermissions(BasePermission):
    def has_permission(self, request: Request, view):
        if ('subscriptions' or 'me') in str(request.path):
            return request.user.is_authenticated
        return ((request.method == 'POST' and request.path == '/api/users/')
                or (request.method == 'POST' and 'login' in str(request.path))
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if 'subscribe' in str(request.path):
            return request.user.is_authenticated

