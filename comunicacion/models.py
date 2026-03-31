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
    
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name="Tipo de Solicitud")
    titulo = models.CharField(max_length=100, verbose_name="Título/Asunto")
    descripcion = models.TextField(verbose_name="Descripción detallada")
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='Media')

    # --- 2. SOLICITANTE ---
    # Al usar related_name='comunicaciones', facilitamos las consultas desde el usuario
    solicitante = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='comunicaciones', verbose_name="Residente Solicitante")

    # --- 3. UBICACIÓN ---
    ZONAS = [('Apartamento', 'Apartamento'), ('Zona Comun', 'Zona Común'), ('Parqueadero', 'Parqueadero'), ('Porteria', 'Portería')]
    zona_afectada = models.CharField(max_length=20, choices=ZONAS, default='Apartamento')
    ubicacion_especifica = models.CharField(max_length=100, blank=True, help_text="Ej: Torre A Apto 101 o Salón Social")

    # --- 4. GESTIÓN E INTERNOS ---
    AREAS = [('Admin', 'Administración'), ('Mantenimiento', 'Mantenimiento'), ('Seguridad', 'Seguridad'), ('Aseo', 'Aseo')]
    area_responsable = models.CharField(max_length=20, choices=AREAS, default='Admin')
    asignado_a = models.CharField(max_length=100, blank=True, verbose_name="Personal encargado")
    
    ESTADOS = [
        ('Abierto', 'Abierto'), ('En Proceso', 'En Proceso'), 
        ('Pendiente Residente', 'Pendiente Residente'), ('Resuelto', 'Resuelto'), ('Cerrado', 'Cerrado')
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierto')

    # --- 5. CONTROL DE TIEMPOS ---
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")
    fecha_limite = models.DateField(null=True, blank=True, verbose_name="Fecha Límite de Respuesta")
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    # --- 6. EVIDENCIAS Y SEGUIMIENTO ---
    imagen_evidencia = models.ImageField(upload_to='comunicaciones/evidencias/', null=True, blank=True, verbose_name="Foto de Evidencia")
    observaciones_internas = models.TextField(blank=True, verbose_name="Notas de la Administración")
    respuesta_residente = models.TextField(blank=True, verbose_name="Respuesta final al residente")

    def __str__(self):
        # Usamos el nombre_completo del PerfilUsuario que ya definimos antes
        return f"{self.get_tipo_display()} - {self.solicitante.nombre_completo} ({self.titulo})"

    class Meta:
        verbose_name = "Comunicación / PQRS"
        verbose_name_plural = "Comunicaciones / PQRS"
        ordering = ['-fecha_creacion'] # Las más recientes aparecen primero