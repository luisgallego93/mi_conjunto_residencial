from django.contrib import admin
from .models import PerfilUsuario, Apartamento

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    # Definimos qué columnas ver y cuál será el enlace principal
    list_display = ('id', 'mostrar_identificador', 'torre', 'piso', 'residente_principal')
    
    # Hacemos que el enlace principal sea nuestro nuevo identificador formateado
    list_display_links = ('mostrar_identificador',)
    
    list_filter = ('torre', 'piso')
    search_fields = ('numero', 'torre')

    # Función para mostrar un nombre claro en la lista (evita el "mi" o "do")
    @admin.display(description="Apartamento")
    def mostrar_identificador(self, obj):
        return f"Apartamento {obj.numero}"

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'documento', 'rol', 'activo')
    list_filter = ('rol', 'activo')
    search_fields = ('nombre_completo', 'documento')