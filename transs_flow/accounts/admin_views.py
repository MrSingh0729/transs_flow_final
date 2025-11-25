from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
import logging
import uuid

from .models import (
    Employee,
    PasswordChangeRequest,
    AdminPasswordChange,
    ProfilePictureChange,
    UserLoginLog
)

from .forms import PasswordChangeActionForm, AdminPasswordResetForm

logger = logging.getLogger(__name__)


# ========================= ADMIN DASHBOARD =========================

@login_required
@staff_member_required
def admin_dashboard(request):

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()

    pending_requests = PasswordChangeRequest.objects.filter(status='PENDING').count()
    approved_requests = PasswordChangeRequest.objects.filter(status='APPROVED').count()
    rejected_requests = PasswordChangeRequest.objects.filter(status='REJECTED').count()

    recent_password_changes = AdminPasswordChange.objects.select_related('target_user', 'admin').order_by('-changed_at')[:10]
    recent_profile_changes = ProfilePictureChange.objects.select_related('user', 'changed_by').order_by('-changed_at')[:5]
    recent_logins = UserLoginLog.objects.select_related('user').order_by('-login_time')[:10]

    roles = ['IPQC', 'QA', 'PQE', 'Admin', 'Supervisor', 'Manager', 'Engineer', 'Operator']
    role_stats = {role: Employee.objects.filter(role=role, is_active=True).count() for role in roles}

    return render(request, 'accounts/admin/admin_dashboard.html', {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'recent_password_changes': recent_password_changes,
        'recent_profile_changes': recent_profile_changes,
        'recent_logins': recent_logins,
        'role_stats': role_stats,
    })


# ========================= USER LIST =========================

@login_required
@staff_member_required
def admin_user_list(request):

    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')

    employees = Employee.objects.all()

    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if status_filter == 'active':
        employees = employees.filter(is_active=True)
    elif status_filter == 'inactive':
        employees = employees.filter(is_active=False)

    if role_filter:
        employees = employees.filter(role=role_filter)

    paginator = Paginator(employees.order_by('-created_at'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/admin/admin_user_list.html', {
        'employees': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'is_paginated': page_obj.has_other_pages(),
    })


# ========================= USER DETAIL =========================

@staff_member_required
def admin_user_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    password_requests = PasswordChangeRequest.objects.filter(user=employee).order_by('-requested_at')
    profile_changes = ProfilePictureChange.objects.filter(user=employee).order_by('-changed_at')
    login_logs = UserLoginLog.objects.filter(user=employee).order_by('-login_time')[:10]

    return render(request, 'accounts/admin/admin_user_detail.html', {
        'employee': employee,
        'password_requests': password_requests,
        'profile_changes': profile_changes,
        'login_logs': login_logs,
    })


# ========================= TOGGLE USER STATUS =========================

@staff_member_required
@require_POST
def admin_toggle_user_status(request, pk):

    if not request.headers.get('x-requested-with'):
        return HttpResponseBadRequest("Invalid request")

    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save()

    AdminPasswordChange.objects.create(
        admin=request.user,
        target_user=employee,
        old_password_hash='',
        new_password_hash='',
        reason=f"Admin toggled user {'active' if employee.is_active else 'inactive'}",
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
    )

    return JsonResponse({'success': True, 'is_active': employee.is_active})


# ========================= DIRECT PASSWORD RESET =========================

@staff_member_required
def admin_reset_user_password(request, pk):

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():

            new_password = form.cleaned_data['new_password']
            old_hash = employee.password

            employee.set_password(new_password)
            employee.save()

            AdminPasswordChange.objects.create(
                admin=request.user,
                target_user=employee,
                old_password_hash=old_hash,
                new_password_hash=employee.password,
                reason="Admin manually reset user password",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )

            messages.success(request, f"Password reset for {employee.full_name}.")
            return redirect('admin_user_list')

    else:
        form = AdminPasswordResetForm()

    return render(request, 'accounts/admin/admin_reset_password.html', {
        'employee': employee,
        'form': form
    })


# ========================= PASSWORD REQUEST LIST =========================

@login_required
@staff_member_required
def password_change_requests(request):

    requests = PasswordChangeRequest.objects.select_related('user').order_by('-requested_at')

    paginator = Paginator(requests, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/admin/password_change_requests.html', {
        'requests': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })


# ========================= PROCESS REQUEST =========================

@login_required
@staff_member_required
def admin_process_single_request(request, pk):

    password_request = get_object_or_404(PasswordChangeRequest, pk=pk)

    if password_request.is_expired():
        messages.error(request, "Request expired.")
        return redirect('admin_password_requests')

    if request.method == "POST":
        form = PasswordChangeActionForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data['action']
            password_request.status = action.upper()
            password_request.processed_at = timezone.now()
            password_request.save()

            if action == 'approve':

                token = uuid.uuid4()
                password_request.reset_token = token
                password_request.reset_token_expires = timezone.now() + timezone.timedelta(days=1)
                password_request.save()

                reset_link = request.build_absolute_uri(
                    reverse('admin_reset_password', kwargs={'token': token})
                )

                send_mail(
                    'Password Reset Approved',
                    f"Click to reset password:\n{reset_link}",
                    settings.DEFAULT_FROM_EMAIL,
                    [password_request.user.email],
                    fail_silently=True
                )

            messages.success(request, f"Request {action.upper()} successful.")
            return redirect('admin_password_requests')

    else:
        form = PasswordChangeActionForm()

    return render(request, 'accounts/admin/admin_process_single_request.html', {
        'password_request': password_request,
        'form': form
    })


# ========================= RESET PASSWORD BY TOKEN =========================

@login_required
@staff_member_required
def admin_reset_password(request, token):

    try:
        password_request = PasswordChangeRequest.objects.get(
            reset_token=token,
            status='APPROVED',
            reset_token_expires__gte=timezone.now()
        )
    except PasswordChangeRequest.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == "POST":
        form = AdminPasswordResetForm(request.POST)

        if form.is_valid():
            user = password_request.user
            old_hash = user.password

            user.set_password(form.cleaned_data['new_password'])
            user.save()

            password_request.status = 'COMPLETED'
            password_request.save()

            AdminPasswordChange.objects.create(
                admin=request.user,
                target_user=user,
                old_password_hash=old_hash,
                new_password_hash=user.password,
                reason="Reset via approved request",
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )

            messages.success(request, "Password successfully reset.")
            return redirect('admin_password_requests')

    else:
        form = AdminPasswordResetForm()

    return render(request, 'accounts/admin/admin_reset_password.html', {
        'form': form,
        'password_request': password_request,
        'employee': password_request.user
    })


# ========================= PASSWORD CHANGE LOGS =========================

@login_required
@staff_member_required
def admin_password_change_logs(request):

    logs = AdminPasswordChange.objects.select_related(
        'admin', 'target_user'
    ).order_by('-changed_at')

    paginator = Paginator(logs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/admin/admin_password_change_logs.html', {
        'logs': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })
