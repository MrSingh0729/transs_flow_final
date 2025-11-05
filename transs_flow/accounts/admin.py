from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee

class EmployeeAdmin(UserAdmin):
    model = Employee
    # Replace 'username' with your USERNAME_FIELD
    list_display = ("employee_id", "full_name", "role", "department", "factory_code", "is_staff", "is_superuser")
    
    # Set fieldsets for admin create/edit page
    fieldsets = (
        (None, {"fields": ("employee_id", "password")}),
        ("Personal Info", {"fields": ("full_name", "role", "department", "factory_code", "factory_name", "country_code", "country_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("employee_id", "full_name", "role", "department", "factory_code", "factory_name", "country_code", "country_name", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    search_fields = ("employee_id", "full_name")
    ordering = ("employee_id",)  # <-- important fix
    filter_horizontal = ("groups", "user_permissions")

admin.site.register(Employee, EmployeeAdmin)
