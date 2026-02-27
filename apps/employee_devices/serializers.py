from rest_framework import serializers
from .models import EmployeeDevice


class EmployeeDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDevice
        fields = "__all__"
        read_only_fields = (
            "employee",
            "registered_at",
            "last_used_at",
        )
