
from django.db import models
from django.contrib.auth.models import User
from cms_project.tenants.models import Tenant


class Property(models.Model):
    """
    Modelo para las propiedades inmobiliarias
    """
    PROPERTY_TYPES = [
        ('house', 'Casa'),
        ('apartment', 'Apartamento'),
        ('condo', 'Condominio'),
        ('townhouse', 'Casa adosada'),
        ('land', 'Terreno'),
        ('commercial', 'Comercial'),
    ]
    
    SALE_TYPES = [
        ('sale', 'Venta'),
        ('rent', 'Alquiler'),
        ('both', 'Venta y Alquiler'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Tenant")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, verbose_name="Tipo de propiedad")
    sale_type = models.CharField(max_length=10, choices=SALE_TYPES, default='sale', verbose_name="Tipo de venta")
    
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio")
    price_currency = models.CharField(max_length=3, default='USD', verbose_name="Moneda")
    
    # Ubicación
    address = models.CharField(max_length=255, verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Estado/Provincia")
    country = models.CharField(max_length=100, verbose_name="País")
    zip_code = models.CharField(max_length=20, blank=True, verbose_name="Código postal")
    
    # Características
    bedrooms = models.PositiveIntegerField(default=0, verbose_name="Habitaciones")
    bathrooms = models.PositiveIntegerField(default=0, verbose_name="Baños")
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área (m²)")
    parking_spaces = models.PositiveIntegerField(default=0, verbose_name="Espacios de estacionamiento")
    
    # Estado y metadatos
    is_featured = models.BooleanField(default=False, verbose_name="Destacada")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.city} ({self.tenant.name})"
    
    def get_main_image(self):
        """Obtiene la primera imagen de la propiedad"""
        return self.propertyimage_set.first()


class PropertyImage(models.Model):
    """
    Imágenes asociadas a las propiedades
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Propiedad")
    image = models.ImageField(upload_to='properties/', verbose_name="Imagen")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texto alternativo")
    is_main = models.BooleanField(default=False, verbose_name="Imagen principal")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Propiedad"
        verbose_name_plural = "Imágenes de Propiedades"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.property.title} - Imagen {self.order}"


class Page(models.Model):
    """
    Modelo para las páginas/landing pages de cada tenant
    """
    PAGE_TYPES = [
        ('home', 'Página Principal'),
        ('properties', 'Catálogo de Propiedades'),
        ('about', 'Acerca de'),
        ('contact', 'Contacto'),
        ('custom', 'Personalizada'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Tenant")
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, verbose_name="URL amigable")
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, verbose_name="Tipo de página")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    is_homepage = models.BooleanField(default=False, verbose_name="¿Es página principal?")
    meta_description = models.TextField(max_length=300, blank=True, verbose_name="Meta descripción")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Página"
        verbose_name_plural = "Páginas"
        unique_together = ('tenant', 'slug')
        
    def __str__(self):
        return f"{self.title} ({self.tenant.name})"


class Section(models.Model):
    """
    Secciones/componentes de las páginas
    """
    SECTION_TYPES = [
        ('hero', 'Hero Section'),
        ('properties_grid', 'Galería de Propiedades'),
        ('contact_form', 'Formulario de Contacto'),
        ('text_content', 'Contenido de Texto'),
        ('image_gallery', 'Galería de Imágenes'),
        ('footer', 'Footer'),
    ]
    
    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name="Página")
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, verbose_name="Tipo de sección")
    title = models.CharField(max_length=200, blank=True, verbose_name="Título")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="Subtítulo")
    content = models.TextField(blank=True, verbose_name="Contenido")
    
    # Campos para Hero section
    hero_button_text = models.CharField(max_length=50, blank=True, verbose_name="Texto del botón")
    hero_button_link = models.CharField(max_length=200, blank=True, verbose_name="Enlace del botón")
    background_image = models.ImageField(upload_to='sections/', blank=True, verbose_name="Imagen de fondo")
    
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    
    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.page.title} - {self.get_section_type_display()}"


class ContactSubmission(models.Model):
    """
    Envíos del formulario de contacto
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Tenant")
    page = models.ForeignKey(Page, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Página")
    
    name = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    subject = models.CharField(max_length=200, blank=True, verbose_name="Asunto")
    message = models.TextField(verbose_name="Mensaje")
    
    # Propiedad de interés (opcional)
    property_interest = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Propiedad de interés"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")
    is_read = models.BooleanField(default=False, verbose_name="Leído")
    
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.tenant.name} ({self.created_at.strftime('%d/%m/%Y')})"
