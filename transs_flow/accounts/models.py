from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class EmployeeManager(BaseUserManager):
    def create_user(self, employee_id, full_name, password=None, **extra_fields):
        if not employee_id:
            raise ValueError("Employee ID is required")
        user = self.model(employee_id=employee_id, full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, employee_id, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(employee_id, full_name, password, **extra_fields)


class Employee(AbstractBaseUser, PermissionsMixin):
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    factory_code = models.CharField(max_length=20)
    factory_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    country_name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmployeeManager()

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"
