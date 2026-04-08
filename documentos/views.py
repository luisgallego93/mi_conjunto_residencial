from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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

    return render(request, 'documentos/lista.html', {
        'documentos': documentos,
        'categorias': categorias_disponibles,
        'categoria_activa': categoria
    })

@login_required
def subir_documento(request):
    # En un escenario real, validaríamos que el usuario es admin o de gestión
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento subido correctamente.")
            return redirect('documentos:lista')
    else:
        form = DocumentoForm()
        
    return render(request, 'documentos/crear.html', {'form': form})
