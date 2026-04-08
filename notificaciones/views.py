from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Importaciones directas de tus apps
from comunicaciones.models import PQRS, Comunicado
from reservas.models import Reserva
from finanzas.models import CuentaCobro
from visitantes.models import Visitante

@login_required
def dashboard_principal(request):
    hoy = timezone.now().date()
    
    context = {
        'pqrs_abiertos': PQRS.objects.filter(estado='Abierto').count(),
        'reservas_hoy': Reserva.objects.filter(fecha=hoy), 
        'total_morosidad': CuentaCobro.objects.filter(estado='Pendiente').count(),
        'visitantes_hoy': Visitante.objects.count(), 
        'ultimos_comunicados': Comunicado.objects.all().order_by('-fecha_publicacion')[:3],
    }
    return render(request, 'dashboard/index.html', context)