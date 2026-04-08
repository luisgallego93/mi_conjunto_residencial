from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm

@login_required
def lista_reservas(request):
    reservas = Reserva.objects.all().order_by('-fecha')
    return render(request, 'reservas/lista.html', {'reservas': reservas})

@login_required
def crear_reserva(request):
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
                reserva.estado_reserva = 'Pendiente'
                reserva.save()
                messages.success(request, "Pre-reserva generada. Realice el pago o suba comprobante para su aprobación final.")
                return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm()
        
    import json
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
        'fechas_ocupadas': json.dumps(fechas_ocupadas)
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
            messages.info(request, "El comprobante de pago fue subido y esta en revision.")
    return redirect('reservas:lista_reservas')
