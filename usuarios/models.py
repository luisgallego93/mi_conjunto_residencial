from django.db import models
from django.contrib.auth.models import User

# --- 1. ENTIDAD: APARTAMENTO (El Activo Físico) ---
class Apartamento(models.Model):
    torre = models.CharField(max_length=10, verbose_name="Torre / Bloque")
    numero = models.CharField(max_length=10, verbose_name="Número de Apartamento")
    piso = models.PositiveIntegerField(verbose_name="Piso")
    codigo_pago = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Ej: 14501", verbose_name="Código Bancario CSV")
    
    # NUEVA ARQUITECTURA (Dualidad Propietario/Inquilino)
    propietario = models.ForeignKey(
        'PerfilUsuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="propiedades_asignadas",
        verbose_name="Propietario Legal"
    )
    inquilino = models.ForeignKey(
        'PerfilUsuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="arrendamientos_asignados",
        verbose_name="Inquilino / Arrendatario"
    )

    # CAMPO LEGADO (Para compatibilidad con módulos antiguos)
    residente_principal = models.ForeignKey(
        'PerfilUsuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="apartamentos_asignados",
        verbose_name="Residente Principal (LEGACY)"
    )

    def __str__(self):
        return f"Apto {self.numero} (Torre {self.torre})"

    class Meta:
        verbose_name = "Apartamento"
        verbose_name_plural = "Apartamentos"
        ordering = ['torre', 'numero']
        unique_together = ('torre', 'numero')


# --- 2. ENTIDAD: PERFIL DE USUARIO (La Persona) ---
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario de Sistema")
    
    ROLES = [
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
        ('ADMIN_CONJUNTO', 'Administrador del Conjunto'),
        ('RESIDENTE', 'Residente / Propietario'),
        ('VIGILANCIA', 'Vigilancia'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='RESIDENTE')
    activo = models.BooleanField(default=True, verbose_name="Cuenta Activa")
    primer_ingreso = models.BooleanField(default=True, verbose_name="¿Es su primer ingreso?")

    # --- Datos Personales ---
    documento = models.CharField(max_length=20, unique=True, verbose_name="Número de Documento")
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15)
    email_personal = models.EmailField(blank=True)

    # --- Datos de Ocupación ---
    TIPOS_OCUPACION = [
        ('Propietario', 'Propietario'),
        ('Arrendatario', 'Arrendatario'),
        ('Familiar', 'Familiar del Propietario'),
    ]
    tipo_ocupacion = models.CharField(max_length=20, choices=TIPOS_OCUPACION, default='Propietario')
    fecha_ingreso = models.DateField(null=True, blank=True)

    # --- Contacto de Emergencia ---
    emergencia_nombre = models.CharField(max_length=100, verbose_name="Nombre de Emergencia", blank=True)
    emergencia_telefono = models.CharField(max_length=15, verbose_name="Teléfono de Emergencia", blank=True)
    emergencia_parentesco = models.CharField(max_length=50, blank=True)

    # --- Configuración ---
    recibir_notificaciones = models.BooleanField(default=True)
    permitir_acceso_portal = models.BooleanField(default=True)
    observaciones = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.nombre_completo} - Doc: {self.documento}"

    class Meta:
        verbose_name = "Ficha de Usuario"
        verbose_name_plural = "Fichas de Usuarios"
        ordering = ['nombre_completo']


# --- 3. ENTIDAD: OCUPANTE (Censo Poblacional) ---
class Ocupante(models.Model):
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, related_name="habitantes")
    nombre_completo = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, blank=True)
    parentesco = models.CharField(max_length=50, help_text="Ej: Esposa, Hijo, Madre")
    telefono = models.CharField(max_length=15, blank=True)
    es_menor_edad = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco}) - Apto {self.apartamento.numero}"

    class Meta:
        verbose_name = "Ocupante"
        verbose_name_plural = "Censo: Ocupantes"