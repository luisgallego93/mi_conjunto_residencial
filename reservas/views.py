"""
Descripción General: Controladores para la gestión de disponibilidad y reservas de zonas comunes.
Módulo: reservas
Propósito del archivo: Gestionar el flujo de solicitudes de reserva, visualización en calendario y administración de tarifas.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva, TarifaZona
from .forms import ReservaForm
import calendar
from datetime import date
import json

@login_required
def lista_reservas(request):
    """
    Consola de Control de Reservas.

    Qué hace:
        Muestra un listado filtrable de reservas y un calendario mensual de disponibilidad.
        Diferencia el contenido si el usuario es residente o administrador.

    Parámetros:
        pago (GET): Filtro por estado de recaudo (pagado/pendiente).
        estado (GET): Filtro por estado administrativo (Aprobado/Pendiente/Rechazado).
        zona (GET): Filtro por espacio común.
    """
    es_residente = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    # Filtrado dinámico
    pago_filtro = request.GET.get('pago')
    estado_filtro = request.GET.get('estado')
    zona_filtro = request.GET.get('zona')

    queryset = Reserva.objects.all()

    if es_residente:
        perfil = request.user.perfilusuario
        queryset = queryset.filter(solicitante=perfil)

    if pago_filtro == 'pagado':
        queryset = queryset.filter(estado_pago=True)
    elif pago_filtro == 'pendiente':
        queryset = queryset.filter(estado_pago=False)

    if estado_filtro:
        queryset = queryset.filter(estado_reserva=estado_filtro)

    if zona_filtro:
        queryset = queryset.filter(zona_comun=zona_filtro)

    reservas = queryset.order_by('-fecha').select_related('solicitante')

    # Generación de Calendario Mensual
    hoy = date.today()
    try:
        mes_actual = int(request.GET.get('mes', hoy.month))
        anio_actual = int(request.GET.get('anio', hoy.year))
    except ValueError:
        mes_actual = hoy.month
        anio_actual = hoy.year

    if mes_actual == 1:
        mes_anterior, anio_anterior = 12, anio_actual - 1
    else:
        mes_anterior, anio_anterior = mes_actual - 1, anio_actual

    if mes_actual == 12:
        mes_siguiente, anio_siguiente = 1, anio_actual + 1
    else:
        mes_siguiente, anio_siguiente = mes_actual + 1, anio_actual

    MESES_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    nombre_mes = MESES_ES[mes_actual - 1]

    cal = calendar.monthcalendar(anio_actual, mes_actual)

    # Marcadores de ocupación para el calendario
    reservas_mes = Reserva.objects.filter(
        fecha__year=anio_actual,
        fecha__month=mes_actual
    ).exclude(estado_reserva__in=['Rechazado', 'Cancelado']).select_related('solicitante')

    reservas_por_dia = {}
    for r in reservas_mes:
        dia = r.fecha.day
        if dia not in reservas_por_dia:
            reservas_por_dia[dia] = []

        apto_num = '—'
        solicitante_val = r.solicitante.nombre_completo if r.solicitante else '—'

        # --- REGLA DE PRIVACIDAD: Ocultar datos de otros residentes ---
        perfil_actual = getattr(request.user, 'perfilusuario', None)
        es_admin_full = perfil_actual and perfil_actual.rol in ['ADMIN_CONJUNTO', 'ADMIN_SISTEMA']
        es_dueno = r.solicitante == perfil_actual

        if not es_admin_full and not es_dueno:
            solicitante_val = "OCUPADO"
            apto_num = "—"
        else:
            if r.solicitante:
                # Buscar en todas las posibles relaciones
                apto = (r.solicitante.apartamentos_asignados.first() or 
                        r.solicitante.propiedades_asignadas.first() or 
                        r.solicitante.arrendamientos_asignados.first())
                if apto:
                    apto_num = apto.numero

        reservas_por_dia[dia].append({
            'zona': r.zona_comun,
            'zona_display': r.get_zona_comun_display(),
            'solicitante': solicitante_val,
            'apto': apto_num,
            'estado': r.estado_reserva,
        })

    return render(request, 'reservas/lista.html', {
        'reservas': reservas,
        'cal': cal,
        'nombre_mes': nombre_mes,
        'anio_actual': anio_actual,
        'mes_actual': mes_actual,
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente,
        'hoy_dia': hoy.day,
        'reservas_por_dia': reservas_por_dia,
        'es_residente': es_residente,
        'filtros': {
            'pago': pago_filtro,
            'estado': estado_filtro,
            'zona': zona_filtro
        },
        'dias_semana': ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO'],
    })

@login_required
def crear_reserva(request):
    """
    Formulario de Solicitud de Reserva.

    Qué hace:
        Permite a un residente solicitar un espacio. Valida que no existan
        reservas previas para la misma zona y fecha. Asigna tarifas automáticas.
    """
    es_res = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    # Validación e inicialización de tarifas dinámicas
    tarifas_list = [
        {'zona': t.zona, 'valor': int(t.valor), 'deposito': int(t.deposito_garantia), 'descripcion': t.descripcion}
        for t in TarifaZona.objects.filter(activa=True)
    ]

    if request.method == 'POST':
        form = ReservaForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            reserva = form.save(commit=False)

            if es_res:
                reserva.solicitante = request.user.perfilusuario

            # Regla de Negocio: 1 reserva por zona/día
            superposicion = Reserva.objects.filter(
                zona_comun=reserva.zona_comun,
                fecha=reserva.fecha
            ).exclude(estado_reserva__in=['Rechazado', 'Cancelado']).exists()

            if superposicion:
                messages.error(request, "Error: Ese día ya se encuentra reservado.")
            else:
                try:
                    tarifa = TarifaZona.objects.get(zona=reserva.zona_comun)
                    reserva.valor = tarifa.valor
                    reserva.deposito = tarifa.deposito_garantia
                except TarifaZona.DoesNotExist:
                    pass

                reserva.estado_reserva = 'Pendiente'
                reserva.save()
                messages.success(request, f"Pre-reserva generada. Valor: ${reserva.valor:,.0f}.")
                return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm(user=request.user)

    # Datos para bloqueo de fechas en el frontend (DatePicker)
    ocupadas_qs = Reserva.objects.exclude(estado_reserva__in=['Rechazado', 'Cancelado'])
    fechas_ocupadas = {}
    for r in ocupadas_qs:
        zona = r.zona_comun
        fecha_str = r.fecha.strftime('%Y-%m-%d')
        if zona not in fechas_ocupadas:
            fechas_ocupadas[zona] = []
        fechas_ocupadas[zona].append(fecha_str)

    perfil_residente = request.user.perfilusuario if es_res else None

    return render(request, 'reservas/crear.html', {
        'form': form,
        'fechas_ocupadas': json.dumps(fechas_ocupadas),
        'tarifas': json.dumps(tarifas_list, ensure_ascii=False),
        'es_residente': es_res,
        'perfil_residente': perfil_residente,
    })

@login_required
def gestionar_reserva(request, reserva_id):
    """
    Panel de Aprobación Administrativa.

    Qué hace:
        Cambia el estado de una reserva a 'Aprobado' o 'Rechazado'.
        Si se aprueba, se marca como pagada asumiendo recaudo previo.
    """
    perfil = getattr(request.user, 'perfilusuario', None)
    if not perfil or perfil.rol not in ['ADMIN_CONJUNTO', 'ADMIN_SISTEMA']:
        messages.error(request, "Acceso denegado.")
        return redirect('reservas:lista_reservas')

    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            reserva.estado_reserva = 'Aprobado'
            reserva.estado_pago = True
            messages.success(request, "Reserva Aprobada.")
        elif accion == 'rechazar':
            reserva.estado_reserva = 'Rechazado'
            messages.error(request, "Reserva Rechazada.")
        reserva.save()
    return redirect('reservas:lista_reservas')

@login_required
def subir_comprobante(request, reserva_id):
    """
    Carga de Soportes de Pago.

    Qué hace:
        Permite al residente adjuntar la foto o PDF del recibo de consignación
        para que administración proceda con la aprobación.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        archivo = request.FILES.get('comprobante_pago')
        if archivo:
            reserva.comprobante_pago = archivo
            reserva.save()
            messages.info(request, "Comprobante recibido. En revisión.")
    return redirect('reservas:lista_reservas')

@login_required
def tarifario(request):
    """
    Administrador de Precios.

    Qué hace:
        Muestra y permite editar el valor de uso y depósitos para cada zona.
    """
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE':
        return redirect('reservas:lista_reservas')

    tarifas = TarifaZona.objects.all()
    return render(request, 'reservas/tarifario.html', {'tarifas': tarifas})


@login_required
def editar_tarifa(request, tarifa_id):
    """
    Controlador de Actualización de Tarifa.

    Qué hace:
        Procesa el formulario POST desde el tarifario para actualizar los valores
        y la disponibilidad de una zona específica.
    """
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE':
        return redirect('reservas:lista_reservas')

    tarifa = get_object_or_404(TarifaZona, id=tarifa_id)
    if request.method == 'POST':
        tarifa.valor = request.POST.get('valor', tarifa.valor)
        tarifa.descripcion = request.POST.get('descripcion', tarifa.descripcion)
        tarifa.activa = 'activa' in request.POST
        tarifa.save()
        messages.success(request, f"Tarifa de {tarifa.get_zona_display()} actualizada.")

    return redirect('reservas:tarifario')


@login_required
def cancelar_reserva(request, reserva_id):
    """
    Liberación de Cupos.

    Qué hace:
        Cambia el estado de la reserva a 'Cancelado', permitiendo que otros
        residentes tomen el cupo para esa fecha.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    perfil = request.user.perfilusuario
    es_admin = perfil.rol in ['ADMIN_CONJUNTO', 'ADMIN_SISTEMA']

    if not es_admin and reserva.solicitante != perfil:
        messages.error(request, "Sin permisos.")
        return redirect('reservas:lista_reservas')

    reserva.estado_reserva = 'Cancelado'
    reserva.save()
    messages.success(request, "Reserva cancelada.")
    return redirect('reservas:lista_reservas')
