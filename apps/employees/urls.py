from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentViewSet,
    PositionViewSet,
    GradeViewSet,
    EmploymentStatusViewSet,
    EmployeeViewSet,
)


router = DefaultRouter()

router.register(r"employee", EmployeeViewSet, basename="employee")
router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"positions", PositionViewSet, basename="positions")
router.register(r"grades", GradeViewSet, basename="grades")
router.register(r"employment-statuses", EmploymentStatusViewSet, basename="employment-statuses")

urlpatterns = [

    # router endpoints
    path("", include(router.urls)),

]
