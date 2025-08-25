from django import forms
from django.contrib.auth.forms import AuthenticationForm
from cms_project.tenants.models import Tenant, TenantUser

class TenantAdminAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        request = self.request
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        if user.is_superuser:
            return
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
            if not TenantUser.objects.filter(user=user, tenant=tenant).exists():
                raise forms.ValidationError(
                    "No tienes acceso a este tenant.",
                    code='invalid_login',
                )
        except Tenant.DoesNotExist:
            raise forms.ValidationError(
                "Tenant no encontrado.",
                code='invalid_login',
            )