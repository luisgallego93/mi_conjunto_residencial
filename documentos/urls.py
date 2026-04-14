"""
Descripción General: Definición de rutas para el repositorio de documentos.
Módulo: documentos
Propósito del archivo: Mapear las URL del sistema a las vistas de consulta y carga de archivos institucionales del conjunto.
"""

from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    # Visualización y Descarga
    path('', views.lista_documentos, name='lista'),

    # Carga Administrativa
    path('subir/', views.subir_documento, name='subir'),
]
