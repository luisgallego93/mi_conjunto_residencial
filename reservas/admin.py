from django.contrib import admin
from .models import ZonaComun, Reserva  # Traemos tus modelos

# Esto le dice a Django: "Muéstrame estas tablas en el panel"
admin.site.register(ZonaComun)
admin.site.register(Reserva)