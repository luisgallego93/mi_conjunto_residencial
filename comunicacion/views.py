from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comunicacion
from .forms import ComunicacionForm

@login_required
def lista_pqrs(request):
    comunicaciones = Comunicacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'comunicacion/lista.html', {'comunicaciones': comunicaciones})

@login_required
def crear_pqrs(request):
    if request.method == 'POST':
        form = ComunicacionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "PQRS radicada exitosamente.")
            return redirect('comunicacion:lista_pqrs')
    else:
        form = ComunicacionForm()
    
    return render(request, 'comunicacion/crear.html', {'form': form})

@login_required
def ver_pqrs(request, pqrs_id):
    pqrs = get_object_or_404(Comunicacion, id=pqrs_id)
    
    if request.method == 'POST':
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
                messages.success(request, "Su respuesta ha sido registrada en el hilo de conversacion.")
        
        return redirect('comunicacion:ver_pqrs', pqrs_id=pqrs.id)
            
    return render(request, 'comunicacion/detalle.html', {'pqrs': pqrs})
