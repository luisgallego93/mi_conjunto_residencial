from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# --- IMPORTACIONES PROTEGIDAS DE MODELOS ---
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

try:
    from visitantes.models import Visitante
except ImportError:
    Visitante = None

# --- VISTAS ---

@login_required
def dashboard_principal(request):
    hoy = timezone.now().date()
    
    context = {
        'pqrs_abiertos': PQRS.objects.filter(estado='Abierto').count() if PQRS else 0,
        'reservas_hoy': Reserva.objects.all() if Reserva else [], 
        'total_morosidad': CuentaCobro.objects.count() if CuentaCobro else 0,
        'visitantes_hoy': Visitante.objects.count() if Visitante else 0,
        'ultimos_comunicados': Comunicado.objects.all().order_by('-fecha_publicacion')[:3] if Comunicado else [],
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def generar_informes(request):
    total_pqrs = PQRS.objects.count() if PQRS else 0
    context = {
        'total_pqrs': total_pqrs,
    }
    return render(request, 'dashboard/informes.html', context)