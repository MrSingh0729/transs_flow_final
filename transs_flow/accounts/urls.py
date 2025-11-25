from django.urls import path
from . import views as account_views
from . import admin_views


urlpatterns = [

    # ====== CUSTOM MANAGEMENT PANEL ======
    path('management/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('management/users/', admin_views.admin_user_list, name='admin_user_list'),
    path('management/password-requests/', admin_views.password_change_requests, name='admin_password_requests'),
    path('management/reset-password/<uuid:token>/', admin_views.admin_reset_password, name='admin_reset_password'),
    path('management/user-reset/<int:pk>/', admin_views.admin_reset_user_password, name='admin_reset_user_password'),

    # ====== USER SIDE ======
    path('dashboard/', account_views.dashboard, name='dashboard'),
    path('profile/', account_views.user_profile, name='user_profile'),
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),

    # ====== PASSWORD MANAGEMENT ======
    path('request-password-change/', account_views.request_password_change, name='request_password_change'),
    # path('submit-password-request/', account_views.submit_password_request, name='submit_password_request'),
    path('reset-password/<uuid:token>/', account_views.reset_password, name='reset_password'),
    path('password-change-requests/', account_views.user_password_requests, name='user_password_requests'),
    # path('password-change-popup/', account_views.change_password_popup, name='change_password_popup'),

    # ====== SERVICES ======
    # path('profile-picture-change-history/', account_views.profile_picture_change_history, name='profile_picture_change_history'),
    # path('profile-pic-input/', account_views.profile_pic_input, name='profile_pic_input'),
    path('validate-employee/', account_views.validate_employee, name='validate_employee'),
    path('check-status/', account_views.check_status, name='check_status'),
    path('get-profile-data/', account_views.get_profile_data, name='get_profile_data'),
    path('update-profile/', account_views.update_profile, name='update_profile'),
]
