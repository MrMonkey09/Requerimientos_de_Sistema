
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('propiedad/<int:property_id>/', views.property_detail_view, name='property_detail'),
    path('contacto/', views.contact_form_view, name='contact'),
    path('<slug:slug>/', views.page_detail_view, name='page_detail'),
]
