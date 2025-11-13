# accounts/serializers.py
from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'full_name',
            'role',
            'department',
            'factory_code',
            'factory_name',
            'country_code',
            'country_name',
        ]
