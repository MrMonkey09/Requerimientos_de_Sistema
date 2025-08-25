
from django.db import models
from django.contrib.auth.models import User


class Tenant(models.Model):
    """
    Modelo para representar un tenant (cliente) del sistema multi-tenant
    """
    name = models.CharField(max_length=100, verbose_name="Nombre del Tenant")
    subdomain = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Subdominio",
        help_text="Subdominio para acceder al tenant (ej: cliente1)"
    )
    domain = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Dominio personalizado",
        help_text="Dominio personalizado opcional"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    # Información de contacto por defecto
    contact_email = models.EmailField(blank=True, verbose_name="Email de contacto")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono de contacto")
    address = models.TextField(blank=True, verbose_name="Dirección")
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        
    def __str__(self):
        return f"{self.name} ({self.subdomain})"


class TenantUser(models.Model):
    """
    Relación entre usuarios y tenants para controlar permisos
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Tenant")
    is_owner = models.BooleanField(default=False, verbose_name="Es dueño")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'tenant')
        verbose_name = "Usuario del Tenant"
        verbose_name_plural = "Usuarios del Tenant"
        
    def __str__(self):
        role = "Dueño" if self.is_owner else "Usuario"
        return f"{self.user.username} - {self.tenant.name} ({role})"
