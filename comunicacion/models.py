from django.db import models
from django.utils import timezone
from usuarios.models import PerfilUsuario 

class Comunicacion(models.Model):
    # --- 1. DATOS PRINCIPALES ---
    TIPOS = [
        ('Peticion', 'Petición'), ('Queja', 'Queja'), ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'), ('Mantenimiento', 'Mantenimiento'),
        ('Seguridad', 'Seguridad'), ('Convivencia', 'Convivencia')
    ]
    PRIORIDADES = [('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta'), ('Urgente', 'Urgente')]
    
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='Media')

    # --- 2. SOLICITANTE ---
    solicitante = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)

    # --- 3. UBICACIÓN ---
    ZONAS = [('Apartamento', 'Apartamento'), ('Zona Comun', 'Zona Común'), ('Parqueadero', 'Parqueadero'), ('Porteria', 'Portería')]
    zona_afectada = models.CharField(max_length=20, choices=ZONAS, default='Apartamento')
    ubicacion_especifica = models.CharField(max_length=100, blank=True)

    # --- 4. GESTIÓN E INTERNOS ---
    AREAS = [('Admin', 'Administración'), ('Mantenimiento', 'Mantenimiento'), ('Seguridad', 'Seguridad'), ('Aseo', 'Aseo')]
    area_responsable = models.CharField(max_length=20, choices=AREAS, default='Admin')
    asignado_a = models.CharField(max_length=100, blank=True)
    
    ESTADOS = [
        ('Abierto', 'Abierto'), ('En Proceso', 'En Proceso'), 
        ('Pendiente Residente', 'Pendiente Residente'), ('Resuelto', 'Resuelto'), ('Cerrado', 'Cerrado')
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierto')

    # --- 5. CONTROL DE TIEMPOS ---
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    # --- 6. EVIDENCIAS Y SEGUIMIENTO ---
    imagen_evidencia = models.ImageField(upload_to='comunicaciones/evidencias/', null=True, blank=True)
    observaciones_internas = models.TextField(blank=True)
    respuesta_residente = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo}: {self.titulo} - {self.solicitante.nombre_completo}"

    class Meta:
        verbose_name = "Comunicación / PQRS"
        verbose_name_plural = "Comunicaciones / PQRS"