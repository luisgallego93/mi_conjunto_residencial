from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('residentes/', views.directorio_residentes, name='directorio_residentes'),
    path('residentes/registrar/', views.registrar_residente, name='registrar_residente'),
    path('apartamentos/', views.directorio_apartamentos, name='directorio_apartamentos'),
    path('vincular/<int:apto_id>/', views.vincular_residente, name='vincular_residente'),
    path('desvincular/<int:apto_id>/<str:rol>/', views.desvincular_residente, name='desvincular_residente'),
    path('editar/<int:residente_id>/', views.editar_residente, name='editar_residente'),
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),
]
