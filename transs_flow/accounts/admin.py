from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    model = Employee

    list_display = (
        "employee_id",
        "full_name",
        "role",
        "department",
        "factory_name",
        "is_staff",
        "is_active",
    )

    search_fields = ("employee_id", "full_name", "department", "factory_name")
    list_filter = ("department", "factory_name", "is_staff", "is_active")
    ordering = ("employee_id",)

    fieldsets = (
        ("Login Info", {
            "fields": ("employee_id", "password")
        }),
        ("Personal Info", {
            "fields": (
                "full_name",
                "role",
                "department",
                "factory_code",
                "factory_name",
                "country_code",
                "country_name"
            )
        }),
        ("Permissions", {
            "fields": ("is_staff", "is_superuser", "is_active")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "employee_id",
                "full_name",
                "password1",
                "password2",
                "role",
                "department",
                "factory_code",
                "factory_name",
                "country_code",
                "country_name",
                "is_staff",
                "is_superuser"
            ),
        }),
    )
