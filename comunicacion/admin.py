from django.contrib import admin
from .models import Comunicacion

@admin.register(Comunicacion)
class ComunicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'get_solicitante', 'prioridad', 'estado', 'area_responsable', 'fecha_creacion')
    list_filter = ('estado', 'tipo', 'prioridad', 'area_responsable')
    search_fields = ('titulo', 'solicitante__nombre_completo', 'solicitante__documento')

    fieldsets = (
        ('Datos de la Solicitud', {
            'fields': ('tipo', 'titulo', 'descripcion', 'prioridad')
        }),
        ('Información del Solicitante', {
            'fields': ('solicitante',)
        }),
        ('Ubicación del Problema', {
            'fields': ('zona_afectada', 'ubicacion_especifica')
        }),
        ('Gestión y Asignación', {
            'fields': ('area_responsable', 'asignado_a', 'estado')
        }),
        ('Control de Tiempos', {
            'fields': ('fecha_limite', 'fecha_cierre')
        }),
        ('Evidencias y Seguimiento', {
            'fields': ('imagen_evidencia', 'respuesta_residente', 'observaciones_internas')
        }),
    )

    def get_solicitante(self, obj):
        return obj.solicitante.nombre_completo
    get_solicitante.short_description = 'Residente'