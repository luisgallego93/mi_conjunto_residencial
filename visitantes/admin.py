from django.contrib import admin
from .models import Visitante
from django.utils import timezone

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    # CORRECCIÓN: Usamos 'hora_ingreso_real' que es el nombre nuevo en models.py
    list_display = ('nombre', 'tipo_visitante', 'apartamento_destino', 'estado', 'hora_ingreso_real')
    list_filter = ('estado', 'tipo_visitante', 'fecha_programada')
    search_fields = ('nombre', 'documento', 'placa', 'apartamento_destino__numero')

    fieldsets = (
        ('Datos del Visitante', {'fields': ('nombre', 'documento', 'tipo_visitante', 'motivo_visita')}),
        ('Destino y Autorización', {'fields': ('apartamento_destino', 'autorizado_por')}),
        ('Vehículo', {'fields': ('tipo_vehiculo', 'placa', 'cupo_asignado')}),
        ('Control de Portería', {'fields': ('estado', 'observaciones_vigilancia')}),
    )

    def save_model(self, request, obj, form, change):
        # Asignar automáticamente el portero/admin que registra
        if not obj.pk:
            obj.registrado_por = request.user

        # Lógica de tiempos reales según estado
        if obj.estado == 'Dentro' and not obj.hora_ingreso_real:
            obj.hora_ingreso_real = timezone.now()
        elif obj.estado == 'Salió' and not obj.hora_salida_real:
            obj.hora_salida_real = timezone.now()

        super().save_model(request, obj, form, change)
