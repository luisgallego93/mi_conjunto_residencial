from django import forms
from .models import Visitante

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombre', 'documento', 'tipo_visitante', 'motivo_visita', 'apartamento_destino', 'autorizado_por_nombre', 'tipo_vehiculo', 'placa', 'foto_visitante']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del visitante o domiciliario'}),
            'documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula o NIT'}),
            'tipo_visitante': forms.Select(attrs={'class': 'form-select'}),
            'motivo_visita': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcional'}),
            'apartamento_destino': forms.Select(attrs={'class': 'form-select'}),
            'autorizado_por_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de quien autoriza'}),
            'tipo_vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'placa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco si no aplica'}),
            'foto_visitante': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_vehiculo'].required = False
        self.fields['tipo_vehiculo'].initial = 'Ninguno'
        self.fields['autorizado_por_nombre'].required = True
