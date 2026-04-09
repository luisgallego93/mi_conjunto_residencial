from django.db import models
from usuarios.models import PerfilUsuario 

class Reserva(models.Model):
    # --- 1. DATOS DE LA RESERVA ---
    ZONAS = [('salon', 'Salón Social'), ('bbq', 'Zona BBQ'), ('piscina', 'Piscina')]
    zona_comun = models.CharField(max_length=50, choices=ZONAS)
    fecha = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    asistentes = models.PositiveIntegerField(verbose_name="Número de asistentes")
    motivo = models.CharField(max_length=200, blank=True)

    # --- 2. SOLICITANTE (Automatizado) ---
    # Permitimos null=True y blank=True para que el sistema lo llene solo al guardar
    solicitante = models.ForeignKey(
        PerfilUsuario, 
        on_delete=models.CASCADE, 
        verbose_name="Residente que solicita",
        null=True, 
        blank=True
    )

    # --- 3. ESTADO Y CONTROL ---
    ESTADOS = [('Pendiente', 'Pendiente'), ('Aprobado', 'Aprobado'), ('Rechazado', 'Rechazado')]
    estado_reserva = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    aprobado_por = models.CharField(max_length=100, blank=True, verbose_name="Administrador que aprueba")
    
    # --- 4. FINANCIERO Y CONTROL ---
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposito = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_pago = models.BooleanField(default=False, verbose_name="¿Está pagado?")
    comprobante_pago = models.FileField(upload_to='reservas/pagos/', null=True, blank=True, verbose_name="Recibo o Comprobante de Transacción")
    requiere_aseo = models.BooleanField(default=False)
    inventario_entregado = models.BooleanField(default=False)

    def __str__(self):
        # Usamos un condicional por si el solicitante aún no se ha asignado
        nombre = self.solicitante.nombre_completo if self.solicitante else "Sin asignar"
        return f"{self.zona_comun} - {nombre} ({self.fecha})"


class TarifaZona(models.Model):
    """
    Tarifario de Zonas Comunes — El administrador puede actualizar los precios
    desde el panel de gestión sin necesidad de tocar el código fuente.
    """
    ZONAS = [('salon', 'Salón Social'), ('bbq', 'Zona BBQ'), ('piscina', 'Piscina')]
    
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
        return f"{self.get_zona_display()} — ${self.valor:,.0f}"

    class Meta:
        verbose_name = "Tarifa de Zona"
        verbose_name_plural = "Tarifario de Zonas Comunes"
        ordering = ['zona']