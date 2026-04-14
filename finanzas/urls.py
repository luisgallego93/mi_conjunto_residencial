"""
Descripción General: Definición de rutas para el módulo financiero.
Módulo: finanzas
Propósito del archivo: Mapear las URL del sistema a las vistas de recaudo, facturación y gestión de cartera.
"""

from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # Gestión de Cartera y Facturación Masiva
    path('cartera/', views.cartera, name='cartera'),
    path('generar/', views.generar_facturacion, name='generar_facturacion'),
    path('eliminar-periodo/', views.eliminar_periodo, name='eliminar_periodo'),

    # Recaudos y Pagos
    path('pago/<int:apartamento_id>/', views.recibir_pago, name='recibir_pago'),
    path('pagos/plantilla/', views.descargar_plantilla_pagos, name='plantilla_pagos'),
    path('pagos/cargar/', views.cargar_pagos_csv, name='cargar_pagos_csv'),

    # Sanciones y Notificaciones
    path('multa/nueva/', views.registrar_multa, name='registrar_multa'),
    path('multa/eliminar/<int:multa_id>/', views.eliminar_multa, name='eliminar_multa'),
    path('notificar/', views.notificar_morosos, name='notificar_morosos'),

    # Seguimiento y CRM de Cobranza
    path('expediente/<int:apartamento_id>/', views.expediente_cobranza, name='expediente_cobranza'),
    path('historial/<int:apartamento_id>/', views.historial_apartamento_admin, name='historial_apartamento_admin'),
    path('mis-movimientos/', views.mi_estado_cuenta, name='mi_estado_cuenta'),
]
