"""
Descripción General: Definición de rutas para el módulo de reservas.
Módulo: reservas
Propósito del archivo: Mapear las URL del sistema a las vistas de consulta, creación y gestión administrativa de reservas de zonas comunes.
"""

from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # Gestión de Reservas por el Residente
    path('', views.lista_reservas, name='lista_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('pago/<int:reserva_id>/', views.subir_comprobante, name='subir_comprobante'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),

    # Administración y Tarifario (Restringido)
    path('gestionar/<int:reserva_id>/', views.gestionar_reserva, name='gestionar_reserva'),
    path('tarifario/', views.tarifario, name='tarifario'),
    path('tarifa/editar/<int:tarifa_id>/', views.editar_tarifa, name='editar_tarifa'),
]
