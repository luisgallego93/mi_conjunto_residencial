from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Comunicado(models.Model):
    PRIORIDAD = [
        ('Baja', 'Informativo'),
        ('Media', 'Importante'),
        ('Alta', 'Urgente / Alerta'),
    ]
    
    TORRES = [
        ('Todas', 'Todas las Torres'),
        ('Torre 1', 'Torre 1'),
        ('Torre 2', 'Torre 2'),
        ('Torre 3', 'Torre 3'),
        ('Torre 4', 'Torre 4'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Aviso")
    contenido = models.TextField(verbose_name="Cuerpo del Mensaje")
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD, default='Baja')
    segmentacion = models.CharField(max_length=20, choices=TORRES, default='Todas')
    
    # Para adjuntar circulares o reglamentos
    archivo_adjunto = models.FileField(upload_to='comunicados/pdfs/', blank=True, null=True)
    
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    esta_activo = models.BooleanField(default=True, verbose_name="Publicado")

    def __str__(self):
        return f"[{self.prioridad}] {self.titulo}"

    class Meta:
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados y Noticias"

# ... mantén tu código de Comunicado arriba ...

class PQRS(models.Model):
    TIPO_CHOICES = [
        ('Peticion', 'Petición'),
        ('Queja', 'Queja'),
        ('Reclamo', 'Reclamo'),
        ('Sugerencia', 'Sugerencia'),
    ]
    
    ESTADO_CHOICES = [
        ('Abierto', 'Abierto'),
        ('En Proceso', 'En Proceso'),
        ('Cerrado', 'Cerrado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Residente")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Queja')
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField(verbose_name="Detalle de la solicitud")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Respuesta administrativa
    respuesta_admin = models.TextField(blank=True, null=True, verbose_name="Respuesta de la Administración")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Abierto')
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo}: {self.asunto} - {self.usuario.username}"

    class Meta:
        verbose_name = "PQRS"
        verbose_name_plural = "PQRS (Quejas y Reclamos)"