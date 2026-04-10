from django import forms
from .models import Reserva, TarifaZona

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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'RESIDENTE':
            from usuarios.models import PerfilUsuario
            self.fields['solicitante'].queryset = PerfilUsuario.objects.filter(id=user.perfilusuario.id)
            self.fields['solicitante'].initial = user.perfilusuario
            self.fields['solicitante'].widget.attrs['readonly'] = True
            
        # Inyectar datos de tarifas directamente en los atributos de las opciones (choices)
        tarifas = {t.zona: t for t in TarifaZona.objects.all()}
        new_choices = []
        for val, label in self.fields['zona_comun'].choices:
            if not val: # Opción vacía ("---------")
                new_choices.append((val, label))
                continue
            
            tarifa = tarifas.get(val)
            attrs = {}
            if tarifa:
                attrs = {
                    'data-valor': int(tarifa.valor),
                    'data-deposito': int(tarifa.deposito_garantia),
                    'data-descripcion': tarifa.descripcion
                }
            # En Django, para meter atributos en opciones específicas, usualmente se hace en el template
            # o con un widget personalizado. Pero aquí usaremos un truco de JS más adelante.
            # Por ahora, aseguramos que las claves coincidan.
            new_choices.append((val, label))
        
        self.fields['zona_comun'].choices = new_choices

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
