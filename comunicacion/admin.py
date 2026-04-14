from django.contrib import admin
from .models import Comunicacion

@admin.register(Comunicacion)
class ComunicacionAdmin(admin.ModelAdmin):
    # Esto quita el selector manual del formulario
    exclude = ('solicitante',)

    # Esto organiza las columnas que viste en tus imágenes
    list_display = ('tipo', 'titulo', 'mostrar_residente', 'estado', 'prioridad', 'fecha_creacion')

    def save_model(self, request, obj, form, change):
        # Si la PQRS es nueva, el sistema le asigna el usuario que está logueado
        if not change:
            obj.solicitante = request.user.perfilusuario
        super().save_model(request, obj, form, change)

    def mostrar_residente(self, obj):
        return obj.solicitante.nombre_completo
    mostrar_residente.short_description = 'Residente'
