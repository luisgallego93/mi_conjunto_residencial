"""
Descripción General: Definición de rutas del Dashboard.
Módulo: dashboard
Propósito del archivo: Mapear las URLs de la aplicación a sus respectivos controladores (vistas).
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('informes/', views.informes, name='informes'),
]
