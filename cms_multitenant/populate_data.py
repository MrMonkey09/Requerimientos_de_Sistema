
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms_project.settings')
django.setup()

from cms_project.tenants.models import Tenant, TenantUser
from cms_project.main.models import Property, Page, Section
from django.contrib.auth.models import User
from decimal import Decimal
import random


def create_sample_data():
    print("Creando datos de ejemplo...")
    
    # Crear tenants de ejemplo
    tenants_data = [
        {
            'name': 'Inmobiliaria del Valle',
            'subdomain': 'valle',
            'contact_email': 'info@inmobiliariavalle.com',
            'contact_phone': '+34-911-123456',
            'address': 'Calle Principal 123, Madrid, España'
        },
        {
            'name': 'Costa Propiedades',
            'subdomain': 'costa',
            'contact_email': 'contacto@costapropiedades.com',
            'contact_phone': '+34-922-654321',
            'address': 'Avenida del Mar 456, Valencia, España'
        },
        {
            'name': 'Metro Homes',
            'subdomain': 'metro',
            'contact_email': 'ventas@metrohomes.com',
            'contact_phone': '+34-933-789012',
            'address': 'Plaza Central 789, Barcelona, España'
        }
    ]
    
    tenants = []
    for tenant_data in tenants_data:
        tenant, created = Tenant.objects.get_or_create(
            subdomain=tenant_data['subdomain'],
            defaults=tenant_data
        )
        tenants.append(tenant)
        if created:
            print(f"Tenant creado: {tenant.name}")
    
    # Crear usuarios dueños para cada tenant
    admin_user = User.objects.get(username='admin')
    for i, tenant in enumerate(tenants):
        # Crear usuario dueño
        owner_username = f'owner_{tenant.subdomain}'
        owner, created = User.objects.get_or_create(
            username=owner_username,
            defaults={
                'email': tenant.contact_email,
                'first_name': f'Dueño {tenant.name}',
                'is_staff': True
            }
        )
        if created:
            owner.set_password('password123')
            owner.save()
            print(f"Usuario dueño creado: {owner_username}")
        
        # Asociar usuario con tenant
        TenantUser.objects.get_or_create(
            user=owner,
            tenant=tenant,
            defaults={'is_owner': True}
        )
    
    # Crear propiedades de ejemplo
    property_types = ['house', 'apartment', 'condo', 'townhouse']
    sale_types = ['sale', 'rent', 'both']
    
    cities_by_tenant = {
        'valle': ['Madrid', 'Alcalá de Henares', 'Getafe', 'Leganés'],
        'costa': ['Valencia', 'Alicante', 'Castellón', 'Gandía'],
        'metro': ['Barcelona', 'Hospitalet', 'Badalona', 'Sabadell']
    }
    
    sample_properties = [
        {
            'title': 'Casa moderna con jardín',
            'description': 'Hermosa casa moderna de dos plantas con amplio jardín, perfecta para familias. Cuenta con acabados de primera calidad y una excelente ubicación cerca de colegios y centros comerciales.',
            'bedrooms': 4,
            'bathrooms': 3,
            'area': Decimal('180.50'),
            'parking_spaces': 2
        },
        {
            'title': 'Apartamento céntrico reformado',
            'description': 'Apartamento completamente reformado en el centro de la ciudad. Ideal para parejas o profesionales que buscan comodidad y ubicación privilegiada.',
            'bedrooms': 2,
            'bathrooms': 2,
            'area': Decimal('85.30'),
            'parking_spaces': 1
        },
        {
            'title': 'Chalet con piscina',
            'description': 'Espectacular chalet independiente con piscina privada y barbacoa. Perfecto para disfrutar en familia con todas las comodidades.',
            'bedrooms': 5,
            'bathrooms': 4,
            'area': Decimal('250.00'),
            'parking_spaces': 3
        },
        {
            'title': 'Piso luminoso con terraza',
            'description': 'Piso muy luminoso con amplia terraza y vistas despejadas. Excelente oportunidad de inversión en zona en crecimiento.',
            'bedrooms': 3,
            'bathrooms': 2,
            'area': Decimal('95.75'),
            'parking_spaces': 1
        },
        {
            'title': 'Casa adosada en urbanización',
            'description': 'Casa adosada en urbanización privada con zonas comunes, piscina comunitaria y parque infantil. Perfecta para familias.',
            'bedrooms': 3,
            'bathrooms': 2,
            'area': Decimal('120.25'),
            'parking_spaces': 1
        },
        {
            'title': 'Ático con vistas panorámicas',
            'description': 'Exclusivo ático con vistas panorámicas a la ciudad. Acabados de lujo y ubicación premium en el mejor barrio.',
            'bedrooms': 4,
            'bathrooms': 3,
            'area': Decimal('160.00'),
            'parking_spaces': 2
        }
    ]
    
    for tenant in tenants:
        cities = cities_by_tenant[tenant.subdomain]
        
        for i, prop_data in enumerate(sample_properties):
            # Crear variaciones para cada tenant
            city = random.choice(cities)
            property_type = random.choice(property_types)
            sale_type = random.choice(sale_types)
            
            # Generar precio según tipo y ciudad
            base_price = random.randint(150000, 800000)
            if sale_type == 'rent':
                base_price = random.randint(800, 2500)
            
            is_featured = i < 3  # Primeras 3 propiedades como destacadas
            
            property_obj = Property.objects.create(
                tenant=tenant,
                title=f"{prop_data['title']} - {city}",
                description=prop_data['description'],
                property_type=property_type,
                sale_type=sale_type,
                price=Decimal(str(base_price)),
                address=f"{random.choice(['Calle', 'Avenida', 'Plaza'])} {random.choice(['Los Olivos', 'Las Flores', 'San Juan', 'La Paz'])} {random.randint(1, 200)}",
                city=city,
                state=random.choice(['Madrid', 'Valencia', 'Cataluña']),
                country='España',
                zip_code=f"{random.randint(10000, 50000)}",
                bedrooms=prop_data['bedrooms'],
                bathrooms=prop_data['bathrooms'],
                area=prop_data['area'],
                parking_spaces=prop_data['parking_spaces'],
                is_featured=is_featured,
                is_available=True
            )
            
            print(f"Propiedad creada: {property_obj.title}")
    
    # Crear páginas por defecto para cada tenant
    for tenant in tenants:
        # Verificar si ya existe homepage
        if not Page.objects.filter(tenant=tenant, is_homepage=True).exists():
            from cms_project.main.views import create_default_homepage
            create_default_homepage(tenant)
            print(f"Homepage creada para {tenant.name}")
        
        # Crear página de propiedades
        props_page, created = Page.objects.get_or_create(
            tenant=tenant,
            slug='propiedades',
            defaults={
                'title': 'Nuestras Propiedades',
                'page_type': 'properties',
                'meta_description': f'Descubre todas las propiedades disponibles en {tenant.name}'
            }
        )
        if created:
            print(f"Página de propiedades creada para {tenant.name}")
    
    print("¡Datos de ejemplo creados exitosamente!")
    print("\nInformación de acceso:")
    print("Superusuario: admin / admin123")
    for tenant in tenants:
        print(f"Tenant {tenant.name}: owner_{tenant.subdomain} / password123")
    print("\nTenants disponibles:")
    for tenant in tenants:
        print(f"- {tenant.name}: {tenant.subdomain}.localhost:8000")


if __name__ == '__main__':
    create_sample_data()
