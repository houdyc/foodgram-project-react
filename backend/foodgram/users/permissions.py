from rest_framework import permissions


class IsAuthorPermission(permissions.BasePermission):
    """Проверка пользователя на роль автора."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminPermission(permissions.BasePermission):
    """Проверка пользователя на роль Администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )
