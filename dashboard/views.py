from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Importamos los modelos de tus otras apps para alimentar el Dashboard
# Si alguna app no existe aún, el 'try' evitará que el sistema se rompa
try:
    from comunicaciones.models import PQRS, Comunicado
except ImportError:
    PQRS = Comunicado = None

try:
    from reservas.models import Reserva
except ImportError:
    Reserva = None

try:
    from finanzas.models import CuentaCobro
except ImportError:
    CuentaCobro = None

@login_required
def index(request):
    hoy = timezone.now().date()
    
    context = {
        'pqrs_abiertos': PQRS.objects.filter(estado='Abierto').count() if PQRS else 0,
        'reservas_hoy': Reserva.objects.filter(fecha=hoy) if Reserva else [],
        'total_morosidad': CuentaCobro.objects.filter(estado='Pendiente').count() if CuentaCobro else 0,
        'ultimos_comunicados': Comunicado.objects.all().order_by('-fecha_publicacion')[:3] if Comunicado else [],
    }
    # Apuntamos a la carpeta dashboard dentro de templates
    return render(request, 'dashboard/index.html', context)

@login_required
def informes(request):
    total_pqrs = PQRS.objects.count() if PQRS else 0
    context = {
        'total_pqrs': total_pqrs,
        'efectividad': 85.0, # Valor estático inicial para pruebas
    }
    return render(request, 'dashboard/informes.html', context)