from django.db import models
from usuarios.models import Apartamento, PerfilUsuario
from django.utils import timezone
from django.contrib.auth.models import User

class Visitante(models.Model):
    # Estados y Tipos mejorados para trazabilidad
    ESTADOS = [
        ('Programado', 'Programado'),
        ('Dentro', 'En Sitio / Dentro'),
        ('Salió', 'Salió'),
        ('Cancelado', 'Cancelado'),
        ('No llegó', 'No llegó'),
    ]
    
    TIPOS = [
        ('Familiar', 'Familiar'),
        ('Domiciliario', 'Domiciliario'),
        ('Técnico', 'Técnico'),
        ('Proveedor', 'Proveedor'),
        ('Ocasional', 'Visitante Ocasional'),
    ]

    # Datos del Visitante
    nombre = models.CharField(max_length=150, verbose_name="Nombre Completo")
    documento = models.CharField(max_length=20, verbose_name="Documento/ID")
    tipo_visitante = models.CharField(max_length=20, choices=TIPOS, default='Ocasional')
    motivo_visita = models.CharField(max_length=100, blank=True, help_text="Ej: Reparación, Entrega paquete")
    foto_visitante = models.ImageField(upload_to='visitantes/', null=True, blank=True, verbose_name="Fotografía")

    # Destino
    apartamento_destino = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    autorizado_por = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Vehículo
    tipo_vehiculo = models.CharField(
        max_length=20, 
        choices=[('Ninguno', 'Ninguno'), ('Carro', 'Carro'), ('Moto', 'Moto'), ('Bicicleta', 'Bicicleta')],
        default='Ninguno'
    )
    placa = models.CharField(max_length=10, blank=True)
    cupo_asignado = models.CharField(max_length=10, blank=True)

    # Control de Tiempos Reales
    fecha_programada = models.DateField(default=timezone.now)
    hora_ingreso_real = models.DateTimeField(null=True, blank=True)
    hora_salida_real = models.DateTimeField(null=True, blank=True)
    
    # Seguridad y Auditoría
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Programado')
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registros_porteria')
    observaciones_vigilancia = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.apartamento_destino}"

    class Meta:
        verbose_name = "Control de Acceso"
        verbose_name_plural = "Control de Acceso (Portería)"