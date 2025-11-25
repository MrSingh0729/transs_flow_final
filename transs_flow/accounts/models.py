from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password
import uuid
import os

# ========================= USER MANAGER =========================

class CustomUserManager(BaseUserManager):
    def create_user(self, employee_id, full_name, email, password=None, **extra_fields):
        if not employee_id:
            raise ValueError("Employee ID is required")

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            employee_id=employee_id,
            full_name=full_name,
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, full_name, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Admin')
        return self.create_user(employee_id, full_name, email, password, **extra_fields)

# ========================= EMPLOYEE MODEL =========================

class Employee(AbstractBaseUser, PermissionsMixin):

    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=50,
        choices=[
            ('IPQC', 'IPQC Inspector'),
            ('QA', 'Quality Assurance'),
            ('PQE', 'Process Quality Engineer'),
            ('Admin', 'Administrator'),
            ('Supervisor', 'Supervisor'),
            ('Engineer', 'Engineer'),
            ('Operator', 'Operator'),
            ('Manager', 'Manager'),
        ],
        default='IPQC'
    )

    department = models.CharField(max_length=100, blank=True, null=True)
    factory_code = models.CharField(max_length=50, blank=True, null=True)
    factory_name = models.CharField(max_length=100, blank=True, null=True)

    country_code = models.CharField(max_length=10, blank=True, null=True)
    country_name = models.CharField(max_length=50, blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to='employee_profile_pics/',
        blank=True,
        null=True,
        default='employee_profile_pics/default.jpg'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['full_name', 'email']

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    def clean(self):
        if Employee.objects.filter(email__iexact=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("Email already exists.")

    def get_full_name(self):
        return self.full_name

    def check_password(self, raw_password):
        return super().check_password(raw_password)

    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/employee_profile_pics/default.jpg'

# ========================= PASSWORD CHANGE REQUEST =========================

class PasswordChangeRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_requests'
    )

    old_password_hash = models.CharField(max_length=255, editable=False)
    request_reason = models.TextField()

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWING', 'Reviewing'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    admin_notes = models.TextField(blank=True, null=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    reset_token = models.UUIDField(default=uuid.uuid4, unique=True)
    reset_token_expires = models.DateTimeField(null=True, blank=True)

    new_password_hash = models.CharField(max_length=255, blank=True, null=True)

    user_notified = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Request by {self.user.employee_id}"

    def is_expired(self):
        if self.reset_token_expires:
            return timezone.now() > self.reset_token_expires
        return False

    def can_be_processed(self):
        return self.status in ['PENDING', 'REVIEWING'] and not self.is_expired()

# ========================= ADMIN PASSWORD CHANGE LOG =========================

class AdminPasswordChange(models.Model):

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_changes_done'
    )

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_changes_received'
    )

    old_password_hash = models.CharField(max_length=255)
    new_password_hash = models.CharField(max_length=255)

    reason = models.CharField(max_length=500)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.employee_id} → {self.target_user.employee_id}"

# ========================= PROFILE PICTURE LOG =========================

class ProfilePictureChange(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_picture_changes'
    )

    old_picture = models.ImageField(upload_to='profile_history_pics/', blank=True, null=True)
    new_picture = models.ImageField(upload_to='profile_history_pics/', blank=True, null=True)

    changed_at = models.DateTimeField(auto_now_add=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='profile_picture_changes_made'
    )

    def __str__(self):
        return f"Profile picture update for {self.user.employee_id}"

# ========================= LOGIN LOG =========================

class UserLoginLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_logs'
    )

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    session_duration = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.employee_id} login at {self.login_time}"

# ========================= STORAGE FOLDERS =========================

if not os.path.exists('employee_profile_pics'):
    os.makedirs('employee_profile_pics', exist_ok=True)

if not os.path.exists('profile_history_pics'):
    os.makedirs('profile_history_pics', exist_ok=True)
