from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Corrección de Importaciones
from comunicacion.models import Comunicacion
from reservas.models import Reserva
from finanzas.models import CuentaCobro, Multa
from visitantes.models import Visitante
from correspondencia.models import Paquete
from usuarios.models import Apartamento, PerfilUsuario

@login_required
def index(request):
    """
    Dashboard Core Controller: Centro de Mando Gerencial.
    Recopila, cruza y procesa la información condensada de todas las aplicaciones del ecosistema:
    - Finanzas: Totalización de deudas (sumatoria de base y multas).
    - Censo: Conteo de apartamentos base y residentes matriculados.
    - CRM: Extracción de PQRS en estados de seguimiento.
    - Operativa: Tracking en tiempo real de recepciones (paquetes y visitantes en la estructura).
    Al final, este motor inyecta (context) las variables matemáticas procesadas al entorno frontend (index.html),
    alojando las gráficas en tiempo real.
    """
    # Finanzas
    cuentas_pendientes = CuentaCobro.objects.filter(estado='Pendiente')
    total_deuda_admin = sum(c.valor_base for c in cuentas_pendientes)
    multas_pendientes = Multa.objects.filter(aplicada_en_cobro=False)
    total_deuda_multas = sum(m.valor for m in multas_pendientes)
    gran_total_mora = total_deuda_admin + total_deuda_multas
    
    # Operativo
    pqrs_abiertos = Comunicacion.objects.filter(estado__in=['Abierto', 'En Proceso']).count()
    reservas_pendientes = Reserva.objects.filter(estado_reserva='Pendiente').count()
    
    # Portería
    visitantes_sitio = Visitante.objects.filter(estado='Dentro').count()
    paquetes_porteria = Paquete.objects.filter(estado__in=['Recibido', 'Notificado']).count()
    
    # Censo
    aptos_registrados = Apartamento.objects.count()
    residentes_activos = PerfilUsuario.objects.filter(activo=True).count()
    aptos_ocupados = Apartamento.objects.exclude(residente_principal__isnull=True).count()
    
    # --- MATEMATICA PARA BARRAS DE PROGRESO DE DASHBOARD ---
    total_pqrs = Comunicacion.objects.count()
    pqrs_cerradas = Comunicacion.objects.filter(estado='Cerrado').count()
    eficiencia_pqrs = int((pqrs_cerradas / total_pqrs * 100)) if total_pqrs > 0 else 100
    
    cuentas_totales = CuentaCobro.objects.count()
    cuentas_pagadas = CuentaCobro.objects.filter(estado='Pagado').count()
    recaudo_porcentaje = int((cuentas_pagadas / cuentas_totales * 100)) if cuentas_totales > 0 else 100
    
    ocupacion = int((aptos_ocupados / aptos_registrados * 100)) if aptos_registrados > 0 else 0
    
    total_reservas = Reserva.objects.count()
    reservas_aprobadas = Reserva.objects.filter(estado_reserva='Aprobado').count()
    eficiencia_reservas = int((reservas_aprobadas / total_reservas * 100)) if total_reservas > 0 else 100
    
    from django.db.models import Sum
    recaudo_reservas = Reserva.objects.filter(estado_pago=True).aggregate(t=Sum('valor'))['t'] or 0
    
    context = {
        'gran_total_mora': gran_total_mora,
        'cuentas_pendientes_count': cuentas_pendientes.count(),
        'pqrs_abiertos': pqrs_abiertos,
        'reservas_pendientes': reservas_pendientes,
        'visitantes_sitio': visitantes_sitio,
        'paquetes_porteria': paquetes_porteria,
        'aptos_registrados': aptos_registrados,
        'residentes_activos': residentes_activos,
        # Nuevas variables
        'eficiencia_pqrs': eficiencia_pqrs,
        'recaudo_porcentaje': recaudo_porcentaje,
        'ocupacion_porcentaje': ocupacion,
        'eficiencia_reservas': eficiencia_reservas,
        'recaudo_reservas': recaudo_reservas,
    }
    return render(request, 'dashboard/index.html', context)

from datetime import date

@login_required
def informes(request):
    """
    Panel de Reportes Gerenciales, incluyendo Edades de Mora
    """
    hoy = date.today()
    cuentas_pendientes = CuentaCobro.objects.filter(estado='Pendiente').select_related('apartamento')
    
    # Canastas de morosidad
    mora_30 = []
    mora_60 = []
    mora_90 = []
    mora_120 = []
    mas_120 = []
    
    for c in cuentas_pendientes:
        # Calcular edad de la factura
        # mes_referencia viene de '01' a '12'
        mes = int(c.mes_referencia)
        anio = c.anio
        
        # Diferencia en meses aproximada
        meses_diferencia = (hoy.year - anio) * 12 + (hoy.month - mes)
        # Convertir a días (aproximado 30 por mes)
        dias_mora = meses_diferencia * 30
        
        # Si es del mes actual o futuro, la mora es 0
        if dias_mora < 0: dias_mora = 0
            
        if dias_mora <= 30:
            mora_30.append(c)
        elif 31 <= dias_mora <= 60:
            mora_60.append(c)
        elif 61 <= dias_mora <= 90:
            mora_90.append(c)
        elif 91 <= dias_mora <= 120:
            mora_120.append(c)
        else:
            mas_120.append(c)
            
    # Apartamentos al Día (Los que no tienen facturas pendientes ni multas no aplicadas)
    # Primero buscamos qué aptos deben
    aptos_con_deuda_admin = CuentaCobro.objects.filter(estado='Pendiente').values_list('apartamento_id', flat=True)
    aptos_con_deuda_multa = Multa.objects.filter(aplicada_en_cobro=False).values_list('apartamento_id', flat=True)
    aptos_con_deuda = set(list(aptos_con_deuda_admin) + list(aptos_con_deuda_multa))
    
    aptos_al_dia = Apartamento.objects.exclude(id__in=aptos_con_deuda).count()
    total_aptos = Apartamento.objects.count()

    context = {
        'total_aptos': total_aptos,
        'aptos_al_dia': aptos_al_dia,
        'deudores_count': len(aptos_con_deuda),
        'mora_30': {
            'cantidad': len(mora_30),
            'dinero': sum(c.valor_base for c in mora_30)
        },
        'mora_60': {
            'cantidad': len(mora_60),
            'dinero': sum(c.valor_base for c in mora_60)
        },
        'mora_90': {
            'cantidad': len(mora_90),
            'dinero': sum(c.valor_base for c in mora_90)
        },
        'mora_120': {
            'cantidad': len(mora_120),
            'dinero': sum(c.valor_base for c in mora_120)
        },
        'mas_120': {
            'cantidad': len(mas_120),
            'dinero': sum(c.valor_base for c in mas_120)
        }
    }
    return render(request, 'dashboard/informes.html', context)