from django import forms
from .models import Visitante

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombre', 'documento', 'tipo_visitante', 'motivo_visita', 'apartamento_destino', 'autorizado_por', 'tipo_vehiculo', 'placa', 'foto_visitante']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del visitante o domiciliario'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula o NIT'}),
            'tipo_visitante': forms.Select(attrs={'class': 'form-select'}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'apartamento_destino': forms.Select(attrs={'class': 'form-select'}),
            'autorizado_por': forms.Select(attrs={'class': 'form-select'}),
            'tipo_vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco si no aplica'}),
            'foto_visitante': forms.FileInput(attrs={'class': 'form-control'}),
        }
