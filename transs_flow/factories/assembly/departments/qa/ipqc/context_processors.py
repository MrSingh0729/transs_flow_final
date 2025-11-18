# context_processors.py
def csrf_token(request):
    return {'csrf_token': str(request.META.get('CSRF_COOKIE', ''))}
