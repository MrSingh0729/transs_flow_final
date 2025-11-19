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
from django.urls import reverse



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



FEISHU_APP_ID = settings.IFEISHU_APP_ID
FEISHU_APP_SECRET = settings.IFEISHU_APP_SECRET

def feishu_oauth_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state", "/")

    # Exchange code for token
    token_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": FEISHU_APP_ID,
        "client_secret": FEISHU_APP_SECRET
    }

    resp = requests.post(token_url, json=data).json()

    if resp.get("code") != 0:
        return HttpResponse("OAuth Error: " + str(resp))

    access_token = resp["data"]["access_token"]
    refresh_token = resp["data"]["refresh_token"]
    expires_in = resp["data"]["expires_in"]  # 7200 sec = 2 hours

    # Store in Django session
    request.session["feishu_access_token"] = access_token
    request.session["feishu_refresh_token"] = refresh_token
    request.session["feishu_expires_at"] = time.time() + expires_in

    return redirect(state)


def get_valid_feishu_token(request):
    import time

    access = request.session.get("feishu_access_token")
    refresh = request.session.get("feishu_refresh_token")
    expires_at = request.session.get("feishu_expires_at")

    # 1. No token stored → needs OAuth
    if not access or not refresh:
        return None

    # 2. Token is still valid
    if time.time() < expires_at - 60:
        return access

    # 3. Token expired → refresh
    refresh_url = "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": FEISHU_APP_ID,
        "client_secret": FEISHU_APP_SECRET
    }

    resp = requests.post(refresh_url, json=data).json()

    if resp.get("code") != 0:
        # refresh failed → force OAuth again
        return None

    # update session
    request.session["feishu_access_token"] = resp["data"]["access_token"]
    request.session["feishu_refresh_token"] = resp["data"]["refresh_token"]
    request.session["feishu_expires_at"] = time.time() + resp["data"]["expires_in"]

    return resp["data"]["access_token"]


def get_shareable_link(request):
    import json
    data = json.loads(request.body)
    scanned_url = data.get("scanned_url")

    token = get_valid_feishu_token(request)

    if not token:
        # Need OAuth
        return JsonResponse({
            "need_oauth": True,
            "oauth_url": f"https://open.feishu.cn/open-apis/authen/v1/authorize?client_id={FEISHU_APP_ID}&redirect_uri={REDIRECT_URL}&response_type=code"
        })

    # otherwise continue normally
    headers = {"Authorization": f"Bearer {token}"}
    # call feishu record API here...

    return JsonResponse({
        "ok": True,
        "share_url": GENERATED_SHARE_URL
    })