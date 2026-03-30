from django.db import models
from usuarios.models import PerfilUsuario 

class Reserva(models.Model):
    # --- 1. DATOS DE LA RESERVA ---
    ZONAS = [('Salón', 'Salón Social'), ('BBQ', 'Zona BBQ'), ('Piscina', 'Piscina')]
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
    requiere_aseo = models.BooleanField(default=False)
    inventario_entregado = models.BooleanField(default=False)

    def __str__(self):
        # Usamos un condicional por si el solicitante aún no se ha asignado
        nombre = self.solicitante.nombre_completo if self.solicitante else "Sin asignar"
        return f"{self.zona_comun} - {nombre} ({self.fecha})"