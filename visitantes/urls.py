"""
Descripción General: Definición de rutas para el módulo de visitantes.
Módulo: visitantes
Propósito del archivo: Mapear las URL del sistema a las vistas de consulta, ingreso y salida de visitantes en portería.
"""

from django.urls import path
from . import views

app_name = 'visitantes'

urlpatterns = [
    # Bitácora e Historial de Acceso
    path('', views.lista_visitantes, name='lista_visitantes'),

    # Procesos de Ingreso y Egreso
    path('ingresar/', views.registrar_visitante, name='registrar_visitante'),
    path('salida/<int:visitante_id>/', views.registrar_salida, name='registrar_salida'),
]
