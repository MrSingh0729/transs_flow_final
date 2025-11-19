from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import EmployeeForm
from .models import Employee
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
import requests
import json
import re
from urllib.parse import urlencode

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



# ---------- Helpers ----------
FEISHU_AUTH_URL = "https://open.feishu.cn/open-apis/authen/v1/index"  # OAuth entry
# Token exchange + user token docs referenced in Feishu docs
FEISHU_USER_TOKEN_EXCHANGE = "https://open.feishu.cn/open-apis/authen/v1/access_token"
# Bitable/record share endpoint (example structure; fill with IDs you parse or know)
# POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}/share

def build_oauth_redirect(app_id: str, redirect_uri: str, state: str=None):
    params = {
        "app_id": app_id,
        "redirect_uri": redirect_uri
    }
    if state:
        params["state"] = state
    return f"{FEISHU_AUTH_URL}?{urlencode(params)}"


# ---------- Step A: start OAuth flow ----------
def feishu_login(request):
    # You can pass along a `next` param in state if you want
    state = request.GET.get("next", "/")
    oauth_url = build_oauth_redirect(settings.IFEISHU_APP_ID, settings.IFEISHU_REDIRECT_URI, state=state)
    return redirect(oauth_url)


# ---------- Step B: OAuth callback - exchange code for user_access_token ----------
@csrf_exempt
def feishu_callback(request):
    """
    Feishu will redirect to this endpoint with ?code=...&state=...
    Exchange code for user_access_token and store in session.
    """
    code = request.GET.get("code")
    state = request.GET.get("state", "/")
    if not code:
        return HttpResponseBadRequest("Missing code")

    # Exchange code for user_access_token (server-side)
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "app_id": settings.IFEISHU_APP_ID,
        "app_secret": settings.IFEISHU_APP_SECRET,
        "redirect_uri": settings.IFEISHU_REDIRECT_URI
    }

    resp = requests.post(FEISHU_USER_TOKEN_EXCHANGE, json=payload, timeout=10)
    if resp.status_code != 200:
        return HttpResponseBadRequest("Failed to exchange code: " + resp.text)

    data = resp.json()
    # The exact keys depend on Feishu version; typical fields: tenant_access_token / user_access_token / refresh_token
    # Save them in session (or DB) — keep secure
    request.session['feishu_token_response'] = data
    request.session.modified = True

    # Redirect to original state (client should detect session token present)
    return redirect(state or '/')


# ---------- Step C: create shareable link for given scanned record URL ----------
@csrf_exempt
def get_shareable_link(request):
    """
    Expects JSON POST:
    { "scanned_url": "https://transsioner.feishu.cn/record/FhzArCp..." }
    Returns JSON: { "ok": true, "share_url": "..."} or { "need_oauth": true, "oauth_url": "..." }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        body = json.loads(request.body.decode())
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    scanned_url = body.get("scanned_url")
    if not scanned_url:
        return JsonResponse({"error": "missing scanned_url"}, status=400)

    # If no feishu token in session, tell client to initiate OAuth
    token_resp = request.session.get('feishu_token_response')
    if not token_resp:
        oauth_url = build_oauth_redirect(settings.IFEISHU_APP_ID, settings.IFEISHU_REDIRECT_URI)
        return JsonResponse({"need_oauth": True, "oauth_url": oauth_url})

    # Extract user_access_token (or tenant token) depending on your app type
    # NOTE: keys may vary. Inspect token_resp for correct fields.
    user_access_token = token_resp.get("data", {}).get("user_access_token") or token_resp.get("user_access_token")
    if not user_access_token:
        # fallback: tenant token (for server-server) — but shareable links usually need user-level permission
        tenant_token = token_resp.get("data", {}).get("tenant_access_token") or token_resp.get("tenant_access_token")
        if not tenant_token:
            return JsonResponse({"error": "no access token found in session"}, status=400)
        auth_token = tenant_token
    else:
        auth_token = user_access_token

    # Parse the scanned URL to find what resource it points to.
    # Example record URL: https://transsioner.feishu.cn/record/FhzArCpfoevb8kcvYIccnNOmnUh
    # You need to know how to translate that to app / table / record ids via Feishu APIs.
    # For many Feishu record URLs, the final token is an internal record ID. We'll attempt to extract token-like id.
    m = re.search(r'/record/([A-Za-z0-9_-]+)', scanned_url)
    if not m:
        return JsonResponse({"error": "cannot parse record id from URL"}, status=400)

    record_token = m.group(1)

    # --- Call Feishu Bitable (or record) share API to get a temporary embeddable link ---
    # NOTE: The exact endpoint path depends on how your Feishu tenant's record structures map.
    # Example (doc reference): POST https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}/share
    #
    # Here we assume you can construct app_token/table_id/record_id from the record_token,
    # but often you might need to call a search API first to map the token -> record_id/table_id.
    #
    # For clarity, below is a sample POST. Replace {app_token}, {table_id}, {record_id} with correct values
    # or add code to map record_token -> actual IDs using Feishu APIs (search record endpoint).
    #
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # You will likely need to call search/mapping API first. The example below is placeholder.
    # Example placeholder endpoint:
    bitable_share_endpoint = f"https://open.feishu.cn/open-apis/bitable/v1/apps/YOUR_APP_TOKEN/tables/YOUR_TABLE_ID/records/{record_token}/share"

    share_payload = {
        # payload depends on API; often empty or with expiry/permission options
        # e.g. {"expire_seconds": 3600, "scope": "view"}
    }

    resp = requests.post(bitable_share_endpoint, headers=headers, json=share_payload, timeout=10)

    if resp.status_code != 200:
        # If the API responded with 401/403 or cannot be embedded, let client know
        return JsonResponse({"error": "failed to create share link", "details": resp.text}, status=resp.status_code)

    resp_data = resp.json()
    # Extract the share url from response - depends on API response format
    share_url = resp_data.get("data", {}).get("share_url") or resp_data.get("share_url") or resp_data.get("data", {}).get("preview_url")

    if not share_url:
        return JsonResponse({"error": "share_url missing in API response", "details": resp_data}, status=500)

    return JsonResponse({"ok": True, "share_url": share_url})