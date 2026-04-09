from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from .models import PerfilUsuario, Apartamento, Ocupante

def sync_residente_principal(apto):
    """
    Sincronización Inteligente: El Inquilino tiene prioridad sobre el Propietario
    para ser el 'Residente Principal' (quien recibe paquetes y visitas).
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
    residentes = PerfilUsuario.objects.all().order_by('nombre_completo')
    todos_apartamentos = Apartamento.objects.select_related('propietario', 'inquilino').order_by('torre', 'numero')
    return render(request, 'usuarios/directorio_residentes.html', {
        'residentes': residentes,
        'todos_apartamentos': todos_apartamentos,
    })

@login_required
def directorio_apartamentos(request):
    apartamentos = Apartamento.objects.select_related('propietario', 'inquilino', 'residente_principal').order_by('torre', 'numero')
    todos_residentes = PerfilUsuario.objects.filter(activo=True).order_by('nombre_completo')
    return render(request, 'usuarios/directorio_apartamentos.html', {
        'apartamentos': apartamentos,
        'todos_residentes': todos_residentes
    })

@login_required
def registrar_residente(request):
    """
    Crea un nuevo Usuario + Perfil desde el frontend y opcionalmente lo vincula
    a un apartamento, todo en un solo paso.
    El username y contraseña inicial = número de documento (CC).
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        doc = request.POST.get('documento', '').strip()
        tipo = request.POST.get('tipo_ocupacion', 'Propietario')
        tel = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        apto_id = request.POST.get('apto_id', '').strip()

        # Determinar el rol de sistema según el tipo de persona
        # Residentes y vigilancia tienen su propio rol
        rol_sistema = request.POST.get('rol', 'RESIDENTE')

        if not nombre or not doc:
            messages.error(request, "Nombre y Número de Documento son obligatorios.")
            return redirect('usuarios:directorio_residentes')

        try:
            with transaction.atomic():
                if User.objects.filter(username=doc).exists():
                    messages.error(request, f"Ya existe un usuario con el documento {doc}. Verifique antes de continuar.")
                    return redirect('usuarios:directorio_residentes')

                # Crear usuario Django (username = CC, contraseña inicial = CC)
                user = User.objects.create_user(username=doc, password=doc, email=email or '')
                user.first_name = nombre.split(' ')[0]
                user.last_name = ' '.join(nombre.split(' ')[1:]) if len(nombre.split(' ')) > 1 else ''
                user.save()

                # Crear perfil extendido
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

                # Vincular al apartamento si se seleccionó uno
                if apto_id:
                    try:
                        apto = Apartamento.objects.get(id=apto_id)
                        if tipo == 'Propietario':
                            apto.propietario = perfil
                        else:
                            apto.inquilino = perfil
                        sync_residente_principal(apto)  # Tambien guarda el apto
                        messages.success(
                            request,
                            f"✅ {nombre} registrado y vinculado al Apto {apto.numero} como {tipo}. "
                            f"🔑 Usuario para ingresar: {doc}  |  Contraseña inicial: {doc}"
                        )
                    except Apartamento.DoesNotExist:
                        messages.warning(request, f"✅ {nombre} creado, pero el apartamento seleccionado no existe. Vincúlalo manualmente.")
                else:
                    messages.success(
                        request,
                        f"✅ {nombre} registrado correctamente. "
                        f"🔑 Usuario: {doc}  |  Contraseña inicial: {doc}"
                    )
        except Exception as e:
            messages.error(request, f"Error al registrar: {str(e)}")

    return redirect('usuarios:directorio_residentes')

@login_required
def vincular_residente(request, apto_id):
    """
    Vincula a un residente (buscado por Cédula) a un apartamento.
    El rol (Propietario/Inquilino) se toma del tipo_ocupacion del perfil,
    evitando preguntar dos veces.
    """
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apto_id)
        cedula = request.POST.get('cedula_buscar', '').strip()

        if not cedula:
            messages.error(request, "Debe ingresar un número de cédula para buscar.")
            return redirect('usuarios:directorio_apartamentos')

        try:
            residente = PerfilUsuario.objects.get(documento=cedula)
        except PerfilUsuario.DoesNotExist:
            messages.error(request, f"No se encontró ningún residente con cédula {cedula}. Regístrelo primero.")
            return redirect('usuarios:directorio_apartamentos')

        # Determinar el rol autómaticamente por el tipo de ocupación del perfil
        if residente.tipo_ocupacion == 'Propietario':
            apto.propietario = residente
            rol_texto = "Propietario"
        else:
            apto.inquilino = residente
            rol_texto = "Inquilino"

        sync_residente_principal(apto)
        messages.success(
            request,
            f"✅ {residente.nombre_completo} (CC: {cedula}) vinculado como {rol_texto} al Apto {apto.numero}."
        )

    return redirect('usuarios:directorio_apartamentos')

@login_required
def desvincular_residente(request, apto_id, rol):
    """
    Elimina la vinculación de propietario o inquilino de un apartamento.
    """
    apto = get_object_or_404(Apartamento, id=apto_id)
    if rol == 'propietario':
        apto.propietario = None
    elif rol == 'inquilino':
        apto.inquilino = None
    
    sync_residente_principal(apto)
    messages.warning(request, f"Se ha desvinculado al {rol} del Apto {apto.numero}.")
    return redirect('usuarios:directorio_apartamentos')

@login_required
def editar_residente(request, residente_id):
    if request.method == 'POST':
        r = get_object_or_404(PerfilUsuario, id=residente_id)
        r.telefono = request.POST.get('telefono', r.telefono)
        r.email_personal = request.POST.get('email_personal', r.email_personal)
        r.emergencia_nombre = request.POST.get('emergencia_nombre', r.emergencia_nombre)
        r.emergencia_telefono = request.POST.get('emergencia_telefono', r.emergencia_telefono)
        r.tipo_ocupacion = request.POST.get('tipo_ocupacion', r.tipo_ocupacion)
        r.save()
@login_required
def completar_perfil(request):
    """
    Wizard de Bienvenida: El residente completa su censo y cambia su clave inicial.
    """
    perfil = request.user.perfilusuario
    # Buscamos el apartamento vinculado (ya sea como propietario o inquilino)
    from django.db.models import Q
    apartamento = Apartamento.objects.filter(Q(propietario=perfil) | Q(inquilino=perfil)).first()

    if request.method == 'POST':
        # 1. Actualizar Datos Personales
        perfil.telefono = request.POST.get('telefono', perfil.telefono)
        perfil.email_personal = request.POST.get('email_personal', perfil.email_personal)
        perfil.emergencia_nombre = request.POST.get('emergencia_nombre', perfil.emergencia_nombre)
        perfil.emergencia_telefono = request.POST.get('emergencia_telefono', perfil.emergencia_telefono)
        
        # 2. Registrar Ocupantes (Censo)
        nombres = request.POST.getlist('ocu_nombre')
        parentescos = request.POST.getlist('ocu_parentesco')
        
        if apartamento:
            # Limpiamos ocupantes previos para evitar duplicados en re-intentos
            apartamento.habitantes.all().delete()
            for n, p in zip(nombres, parentescos):
                if n and p:
                    Ocupante.objects.create(
                        apartamento=apartamento,
                        nombre_completo=n,
                        parentesco=p
                    )

        # 3. Cambio de Contraseña (si se provee)
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 and pass1 == pass2:
            request.user.set_password(pass1)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

        # 4. Finalizar Onboarding
        perfil.primer_ingreso = False
        perfil.save()
        
        messages.success(request, "¡Gracias! Tu información y censo familiar han sido registrados correctamente.")
        return redirect('dashboard:index')

    return render(request, 'usuarios/completar_perfil.html', {
        'perfil': perfil,
        'apartamento': apartamento
    })
