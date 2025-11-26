from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
import csv
from datetime import timedelta
from django.db.models import Avg
from django.db.models import F, ExpressionWrapper, DurationField

from .forms import (
    EmployeeForm,
    ProfileForm,
    ForgotPasswordRequestForm,
    AdminPasswordChangeForm,
)
from .models import Employee, PasswordChangeRequest

# ----------------- Auth -----------------
def login_view(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        user = authenticate(request, employee_id=employee_id, password=password)

        if user is not None:
            login(request, user)

            # 🔹 Role-based redirection
            if user.is_superuser or getattr(user, 'role', '').lower() == "admin" or getattr(user, 'role', '').upper() == "PQE":
                return redirect('dashboard')
            elif getattr(user, 'role', '').upper() == "IPQC":
                return redirect('ipqc_home')
            else:
                # Default redirect (if no role matches)
                return redirect('dashboard')

        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

# ----------------- Dashboard -----------------
@login_required
def dashboard(request):
    # Check if user is superuser or has role 'admin'
    
    if not (request.user.is_superuser or getattr(request.user, 'role', '').lower() == 'admin' or getattr(request.user, 'role', '').upper() == 'PQE'):
        return HttpResponseForbidden("You are not authorized to view this page.")

    total_employees = Employee.objects.count()

    context = {
        "total_employees": total_employees,
    }
    return render(request, "accounts/dashboard.html", context)

# ----------------- Employee CRUD -----------------
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "accounts/employee_list.html", {"employees": employees})

@login_required
def employee_create(request):
    title = "Create"  # Add this so template can use {{ title }}
    
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Employee.objects.create_user(
                employee_id=data['employee_id'],
                full_name=data['full_name'],
                password=data['password'],
                role=data['role'],
                department=data['department'],
                factory_code=data['factory_code'],
                factory_name=data['factory_name'],
                country_code=data['country_code'],
                country_name=data['country_name']
            )
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    
    return render(
        request,
        "accounts/employee_create.html",
        {
            "form": form,
            "title": title  # Pass title to template
        }
    )

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            emp = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                emp.set_password(password)
            emp.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "accounts/employee_edit.html", {"form": form, "employee": employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == "POST":
        # User confirmed deletion
        employee.delete()
        return redirect('employee_list')
    
    # Render confirmation page
    return render(request, "accounts/employee_delete.html", {"employee": employee})



@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})


# ----------------- Password Change Requests -----------------
@login_required
def raise_password_change_request(request):
    """
    From logged-in user (Change Password in profile dropdown).
    Just creates a request; does NOT change password itself.
    """
    existing_pending = PasswordChangeRequest.objects.filter(
        user=request.user, status=PasswordChangeRequest.STATUS_PENDING
    ).first()

    if existing_pending:
        messages.info(request, "You already have a pending password change request.")
        return redirect("profile")

    PasswordChangeRequest.objects.create(
        user=request.user,
        employee_id=request.user.employee_id,
        full_name=request.user.full_name,
    )
    messages.success(
        request,
        "Password change request submitted. Admin will update your password."
    )
    return redirect("profile")


def forgot_password_request(request):
    """
    From login page "Forgot Password?" (not logged in).
    User enters employee_id; we create a request if employee exists.
    """
    if request.method == "POST":
        form = ForgotPasswordRequestForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            try:
                user = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                messages.error(request, "No user found with that Employee ID.")
            else:
                existing_pending = PasswordChangeRequest.objects.filter(
                    user=user, status=PasswordChangeRequest.STATUS_PENDING
                ).first()
                if existing_pending:
                    messages.info(
                        request,
                        "A pending password change request already exists for this user."
                    )
                else:
                    PasswordChangeRequest.objects.create(
                        user=user,
                        employee_id=user.employee_id,
                        full_name=user.full_name,
                    )
                    messages.success(
                        request,
                        "Password change request submitted. Admin will contact you."
                    )
            return redirect("forgot_password")
    else:
        form = ForgotPasswordRequestForm()

    return render(request, "accounts/forgot_password.html", {"form": form})


@login_required
def password_request_list(request):
    """
    Admin/superuser list of all password change requests + analytics.
    """
    if not (request.user.is_superuser or getattr(request.user, "role", "").lower() == "admin"):
        return HttpResponseForbidden("You are not authorized to view this page.")

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # -------------------------------
    # All Requests (Table)
    # -------------------------------
    requests_qs = PasswordChangeRequest.objects.all().order_by("-created_at")

    # -------------------------------
    # Pending Requests Today
    # -------------------------------
    pending_today = PasswordChangeRequest.objects.filter(
        status="pending",
        created_at__date=today
    ).count()

    pending_yesterday = PasswordChangeRequest.objects.filter(
        status="pending",
        created_at__date=yesterday
    ).count()

    pending_change = (
        ((pending_today - pending_yesterday) / pending_yesterday) * 100
        if pending_yesterday
        else pending_today * 100
    )

    # -------------------------------
    # Processed Requests Today
    # -------------------------------
    processed_today = PasswordChangeRequest.objects.filter(
        status="approved",
        processed_at__date=today    # ✅ FIXED HERE
    ).count()

    processed_yesterday = PasswordChangeRequest.objects.filter(
        status="approved",
        processed_at__date=yesterday  # ✅ FIXED HERE
    ).count()

    processed_change = (
        ((processed_today - processed_yesterday) / processed_yesterday) * 100
        if processed_yesterday
        else processed_today * 100
    )

    # -------------------------------
    # Total Requests
    # -------------------------------
    total_requests = PasswordChangeRequest.objects.count()

    # -------------------------------
    # Average Processing Time
    # processed_time = processed_at - created_at
    # -------------------------------
    avg_processing = PasswordChangeRequest.objects.filter(
        status="approved",
        processed_at__isnull=False
    ).annotate(
        processing_time=ExpressionWrapper(
            F("processed_at") - F("created_at"),
            output_field=DurationField()
        )
    ).aggregate(avg=Avg("processing_time"))["avg"]

    if avg_processing:
        avg_seconds = avg_processing.total_seconds()
        avg_minutes = round(avg_seconds / 60, 1)
        avg_processing_time = f"{avg_minutes} mins"
    else:
        avg_processing_time = "N/A"

    # -------------------------------
    # Context
    # -------------------------------
    context = {
        "requests": requests_qs,

        "pending_count": pending_today,
        "pending_change": round(pending_change, 2),

        "processed_count": processed_today,
        "processed_change": round(processed_change, 2),

        "total_requests": total_requests,
        "avg_processing_time": avg_processing_time,
    }

    return render(request, "accounts/password_request_list.html", context)


@login_required
def admin_change_user_password(request, pk):
    """
    Admin page to set a new password for the user of a specific request.
    """
    if not (request.user.is_superuser or getattr(request.user, "role", "").lower() == "admin"):
        return HttpResponseForbidden("You are not authorized to view this page.")

    pwd_request = get_object_or_404(PasswordChangeRequest, pk=pk)
    user = pwd_request.user

    if request.method == "POST":
        form = AdminPasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password1"]
            user.set_password(new_password)
            user.save()

            pwd_request.status = PasswordChangeRequest.STATUS_COMPLETED
            pwd_request.processed_by = request.user
            pwd_request.processed_at = timezone.now()
            pwd_request.save()

            messages.success(
                request,
                f"Password updated for {user.employee_id} - {user.full_name}."
            )
            return redirect("password_request_list")
    else:
        form = AdminPasswordChangeForm()

    return render(
        request,
        "accounts/admin_change_password.html",
        {"form": form, "pwd_request": pwd_request, "user_obj": user},
    )
    
    
def export_password_requests(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="password_requests.csv"'

    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Email', 'Status', 'Created At'])

    requests = PasswordChangeRequest.objects.all().order_by('-created_at')

    for req in requests:
        writer.writerow([
            req.user.employee_id,
            req.user.email,
            req.status,
            req.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response