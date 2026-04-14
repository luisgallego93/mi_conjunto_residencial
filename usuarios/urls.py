"""
Descripción General: Definición de rutas para el módulo de Usuarios.
Módulo: usuarios
Propósito del archivo: Mapear las URL del sistema a las vistas de gestión de residentes, apartamentos y perfiles.
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Gestión de Residentes
    path('residentes/', views.directorio_residentes, name='directorio_residentes'),
    path('residentes/registrar/', views.registrar_residente, name='registrar_residente'),
    path('editar/<int:residente_id>/', views.editar_residente, name='editar_residente'),
    path('estado/<int:residente_id>/', views.alternar_estado_residente, name='alternar_estado_residente'),

    # Gestión de Apartamentos y Vinculación
    path('apartamentos/', views.directorio_apartamentos, name='directorio_apartamentos'),
    path('vincular/<int:apto_id>/', views.vincular_residente, name='vincular_residente'),
    path('desvincular/<int:apto_id>/<str:rol>/', views.desvincular_residente, name='desvincular_residente'),

    # Perfil y Autogestión (Residente)
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
    path('familia/', views.gestionar_familia, name='gestionar_familia'),
    path('ocupante/eliminar/<int:ocupante_id>/', views.eliminar_ocupante, name='eliminar_ocupante'),
]
