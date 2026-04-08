from django import forms
from .models import Comunicacion

class ComunicacionForm(forms.ModelForm):
    class Meta:
        model = Comunicacion
        # Solo pediremos estos campos al usuario que radica la solicitud
        fields = ['tipo', 'titulo', 'descripcion', 'prioridad', 'solicitante', 'zona_afectada', 'ubicacion_especifica', 'imagen_evidencia']
        
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Fuga de agua en el baño'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe detalladamente la situación...'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'solicitante': forms.Select(attrs={'class': 'form-select'}),
            'zona_afectada': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_especifica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Apartamento 301. Zona lavandería.'}),
            'imagen_evidencia': forms.FileInput(attrs={'class': 'form-control'}),
        }
