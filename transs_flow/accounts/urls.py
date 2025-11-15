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
]
