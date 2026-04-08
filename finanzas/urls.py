from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('cartera/', views.cartera, name='cartera'),
    path('generar/', views.generar_facturacion, name='generar_facturacion'),
    path('multa/nueva/', views.registrar_multa, name='registrar_multa'),
    path('notificar/', views.notificar_morosos, name='notificar_morosos'),
    path('pago/<int:apartamento_id>/', views.recibir_pago, name='recibir_pago'),
]
