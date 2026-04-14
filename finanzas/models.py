"""
Descripción General: Definición de modelos para la gestión financiera y de cartera.
Módulo: finanzas
Propósito del archivo: Estructurar la base de datos para cuentas de cobro, multas y seguimiento de cobranza (CRM Cartera).
"""

from django.db import models
from usuarios.models import Apartamento
from django.utils import timezone
from django.contrib.auth.models import User

class CuentaCobro(models.Model):
    """
    Representa una factura mensual emitida a un apartamento.
    """
    MESES = [(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)]

    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apartamento")
    mes_referencia = models.CharField(max_length=2, choices=MESES, verbose_name="Mes")
    anio = models.IntegerField(default=2026, verbose_name="Año")
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Facturado")
    valor_abonado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Abonado")

    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado')
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    @property
    def saldo_pendiente(self):
        """
        Calcula el saldo remanente de la factura.

        Valor de retorno:
            Decimal: Diferencia entre el valor base y los abonos realizados.
        """
        return self.valor_base - self.valor_abonado

    def __str__(self):
        """Retorna la representación legible del periodo facturado."""
        return f"{self.apartamento} - Periodo {self.mes_referencia}/{self.anio}"

    class Meta:
        verbose_name = "Cuenta de Cobro"
        verbose_name_plural = "Cuentas de Cobro"

class Multa(models.Model):
    """
    Registro de sanciones económicas aplicadas por incumplimiento del reglamento interno.
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
    aplicada_en_cobro = models.BooleanField(default=False, verbose_name="¿Ya facturada?")

    def __str__(self):
        """Retorna el resumen de la multa."""
        return f"Multa {self.tipo} - {self.apartamento} (${self.valor:,.0f})"

    class Meta:
        verbose_name = "Multa"
        verbose_name_plural = "Multas"

class GestionCartera(models.Model):
    """
    Bitácora de seguimiento de cobranza y acuerdos de pago (CRM de Cartera).
    """
    TIPOS = [
        ('Llamada Telefonica', 'Llamada Telefónica'),
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
        """Retorna el tipo de gestión y el apartamento afectado."""
        return f"Gestión: {self.tipo_gestion} - Apto {self.apartamento.numero}"

    class Meta:
        verbose_name = "Gestión de Cartera"
        verbose_name_plural = "Gestiones de Cartera"
        ordering = ['-fecha_registro']

class Recaudo(models.Model):
    """
    Registro histórico de ingresos monetarios.
    Habilita la generación de analíticas temporales y métricas de desempeño.
    """
    CATEGORIAS = [
        ('Administracion', 'Administración'),
        ('Multa', 'Multa'),
        ('Reserva', 'Reserva'),
        ('Otro', 'Otro')
    ]

    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE, verbose_name="Apartamento")
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Recaudado")
    fecha_recaudo = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Pago")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='Administracion')
    referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia de Pago (Consignación/Transferencia)")

    class Meta:
        verbose_name = "Recaudo"
        verbose_name_plural = "Recaudos"
        ordering = ['-fecha_recaudo']

    def __str__(self):
        return f"Recaudo {self.categoria} - Apto {self.apartamento.numero} (${self.valor:,.0f})"
