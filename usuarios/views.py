from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PerfilUsuario, Apartamento

@login_required
def directorio_residentes(request):
    """
    Vista encargada de listar todos los perfiles de usuario del sistema (Residentes y Personal).
    Extrae la data completa incluyendo información de emergencia.
    """
    residentes = PerfilUsuario.objects.all().order_by('nombre_completo')
    return render(request, 'usuarios/directorio_residentes.html', {'residentes': residentes})

@login_required
def directorio_apartamentos(request):
    """
    Lista el censo total de los inmuebles (Bienes Privados) del complejo.
    Carga también a todos los residentes disponibles para mostrarlos en el modal de asignación.
    """
    apartamentos = Apartamento.objects.select_related('residente_principal').order_by('torre', 'numero')
    todos_residentes = PerfilUsuario.objects.filter(activo=True).order_by('nombre_completo')
    return render(request, 'usuarios/directorio_apartamentos.html', {
        'apartamentos': apartamentos,
        'todos_residentes': todos_residentes
    })

@login_required
def vincular_residente(request, apto_id):
    """
    Asigna un residente como propietario/inquilino principal a un apartamento, 
    gestionando la relación de llave foránea desde la interfaz y sin entrar al Admin.
    """
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apto_id)
        residente_id = request.POST.get('residente_id')
        
        if residente_id:
            residente = get_object_or_404(PerfilUsuario, id=residente_id)
            apto.residente_principal = residente
            apto.save()
            messages.success(request, f"Se ha vinculado correctamente a {residente.nombre_completo} al Apartamento {apto.numero}.")
        else:
            messages.error(request, "Debe seleccionar un residente válido.")
@login_required
def editar_residente(request, residente_id):
    """
    Controlador para actualizar la ficha básica de un residente 
    sin salir del frontend.
    """
    if request.method == 'POST':
        r = get_object_or_404(PerfilUsuario, id=residente_id)
        r.telefono = request.POST.get('telefono', r.telefono)
        r.email_personal = request.POST.get('email_personal', r.email_personal)
        r.emergencia_nombre = request.POST.get('emergencia_nombre', r.emergencia_nombre)
        r.emergencia_telefono = request.POST.get('emergencia_telefono', r.emergencia_telefono)
        r.tipo_ocupacion = request.POST.get('tipo_ocupacion', r.tipo_ocupacion)
        r.save()
        messages.success(request, f"¡Perfil de {r.nombre_completo} actualizado correctamente!")
    return redirect('usuarios:directorio_residentes')
