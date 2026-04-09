from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('cartera/', views.cartera, name='cartera'),
    path('generar/', views.generar_facturacion, name='generar_facturacion'),
    path('multa/nueva/', views.registrar_multa, name='registrar_multa'),
    path('notificar/', views.notificar_morosos, name='notificar_morosos'),
    path('pago/<int:apartamento_id>/', views.recibir_pago, name='recibir_pago'),
    path('pagos/plantilla/', views.descargar_plantilla_pagos, name='plantilla_pagos'),
    path('pagos/cargar/', views.cargar_pagos_csv, name='cargar_pagos_csv'),
    path('expediente/<int:apartamento_id>/', views.expediente_cobranza, name='expediente_cobranza'),
    path('eliminar-periodo/', views.eliminar_periodo, name='eliminar_periodo'),
    path('mis-movimientos/', views.mi_estado_cuenta, name='mi_estado_cuenta'),
]
