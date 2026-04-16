"""
Descripción General: Controladores principales del Dashboard.
Módulo: dashboard
Propósito del archivo: Gestionar la lógica de negocio para la visualización de métricas en tiempo real y generación de informes de morosidad.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Sum
import calendar as cal_module

# Importaciones de modelos de otros módulos para consolidación de datos
from comunicacion.models import Comunicacion
from reservas.models import Reserva
from finanzas.models import CuentaCobro, Multa, Recaudo
from visitantes.models import Visitante
from correspondencia.models import Paquete
from usuarios.models import Apartamento, PerfilUsuario

def _get_period_filters(request, date_field='fecha_registro'):
    """
    Calcula el rango de fechas y filtros para consultas según los parámetros GET.
    Soporta: anio, mes, trimestre.
    """
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')
    trimestre = request.GET.get('trimestre')
    
    hoy = date.today()
    if not anio:
        anio = hoy.year
    
    anio = int(anio)
    start_date = date(anio, 1, 1)
    end_date = date(anio, 12, 31)
    periodo_txt = f"Año {anio}"

    if mes and mes != 'todos':
        mes = int(mes)
        ultimo_dia = cal_module.monthrange(anio, mes)[1]
        start_date = date(anio, mes, 1)
        end_date = date(anio, mes, ultimo_dia)
        meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        periodo_txt = f"{meses_nombres[mes-1]} {anio}"
    elif trimestre and trimestre != 'todos':
        trimestre = int(trimestre)
        if trimestre == 1:
            start_date = date(anio, 1, 1); end_date = date(anio, 3, 31)
        elif trimestre == 2:
            start_date = date(anio, 4, 1); end_date = date(anio, 6, 30)
        elif trimestre == 3:
            start_date = date(anio, 7, 1); end_date = date(anio, 9, 30)
        elif trimestre == 4:
            start_date = date(anio, 10, 1); end_date = date(anio, 12, 31)
        periodo_txt = f"Trimestre {trimestre} - {anio}"

    filters = {f"{date_field}__range": (start_date, end_date)}
    return filters, start_date, end_date, periodo_txt, anio, mes, trimestre


@login_required
def index(request):
    """
    Controlador central del Dashboard (Centro de Mando).

    Qué hace:
        Recopila y procesa información de todos los módulos (Finanzas, PQRS, Reservas, Portería, Censo)
        para presentar un resumen ejecutivo en tiempo real.

    Parámetros:
        request: El objeto de solicitud HTTP de Django.

    Valor de retorno:
        Un objeto renderizado del template 'dashboard/index.html' con el contexto de métricas.
    """
    # --- FILTROS DE PERIODO ---
    filters_comu, sd_comu, ed_comu, periodo_txt, v_anio, v_mes, v_trim = _get_period_filters(request, 'fecha_creacion')
    filters_res, sd_res, ed_res, _, _, _, _ = _get_period_filters(request, 'fecha')
    filters_recaudo, sd_rec, ed_rec, _, _, _, _ = _get_period_filters(request, 'fecha_recaudo')

    # --- PROCESAMIENTO DE FINANZAS ---
    cuentas_pendientes = CuentaCobro.objects.filter(estado='Pendiente')
    total_deuda_admin = sum(c.valor_base for c in cuentas_pendientes)
    multas_pendientes = Multa.objects.filter(aplicada_en_cobro=False)
    total_deuda_multas = sum(m.valor for m in multas_pendientes)
    gran_total_mora = total_deuda_admin + total_deuda_multas

    # --- MÉTRICAS OPERATIVAS (FILTRADAS) ---
    pqrs_abiertos = Comunicacion.objects.filter(estado__in=['Abierto', 'En Proceso']).filter(**filters_comu).count()
    reservas_pendientes = Reserva.objects.filter(estado_reserva='Pendiente').filter(**filters_res).count()

    # --- MONITOREO DE PORTERÍA ---
    visitantes_sitio = Visitante.objects.filter(estado='Dentro').count()
    paquetes_porteria = Paquete.objects.filter(estado__in=['Recibido', 'Notificado']).count()

    # --- ESTADÍSTICAS DEL CENSO ---
    aptos_registrados = Apartamento.objects.count()
    residentes_activos = PerfilUsuario.objects.filter(activo=True).count()
    aptos_ocupados = Apartamento.objects.exclude(residente_principal__isnull=True).count()

    # --- CÁLCULO DE INDICADORES (KPIs) PARA BARRAS DE PROGRESO ---
    total_pqrs = Comunicacion.objects.filter(**filters_comu).count()
    pqrs_cerradas = Comunicacion.objects.filter(estado='Cerrado').filter(**filters_comu).count()
    eficiencia_pqrs = int((pqrs_cerradas / total_pqrs * 100)) if total_pqrs > 0 else 100

    cuentas_totales = CuentaCobro.objects.filter(anio=v_anio).count()
    cuentas_pagadas = CuentaCobro.objects.filter(estado='Pagado', anio=v_anio).count()
    recaudo_porcentaje = int((cuentas_pagadas / cuentas_totales * 100)) if cuentas_totales > 0 else 100

    ocupacion = int((aptos_ocupados / aptos_registrados * 100)) if aptos_registrados > 0 else 0

    total_reservas = Reserva.objects.filter(**filters_res).count()
    reservas_aprobadas = Reserva.objects.filter(estado_reserva='Aprobado').filter(**filters_res).count()
    eficiencia_reservas = int((reservas_aprobadas / total_reservas * 100)) if total_reservas > 0 else 100

    recaudo_reservas = Reserva.objects.filter(estado_pago=True).filter(**filters_res).aggregate(t=Sum('valor'))['t'] or 0

    # Años disponibles para el filtro (Limpiamos valores vacíos para evitar errores de ordenamiento)
    recaudos_anios = list(Recaudo.objects.values_list('fecha_recaudo__year', flat=True).distinct())
    anios_disponibles = sorted(list(set(
        [y for y in recaudos_anios if y is not None] + 
        [date.today().year]
    )), reverse=True)

    context = {
        'gran_total_mora': gran_total_mora,
        'cuentas_pendientes_count': cuentas_pendientes.count(),
        'pqrs_abiertos': pqrs_abiertos,
        'reservas_pendientes': reservas_pendientes,
        'visitantes_sitio': visitantes_sitio,
        'paquetes_porteria': paquetes_porteria,
        'aptos_registrados': aptos_registrados,
        'residentes_activos': residentes_activos,
        'eficiencia_pqrs': eficiencia_pqrs,
        'recaudo_porcentaje': recaudo_porcentaje,
        'ocupacion_porcentaje': ocupacion,
        'eficiencia_reservas': eficiencia_reservas,
        'recaudo_reservas': recaudo_reservas,
        'periodo_txt': periodo_txt,
        'v_anio': v_anio,
        'v_mes': v_mes,
        'v_trim': v_trim,
        'anios_disponibles': anios_disponibles,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def informes(request):
    """
    Panel de Reportes Gerenciales y Análisis de Cartera.

    Qué hace:
        Clasifica la morosidad en canastas de tiempo (30, 60, 90, 120+ días)
        y calcula el estado general de paz y salvo del conjunto.

    Parámetros:
        request: El objeto de solicitud HTTP de Django.

    Valor de retorno:
        Un objeto renderizado del template 'dashboard/informes.html' con el análisis de mora.
    """
    # --- FILTROS DE PERIODO ---
    filters_recaudo, sd_rec, ed_rec, periodo_txt, v_anio, v_mes, v_trim = _get_period_filters(request, 'fecha_recaudo')

    # --- ANÁLISIS DE MOROSIDAD (Estado Actual Siempre) ---
    hoy_date = date.today()
    cuentas_pendientes = CuentaCobro.objects.filter(estado='Pendiente').select_related('apartamento')

    mora_30 = []
    mora_60 = []
    mora_90 = []
    mora_120 = []
    mas_120 = []

    for c in cuentas_pendientes:
        mes = int(c.mes_referencia)
        anio = c.anio
        meses_diferencia = (hoy_date.year - anio) * 12 + (hoy_date.month - mes)
        dias_mora = meses_diferencia * 30

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

    aptos_con_deuda_admin = CuentaCobro.objects.filter(estado='Pendiente').values_list('apartamento_id', flat=True)
    aptos_con_deuda_multa = Multa.objects.filter(aplicada_en_cobro=False).values_list('apartamento_id', flat=True)
    aptos_con_deuda = set(list(aptos_con_deuda_admin) + list(aptos_con_deuda_multa))

    aptos_al_dia = Apartamento.objects.exclude(id__in=aptos_con_deuda).count()
    total_aptos = Apartamento.objects.count()

    # --- NUEVAS MÉTRICAS INTERACTIVAS (FILTRADAS) ---
    # 1. Tendencia Mensual de Recaudos
    recaudos_filtrados = Recaudo.objects.filter(**filters_recaudo).order_by('fecha_recaudo')
    
    dict_mensual = {}
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for r in recaudos_filtrados:
        clave = f"{r.fecha_recaudo.year}-{str(r.fecha_recaudo.month).zfill(2)}"
        if clave not in dict_mensual:
            dict_mensual[clave] = {
                'label': f"{meses_nombres[r.fecha_recaudo.month-1]} {r.fecha_recaudo.year}",
                'total': 0
            }
        dict_mensual[clave]['total'] += float(r.valor)

    sorted_keys = sorted(dict_mensual.keys())
    chart_labels = [dict_mensual[k]['label'] for k in sorted_keys]
    chart_data = [dict_mensual[k]['total'] for k in sorted_keys]

    # 2. Distribución por Categorías
    categorias_data = Recaudo.objects.filter(**filters_recaudo).values('categoria').annotate(
        total=Sum('valor')
    )
    mapa_cats = {
        'Administracion': 'Administración',
        'Multa': 'Multas',
        'Reserva': 'Reservas',
        'Otro': 'Otros'
    }
    cat_labels = [mapa_cats.get(c['categoria'], c['categoria']) for c in categorias_data]
    cat_values = [float(c['total']) for c in categorias_data]

    # Años disponibles (Limpieza de None para evitar TypeError en sorted)
    recaudos_anios = list(Recaudo.objects.values_list('fecha_recaudo__year', flat=True).distinct())
    anios_disponibles = sorted(list(set(
        [y for y in recaudos_anios if y is not None] + 
        [date.today().year]
    )), reverse=True)

    context = {
        'total_aptos': total_aptos,
        'aptos_al_dia': aptos_al_dia,
        'deudores_count': len(aptos_con_deuda),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'periodo_txt': periodo_txt,
        'v_anio': v_anio,
        'v_mes': v_mes,
        'v_trim': v_trim,
        'anios_disponibles': anios_disponibles,
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
