from django import forms
from .models import Paquete

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['apartamento', 'transportadora', 'destinatario', 'guia', 'observaciones']

        widgets = {
            'apartamento': forms.Select(attrs={'class': 'form-select'}),
            'transportadora': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Servientrega, MercadoLibre, Amazon'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A quién va dirigido el paquete'}),
            'guia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nro. de tracking o guía (Opcional)'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Caja grande, frágil, etc. (Opcional)'}),
        }
