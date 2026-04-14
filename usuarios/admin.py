from django.contrib import admin
from .models import PerfilUsuario, Apartamento, Ocupante

class OcupanteInline(admin.TabularInline):
    model = Ocupante
    extra = 1

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    # Definimos qué columnas ver y cuál será el enlace principal
    list_display = ('id', 'mostrar_identificador', 'torre', 'propietario', 'inquilino', 'residente_principal')

    # Hacemos que el enlace principal sea nuestro nuevo identificador formateado
    list_display_links = ('mostrar_identificador',)

    list_filter = ('torre', 'piso')
    search_fields = ('numero', 'torre', 'propietario__nombre_completo', 'inquilino__nombre_completo')
    inlines = [OcupanteInline]

    # Función para mostrar un nombre claro en la lista (evita el "mi" o "do")
    @admin.display(description="Apartamento")
    def mostrar_identificador(self, obj):
        return f"Apartamento {obj.numero}"

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'documento', 'rol', 'tipo_ocupacion', 'activo', 'primer_ingreso')
    list_filter = ('rol', 'tipo_ocupacion', 'activo', 'primer_ingreso')
    search_fields = ('nombre_completo', 'documento')

@admin.register(Ocupante)
class OcupanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'apartamento', 'parentesco', 'es_menor_edad')
    list_filter = ('es_menor_edad', 'parentesco')
    search_fields = ('nombre_completo', 'apartamento__numero')
