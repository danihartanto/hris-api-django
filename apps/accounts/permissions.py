from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """
    Cara pakai di View:
    permission_classes = [HasPermission]
    required_permissions = ["employees.view"]
    """

    def has_permission(self, request, view):
        required = getattr(view, "required_permissions", [])

        if not required:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        user_perms = user.get_permissions()

        return all(perm in user_perms for perm in required)
