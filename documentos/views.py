from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Documento
from .forms import DocumentoForm

@login_required
def lista_documentos(request):
    categoria = request.GET.get('categoria', '')
    if categoria:
        documentos = Documento.objects.filter(categoria=categoria)
    else:
        documentos = Documento.objects.all()
        
    categorias_disponibles = Documento.CATEGORIAS

    # Detectar si es residente (no admin ni staff)
    es_residente = False
    if hasattr(request.user, 'perfilusuario'):
        rol = request.user.perfilusuario.rol
        es_residente = rol == 'RESIDENTE'

    return render(request, 'documentos/lista.html', {
        'documentos': documentos,
        'categorias': categorias_disponibles,
        'categoria_activa': categoria,
        'puede_subir': not es_residente,  # Solo admin/vigilancia pueden subir
    })

@login_required
def subir_documento(request):
    # Residentes no pueden subir documentos
    if hasattr(request.user, 'perfilusuario'):
        if request.user.perfilusuario.rol == 'RESIDENTE':
            messages.error(request, "No tienes permisos para subir documentos.")
            return redirect('documentos:lista')

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento subido correctamente.")
            return redirect('documentos:lista')
    else:
        form = DocumentoForm()
        
    return render(request, 'documentos/crear.html', {'form': form})
