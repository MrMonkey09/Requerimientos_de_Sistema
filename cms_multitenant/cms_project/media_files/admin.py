from django.contrib import admin
from .models import MediaFile
from cms_project.tenants.custom_admin import tenant_admin_site


class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'media_type', 'file_size', 'tenant', 'created_at']
    list_filter = ['media_type', 'tenant', 'created_at']
    search_fields = ['original_name', 'description', 'alt_text']
    readonly_fields = ['created_at', 'updated_at', 'file_size']

    fieldsets = (
        ('Archivo', {
            'fields': ('tenant', 'file', 'original_name', 'media_type', 'file_size')
        }),
        ('Información adicional', {
            'fields': ('alt_text', 'description')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.file:
            obj.file_size = obj.file.size
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and hasattr(request, 'tenant'):
            qs = qs.filter(tenant=request.tenant)
        return qs


tenant_admin_site.register(MediaFile, MediaFileAdmin)
