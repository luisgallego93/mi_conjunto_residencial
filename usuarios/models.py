from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    # --- 1. DATOS BÁSICOS (Vínculo con el sistema) ---
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario de Sistema")
    
    ROLES = [
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
        ('ADMIN_CONJUNTO', 'Administrador del Conjunto'),
        ('RESIDENTE', 'Residente / Propietario'),
        ('VIGILANCIA', 'Vigilancia'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='RESIDENTE')
    activo = models.BooleanField(default=True, verbose_name="Cuenta Activa")

    # --- 2. DATOS PERSONALES ---
    documento = models.CharField(max_length=20, unique=True, verbose_name="Número de Documento")
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15)
    email_personal = models.EmailField(blank=True)

    # --- 3. DATOS RESIDENCIALES ---
    torre = models.CharField(max_length=10, verbose_name="Torre / Bloque")
    apartamento = models.CharField(max_length=10)
    
    TIPOS_OCUPACION = [
        ('Propietario', 'Propietario'),
        ('Arrendatario', 'Arrendatario'),
        ('Familiar', 'Familiar del Propietario'),
    ]
    tipo_ocupacion = models.CharField(max_length=20, choices=TIPOS_OCUPACION, default='Propietario')
    fecha_ingreso = models.DateField(null=True, blank=True)

    # --- 4. CONTACTO DE EMERGENCIA ---
    emergencia_nombre = models.CharField(max_length=100, verbose_name="Nombre de Emergencia", blank=True)
    emergencia_telefono = models.CharField(max_length=15, verbose_name="Teléfono de Emergencia", blank=True)
    emergencia_parentesco = models.CharField(max_length=50, blank=True)

    # --- 5. CONFIGURACIÓN Y OTROS ---
    recibir_notificaciones = models.BooleanField(default=True)
    permitir_acceso_portal = models.BooleanField(default=True)
    observaciones = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.torre}-{self.apartamento})"

    class Meta:
        verbose_name = "Ficha de Usuario"
        verbose_name_plural = "Fichas de Usuarios"