from rest_framework.permissions import SAFE_METHODS, BasePermission


class InactiveEntitiesAreReadOnly(BasePermission):
    message = "This entity is inactive and can no longer be changed."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.is_active
