
from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms_project.tenants'
    verbose_name = 'Gestión de Tenants'
