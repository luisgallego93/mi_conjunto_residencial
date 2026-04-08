from django.db import models
from usuarios.models import Apartamento
from django.utils import timezone
from django.contrib.auth.models import User

class Paquete(models.Model):
    ESTADOS = [
        ('Recibido', 'Recibido en Portería'),
        ('Notificado', 'Residente Notificado'),
        ('Entregado', 'Entregado al Residente'),
        ('Devuelto', 'Devuelto a Transportadora'),
    ]

    # Datos del Paquete
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apto Destino")
    transportadora = models.CharField(max_length=50, help_text="Ej: Servientrega, Envia, Amazon")
    destinatario = models.CharField(max_length=100, verbose_name="Nombre en el paquete")
    guia = models.CharField(max_length=50, blank=True, verbose_name="Número de Guía")
    
    # Control de Portería
    fecha_recepcion = models.DateTimeField(default=timezone.now)
    recibido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='paquetes_recibidos')
    
    # Entrega al Residente
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Recibido')
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    entregado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paquetes_entregados')
    quien_recoge = models.CharField(max_length=100, blank=True, help_text="Nombre de quien retira el paquete")
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.transportadora} - Apto {self.apartamento.numero}"

    class Meta:
        verbose_name = "Correspondencia"
        verbose_name_plural = "Correspondencia (Paquetes)"