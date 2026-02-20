from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, MeView, EmployeeUserViewSet
from .views_role_permission import RoleViewSet, PermissionViewSet, UserRoleViewSet

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="roles")
router.register(r"permissions", PermissionViewSet, basename="permissions")
router.register(r"employees", EmployeeUserViewSet, basename="employees")

urlpatterns = [
    # auth
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),

    # role & permission
    path("", include(router.urls)),

    # user role management
    path("user-role/users/", UserRoleViewSet.as_view({"get": "users"})),
    path("user-role/user/<int:user_id>/", UserRoleViewSet.as_view({"get": "user_detail"})),
    path("user-role/assign-roles/", UserRoleViewSet.as_view({"post": "assign_roles"})),
    path("user-role/remove-roles/", UserRoleViewSet.as_view({"post": "remove_roles"})),
    path("me/", MeView.as_view(), name="me"),
    
]


