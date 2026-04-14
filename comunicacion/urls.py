"""
Descripción General: Definición de rutas para el módulo de comunicaciones y PQRS.
Módulo: comunicacion
Propósito del archivo: Mapear las URL del sistema a las vistas de consulta, radicación y seguimiento de requerimientos ciudadanos.
"""

from django.urls import path
from . import views

app_name = 'comunicacion'

urlpatterns = [
    # Monitoreo y Radicación
    path('', views.lista_pqrs, name='lista_pqrs'),
    path('crear/', views.crear_pqrs, name='crear_pqrs'),

    # Detalle e Interacción
    path('ver/<int:pqrs_id>/', views.ver_pqrs, name='ver_pqrs'),
]
