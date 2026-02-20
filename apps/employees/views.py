from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status

from apps.accounts.models import User
from apps.accounts.permissions import HasPermission

from .models import (
    Department,
    Position,
    Grade,
    EmploymentStatus,
    Employee,
)

from .serializers import (
    DepartmentSerializer,
    PositionSerializer,
    GradeSerializer,
    EmploymentStatusSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
)


# ============================================================
# MASTER CRUD
# ============================================================
class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer


class PositionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Position.objects.select_related("department").all().order_by("name")
    serializer_class = PositionSerializer


class GradeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Grade.objects.all().order_by("level")
    serializer_class = GradeSerializer


class EmploymentStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmploymentStatus.objects.all().order_by("name")
    serializer_class = EmploymentStatusSerializer


# ============================================================
# EMPLOYEE CRUD
# ============================================================
class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related(
        "user",
        "department",
        "position",
        "grade",
        "employment_status",
        "manager",
        "manager__user",
    ).all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        if self.action == "retrieve":
            return EmployeeDetailSerializer
        if self.action == "create":
            return EmployeeCreateSerializer
        if self.action in ["update", "partial_update"]:
            return EmployeeUpdateSerializer
        return EmployeeDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        Override supaya response setelah create itu detail employee.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()

        return Response(
            EmployeeDetailSerializer(employee).data,
            status=status.HTTP_201_CREATED,
        )
