"""
Descripción General: Definición de modelos para el repositorio de documentos oficiales del conjunto.
Módulo: documentos
Propósito del archivo: Almacenar la normativa, manuales de convivencia y formatos descargables para el acceso de todos los residentes.
"""

from django.db import models
from django.core.validators import FileExtensionValidator

class Documento(models.Model):
    """
    Representa un archivo PDF oficial compartido por la administración.
    """
    CATEGORIAS = [
        ('Manual', 'Manual de Convivencia'),
        ('Reglamento', 'Reglamento Interno'),
        ('Planos', 'Planos y Estructuras'),
        ('Circulares', 'Circulares Informativas'),
        ('Formatos', 'Formatos Descargables'),
        ('Otro', 'Otro Documento')
    ]

    # Datos Descriptivos
    titulo = models.CharField(max_length=200, verbose_name="Título del Documento")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Corta")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Otro')

    # Gestión de Archivo
    archivo = models.FileField(
        upload_to='documentos_generales/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name="Archivo PDF",
        help_text="Solo se permiten archivos en formato PDF."
    )

    # Metadatos
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-fecha_subida']

    def __str__(self):
        """Retorna el título y la categoría del documento."""
        return f"{self.titulo} - {self.categoria}"
