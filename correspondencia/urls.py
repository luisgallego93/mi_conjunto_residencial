"""
Descripción General: Definición de rutas para el módulo de correspondencia.
Módulo: correspondencia
Propósito del archivo: Mapear las URL del sistema a las vistas de consulta, recepción y entrega de paquetes en portería.
"""

from django.urls import path
from . import views

app_name = 'correspondencia'

urlpatterns = [
    # Gestión de Inventario de Paquetes
    path('', views.lista_paquetes, name='lista_paquetes'),

    # Procesos Operativos (Portería)
    path('recibir/', views.recibir_paquete, name='recibir_paquete'),
    path('entregar/<int:paquete_id>/', views.entregar_paquete, name='entregar_paquete'),
]
