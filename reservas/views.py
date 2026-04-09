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
    reservas = Reserva.objects.all().order_by('-fecha').select_related('solicitante')
    
    # --- Contexto para el Calendario Mensual ---
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    MESES_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
    nombre_mes = MESES_ES[mes_actual - 1]
    
    cal = calendar.monthcalendar(anio_actual, mes_actual)
    
    # Enriquecer reservas del mes con nombre + apartamento del solicitante
    reservas_mes = Reserva.objects.filter(
        fecha__year=anio_actual,
        fecha__month=mes_actual
    ).exclude(estado_reserva='Rechazado').select_related('solicitante')
    
    reservas_por_dia = {}
    for r in reservas_mes:
        dia = r.fecha.day
        if dia not in reservas_por_dia:
            reservas_por_dia[dia] = []
        
        # Obtener el número de apartamento del solicitante
        apto_num = '—'
        if r.solicitante:
            apto = r.solicitante.apartamentos_asignados.first()
            if apto:
                apto_num = apto.numero
        
        reservas_por_dia[dia].append({
            'zona': r.zona_comun,
            'zona_display': r.get_zona_comun_display(),
            'solicitante': r.solicitante.nombre_completo if r.solicitante else '—',
            'apto': apto_num,
            'estado': r.estado_reserva,
        })
    
    return render(request, 'reservas/lista.html', {
        'reservas': reservas,
        'cal': cal,
        'nombre_mes': nombre_mes,
        'anio_actual': anio_actual,
        'mes_actual': mes_actual,
        'hoy_dia': hoy.day,
        'reservas_por_dia': reservas_por_dia,
    })


@login_required
def crear_reserva(request):
    # Garantizar que las tarifas por defecto existan en BD con los nuevos IDs
    zonas_default = [
        {'zona': 'salon', 'valor': 80000, 'deposito_garantia': 50000, 
         'descripcion': 'Capacidad máx. 80 personas. Horario: 8am - 11pm. Incluye sillas y mesas.'},
        {'zona': 'bbq', 'valor': 40000, 'deposito_garantia': 30000, 
         'descripcion': 'Capacidad máx. 20 personas. Horario: 9am - 8pm. Aseo no incluido.'},
        {'zona': 'piscina', 'valor': 0, 'deposito_garantia': 0, 
         'descripcion': 'Uso libre para residentes. Horario: 7am - 8pm.'},
    ]
    for zd in zonas_default:
        TarifaZona.objects.get_or_create(zona=zd['zona'], defaults=zd)

    # Cargar tarifas como lista (evita problemas de encoding con caracteres especiales en claves JS)
    tarifas_list = [
        {'zona': t.zona, 'valor': int(t.valor), 'deposito': int(t.deposito_garantia), 'descripcion': t.descripcion}
        for t in TarifaZona.objects.filter(activa=True)
    ]
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, request.FILES)
        if form.is_valid():
            reserva = form.save(commit=False)
            
            superposicion = Reserva.objects.filter(
                zona_comun=reserva.zona_comun, 
                fecha=reserva.fecha
            ).exclude(estado_reserva='Rechazado').exists()
            
            if superposicion:
                messages.error(request, "Error: Ese día ya se encuentra reservado para ese espacio. Sólo se permite un grupo por día.")
            else:
                # Autoasignar el valor de la tarifa vigente
                try:
                    tarifa = TarifaZona.objects.get(zona=reserva.zona_comun)
                    reserva.valor = tarifa.valor
                    reserva.deposito = tarifa.deposito_garantia
                except TarifaZona.DoesNotExist:
                    pass  # Si no hay tarifa configurada, queda en 0
                
                reserva.estado_reserva = 'Pendiente'
                reserva.save()
                messages.success(request, f"Pre-reserva generada por ${reserva.valor:,.0f}. Realice el pago o suba el comprobante para confirmación final.")
                return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm()
        
    ocupadas_qs = Reserva.objects.exclude(estado_reserva='Rechazado')
    fechas_ocupadas = {}
    for r in ocupadas_qs:
        zona = r.zona_comun
        fecha_str = r.fecha.strftime('%Y-%m-%d')
        if zona not in fechas_ocupadas:
            fechas_ocupadas[zona] = []
        fechas_ocupadas[zona].append(fecha_str)
        
    return render(request, 'reservas/crear.html', {
        'form': form,
        'fechas_ocupadas': json.dumps(fechas_ocupadas),
        'tarifas': json.dumps(tarifas_list, ensure_ascii=False),
    })


@login_required
def gestionar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            reserva.estado_reserva = 'Aprobado'
            reserva.estado_pago = True
            messages.success(request, "Reserva Aprobada y Pagada Correctamente.")
        elif accion == 'rechazar':
            reserva.estado_reserva = 'Rechazado'
            messages.error(request, "Reserva Rechazada.")
        reserva.save()
    return redirect('reservas:lista_reservas')


@login_required
def subir_comprobante(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        archivo = request.FILES.get('comprobante_pago')
        if archivo:
            reserva.comprobante_pago = archivo
            reserva.save()
            messages.info(request, "El comprobante de pago fue subido y está en revisión.")
    return redirect('reservas:lista_reservas')


@login_required
def tarifario(request):
    """
    Panel de gestión del Tarifario de Zonas Comunes.
    Muestra las tarifas actuales y permite editarlas inline.
    """
    tarifas = TarifaZona.objects.all()
    
    # Si no existen las tarifas base, crearlas con los valores por defecto
    zonas_default = [
        {'zona': 'Salón', 'valor': 80000, 'deposito_garantia': 50000,
         'descripcion': 'Capacidad máx. 80 personas. Horario: 8am - 11pm. Incluye sillas y mesas.'},
        {'zona': 'BBQ', 'valor': 40000, 'deposito_garantia': 30000,
         'descripcion': 'Capacidad máx. 20 personas. Horario: 9am - 8pm. Aseo no incluido.'},
        {'zona': 'Piscina', 'valor': 0, 'deposito_garantia': 0,
         'descripcion': 'Uso libre para residentes. Horario: 7am - 8pm.'},
    ]
    for zd in zonas_default:
        TarifaZona.objects.get_or_create(zona=zd['zona'], defaults=zd)
    
    tarifas = TarifaZona.objects.all()
    return render(request, 'reservas/tarifario.html', {'tarifas': tarifas})


@login_required
def editar_tarifa(request, tarifa_id):
    """Actualiza el precio de una zona vía POST."""
    tarifa = get_object_or_404(TarifaZona, id=tarifa_id)
    if request.method == 'POST':
        try:
            tarifa.valor = int(request.POST.get('valor', tarifa.valor))
            tarifa.deposito_garantia = int(request.POST.get('deposito_garantia', tarifa.deposito_garantia))
            tarifa.descripcion = request.POST.get('descripcion', tarifa.descripcion)
            tarifa.activa = request.POST.get('activa') == 'on'
            tarifa.save()
            messages.success(request, f"Tarifa de {tarifa.get_zona_display()} actualizada a ${tarifa.valor:,.0f}.")
        except (ValueError, TypeError) as e:
            messages.error(request, f"Error al actualizar la tarifa: {e}")
    return redirect('reservas:tarifario')

