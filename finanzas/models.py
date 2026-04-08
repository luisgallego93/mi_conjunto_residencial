from django.db import models
from usuarios.models import Apartamento
from django.utils import timezone
from django.contrib.auth.models import User

class CuentaCobro(models.Model):
    MESES = [(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)]
    
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apartamento")
    mes_referencia = models.CharField(max_length=2, choices=MESES, verbose_name="Mes")
    anio = models.IntegerField(default=2026, verbose_name="Año")
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Administración Mes")
    estado = models.CharField(
        max_length=20, 
        choices=[('Pendiente', 'Pendiente'), ('Pagado', 'Pagado')], 
        default='Pendiente'
    )

    def __str__(self):
        return f"{self.apartamento} - Periodo {self.mes_referencia}/{self.anio}"

    class Meta:
        verbose_name = "Cuenta de Cobro"
        verbose_name_plural = "Cuentas de Cobro"

class Multa(models.Model):
    """
    Modelo para registrar sanciones económicas aplicadas a los apartamentos
    por incumplimiento del reglamento de propiedad horizontal.
    """
    TIPOS = [
        ('Convivencia', 'Convivencia'), 
        ('Ruido', 'Ruido'), 
        ('Mascotas', 'Mascotas'), 
        ('Escombros', 'Escombros'),
        ('Otros', 'Otros')
    ]
    
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apartamento")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField(verbose_name="Motivo de la sanción")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Multa")
    fecha_suceso = models.DateField(default=timezone.now)
    aplicada_en_cobro = models.BooleanField(default=False, verbose_name="Ya facturada?")

    def __str__(self):
        return f"Multa {self.tipo} - {self.apartamento} (${self.valor:,.0f})"

    class Meta:
        verbose_name = "Multa"
        verbose_name_plural = "Multas"

class GestionCartera(models.Model):
    """
    CRM / Bitácora de seguimiento de cobranza para cada Apartamento con deuda.
    """
    TIPOS = [
        ('Llamada Telefonica', 'Llamada Telefonica'),
        ('Carta Notificatoria', 'Carta Notificatoria'),
        ('WhatsApp / Mensaje', 'WhatsApp / Mensaje'),
        ('Acuerdo de Pago', 'Acuerdo de Pago Presencial'),
        ('Visita', 'Visita Domiciliaria'),
        ('Otro', 'Otro')
    ]
    
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, related_name="gestiones_cartera")
    tipo_gestion = models.CharField(max_length=50, choices=TIPOS)
    observaciones = models.TextField(verbose_name="Observaciones o Acuerdo", blank=True)
    
    acuerdo_pago = models.BooleanField(default=False, verbose_name="¿Generó Acuerdo de Pago?")
    fecha_compromiso = models.DateField(null=True, blank=True, verbose_name="Fecha Compromiso de Pago")
    
    ESTADOS = [
        ('Pendiente', 'Acuerdo Pendiente de Fecha'),
        ('Cumplido', 'Acuerdo Cumplido Exitosamente'),
        ('No Cumplido', 'Incumplió Promesa')
    ]
    estado_acuerdo = models.CharField(max_length=20, choices=ESTADOS, blank=True, null=True)
    
    evidencia = models.FileField(upload_to='finanzas/gestiones/', null=True, blank=True)
    gestor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Gestor / Auxiliar de Cobranza")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gestión: {self.tipo_gestion} - Apto {self.apartamento.numero}"

    class Meta:
        verbose_name = "Gestión de Cartera"
        verbose_name_plural = "Gestiones de Cartera"
        ordering = ['-fecha_registro']