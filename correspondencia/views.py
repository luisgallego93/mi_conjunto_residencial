from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Paquete
from .forms import PaqueteForm

@login_required
def lista_paquetes(request):
    # Paquetes ordenados por los que están "Recibido" primero, luego historial.
    paquetes = Paquete.objects.all().order_by('estado', '-fecha_recepcion')
    return render(request, 'correspondencia/lista.html', {'paquetes': paquetes})

@login_required
def recibir_paquete(request):
    if request.method == 'POST':
        form = PaqueteForm(request.POST)
        if form.is_valid():
            paquete = form.save(commit=False)
            paquete.estado = 'Recibido'
            paquete.fecha_recepcion = timezone.now()
            paquete.recibido_por = request.user
            paquete.save()
            return redirect('correspondencia:lista_paquetes')
    else:
        form = PaqueteForm()
    return render(request, 'correspondencia/crear.html', {'form': form})

@login_required
def entregar_paquete(request, paquete_id):
    if request.method == 'POST':
        paquete = get_object_or_404(Paquete, id=paquete_id)
        if paquete.estado in ['Recibido', 'Notificado']:
            quien_recoge = request.POST.get('quien_recoge', 'Residente/Autorizado')
            paquete.estado = 'Entregado'
            paquete.fecha_entrega = timezone.now()
            paquete.quien_recoge = quien_recoge
            paquete.save()
    return redirect('correspondencia:lista_paquetes')
