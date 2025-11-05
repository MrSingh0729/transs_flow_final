from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


# ==============================
# ✅ FUNCTION-BASED VIEW DECORATOR
# ==============================
def role_required(allowed_roles=None, redirect_url='/no-permission/'):
    """
    Decorator to restrict view access based on user roles.
    - Default: Only ADMIN and SUPERUSER can access.
    - Example: @role_required(["IPQC", "QA"])
    """
    if allowed_roles is None:
        allowed_roles = []  # Default empty means only admin/superuser allowed

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Allow Superuser or Admin by default
            user_role = getattr(user, 'role', '').upper()
            if user.is_superuser or user_role == 'ADMIN':
                return view_func(request, *args, **kwargs)

            # If role is defined and matches
            if allowed_roles and user_role in [r.upper() for r in allowed_roles]:
                return view_func(request, *args, **kwargs)

            # Access denied → redirect to custom page or raise 403
            if redirect_url:
                return redirect(redirect_url)
            raise PermissionDenied

        return _wrapped_view
    return decorator


# ==============================
# ✅ CLASS-BASED VIEW MIXIN
# ==============================
class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin for class-based views to restrict access based on user roles.
    Usage:
      - allowed_roles = ["IPQC", "QA"]
      - Default allows only ADMIN and SUPERUSER
    """
    allowed_roles = []  # Override in view
    redirect_url = '/no-permission/'

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        user_role = getattr(user, 'role', '').upper()

        # Allow Admin and Superuser by default
        if user.is_superuser or user_role == "ADMIN":
            return super().dispatch(request, *args, **kwargs)

        # Check allowed roles if defined
        if self.allowed_roles:
            if user_role in [role.upper() for role in self.allowed_roles]:
                return super().dispatch(request, *args, **kwargs)

        # Access denied
        if self.redirect_url:
            return redirect(self.redirect_url)
        raise PermissionDenied
