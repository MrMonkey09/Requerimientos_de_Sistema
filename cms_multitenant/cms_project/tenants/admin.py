from .models import Tenant, TenantUser
from django.contrib import admin
from .custom_admin import tenant_admin_site


class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'contact_email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subdomain', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'subdomain', 'domain', 'is_active')
        }),
        ('Información de Contacto', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class TenantUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'is_owner', 'created_at']
    list_filter = ['is_owner', 'tenant', 'created_at']
    search_fields = ['user__username', 'user__email', 'tenant__name']
    
    def get_queryset(self, request):
        """Filtrar por tenant del usuario actual si no es superuser"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Solo mostrar usuarios del tenant actual
            if hasattr(request, 'tenant'):
                qs = qs.filter(tenant=request.tenant)
        return qs


tenant_admin_site.register(Tenant, TenantAdmin)
tenant_admin_site.register(TenantUser, TenantUserAdmin)
