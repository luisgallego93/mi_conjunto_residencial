from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('residentes/', views.directorio_residentes, name='directorio_residentes'),
    path('apartamentos/', views.directorio_apartamentos, name='directorio_apartamentos'),
    path('vincular/<int:apto_id>/', views.vincular_residente, name='vincular_residente'),
    path('editar/<int:residente_id>/', views.editar_residente, name='editar_residente'),
]
