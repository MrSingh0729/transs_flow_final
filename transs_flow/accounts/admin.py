from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    model = Employee
    ordering = ("employee_id",)

    list_display = (
        "employee_id",
        "full_name",
        "role",
        "department",
        "factory_code",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_filter = (
        "role",
        "department",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "employee_id",
        "full_name",
        "email",
    )

    # ❌ REMOVED groups & user_permissions (you don't have them)
    fieldsets = (
        (None, {"fields": ("employee_id", "password")}),
        ("Personal Info", {
            "fields": (
                "full_name",
                "email",
                "phone_number",
                "role",
                "department",
                "factory_code",
                "factory_name",
                "country_code",
                "country_name",
                "profile_picture",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
            )
        }),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "employee_id",
                "full_name",
                "email",
                "phone_number",
                "role",
                "department",
                "factory_code",
                "factory_name",
                "country_code",
                "country_name",
                "password1",
                "password2",
                "is_staff",
                "is_superuser",
                "is_active",
            ),
        }),
    )
