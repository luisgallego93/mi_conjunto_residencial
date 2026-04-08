from django.urls import path
from . import views

app_name = 'visitantes'

urlpatterns = [
    path('', views.lista_visitantes, name='lista_visitantes'),
    path('ingresar/', views.registrar_visitante, name='registrar_visitante'),
    path('salida/<int:visitante_id>/', views.registrar_salida, name='registrar_salida'),
]
