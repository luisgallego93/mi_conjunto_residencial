from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Visitante
from .forms import VisitanteForm

@login_required
def lista_visitantes(request):
    """
    Controlador Principal del Módulo de Portería.
    Renderiza el listado histórico y en vivo de los visitantes que han ingresado al Conjunto.
    Filtra los registros ordenándolos desde los más recientes hasta los más antiguos.
    """
    # Hoy y los que aún están adentro desde ayer
    visitantes = Visitante.objects.all().order_by('-hora_ingreso_real', '-fecha_programada')
    return render(request, 'visitantes/lista.html', {'visitantes': visitantes})

@login_required
def registrar_visitante(request):
    """
    Procesa el formulario de entrada de un nuevo visitante/domiciliario.
    Captura los datos del formulario, inyecta la hora exacta del servidor como 'hora_ingreso_real'
    y define al usuario logueado (ej. el Guarda en turno) como el registrador autorizado.
    """
    if request.method == 'POST':
        form = VisitanteForm(request.POST, request.FILES)
        if form.is_valid():
            visitante = form.save(commit=False)
            visitante.estado = 'Dentro'
            visitante.hora_ingreso_real = timezone.now()
            visitante.registrado_por = request.user
            visitante.save()
            return redirect('visitantes:lista_visitantes')
    else:
        form = VisitanteForm()
    return render(request, 'visitantes/crear.html', {'form': form})

@login_required
def registrar_salida(request, visitante_id):
    visitante = get_object_or_404(Visitante, id=visitante_id)
    if visitante.estado == 'Dentro':
        visitante.estado = 'Salió'
        visitante.hora_salida_real = timezone.now()
        visitante.save()
    return redirect('visitantes:lista_visitantes')
