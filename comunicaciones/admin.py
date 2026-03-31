from django.contrib import admin
from .models import Comunicado

@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridad', 'segmentacion', 'fecha_publicacion', 'esta_activo')
    list_filter = ('prioridad', 'segmentacion', 'esta_activo')
    search_fields = ('titulo', 'contenido')
    
    # Rellenar automáticamente el autor con el usuario logueado
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.autor = request.user
        super().save_model(request, obj, form, change)
