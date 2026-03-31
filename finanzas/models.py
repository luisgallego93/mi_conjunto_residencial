from django.db import models
from usuarios.models import Apartamento
from django.utils import timezone

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