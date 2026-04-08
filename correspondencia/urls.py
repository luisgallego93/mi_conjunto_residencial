from django.urls import path
from . import views

app_name = 'correspondencia'

urlpatterns = [
    path('', views.lista_paquetes, name='lista_paquetes'),
    path('recibir/', views.recibir_paquete, name='recibir_paquete'),
    path('entregar/<int:paquete_id>/', views.entregar_paquete, name='entregar_paquete'),
]
