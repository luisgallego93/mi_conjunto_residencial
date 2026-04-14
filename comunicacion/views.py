"""
Descripción General: Controladores para la gestión de PQRS y comunicaciones oficiales.
Módulo: comunicacion
Propósito del archivo: Administrar el ciclo de vida de las solicitudes (Radicación -> Seguimiento -> Resolución).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Comunicacion
from .forms import ComunicacionForm

def _es_residente(user):
    """Verifica si el usuario autenticado tiene rol de RESIDENTE."""
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'RESIDENTE'

@login_required
def lista_pqrs(request):
    """
    Consola de Seguimiento de PQRS.

    Qué hace:
        Muestra la lista de requerimientos. Filtra por estado, tipo y búsqueda textual.
        Aplica restricciones de privacidad: los residentes solo ven sus radicados.
    """
    es_res = _es_residente(request.user)

    # Captura de parámetros de filtrado
    estado_filtro = request.GET.get('estado')
    tipo_filtro = request.GET.get('tipo')
    search_q = request.GET.get('search')

    queryset = Comunicacion.objects.all()

    if es_res:
        queryset = queryset.filter(solicitante=request.user.perfilusuario)

    # Procesamiento de filtros dinámicos
    if estado_filtro:
        queryset = queryset.filter(estado=estado_filtro)
    if tipo_filtro:
        queryset = queryset.filter(tipo=tipo_filtro)
    if search_q:
        queryset = queryset.filter(
            Q(titulo__icontains=search_q) |
            Q(numero_radicado__icontains=search_q) |
            Q(solicitante__nombre_completo__icontains=search_q)
        )

    comunicaciones = queryset.order_by('-fecha_creacion').prefetch_related(
        'solicitante__apartamentos_asignados',
        'solicitante__propiedades_asignadas',
        'solicitante__arrendamientos_asignados'
    )

    return render(request, 'comunicacion/lista.html', {
        'comunicaciones': comunicaciones,
        'es_residente': es_res,
        'filtros': {
            'estado': estado_filtro,
            'tipo': tipo_filtro,
            'search': search_q
        }
    })

@login_required
def crear_pqrs(request):
    """
    Radicación de Solicitudes.

    Qué hace:
        Permite a un residente o administrativo abrir un nuevo caso.
        Si es residente, los datos de contacto se asocian automáticamente.
    """
    es_res = _es_residente(request.user)

    if request.method == 'POST':
        form = ComunicacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            pqrs = form.save(commit=False)
            if es_res:
                pqrs.solicitante = request.user.perfilusuario
            pqrs.save()
            messages.success(request, f"Solicitud radicada bajo el número: {pqrs.numero_radicado}")
            return redirect('comunicacion:lista_pqrs')
    else:
        initial = {}
        if es_res:
            initial['solicitante'] = request.user.perfilusuario.id
        form = ComunicacionForm(initial=initial, user=request.user)

    return render(request, 'comunicacion/crear.html', {
        'form': form,
        'es_residente': es_res,
    })

@login_required
def ver_pqrs(request, pqrs_id):
    """
    Detalle y Seguimiento de Caso.

    Qué hace:
        Muestra la cronología de un radicado y permite el intercambio de mensajes (hilos).
        Administración puede cambiar el estado de la solicitud.
    """
    pqrs = get_object_or_404(Comunicacion, id=pqrs_id)
    es_res = _es_residente(request.user)

    # Validación de Acceso
    if es_res and pqrs.solicitante != request.user.perfilusuario:
        messages.error(request, "Acceso denegado a este radicado.")
        return redirect('comunicacion:lista_pqrs')

    if request.method == 'POST':
        action = request.POST.get('action')

        # Bloqueo por cierre de caso
        if pqrs.estado == 'Cerrado':
            messages.error(request, "El caso está cerrado.")
            return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)

        if action == 'cambiar_estado' and not es_res:
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in ['Resuelto', 'Cerrado', 'En Proceso', 'Abierto']:
                pqrs.estado = nuevo_estado
                pqrs.save()
                messages.success(request, f"Estado actualizado: {nuevo_estado}")

        elif action == 'responder':
            from .models import RespuestaPQRS
            mensaje = request.POST.get('mensaje')
            evidencia = request.FILES.get('evidencia')
            if mensaje:
                RespuestaPQRS.objects.create(
                    comunicacion=pqrs,
                    mensaje=mensaje,
                    autor=request.user,
                    evidencia=evidencia
                )
                messages.success(request, "Respuesta enviada.")

        return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)

    return render(request, 'comunicacion/detalle.html', {
        'pqrs': pqrs,
        'es_residente': es_res,
    })
