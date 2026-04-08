from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['zona_comun', 'fecha', 'hora_inicio', 'hora_fin', 'asistentes', 'motivo', 'solicitante']
        
        widgets = {
            'zona_comun': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'asistentes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cumpleaños infantil'}),
            'solicitante': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        zona_comun = cleaned_data.get('zona_comun')

        if fecha and zona_comun:
            solapamiento = Reserva.objects.filter(
                fecha=fecha,
                zona_comun=zona_comun,
                estado_reserva='Aprobado'
            ).exists()
            
            if solapamiento:
                raise forms.ValidationError("Para la fecha seleccionada, este espacio ya se encuentra reservado y pagado por otro residente.")
                
        return cleaned_data
