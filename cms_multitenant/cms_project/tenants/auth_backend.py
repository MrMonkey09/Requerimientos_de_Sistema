from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Tenant, TenantUser

class TenantBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            return None
        # Extrae el subdominio del host
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            if TenantUser.objects.filter(user=user, tenant=tenant).exists():
                return user
        return None