from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    
    path('ipqc/', include('factories.assembly.departments.qa.ipqc.urls')),  # <--- nested app
    path("chat/", include("chat.urls", namespace="chat")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)