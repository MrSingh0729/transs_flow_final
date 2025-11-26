from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),

    # Superuser Employee management
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/edit/<int:pk>/", views.employee_edit, name="employee_edit"),
    path("employees/delete/<int:pk>/", views.employee_delete, name="employee_delete"),

    # Profile + password request
    path("profile/", views.profile_view, name="profile"),
    path("password/request/", views.raise_password_change_request, name="password_change_request"),
    path("password/forgot/", views.forgot_password_request, name="forgot_password"),
    path("password/requests/", views.password_request_list, name="password_request_list"),
    path(
        "password/requests/<int:pk>/change/",
        views.admin_change_user_password,
        name="admin_change_user_password",
    ),
    path('password-requests/export/', views.export_password_requests, name='export_password_requests'),
]
