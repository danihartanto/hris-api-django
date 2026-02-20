from django.shortcuts import render

# Create your views here.
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.accounts.permissions import HasPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from .serializers import MeSerializer, CreateEmployeeUserSerializer, UserMiniSerializer
from apps.accounts.models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class EmployeeListAPIView(APIView):
    permission_classes = [HasPermission]
    required_permissions = ["employees.view"]

    def get(self, request):
        return Response({"message": "ok"})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)

class EmployeeUserViewSet(viewsets.ModelViewSet):
    """
    CRUD untuk user employee (akun login).
    """
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().order_by("full_name")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CreateEmployeeUserSerializer
        return UserMiniSerializer
