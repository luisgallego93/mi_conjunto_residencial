from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # Así organizo las columnas de la lista principal
    list_display = ('documento', 'nombre_completo', 'torre', 'apartamento', 'rol', 'activo')
    search_fields = ('documento', 'nombre_completo', 'apartamento')
    list_filter = ('rol', 'torre', 'activo')

    # orden
    fieldsets = (
        ('Datos Básicos', {
            'fields': ('user', 'rol', 'activo')
        }),
        ('Datos Personales', {
            'fields': ('documento', 'nombre_completo', 'telefono', 'email_personal')
        }),
        ('Datos Residenciales', {
            'fields': ('torre', 'apartamento', 'tipo_ocupacion', 'fecha_ingreso')
        }),
        ('Contacto de Emergencia', {
            'fields': ('emergencia_nombre', 'emergencia_telefono', 'emergencia_parentesco')
        }),
        ('Configuración y Otros', {
            'fields': ('recibir_notificaciones', 'permitir_acceso_portal', 'observaciones')
        }),
    )