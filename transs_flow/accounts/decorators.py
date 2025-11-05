from functools import wraps
from django.shortcuts import redirect
from core.models import Page, Assignment

def access_control(url_pattern, allowed_roles=None, allowed_departments=None):
    """
    Decorator to restrict access based on role, department, and factory_code
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            user_role = getattr(request.user, "role", None)
            user_department = getattr(request.user, "department", None)
            user_factory_code = getattr(request.user, "factory_code", None)

            try:
                page = Page.objects.get(url_pattern=url_pattern)
            except Page.DoesNotExist:
                return redirect("no_access")

            # Check if assignment exists for this user
            if not Assignment.objects.filter(factory_code=user_factory_code, department=user_department, role=user_role, page=page).exists():
                return redirect("no_access")

            request.page = page
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
