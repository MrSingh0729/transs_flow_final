from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import hashlib, json

from .models import (
    Employee,
    PasswordChangeRequest,
    AdminPasswordChange,
    UserLoginLog,
    ProfilePictureChange
)

from .forms import (
    EmployeeLoginForm,
    EmployeeProfileForm,
    PasswordChangeRequestForm,
    AdminPasswordResetForm
)

# ================== LOGIN ==================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = EmployeeLoginForm(request.POST)

        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            password = form.cleaned_data["password"]
            remember = form.cleaned_data["remember_me"]

            user = authenticate(request, employee_id=employee_id, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is deactivated.")
                    return redirect('login')

                login(request, user)

                UserLoginLog.objects.create(
                    user=user,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT")
                )

                if remember:
                    request.session.set_expiry(60 * 60 * 24)
                else:
                    request.session.set_expiry(60 * 60)

                # Role based redirect
                if user.role == "Admin":
                    return redirect("admin_dashboard")

                return redirect("dashboard")

            else:
                messages.error(request, "Invalid Employee ID or Password.")

    else:
        form = EmployeeLoginForm()

    return render(request, "accounts/login.html", {"form": form})


# ================== LOGOUT ==================

@login_required
def logout_view(request):

    last_login = UserLoginLog.objects.filter(
        user=request.user, logout_time__isnull=True
    ).last()

    if last_login:
        last_login.logout_time = timezone.now()
        duration = (last_login.logout_time - last_login.login_time).seconds // 60
        last_login.session_duration = duration
        last_login.save()

    logout(request)
    messages.success(request, "You have logged out.")
    return redirect("login")


# ================== USER DASHBOARD ==================

@login_required
def dashboard(request):
    user = request.user

    if user.role == "Admin":
        return redirect("admin_dashboard")

    return render(request, "accounts/dashboard.html", {"user": user})


# ================== PROFILE ==================

@login_required
def user_profile(request):

    user = request.user

    if request.method == "POST":
        form = EmployeeProfileForm(
            request.POST,
            request.FILES,
            instance=user
        )

        if form.is_valid():
            old_picture = user.profile_picture
            new_obj = form.save()

            if old_picture != new_obj.profile_picture:
                ProfilePictureChange.objects.create(
                    user=user,
                    old_picture=old_picture,
                    new_picture=new_obj.profile_picture,
                    changed_by=user
                )

            messages.success(request, "Profile updated successfully.")
            return redirect("user_profile")

    else:
        form = EmployeeProfileForm(instance=user)

    history = PasswordChangeRequest.objects.filter(user=user).order_by("-requested_at")

    return render(request, "accounts/user_profile.html", {
        "form": form,
        "requests": history
    })


# ================== REQUEST PASSWORD CHANGE ==================

@login_required
def request_password_change(request):

    user = request.user

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        reason = request.POST.get("reason")

        if not user.check_password(current_password):
            messages.error(request, "Incorrect current password")
            return redirect("user_profile")

        existing = PasswordChangeRequest.objects.filter(
            user=user,
            status__in=["PENDING", "REVIEWING", "APPROVED"]
        ).exists()

        if existing:
            messages.warning(request, "You already have one active request.")
            return redirect("user_profile")

        request_obj = PasswordChangeRequest.objects.create(
            user=user,
            old_password_hash=hashlib.sha256(current_password.encode()).hexdigest(),
            request_reason=reason,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT")
        )

        send_mail(
            "Password Change Request",
            f"{user.full_name} requested password change.",
            settings.DEFAULT_FROM_EMAIL,
            getattr(settings, "ADMIN_EMAILS", []),
            fail_silently=True
        )

        messages.success(request, "Password change request submitted.")
        return redirect("user_profile")


# ================== USER RESET PASSWORD (AFTER ADMIN APPROVAL) ==================

def reset_password(request, token):

    password_request = get_object_or_404(
        PasswordChangeRequest,
        reset_token=token,
        status="APPROVED",
        reset_token_expires__gte=timezone.now()
    )

    if request.method == "POST":

        form = AdminPasswordResetForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user = password_request.user

            old_hash = user.password

            user.set_password(new_password)
            user.save()

            password_request.status = "COMPLETED"
            password_request.save()

            AdminPasswordChange.objects.create(
                admin=request.user if request.user.is_authenticated else None,
                target_user=user,
                old_password_hash=old_hash,
                new_password_hash=user.password,
                reason="Approved password reset"
            )

            messages.success(request, "Password reset successfully.")
            return redirect("login")

    else:
        form = AdminPasswordResetForm()

    return render(request, "accounts/reset_password.html", {
        "form": form,
        "user": password_request.user
    })


# ================== VIEW USER REQUESTS ==================

@login_required
def user_password_requests(request):

    requests = PasswordChangeRequest.objects.filter(user=request.user).order_by('-requested_at')

    return render(request, "accounts/user_password_requests.html", {
        "requests": requests
    })


# ================== AJAX: CHECK PASSWORD REQUEST STATUS ==================

@login_required
def check_status(request):

    latest = PasswordChangeRequest.objects.filter(user=request.user).last()

    if not latest:
        return JsonResponse({"status": "none"})

    return JsonResponse({
        "status": latest.status,
        "reason": latest.get_status_display()
    })


# ================== AJAX: GET PROFILE DATA ==================

@login_required
def get_profile_data(request):

    user = request.user

    data = {
        "employee_id": user.employee_id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone_number,
        "role": user.role,
        "department": user.department,
        "factory_code": user.factory_code,
        "factory_name": user.factory_name,
        "profile_picture": user.get_profile_picture_url()
    }

    return JsonResponse({"data": data})


# ================== AJAX: UPDATE PROFILE ==================

@csrf_exempt
@login_required
@require_POST
def update_profile(request):

    user = request.user
    data = json.loads(request.body)

    editable = [
        'full_name', 'email', 'phone_number',
        'department', 'factory_code', 'factory_name',
        'country_code', 'country_name'
    ]

    for field in editable:
        if field in data:
            setattr(user, field, data[field])

    user.save()

    return JsonResponse({"success": True})


# ================== VALIDATE EMPLOYEE SEARCH ==================

@login_required
def validate_employee(request):

    q = request.GET.get("q", "")

    employees = Employee.objects.filter(
        Q(employee_id__icontains=q) |
        Q(full_name__icontains=q)
    )[:10]

    data = [
        {"id": e.id, "text": f"{e.employee_id} - {e.full_name}"}
        for e in employees
    ]

    return JsonResponse({"results": data})
