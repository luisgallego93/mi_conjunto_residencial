from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notificacion(models.Model):
    TIPOS = [
        ('PQRS', 'Nueva PQRS'),
        ('RESERVA', 'Reserva Aprobada'),
        ('PAGO', 'Pago Pendiente'),
        ('PAQUETE', 'Paquete Recibido'),
        ('COMUNICADO', 'Nuevo Comunicado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tipo} para {self.usuario.username}"

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
