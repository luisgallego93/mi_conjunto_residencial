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
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva creada con éxito.")
            return redirect('reservas:lista_reservas')
    else:
        form = ReservaForm()
        
    return render(request, 'reservas/crear.html', {'form': form})

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

