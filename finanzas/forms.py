from django import forms
from .models import Multa

class MultaForm(forms.ModelForm):
    class Meta:
        model = Multa
        fields = ['apartamento', 'tipo', 'descripcion', 'valor']
        widgets = {
            'apartamento': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej. Ruido excesivo a las 3 AM'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control font-weight-bold text-danger', 'placeholder': '100000'}),
        }
