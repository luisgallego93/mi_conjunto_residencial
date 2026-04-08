from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.lista_reservas, name='lista_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('gestionar/<int:reserva_id>/', views.gestionar_reserva, name='gestionar_reserva'),
    path('pago/<int:reserva_id>/', views.subir_comprobante, name='subir_comprobante'),
]
