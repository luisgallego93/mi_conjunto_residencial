"""
Descripción General: Controladores para la recepción y entrega de paquetería en portería.
Módulo: correspondencia
Propósito del archivo: Gestionar la bitácora de paquetes, permitiendo el registro de ingresos y la confirmación de retiro por parte de los residentes.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Paquete
from .forms import PaqueteForm

def _get_apartamento_del_usuario(user):
    """
    Helper de utilidades.

    Qué hace:
        Identifica la unidad residencial asociada al perfil del usuario autenticado.

    Parámetros:
        user: Instancia de User.

    Valor de retorno:
        Apartamento/None: Instancia del apartamento si se encuentra.
    """
    try:
        from usuarios.models import Apartamento, PerfilUsuario
        perfil = user.perfilusuario
        return Apartamento.objects.filter(
            Q(propietario=perfil) | Q(inquilino=perfil) | Q(residente_principal=perfil)
        ).first()
    except Exception:
        return None

@login_required
def lista_paquetes(request):
    """
    Panel de Control de Correspondencia.

    Qué hace:
        Muestra el listado de paquetes filtrado por estado y fecha.
        - Residentes: Visualizan solo lo pendiente por retirar en su unidad.
        - Administración/Portería: Gestionan el inventario completo de la bodega.
    """
    es_residente = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    if es_residente:
        apartamento = _get_apartamento_del_usuario(request.user)
        if apartamento:
            paquetes = Paquete.objects.filter(apartamento=apartamento).order_by('estado', '-fecha_recepcion')
        else:
            paquetes = Paquete.objects.none()
    else:
        paquetes = Paquete.objects.all().order_by('estado', '-fecha_recepcion')

    return render(request, 'correspondencia/lista.html', {
        'paquetes': paquetes,
        'es_residente': es_residente,
    })

@login_required
def recibir_paquete(request):
    """
    Registro de Entrada de Paquetería.

    Qué hace:
        Crea un nuevo registro de paquete en el sistema, estampa la hora de recepción
        y vincula al operador de portería responsable del ingreso.
    """
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
    """
    Proceso de Salida / Entrega Final.

    Qué hace:
        Cambia el estado del paquete a 'Entregado', registra quién retira físicamente
        y libera el espacio en la bitácora de pendientes de portería.
    """
    if request.method == 'POST':
        paquete = get_object_or_404(Paquete, id=paquete_id)
        if paquete.estado in ['Recibido', 'Notificado']:
            quien_recoge = request.POST.get('quien_recoge', 'Residente/Autorizado')
            paquete.estado = 'Entregado'
            paquete.fecha_entrega = timezone.now()
            paquete.quien_recoge = quien_recoge
            paquete.entregado_por = request.user
            paquete.save()
    return redirect('correspondencia:lista_paquetes')
