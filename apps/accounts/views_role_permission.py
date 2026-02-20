from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Role, Permission, RolePermission, UserRole, User
from .serializers import (
    RoleSerializer,
    RoleDetailSerializer,
    PermissionSerializer,
    AssignPermissionToRoleSerializer,
    AssignRoleToUserSerializer,
    UserRoleDetailSerializer,
    UserMiniSerializer,
)


# ============================================================
# PERMISSION CRUD
# ============================================================
class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by("module", "action")
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["module", "is_active"]
    search_fields = ["code", "name", "module", "action"]
    ordering_fields = ["module", "action", "code", "created_at"]


# ============================================================
# ROLE CRUD
# ============================================================
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by("name")
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return RoleDetailSerializer
        return RoleSerializer

    # -----------------------------
    # Assign permissions to role
    # -----------------------------
    @action(detail=False, methods=["post"], url_path="assign-permissions")
    def assign_permissions(self, request):
        """
        Body:
        {
          "role_id": 1,
          "permission_ids": [1,2,3]
        }
        """
        serializer = AssignPermissionToRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data["role_id"]
        permission_ids = serializer.validated_data["permission_ids"]

        role = Role.objects.filter(id=role_id).first()
        if not role:
            return Response({"detail": "Role tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        permissions = Permission.objects.filter(id__in=permission_ids)
        if permissions.count() != len(permission_ids):
            return Response({"detail": "Ada permission yang tidak ditemukan"}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        for perm in permissions:
            obj, is_created = RolePermission.objects.get_or_create(role=role, permission=perm)
            if is_created:
                created += 1

        return Response(
            {
                "message": "Assign permission berhasil",
                "role_id": role.id,
                "created_count": created,
            },
            status=status.HTTP_200_OK
        )

    # -----------------------------
    # Remove permissions from role
    # -----------------------------
    @action(detail=False, methods=["post"], url_path="remove-permissions")
    def remove_permissions(self, request):
        """
        Body:
        {
          "role_id": 1,
          "permission_ids": [1,2,3]
        }
        """
        serializer = AssignPermissionToRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data["role_id"]
        permission_ids = serializer.validated_data["permission_ids"]

        role = Role.objects.filter(id=role_id).first()
        if not role:
            return Response({"detail": "Role tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        deleted, _ = RolePermission.objects.filter(
            role=role,
            permission_id__in=permission_ids
        ).delete()

        return Response(
            {
                "message": "Remove permission berhasil",
                "role_id": role.id,
                "deleted_count": deleted,
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# USER ROLE MANAGEMENT
# ============================================================
class UserRoleViewSet(viewsets.ViewSet):
    """
    Endpoint untuk assign/unassign role ke user.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="users")
    def users(self, request):
        """
        List user (mini) untuk UI assign role.
        """
        qs = User.objects.all().order_by("full_name")
        return Response(UserMiniSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="user/(?P<user_id>[^/.]+)")
    def user_detail(self, request, user_id=None):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "User tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserRoleDetailSerializer(user).data)

    @action(detail=False, methods=["post"], url_path="assign-roles")
    def assign_roles(self, request):
        """
        Body:
        {
          "user_id": 10,
          "role_ids": [1,2]
        }
        """
        serializer = AssignRoleToUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        role_ids = serializer.validated_data["role_ids"]

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "User tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        roles = Role.objects.filter(id__in=role_ids)
        if roles.count() != len(role_ids):
            return Response({"detail": "Ada role yang tidak ditemukan"}, status=status.HTTP_400_BAD_REQUEST)

        created = 0
        for role in roles:
            obj, is_created = UserRole.objects.get_or_create(user=user, role=role)
            if is_created:
                created += 1

        return Response(
            {
                "message": "Assign role berhasil",
                "user_id": user.id,
                "created_count": created,
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"], url_path="remove-roles")
    def remove_roles(self, request):
        """
        Body:
        {
          "user_id": 10,
          "role_ids": [1,2]
        }
        """
        serializer = AssignRoleToUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        role_ids = serializer.validated_data["role_ids"]

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "User tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

        deleted, _ = UserRole.objects.filter(
            user=user,
            role_id__in=role_ids
        ).delete()

        return Response(
            {
                "message": "Remove role berhasil",
                "user_id": user.id,
                "deleted_count": deleted,
            },
            status=status.HTTP_200_OK
        )
