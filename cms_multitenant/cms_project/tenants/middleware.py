
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware para resolver el tenant basado en el subdominio
    """
    
    def process_request(self, request):
        # Obtener el host de la request
        host = request.get_host().split(':')[0]  # Remover el puerto si existe
        
        # Para desarrollo local, usar un tenant por defecto si no hay subdominio
        if host in ['localhost', '127.0.0.1']:
            try:
                tenant = Tenant.objects.filter(is_active=True).first()
                if not tenant:
                    # Crear tenant por defecto si no existe
                    tenant = Tenant.objects.create(
                        name="Demo Inmobiliaria",
                        subdomain="demo",
                        contact_email="info@demo.com",
                        contact_phone="+1-555-0123"
                    )
            except:
                # Si hay error en la base de datos (migraciones pendientes), continuar
                tenant = None
        else:
            # Extraer subdominio del host
            parts = host.split('.')
            if len(parts) >= 3:
                subdomain = parts[0]
            else:
                subdomain = host.split('.')[0] if '.' in host else host
            
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
            except Tenant.DoesNotExist:
                raise Http404("Tenant no encontrado")
        
        # Agregar el tenant a la request
        request.tenant = tenant
        
        return None
