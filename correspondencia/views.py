from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Paquete
from .forms import PaqueteForm

def _get_apartamento_del_usuario(user):
    """Helper: retorna el apartamento del usuario, buscando por nueva arquitectura y legado."""
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
    # Detectar si es residente
    es_residente = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE'

    if es_residente:
        # Solo muestra paquetes de su apartamento
        apartamento = _get_apartamento_del_usuario(request.user)
        if apartamento:
            paquetes = Paquete.objects.filter(apartamento=apartamento).order_by('estado', '-fecha_recepcion')
        else:
            paquetes = Paquete.objects.none()
    else:
        # Admins y vigilancia ven todo
        paquetes = Paquete.objects.all().order_by('estado', '-fecha_recepcion')

    return render(request, 'correspondencia/lista.html', {
        'paquetes': paquetes,
        'es_residente': es_residente,
    })

@login_required
def recibir_paquete(request):
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
