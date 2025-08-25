
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from .models import Page, Property, ContactSubmission


def home_view(request):
    """
    Vista principal que muestra la página de inicio del tenant
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        raise Http404("Tenant no encontrado")
    
    # Buscar página de inicio del tenant
    try:
        homepage = Page.objects.get(tenant=request.tenant, is_homepage=True, is_active=True)
    except Page.DoesNotExist:
        # Si no hay homepage, crear una por defecto
        homepage = create_default_homepage(request.tenant)
    
    # Obtener secciones de la página
    sections = homepage.section_set.filter(is_active=True).order_by('order')
    
    # Obtener propiedades destacadas para mostrar en la página principal
    featured_properties = Property.objects.filter(
        tenant=request.tenant,
        is_featured=True,
        is_available=True
    )[:6]
    
    context = {
        'page': homepage,
        'sections': sections,
        'featured_properties': featured_properties,
        'tenant': request.tenant,
    }
    
    return render(request, 'main/home.html', context)


def page_detail_view(request, slug):
    """
    Vista para mostrar páginas específicas por slug
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        raise Http404("Tenant no encontrado")
    
    page = get_object_or_404(Page, tenant=request.tenant, slug=slug, is_active=True)
    sections = page.section_set.filter(is_active=True).order_by('order')
    
    # Contexto específico por tipo de página
    context = {
        'page': page,
        'sections': sections,
        'tenant': request.tenant,
    }
    
    if page.page_type == 'properties':
        # Para páginas de propiedades, incluir todas las propiedades del tenant
        properties = Property.objects.filter(
            tenant=request.tenant,
            is_available=True
        ).order_by('-created_at')
        context['properties'] = properties
    
    return render(request, f'main/{page.page_type}.html', context)


def properties_view(request):
    """
    Vista para mostrar el catálogo completo de propiedades
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        raise Http404("Tenant no encontrado")
    
    properties = Property.objects.filter(
        tenant=request.tenant,
        is_available=True
    ).order_by('-created_at')
    
    # Filtros
    property_type = request.GET.get('type')
    sale_type = request.GET.get('sale')
    city = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    if sale_type:
        properties = properties.filter(sale_type=sale_type)
    if city:
        properties = properties.filter(city__icontains=city)
    if min_price:
        try:
            properties = properties.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            properties = properties.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Obtener valores únicos para filtros
    cities = Property.objects.filter(
        tenant=request.tenant,
        is_available=True
    ).values_list('city', flat=True).distinct()
    
    context = {
        'properties': properties,
        'cities': cities,
        'property_types': Property.PROPERTY_TYPES,
        'sale_types': Property.SALE_TYPES,
        'tenant': request.tenant,
        'filters': {
            'property_type': property_type,
            'sale_type': sale_type,
            'city': city,
            'min_price': min_price,
            'max_price': max_price,
        }
    }
    
    return render(request, 'main/properties.html', context)


def property_detail_view(request, property_id):
    """
    Vista para mostrar detalle de una propiedad específica
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        raise Http404("Tenant no encontrado")
    
    property_obj = get_object_or_404(
        Property, 
        id=property_id, 
        tenant=request.tenant,
        is_available=True
    )
    
    # Obtener todas las imágenes de la propiedad
    images = property_obj.propertyimage_set.all().order_by('order')
    
    # Propiedades similares
    similar_properties = Property.objects.filter(
        tenant=request.tenant,
        property_type=property_obj.property_type,
        is_available=True
    ).exclude(id=property_obj.id)[:4]

    print(request.tenant)
    print(property_obj.property_type)
    
    context = {
        'property': property_obj,
        'images': images,
        'similar_properties': similar_properties,
        'tenant': request.tenant,
    }
    
    return render(request, 'main/property_detail.html', context)


@csrf_exempt
@require_POST
def contact_form_view(request):
    """
    Vista para procesar formularios de contacto
    """
    if not hasattr(request, 'tenant') or not request.tenant:
        return JsonResponse({'success': False, 'error': 'Tenant no encontrado'})
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        # Fallback para formularios normales
        data = request.POST
    
    # Validación básica
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({
                'success': False, 
                'error': f'El campo {field} es obligatorio'
            })
    
    # Crear el registro de contacto
    contact = ContactSubmission.objects.create(
        tenant=request.tenant,
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone', ''),
        subject=data.get('subject', ''),
        message=data.get('message'),
    )
    
    # Si se especifica una propiedad de interés
    property_id = data.get('property_id')
    if property_id:
        try:
            property_obj = Property.objects.get(
                id=property_id, 
                tenant=request.tenant
            )
            contact.property_interest = property_obj
            contact.save()
        except Property.DoesNotExist:
            pass
    
    # Respuesta según tipo de request
    if request.content_type == 'application/json':
        return JsonResponse({
            'success': True, 
            'message': 'Mensaje enviado correctamente. Te contactaremos pronto.'
        })
    else:
        messages.success(request, 'Mensaje enviado correctamente. Te contactaremos pronto.')
        return redirect('main:home')


def create_default_homepage(tenant):
    """
    Crea una página de inicio por defecto para un tenant
    """
    from .models import Page, Section
    
    # Crear página principal
    homepage = Page.objects.create(
        tenant=tenant,
        title=f"Bienvenido a {tenant.name}",
        slug="inicio",
        page_type="home",
        is_homepage=True,
        meta_description=f"Encuentra tu hogar ideal con {tenant.name}. Las mejores propiedades inmobiliarias."
    )
    
    # Crear sección hero
    Section.objects.create(
        page=homepage,
        section_type="hero",
        title="Encuentra tu hogar ideal",
        subtitle="Descubre las mejores propiedades en las mejores ubicaciones",
        hero_button_text="Ver Propiedades",
        hero_button_link="/propiedades/",
        order=1
    )
    
    # Crear sección de propiedades destacadas
    Section.objects.create(
        page=homepage,
        section_type="properties_grid",
        title="Propiedades Destacadas",
        subtitle="Conoce nuestras mejores opciones",
        order=2
    )
    
    # Crear sección de contacto
    Section.objects.create(
        page=homepage,
        section_type="contact_form",
        title="Contáctanos",
        subtitle="Estamos aquí para ayudarte a encontrar tu hogar ideal",
        order=3
    )
    
    return homepage
