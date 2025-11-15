from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from transs_flow.serviceworker import serviceworker


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    
    # IPQC App URLs
    path('ipqc/', include('factories.assembly.departments.qa.ipqc.urls')),
    
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('serviceworker.js', serviceworker, name='serviceworker.js'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)