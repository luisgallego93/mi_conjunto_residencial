from django.contrib import admin
from .models import Solicitud # Aquí importo el modelo que acabo de crear

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    # Aquí elijo qué columnas quiero ver en mi tabla principal
    list_display = ('prioridad', 'tipo', 'titulo', 'fecha_creacion', 'estado')
    
    # Añado filtros a la derecha para que yo pueda buscar rápido por urgencia o tipo
    list_filter = ('prioridad', 'tipo', 'estado')
    
    # También agrego un buscador por si tengo muchas solicitudes
    search_fields = ('titulo', 'descripcion')