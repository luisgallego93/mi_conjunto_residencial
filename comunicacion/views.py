from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comunicacion
from .forms import ComunicacionForm

def _es_residente(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'RESIDENTE'

@login_required
def lista_pqrs(request):
    es_res = _es_residente(request.user)
    if es_res:
        # El residente solo ve sus propias PQRS
        comunicaciones = Comunicacion.objects.filter(
            solicitante=request.user.perfilusuario
        ).order_by('-fecha_creacion')
    else:
        comunicaciones = Comunicacion.objects.all().order_by('-fecha_creacion')

    return render(request, 'comunicacion/lista.html', {
        'comunicaciones': comunicaciones,
        'es_residente': es_res,
    })

@login_required
def crear_pqrs(request):
    es_res = _es_residente(request.user)

    if request.method == 'POST':
        form = ComunicacionForm(request.POST, request.FILES)
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
        form = ComunicacionForm(initial=initial)

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

    if request.method == 'POST' and not es_res:
        # Solo admins pueden gestionar el estado
        action = request.POST.get('action')
        if action == 'cambiar_estado':
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in ['Resuelto', 'Cerrado', 'En Proceso']:
                pqrs.estado = nuevo_estado
                pqrs.save()
                messages.success(request, f"Estado actualizado a {nuevo_estado}.")
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
                messages.success(request, "Su respuesta ha sido registrada.")
        return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)

    return render(request, 'comunicacion/detalle.html', {
        'pqrs': pqrs,
        'es_residente': es_res,
    })
