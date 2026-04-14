"""
Descripción General: Definición de modelos para el sistema de PQRS (Peticiones, Quejas, Reclamos y Sugerencias).
Módulo: comunicacion
Propósito del archivo: Estructurar la base de datos para la comunicación oficial entre residentes y administración, trazabilidad de requerimientos y gestión de respuestas.
"""

from django.db import models
from django.utils import timezone
from usuarios.models import PerfilUsuario
from django.contrib.auth.models import User

class Comunicacion(models.Model):
    """
    Representa un requerimiento oficial (PQRS) o reporte técnico dentro del conjunto.
    Incluye lógica para generación automática de número de radicado.
    """
    TIPOS = [
        ('Peticion', 'Petición'), ('Queja', 'Queja'), ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'), ('Mantenimiento', 'Mantenimiento'),
        ('Seguridad', 'Seguridad'), ('Convivencia', 'Convivencia')
    ]
    PRIORIDADES = [('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta'), ('Urgente', 'Urgente')]

    # Categorización
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name="Tipo de Solicitud")
    titulo = models.CharField(max_length=100, verbose_name="Título/Asunto")
    descripcion = models.TextField(verbose_name="Descripción detallada")
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='Media')

    # Identificación Única
    numero_radicado = models.CharField(
        max_length=25,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Número de Radicado",
        help_text="Generado automáticamente al crear la solicitud. Ej: PQRS-2026-000001"
    )

    # Actores y Roles
    solicitante = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        related_name='comunicaciones',
        verbose_name="Residente Solicitante"
    )

    # Contexto Geográfico
    ZONAS = [('Apartamento', 'Apartamento'), ('Zona Comun', 'Zona Común'), ('Parqueadero', 'Parqueadero'), ('Porteria', 'Portería')]
    zona_afectada = models.CharField(max_length=20, choices=ZONAS, default='Apartamento')
    ubicacion_especifica = models.CharField(max_length=100, blank=True, help_text="Ej: Torre A Apto 101 o Salón Social")

    # Flujo de Trabajo
    AREAS = [('Admin', 'Administración'), ('Mantenimiento', 'Mantenimiento'), ('Seguridad', 'Seguridad'), ('Aseo', 'Aseo')]
    area_responsable = models.CharField(max_length=20, choices=AREAS, default='Admin')
    asignado_a = models.CharField(max_length=100, blank=True, verbose_name="Personal encargado")

    ESTADOS = [
        ('Abierto', 'Abierto'), ('En Proceso', 'En Proceso'),
        ('Pendiente Residente', 'Pendiente Residente'), ('Resuelto', 'Resuelto'), ('Cerrado', 'Cerrado')
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Abierto')

    # Línea de Tiempo
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")
    fecha_limite = models.DateField(null=True, blank=True, verbose_name="Fecha Límite de Respuesta")
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    # Multimedia y Retroalimentación
    imagen_evidencia = models.ImageField(
        upload_to='comunicaciones/evidencias/',
        null=True,
        blank=True,
        verbose_name="Foto de Evidencia"
    )
    observaciones_internas = models.TextField(blank=True, verbose_name="Notas de la Administración")
    respuesta_residente = models.TextField(blank=True, verbose_name="Respuesta final al residente")

    def save(self, *args, **kwargs):
        """Genera automáticamente el número de radicado jerárquico al crear el registro."""
        if not self.numero_radicado:
            super().save(*args, **kwargs)
            anio = self.fecha_creacion.year if self.fecha_creacion else timezone.now().year
            self.numero_radicado = f"PQRS-{anio}-{self.pk:06d}"
            Comunicacion.objects.filter(pk=self.pk).update(numero_radicado=self.numero_radicado)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        """Retorna el tipo de radicado, el solicitante y el título."""
        return f"{self.numero_radicado or 'SIN-RADICADO'} | {self.solicitante.nombre_completo} - {self.titulo}"

    class Meta:
        verbose_name = "Comunicación / PQRS"
        verbose_name_plural = "Comunicaciones / PQRS"
        ordering = ['-fecha_creacion']

class RespuestaPQRS(models.Model):
    """
    Hilo de conversación asociado a un radicado de comunicación.
    """
    comunicacion = models.ForeignKey(Comunicacion, on_delete=models.CASCADE, related_name='respuestas')
    mensaje = models.TextField(verbose_name="Cuerpo de la Respuesta")
    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Autor de Respuesta",
        related_name="respuestas_pqrs_enviadas"
    )
    evidencia = models.ImageField(upload_to='comunicaciones/respuestas/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Retorna el resumen de la respuesta y su fecha."""
        return f"Respuesta a {self.comunicacion.numero_radicado} - {self.fecha_creacion.strftime('%d/%m/%Y')}"
