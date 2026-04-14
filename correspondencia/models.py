"""
Descripción General: Definición de modelos para la gestión de correspondencia y paquetería.
Módulo: correspondencia
Propósito del archivo: Registrar los paquetes recibidos en portería, gestionar sus estados y asegurar la trazabilidad de la entrega final.
"""

from django.db import models
from usuarios.models import Apartamento
from django.utils import timezone
from django.contrib.auth.models import User

class Paquete(models.Model):
    """
    Representa un paquete o sobre recibido en portería para un apartamento específico.
    """
    ESTADOS = [
        ('Recibido', 'Recibido en Portería'),
        ('Notificado', 'Residente Notificado'),
        ('Entregado', 'Entregado al Residente'),
        ('Devuelto', 'Devuelto a Transportadora'),
    ]

    # Datos de la Guía y Transportadora
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apto Destino")
    transportadora = models.CharField(max_length=50, help_text="Ej: Servientrega, Envía, Amazon")
    destinatario = models.CharField(max_length=100, verbose_name="Nombre en el paquete")
    guia = models.CharField(max_length=50, blank=True, verbose_name="Número de Guía")

    # Control de Ingreso (Portería)
    fecha_recepcion = models.DateTimeField(default=timezone.now)
    recibido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='paquetes_recibidos')

    # Ciclo de Vida y Entrega
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Recibido')
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    entregado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paquetes_entregados'
    )
    quien_recoge = models.CharField(max_length=100, blank=True, help_text="Nombre de quien retira el paquete")
    observaciones = models.TextField(blank=True)

    def __str__(self):
        """Retorna la transportadora y el número de apartamento de destino."""
        return f"{self.transportadora} - Apto {self.apartamento.numero}"

    class Meta:
        verbose_name = "Correspondencia"
        verbose_name_plural = "Correspondencia (Paquetes)"
