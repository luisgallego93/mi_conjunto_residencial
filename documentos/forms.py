from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'categoria', 'archivo']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Manual de Convivencia 2026'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Opcional'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        }
