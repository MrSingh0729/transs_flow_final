import os
from django.http import FileResponse
from django.conf import settings

def serviceworker(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'serviceworker.js')

    response = FileResponse(open(file_path, 'rb'), content_type='application/javascript')

    # 🔥 Important: Allow service worker full scope over the entire website
    response['Service-Worker-Allowed'] = '/'

    return response
