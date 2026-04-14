"""
Descripción General: Controladores para la gestión de ingresos y salidas de visitantes.
Módulo: visitantes
Propósito del archivo: Administrar la bitácora de portería, registros de vehículos y autorizaciones de acceso.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Visitante
from .forms import VisitanteForm

def _get_apartamento_del_usuario(user):
    """
    Helper de utilidades.

    Qué hace:
        Identifica el apartamento asociado al perfil del usuario autenticado,
        buscando coincidencia como propietario, residente o inquilino.

    Parámetros:
        user: Instancia de User.

    Valor de retorno:
        Apartamento/None: Instancia de Apartamento si existe.
    """
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
    Consola de Bitácora de Portería.

    Qué hace:
        Muestra el historial de visitas. Restringe la vista por privacidad:
        - Residentes: solo ven sus propias visitas.
        - Staff/Vigilancia: ven el consolidado de todo el conjunto.
    """
    es_residente = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    if es_residente:
        apartamento = _get_apartamento_del_usuario(request.user)
        if apartamento:
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
    Control de Ingreso Manual.

    Qué hace:
        Registra la entrada de una persona al conjunto. Captura tiempos reales,
        registra el operador de portería y asocia la unidad de destino.
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

            # Lógica de pre-autorización por residente
            if es_res and apartamento_residente:
                visitante.apartamento_destino = apartamento_residente
                visitante.autorizado_por_nombre = request.user.perfilusuario.nombre_completo
                visitante.autorizado_por = request.user.perfilusuario

            visitante.save()
            messages.success(request, f"¡Ingreso autorizado con éxito para {visitante.nombre}!")
            return redirect('visitantes:lista_visitantes')
        else:
            messages.error(request, "Error de validación: Verifique los datos del visitante.")
    else:
        # Precargar datos si el residente es quien registra (auto-invitación)
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
    """
    Control de Egreso.

    Qué hace:
        Finaliza la visita registrando la estampa de tiempo de salida real.
    """
    visitante = get_object_or_404(Visitante, id=visitante_id)
    if visitante.estado == 'Dentro':
        visitante.estado = 'Salió'
        visitante.hora_salida_real = timezone.now()
        visitante.save()
        messages.success(request, f"Salida registrada para {visitante.nombre}.")
    return redirect('visitantes:lista_visitantes')
