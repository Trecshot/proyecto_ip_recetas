from rest_framework.permissions import BasePermission, SAFE_METHODS


def in_group(user, name):
    return user.groups.filter(name=name).exists()


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff or in_group(request.user, "Administrador")))


class RecipePermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.is_staff or in_group(user, "Administrador"):
            return True
        if request.method in SAFE_METHODS:
            return obj.estado == obj.Estado.PUBLICADA or (in_group(user, "Cocinero") and obj.cocinero_id == user.id)
        return in_group(user, "Cocinero") and obj.cocinero_id == user.id


class OwnResourcePermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_superuser or obj.usuario_id == request.user.id


class IsCookOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser or in_group(user, "Administrador") or in_group(user, "Cocinero")))
