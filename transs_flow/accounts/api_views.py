from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import PasswordChangeRequest
 
@csrf_exempt
@require_POST
@login_required
def change_profile_picture(request):
    """Handle profile picture change via AJAX"""
    if 'profile_picture' not in request.FILES:
        return JsonResponse({'error': 'No image file provided'}, status=400)
    
    image = request.FILES['profile_picture']
    user = request.user
    
    # Validate image
    if image.size > 5 * 1024 * 1024:  # 5MB limit
        return JsonResponse({'error': 'Image size too large. Maximum 5MB allowed.'}, status=400)
    
    if not image.content_type.startswith('image/'):
        return JsonResponse({'error': 'Invalid image format'}, status=400)
    
    try:
        # Save the image
        if user.employee.profile_picture:
            # Delete old profile picture if exists
            user.employee.profile_picture.delete(save=False)
        
        user.employee.profile_picture = image
        user.employee.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile picture changed successfully!',
            'profile_picture_url': user.employee.get_profile_picture_url()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
@csrf_exempt
@require_POST
@login_required
def submit_password_request(request):
    """Handle password change request via AJAX"""
    reason = request.POST.get('reason', '').strip()
    
    if not reason:
        return JsonResponse({'error': 'Reason is required'}, status=400)
    
    try:
        # Create password change request
        request_obj = PasswordChangeRequest.objects.create(
            user=request.user.employee,
            reason=reason,
            status='PENDING'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Your password change request has been submitted. Please wait for administrator approval.'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)