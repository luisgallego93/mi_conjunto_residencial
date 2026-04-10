from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Visitante
from .forms import VisitanteForm

def _get_apartamento_del_usuario(user):
    """Helper: retorna el apartamento del usuario."""
    try:
        from usuarios.models import Apartamento
        perfil = user.perfilusuario
        return Apartamento.objects.filter(
            Q(propietario=perfil) | Q(inquilino=perfil) | Q(residente_principal=perfil)
        ).first()
    except Exception:
        return None

@login_required
def lista_visitantes(request):
    """
    Controlador Principal del Módulo de Portería.
    Residentes: solo ven visitas a su apartamento.
    Administradores y vigilancia: ven todo el historial.
    """
    es_residente = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    if es_residente:
        apartamento = _get_apartamento_del_usuario(request.user)
        if apartamento:
            # El campo apartamento_destino es ForeignKey → filtro exacto por objeto
            visitantes = Visitante.objects.filter(
                apartamento_destino=apartamento
            ).order_by('-hora_ingreso_real', '-fecha_programada')
        else:
            visitantes = Visitante.objects.none()
    else:
        visitantes = Visitante.objects.all().order_by('-hora_ingreso_real', '-fecha_programada')

    return render(request, 'visitantes/lista.html', {
        'visitantes': visitantes,
        'es_residente': es_residente,
    })

@login_required
def registrar_visitante(request):
    """
    Portería registra visitantes. Si es residente, el apartamento destino y
    la voz de autorización se asignan automáticamente de su perfil.
    """
    es_res = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'
    apartamento_residente = None

    if es_res:
        apartamento_residente = _get_apartamento_del_usuario(request.user)

    if request.method == 'POST':
        form = VisitanteForm(request.POST, request.FILES)

        if form.is_valid():
            visitante = form.save(commit=False)
            visitante.estado = 'Dentro'
            visitante.hora_ingreso_real = timezone.now()
            visitante.registrado_por = request.user

            if es_res and apartamento_residente:
                visitante.apartamento_destino = apartamento_residente
                visitante.autorizado_por_nombre = request.user.perfilusuario.nombre_completo
                visitante.autorizado_por = request.user.perfilusuario
            # Si no es residente (es portero/admin), el valor de autorizado_por_nombre 
            # ya se toma automáticamente del formulario al hacer form.save(commit=False)
            # si el campo está en el modelo y en el formulario.

            visitante.save()
            messages.success(request, f"Ingreso autorizado para {visitante.nombre}.")
            return redirect('visitantes:lista_visitantes')
        else:
            messages.error(request, "Hubo un error al procesar el ingreso. Por favor verifica los campos.")
    else:
        initial = {}
        if es_res and apartamento_residente:
            initial['apartamento_destino'] = apartamento_residente.id
            initial['autorizado_por_nombre'] = request.user.perfilusuario.nombre_completo
        form = VisitanteForm(initial=initial)

    return render(request, 'visitantes/crear.html', {
        'form': form,
        'es_residente': es_res,
        'apartamento_residente': apartamento_residente,
    })

@login_required
def registrar_salida(request, visitante_id):
    visitante = get_object_or_404(Visitante, id=visitante_id)
    if visitante.estado == 'Dentro':
        visitante.estado = 'Salió'
        visitante.hora_salida_real = timezone.now()
        visitante.save()
    return redirect('visitantes:lista_visitantes')
