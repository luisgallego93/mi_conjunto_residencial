"""
Descripción General: Controladores para la gestión de usuarios, perfiles y directorio.
Módulo: usuarios
Propósito del archivo: Gestionar el registro de residentes, vinculación a apartamentos, censo familiar y perfiles personales.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib.auth import update_session_auth_hash
from .models import PerfilUsuario, Apartamento, Ocupante

def sync_residente_principal(apto):
    """
    Sincronización Inteligente: Define quién es la cabeza de familia en el sistema.

    Qué hace:
        El Inquilino tiene prioridad sobre el Propietario para ser el 'Residente Principal'
        (quien recibe paquetes y visitas), asumiendo que es quien efectivamente vive allí.

    Parámetros:
        apto: Instancia del modelo Apartamento.
    """
    if apto.inquilino:
        apto.residente_principal = apto.inquilino
    elif apto.propietario:
        apto.residente_principal = apto.propietario
    else:
        apto.residente_principal = None
    apto.save()

@login_required
def directorio_residentes(request):
    """
    Lista maestra de todas las personas registradas en el sistema.

    Qué hace:
        Muestra el directorio de residentes para administración y vigilancia.
        Bloquea el acceso a residentes.

    Parámetros:
        request: Solicitud HTTP.

    Valor de retorno:
        Template renderizado con la lista de residentes.
    """
    if request.user.perfilusuario.rol == 'RESIDENTE':
        messages.warning(request, "Como residente, solo puedes ver tus propios datos en 'Mi Perfil'.")
        return redirect('usuarios:mi_perfil')

    residentes = PerfilUsuario.objects.all().order_by('nombre_completo')
    todos_apartamentos = Apartamento.objects.select_related('propietario', 'inquilino').order_by('torre', 'numero')
    return render(request, 'usuarios/directorio_residentes.html', {
        'residentes': residentes,
        'todos_apartamentos': todos_apartamentos,
    })

@login_required
def directorio_apartamentos(request):
    """
    Inventario de inmuebles y sus estados de ocupación.

    Qué hace:
        Presenta la lista de los 460 apartamentos del conjunto, mostrando quién es el
        propietario o inquilino actual.

    Parámetros:
        request: Solicitud HTTP.
    """
    apartamentos = Apartamento.objects.select_related('propietario', 'inquilino', 'residente_principal').order_by('torre', 'numero')
    todos_residentes = PerfilUsuario.objects.filter(activo=True).order_by('nombre_completo')
    return render(request, 'usuarios/directorio_apartamentos.html', {
        'apartamentos': apartamentos,
        'todos_residentes': todos_residentes
    })

@login_required
def registrar_residente(request):
    """
    Alta de nuevos usuarios en el ecosistema digital.

    Qué hace:
        Crea de forma atómica el User de Django y el PerfilUsuario local.
        Permite la vinculación inmediata a un apartamento.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        doc = request.POST.get('documento', '').strip()
        tipo = request.POST.get('tipo_ocupacion', 'Propietario')
        tel = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        apto_id = request.POST.get('apto_id', '').strip()
        rol_sistema = request.POST.get('rol', 'RESIDENTE')

        if not nombre or not doc:
            messages.error(request, "Nombre y Número de Documento son obligatorios.")
            return redirect('usuarios:directorio_residentes')

        try:
            with transaction.atomic():
                if User.objects.filter(username=doc).exists():
                    messages.error(request, f"Ya existe un usuario con el documento {doc}.")
                    return redirect('usuarios:directorio_residentes')

                # Creación de credenciales (User)
                user = User.objects.create_user(username=doc, password=doc, email=email or '')
                user.first_name = nombre.split(' ')[0]
                user.last_name = ' '.join(nombre.split(' ')[1:]) if len(nombre.split(' ')) > 1 else ''
                user.save()

                # Creación de metadatos (Perfil)
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    nombre_completo=nombre,
                    documento=doc,
                    rol=rol_sistema,
                    telefono=tel or '',
                    email_personal=email or '',
                    tipo_ocupacion=tipo,
                    primer_ingreso=True
                )

                # Vinculación lógica
                if apto_id:
                    try:
                        apto = Apartamento.objects.get(id=apto_id)
                        if tipo == 'Propietario':
                            apto.propietario = perfil
                        else:
                            apto.inquilino = perfil
                        sync_residente_principal(apto)
                        messages.success(request, f"¡Éxito! {nombre} vinculado como {tipo}.")
                    except Apartamento.DoesNotExist:
                        messages.warning(request, "Usuario creado, pero no se halló el apartamento.")
                else:
                    messages.success(request, f"✅ {nombre} registrado correctamente.")
        except Exception as e:
            messages.error(request, f"Error crítico: {str(e)}")

    return redirect('usuarios:directorio_residentes')

@login_required
def vincular_residente(request, apto_id):
    """
    Vínculo manual de un perfil existente a un inmueble.
    """
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apto_id)
        cedula = request.POST.get('cedula_buscar', '').strip()

        try:
            residente = PerfilUsuario.objects.get(documento=cedula)
            if residente.tipo_ocupacion == 'Propietario':
                apto.propietario = residente
            else:
                apto.inquilino = residente
            sync_residente_principal(apto)
            messages.success(request, f"✅ Vinculación completada.")
        except PerfilUsuario.DoesNotExist:
            messages.error(request, "No existe el residente. Regístrelo primero.")

    return redirect('usuarios:directorio_apartamentos')

@login_required
def desvincular_residente(request, apto_id, rol):
    """
    Ruptura de vínculo entre persona e inmueble.
    """
    apto = get_object_or_404(Apartamento, id=apto_id)
    if rol == 'propietario':
        apto.propietario = None
    elif rol == 'inquilino':
        apto.inquilino = None

    sync_residente_principal(apto)
    messages.warning(request, f"Se ha desvinculado al {rol}.")
    return redirect('usuarios:directorio_apartamentos')

@login_required
def editar_residente(request, residente_id):
    """Update de datos básicos de un residente."""
    if request.method == 'POST':
        r = get_object_or_404(PerfilUsuario, id=residente_id)
        r.telefono = request.POST.get('telefono', r.telefono)
        r.email_personal = request.POST.get('email_personal', r.email_personal)
        r.emergencia_nombre = request.POST.get('emergencia_nombre', r.emergencia_nombre)
        r.emergencia_telefono = request.POST.get('emergencia_telefono', r.emergencia_telefono)
        r.tipo_ocupacion = request.POST.get('tipo_ocupacion', r.tipo_ocupacion)
        r.save()
        messages.success(request, "Información actualizada.")
    return redirect('usuarios:directorio_residentes')

@login_required
def completar_perfil(request):
    """
    Asistente de primer ingreso (Onboarding).
    Permite al nuevo residente cambiar su clave y registrar a su familia.
    """
    perfil = request.user.perfilusuario
    apartamento = Apartamento.objects.filter(Q(propietario=perfil) | Q(inquilino=perfil)).first()

    if request.method == 'POST':
        perfil.telefono = request.POST.get('telefono', perfil.telefono)
        perfil.email_personal = request.POST.get('email_personal', perfil.email_personal)
        perfil.emergencia_nombre = request.POST.get('emergencia_nombre', perfil.emergencia_nombre)
        perfil.emergencia_telefono = request.POST.get('emergencia_telefono', perfil.emergencia_telefono)

        nombres = request.POST.getlist('ocu_nombre')
        parentescos = request.POST.getlist('ocu_parentesco')

        if apartamento:
            apartamento.habitantes.all().delete()
            for n, p in zip(nombres, parentescos):
                if n and p:
                    Ocupante.objects.create(apartamento=apartamento, nombre_completo=n, parentesco=p)

        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 and pass1 == pass2:
            request.user.set_password(pass1)
            request.user.save()
            update_session_auth_hash(request, request.user)

        perfil.primer_ingreso = False
        perfil.save()
        messages.success(request, "¡Configuración inicial terminada!")
        return redirect('dashboard:index')

    return render(request, 'usuarios/completar_perfil.html', {'perfil': perfil, 'apartamento': apartamento})

@login_required
def gestionar_familia(request):
    """ABM de miembros del núcleo familiar (Censo del apartamento)."""
    perfil = request.user.perfilusuario
    apartamento = Apartamento.objects.filter(Q(propietario=perfil) | Q(inquilino=perfil)).first()

    if not apartamento:
        messages.warning(request, "Sin apartamento vinculado.")
        return redirect('dashboard:index')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        parentesco = request.POST.get('parentesco')
        if nombre and parentesco:
            Ocupante.objects.create(
                apartamento=apartamento,
                nombre_completo=nombre,
                parentesco=parentesco,
                documento=request.POST.get('documento', ''),
                telefono=request.POST.get('telefono', ''),
                es_menor_edad=request.POST.get('es_menor') == 'on',
                edad=request.POST.get('edad') or None
            )
            messages.success(request, f"Agregado {nombre}.")
        return redirect('usuarios:gestionar_familia')

    return render(request, 'usuarios/gestionar_familia.html', {
        'apartamento': apartamento,
        'ocupantes': apartamento.habitantes.all()
    })

@login_required
def mi_perfil(request):
    """Vista de autogestión de perfil para residentes."""
    perfil = request.user.perfilusuario
    if request.method == 'POST':
        perfil.telefono = request.POST.get('telefono', perfil.telefono)
        perfil.email_personal = request.POST.get('email_personal', perfil.email_personal)
        perfil.emergencia_nombre = request.POST.get('emergencia_nombre', perfil.emergencia_nombre)
        perfil.emergencia_telefono = request.POST.get('emergencia_telefono', perfil.emergencia_telefono)
        perfil.save()
        request.user.email = perfil.email_personal
        request.user.save()
        messages.success(request, "Tus datos han sido actualizados.")
        return redirect('usuarios:mi_perfil')

    apartamento = Apartamento.objects.filter(Q(propietario=perfil) | Q(inquilino=perfil) | Q(residente_principal=perfil)).first()
    return render(request, 'usuarios/perfil.html', {'perfil': perfil, 'apartamento': apartamento})

@login_required
def eliminar_ocupante(request, ocupante_id):
    """Elimina integrante del censo familiar."""
    ocupante = get_object_or_404(Ocupante, id=ocupante_id)
    ocupante.delete()
    messages.warning(request, "Eliminado del censo familiar.")
    return redirect('usuarios:gestionar_familia')

@login_required
def alternar_estado_residente(request, residente_id):
    """Activación/Desactivación lógica de cuentas de usuario."""
    residente = get_object_or_404(PerfilUsuario, id=residente_id)
    nuevo_estado = not residente.user.is_active
    residente.user.is_active = nuevo_estado
    residente.user.save()
    residente.activo = nuevo_estado
    residente.save()
    messages.success(request, f"Perfil {residente.nombre_completo} actualizado.")
    return redirect('usuarios:directorio_residentes')
