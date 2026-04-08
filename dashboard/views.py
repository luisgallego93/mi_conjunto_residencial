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
    
    context = {
        'gran_total_mora': gran_total_mora,
        'cuentas_pendientes_count': cuentas_pendientes.count(),
        'pqrs_abiertos': pqrs_abiertos,
        'reservas_pendientes': reservas_pendientes,
        'visitantes_sitio': visitantes_sitio,
        'paquetes_porteria': paquetes_porteria,
        'aptos_registrados': aptos_registrados,
        'residentes_activos': residentes_activos,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def informes(request):
    # Vista en blanco para futuros desarrollos
    return render(request, 'dashboard/informes.html')