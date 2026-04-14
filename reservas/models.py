"""
Descripción General: Definición de modelos para la gestión de reservas de zonas comunes.
Módulo: reservas
Propósito del archivo: Estructurar la base de datos para el control de disponibilidad, tarifas y estados de las zonas sociales (BBQ, Piscina, Salón).
"""

from django.db import models
from usuarios.models import PerfilUsuario

class Reserva(models.Model):
    """
    Representa una solicitud de uso de una zona común por parte de un residente.
    """
    ZONAS = [
        ('salon', 'Salón Social'),
        ('bbq', 'Zona BBQ'),
        ('piscina', 'Piscina')
    ]

    # Datos de la Reserva
    zona_comun = models.CharField(max_length=50, choices=ZONAS)
    fecha = models.DateField(verbose_name="Fecha de Reserva (Uso)")
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    asistentes = models.PositiveIntegerField(verbose_name="Número de asistentes")
    motivo = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    # Solicitante
    solicitante = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        verbose_name="Residente que solicita",
        null=True,
        blank=True
    )

    # Estado y Control Administrativo
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado')
    ]
    estado_reserva = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    aprobado_por = models.CharField(max_length=100, blank=True, verbose_name="Administrador que aprueba")

    # Información Financiera
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposito = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_pago = models.BooleanField(default=False, verbose_name="¿Está pagado?")
    comprobante_pago = models.FileField(
        upload_to='reservas/pagos/',
        null=True,
        blank=True,
        verbose_name="Recibo o Comprobante de Transacción"
    )

    # Parámetros de Servicio
    requiere_aseo = models.BooleanField(default=False)
    inventario_entregado = models.BooleanField(default=False)

    def __str__(self):
        """Retorna la zona, el solicitante y la fecha de la reserva."""
        nombre = self.solicitante.nombre_completo if self.solicitante else "Sin asignar"
        return f"{self.zona_comun} - {nombre} ({self.fecha})"


class TarifaZona(models.Model):
    """
    Configuración centralizada de precios y condiciones por zona común.
    """
    ZONAS = [
        ('salon', 'Salón Social'),
        ('bbq', 'Zona BBQ'),
        ('piscina', 'Piscina')
    ]

    zona = models.CharField(max_length=50, choices=ZONAS, unique=True, verbose_name="Zona Común")
    valor = models.DecimalField(
        max_digits=10, decimal_places=0, default=0,
        verbose_name="Tarifa de Uso ($)",
        help_text="Valor que debe pagar el residente por el uso de esta zona."
    )
    deposito_garantia = models.DecimalField(
        max_digits=10, decimal_places=0, default=0,
        verbose_name="Depósito de Garantía ($)",
        help_text="Valor reembolsable condicionado al buen uso del espacio."
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción / Condiciones",
        help_text="Capacidad, horarios, condiciones especiales, etc."
    )
    activa = models.BooleanField(default=True, verbose_name="¿Disponible para reservas?")

    def __str__(self):
        """Retorna el nombre de la zona y su tarifa vigente."""
        return f"{self.get_zona_display()} — ${self.valor:,.0f}"

    class Meta:
        verbose_name = "Tarifa de Zona"
        verbose_name_plural = "Tarifario de Zonas Comunes"
        ordering = ['zona']
