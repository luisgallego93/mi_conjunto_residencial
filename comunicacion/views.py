from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Comunicacion
from .forms import ComunicacionForm

def _es_residente(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'RESIDENTE'

@login_required
def lista_pqrs(request):
    es_res = _es_residente(request.user)
    
    # Parámetros de filtro
    estado_filtro = request.GET.get('estado')
    tipo_filtro = request.GET.get('tipo')
    search_q = request.GET.get('search')

    queryset = Comunicacion.objects.all()

    if es_res:
        queryset = queryset.filter(solicitante=request.user.perfilusuario)
    
    # Aplicar filtros adicionales
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
    es_res = _es_residente(request.user)

    if request.method == 'POST':
        form = ComunicacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            pqrs = form.save(commit=False)
            # Si es residente, el solicitante es él mismo automáticamente
            if es_res:
                pqrs.solicitante = request.user.perfilusuario
            pqrs.save()
            messages.success(request, "PQRS radicada exitosamente.")
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
    pqrs = get_object_or_404(Comunicacion, id=pqrs_id)
    es_res = _es_residente(request.user)

    # El residente solo puede ver sus propias PQRS
    if es_res and pqrs.solicitante != request.user.perfilusuario:
        messages.error(request, "No tienes acceso a esta solicitud.")
        return redirect('comunicacion:lista_pqrs')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Bloqueo total si el caso está cerrado
        if pqrs.estado == 'Cerrado':
            messages.error(request, "Este caso está cerrado y no admite más interacciones.")
            return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)

        if action == 'cambiar_estado' and not es_res:
            # Solo admins pueden gestionar el estado
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in ['Resuelto', 'Cerrado', 'En Proceso', 'Abierto']:
                pqrs.estado = nuevo_estado
                pqrs.save()
                messages.success(request, f"Estado actualizado a {nuevo_estado}.")
        
        elif action == 'responder':
            # Tanto residentes (si es suyo) como admins pueden responder
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
                messages.success(request, "Respuesta registrada correctamente.")
        
        return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)

    return render(request, 'comunicacion/detalle.html', {
        'pqrs': pqrs,
        'es_residente': es_res,
    })
