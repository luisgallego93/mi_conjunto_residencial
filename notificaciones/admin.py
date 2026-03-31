from django.contrib import admin
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    # Esto te permite ver qué se le ha enviado a quién
    list_display = ('usuario', 'tipo', 'mensaje', 'fecha_creacion', 'leida')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username', 'mensaje')
    readonly_fields = ('fecha_creacion',) # Para que nadie altere la fecha real