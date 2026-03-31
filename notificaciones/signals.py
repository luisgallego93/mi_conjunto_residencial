from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notificacion
from django.contrib.auth.models import User

# --- IMPORTACIONES PROTEGIDAS ---
try:
    from correspondencia.models import Paquete
except ImportError:
    Paquete = None

try:
    from finanzas.models import CuentaCobro, Multa
except ImportError:
    CuentaCobro = Multa = None

try:
    from reservas.models import Reserva
except ImportError:
    Reserva = None

try:
    # Aquí ya incluimos PQRS y Comunicado
    from comunicaciones.models import PQRS, Comunicado
except ImportError:
    PQRS = Comunicado = None

try:
    from visitantes.models import Visitante
except ImportError:
    Visitante = None

# --- SENSOR MAESTRO ---
@receiver(post_save)
def notificador_maestro(sender, instance, created, **kwargs):
    if not created:
        return

    user = None
    # Lógica para encontrar al residente
    if hasattr(instance, 'apartamento') and instance.apartamento and instance.apartamento.residente_principal:
        user = instance.apartamento.residente_principal.user
    elif hasattr(instance, 'usuario'):
        user = instance.usuario
    elif hasattr(instance, 'autor'): # Para el modelo Comunicado
        user = instance.autor

    if not user:
        return

    # 1. Correspondencia
    if Paquete and isinstance(instance, Paquete):
        Notificacion.objects.create(usuario=user, tipo='PAQUETE', mensaje=f"Paquete de {instance.transportadora} recibido en porteria.")
    
    # 2. Finanzas
    elif (CuentaCobro and isinstance(instance, CuentaCobro)) or (Multa and isinstance(instance, Multa)):
        Notificacion.objects.create(usuario=user, tipo='PAGO', mensaje="Se ha generado un nuevo registro financiero.")
    
    # 3. Reservas
    elif Reserva and isinstance(instance, Reserva):
        Notificacion.objects.create(usuario=user, tipo='RESERVA', mensaje=f"Reserva de {instance.espacio_comun} registrada.")

    # 4. Visitantes
    elif Visitante and isinstance(instance, Visitante):
        Notificacion.objects.create(usuario=user, tipo='COMUNICADO', mensaje=f"Ingreso de visitante: {instance.nombre_visitante}.")

    # 5. PQRS (NUEVO)
    elif PQRS and isinstance(instance, PQRS):
        Notificacion.objects.create(usuario=user, tipo='PQRS', mensaje=f"Tu {instance.tipo} ha sido radicada exitosamente.")

    # 6. Comunicados (NUEVO)
    elif Comunicado and isinstance(instance, Comunicado):
        Notificacion.objects.create(usuario=user, tipo='COMUNICADO', mensaje=f"Nuevo aviso publicado: {instance.titulo}")