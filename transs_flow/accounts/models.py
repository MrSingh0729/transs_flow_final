from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone


def employee_profile_upload_to(instance, filename):
    """
    Save profile pictures as profile_<employee_id>.<ext> inside profile_pictures/
    """
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.employee_id}.{ext}"
    return f"profile_pictures/{filename}"


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

    # 🔹 Profile fields
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to=employee_profile_upload_to,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = EmployeeManager()

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = ["full_name"]

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"


class PasswordChangeRequest(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_change_requests",
    )
    employee_id = models.CharField(max_length=20)
    full_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_password_requests",
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Password request for {self.employee_id} - {self.full_name} ({self.status})"
