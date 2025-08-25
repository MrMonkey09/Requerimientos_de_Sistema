from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cms_project.tenants.custom_admin import tenant_admin_site

urlpatterns = [
    path('admin/', tenant_admin_site.urls),
    path('', include('cms_project.main.urls')),
    path('tenants/', include('cms_project.tenants.urls')),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
