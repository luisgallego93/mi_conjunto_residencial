from django.contrib import admin
from .models import Paquete
from django.utils import timezone

@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    list_display = ('apartamento', 'transportadora', 'destinatario', 'estado', 'fecha_recepcion')
    list_filter = ('estado', 'transportadora')
    search_fields = ('apartamento__numero', 'destinatario', 'guia')
    
    actions = ['marcar_como_entregado']

    @admin.action(description="Marcar como ENTREGADO al residente")
    def marcar_como_entregado(self, request, queryset):
        queryset.update(
            estado='Entregado', 
            fecha_entrega=timezone.now(),
            observaciones="Retirado en portería"
        )
        self.message_user(request, "Paquetes marcados como entregados exitosamente.")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.recibido_por = request.user
        super().save_model(request, obj, form, change)
