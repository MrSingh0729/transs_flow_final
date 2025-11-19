from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import EmployeeForm
from .models import Employee
from django.http import HttpResponseForbidden
from django.conf import settings
import requests
import time
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


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



