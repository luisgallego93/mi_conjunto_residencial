"""
Descripción General: Controladores para el centro de descarga de documentos oficiales.
Módulo: documentos
Propósito del archivo: Gestionar el listado, filtrado y carga de archivos institucionales (PDF) del conjunto residencial.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Documento
from .forms import DocumentoForm

@login_required
def lista_documentos(request):
    """
    Repositorio Digital de Documentos.

    Qué hace:
        Lista los archivos disponibles clasificados por categorías.
        Permite filtrar la vista para localizar rápidamente manuales o reglamentos.

    Parámetros:
        categoria (GET): Slug para filtrar el conjunto de documentos.
        orden (GET): 'desc' (más reciente) o 'asc' (más antiguo).
    """
    categoria = request.GET.get('categoria', '')
    orden = request.GET.get('orden', 'desc')
    
    if categoria:
        documentos = Documento.objects.filter(categoria=categoria)
    else:
        documentos = Documento.objects.all()

    # Aplicar ordenamiento dinámico
    if orden == 'asc':
        documentos = documentos.order_by('fecha_subida')
    else:
        documentos = documentos.order_by('-fecha_subida')

    categorias_disponibles = Documento.CATEGORIAS

    # Seguridad de rol: Residentes tienen acceso de solo lectura
    es_residente = False
    if hasattr(request.user, 'perfilusuario'):
        rol = request.user.perfilusuario.rol
        es_residente = rol == 'RESIDENTE'

    return render(request, 'documentos/lista.html', {
        'documentos': documentos,
        'categorias': categorias_disponibles,
        'categoria_activa': categoria,
        'orden_activo': orden,
        'puede_subir': not es_residente,
    })

@login_required
def subir_documento(request):
    """
    Gestor de Carga de Archivos.

    Qué hace:
        Permite al personal administrativo anexar nuevos documentos al repositorio.
        Valida que el usuario tenga privilegios suficientes y que el archivo sea PDF.
    """
    # Validación de privilegios
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'RESIDENTE':
        messages.error(request, "Acceso denegado: No tiene permisos de carga.")
        return redirect('documentos:lista')

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento publicado exitosamente en el repositorio.")
            return redirect('documentos:lista')
    else:
        form = DocumentoForm()

    return render(request, 'documentos/crear.html', {'form': form})
