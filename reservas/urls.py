from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.lista_reservas, name='lista_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('gestionar/<int:reserva_id>/', views.gestionar_reserva, name='gestionar_reserva'),
    path('pago/<int:reserva_id>/', views.subir_comprobante, name='subir_comprobante'),
    path('tarifario/', views.tarifario, name='tarifario'),
    path('tarifa/editar/<int:tarifa_id>/', views.editar_tarifa, name='editar_tarifa'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
]
