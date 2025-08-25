
from django.db import models
from cms_project.tenants.models import Tenant


class MediaFile(models.Model):
    """
    Gestión de archivos multimedia por tenant
    """
    MEDIA_TYPES = [
        ('image', 'Imagen'),
        ('document', 'Documento'),
        ('video', 'Video'),
        ('other', 'Otro'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name="Tenant")
    file = models.FileField(upload_to='media_files/', verbose_name="Archivo")
    original_name = models.CharField(max_length=255, verbose_name="Nombre original")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, verbose_name="Tipo de medio")
    file_size = models.PositiveIntegerField(verbose_name="Tamaño del archivo (bytes)")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texto alternativo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Archivo Multimedia"
        verbose_name_plural = "Archivos Multimedia"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.original_name} ({self.tenant.name})"
    
    def get_file_type(self):
        """Determina el tipo de archivo basado en la extensión"""
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return 'image'
            elif ext in ['pdf', 'doc', 'docx', 'txt']:
                return 'document'
            elif ext in ['mp4', 'avi', 'mov', 'webm']:
                return 'video'
        return 'other'
