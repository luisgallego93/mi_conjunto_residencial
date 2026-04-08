from django.db import models
from django.contrib.auth.models import User

class Documento(models.fields.Field):
    pass # Replaced below

from django.db import models
from django.core.validators import FileExtensionValidator

class Documento(models.Model):
    CATEGORIAS = [
        ('Manual', 'Manual de Convivencia'),
        ('Reglamento', 'Reglamento Interno'),
        ('Planos', 'Planos y Estructuras'),
        ('Circulares', 'Circulares Informativas'),
        ('Formatos', 'Formatos Descargables'),
        ('Otro', 'Otro Documento')
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título del Documento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Corta")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Otro')
    archivo = models.FileField(
        upload_to='documentos_generales/', 
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name="Archivo PDF"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"{self.titulo} - {self.categoria}"
