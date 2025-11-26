from .models import PasswordChangeRequest

def admin_notifications(request):
    if request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        pending_count = PasswordChangeRequest.objects.filter(status="pending").count()
    else:
        pending_count = 0

    return {
        "pending_password_requests": pending_count
    }
