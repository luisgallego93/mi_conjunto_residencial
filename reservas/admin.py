from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    # 1. Quitamos el campo de la vista del formulario
    exclude = ('solicitante',)

    # 2. Elegimos qué columnas ver en la lista principal
    list_display = ('zona_comun', 'solicitante', 'fecha', 'estado_reserva', 'estado_pago')

    # 3. La MAGIA: Capturar el usuario de la sesión
    def save_model(self, request, obj, form, change):
        # Si la reserva es nueva y no tiene solicitante...
        if not obj.solicitante:
            # Buscamos el PerfilUsuario vinculado al usuario que está logueado (request.user)
            try:
                obj.solicitante = request.user.perfilusuario
            except:
                pass # Por si el admin no tiene perfil creado aún
        super().save_model(request, obj, form, change)