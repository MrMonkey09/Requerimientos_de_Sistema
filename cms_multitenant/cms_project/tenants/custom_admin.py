from django.contrib.admin import AdminSite
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import TenantUser
from django.contrib import messages

class TenantAdminSite(AdminSite):
    site_header = "Administración de Tenants"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_permission(self, request):
        user = request.user
        tenant = getattr(request, 'tenant', None)
        # Solo permite acceso si el usuario está autenticado y pertenece al tenant actual
        if user.is_active and user.is_authenticated and tenant:
            # Superuser puede entrar siempre
            if user.is_superuser:
                return True
            # Si existe relación TenantUser, permitir acceso
            return TenantUser.objects.filter(user=user, tenant=tenant).exists()
        return False

    def login(self, request, extra_context=None):
        """
        Personaliza el mensaje de acceso denegado.
        """
        user = request.user
        tenant = getattr(request, 'tenant', None)
        if user.is_authenticated and tenant and not self.has_permission(request):
            messages.error(request, "No tienes permisos para acceder al panel de este tenant.")
        return super().login(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle_sidebar/', self.admin_view(self.toggle_sidebar), name='toggle_sidebar'),
            path('search/', self.admin_view(self.search), name='search'),
        ]
        return custom_urls + urls

    @csrf_exempt
    def toggle_sidebar(self, request):
        return JsonResponse({'status': 'ok'})

    def search(self, request):
        return render(request, "admin/search.html", {})

tenant_admin_site = TenantAdminSite(name='tenant_admin')
tenant_admin_site.register(User, UserAdmin)
tenant_admin_site.register(Group, GroupAdmin)