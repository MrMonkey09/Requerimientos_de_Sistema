from django.contrib import admin
from .models import Property, PropertyImage, Page, Section, ContactSubmission
from cms_project.tenants.custom_admin import tenant_admin_site


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order']


class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'sale_type', 'price', 'city', 'is_featured', 'is_available', 'tenant']
    list_filter = ['property_type', 'sale_type', 'is_featured', 'is_available', 'tenant', 'created_at']
    search_fields = ['title', 'address', 'city', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tenant', 'title', 'description', 'property_type', 'sale_type')
        }),
        ('Precio', {
            'fields': ('price', 'price_currency')
        }),
        ('Ubicación', {
            'fields': ('address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Características', {
            'fields': ('bedrooms', 'bathrooms', 'area', 'parking_spaces')
        }),
        ('Estado', {
            'fields': ('is_featured', 'is_available')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filtrar propiedades por tenant"""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if hasattr(request, 'tenant'):
                qs = qs.filter(tenant=request.tenant)
        return qs
    
    def save_model(self, request, obj, form, change):
        """Asignar tenant automáticamente"""
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['section_type', 'title', 'subtitle', 'order', 'is_active']


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'is_homepage', 'is_active', 'tenant', 'created_at']
    list_filter = ['page_type', 'is_active', 'is_homepage', 'tenant']
    search_fields = ['title', 'slug', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tenant', 'title', 'slug', 'page_type')
        }),
        ('Configuración', {
            'fields': ('is_active', 'is_homepage', 'meta_description')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if hasattr(request, 'tenant'):
                qs = qs.filter(tenant=request.tenant)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)


class SectionAdmin(admin.ModelAdmin):
    list_display = ['page', 'section_type', 'title', 'order', 'is_active']
    list_filter = ['section_type', 'is_active', 'page__tenant']
    search_fields = ['title', 'subtitle', 'content']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('page', 'section_type', 'title', 'subtitle', 'content')
        }),
        ('Hero Section', {
            'fields': ('hero_button_text', 'hero_button_link', 'background_image'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if hasattr(request, 'tenant'):
                qs = qs.filter(page__tenant=request.tenant)
        return qs


class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'property_interest', 'is_read', 'created_at', 'tenant']
    list_filter = ['is_read', 'tenant', 'created_at', 'property_interest']
    search_fields = ['name', 'email', 'phone', 'subject', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información del Contacto', {
            'fields': ('tenant', 'page', 'name', 'email', 'phone')
        }),
        ('Mensaje', {
            'fields': ('subject', 'message', 'property_interest')
        }),
        ('Estado', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if hasattr(request, 'tenant'):
                qs = qs.filter(tenant=request.tenant)
        return qs
    
    def save_model(self, request, obj, form, change):
        if not change and hasattr(request, 'tenant'):
            obj.tenant = request.tenant
        super().save_model(request, obj, form, change)


class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'alt_text', 'is_main', 'order', 'created_at']
    list_filter = ['is_main', 'property__tenant']
    search_fields = ['property__title', 'alt_text']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if hasattr(request, 'tenant'):
                qs = qs.filter(property__tenant=request.tenant)
        return qs

# --- Registro de modelos ---
tenant_admin_site.register(Property, PropertyAdmin)
tenant_admin_site.register(Page, PageAdmin)
tenant_admin_site.register(Section, SectionAdmin)
tenant_admin_site.register(ContactSubmission, ContactSubmissionAdmin)
tenant_admin_site.register(PropertyImage, PropertyImageAdmin)
