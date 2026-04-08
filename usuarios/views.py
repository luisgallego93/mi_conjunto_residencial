from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario, Apartamento

@login_required
def directorio_residentes(request):
    residentes = PerfilUsuario.objects.all().order_by('nombre_completo')
    return render(request, 'usuarios/directorio_residentes.html', {'residentes': residentes})

@login_required
def directorio_apartamentos(request):
    apartamentos = Apartamento.objects.select_related('residente_principal').order_by('torre', 'numero')
    return render(request, 'usuarios/directorio_apartamentos.html', {'apartamentos': apartamentos})
