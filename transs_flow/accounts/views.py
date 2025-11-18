from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import EmployeeForm
from .models import Employee
from django.http import HttpResponseForbidden
<<<<<<< HEAD
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def receive_platform_token(request):
    try:
        data = json.loads(request.body)
        open_id = data.get('open_id')
        app_access_token = data.get('app_access_token')
        tenant_key = data.get('tenant_key')
        platform = data.get('platform')


        request.session[f'{platform}_access_token'] = app_access_token
        request.session[f'{platform}_open_id'] = open_id
        request.session[f'{platform}_tenant_key'] = tenant_key

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
=======
>>>>>>> 04477622334d2723e9772c0505f780bc04478920


def login_view(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        user = authenticate(request, employee_id=employee_id, password=password)

        if user is not None:
            login(request, user)


            if user.is_superuser or getattr(user, 'role', '').lower() == "admin" or getattr(user, 'role', '').upper() == "PQE":
                return redirect('dashboard')
            elif getattr(user, 'role', '').upper() == "IPQC":
                return redirect('ipqc_home')
            else:

                return redirect('dashboard')

        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})

    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
<<<<<<< HEAD

=======
    # Check if user is superuser or has role 'admin'
    
>>>>>>> 04477622334d2723e9772c0505f780bc04478920
    if not (request.user.is_superuser or getattr(request.user, 'role', '').lower() == 'admin' or getattr(request.user, 'role', '').upper() == 'PQE'):
        return HttpResponseForbidden("You are not authorized to view this page.")

    total_employees = Employee.objects.count()

    context = {
        "total_employees": total_employees,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "accounts/employee_list.html", {"employees": employees})

@login_required
def employee_create(request):
<<<<<<< HEAD
    title = "Create"

=======
    title = "Create"  # Add this so template can use {{ title }}
    
>>>>>>> 04477622334d2723e9772c0505f780bc04478920
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
            "title": title
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

        employee.delete()
        return redirect('employee_list')
<<<<<<< HEAD


=======
    
    # Render confirmation page
>>>>>>> 04477622334d2723e9772c0505f780bc04478920
    return render(request, "accounts/employee_delete.html", {"employee": employee})
