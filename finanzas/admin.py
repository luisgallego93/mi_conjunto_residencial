from django.contrib import admin, messages
from django.db.models import Sum
from .models import CuentaCobro, Multa
from usuarios.models import Apartamento
from datetime import datetime

@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ('apartamento', 'tipo', 'valor', 'fecha_suceso', 'aplicada_en_cobro')
    list_filter = ('tipo', 'aplicada_en_cobro')
    search_fields = ('apartamento__numero',)

@admin.register(CuentaCobro)
class CuentaCobroAdmin(admin.ModelAdmin):
    list_display = ('apartamento', 'mes_referencia', 'valor_base', 'mostrar_mora_y_deuda', 'mostrar_multas', 'total_final', 'estado')
    list_filter = ('estado', 'mes_referencia', 'anio')
    actions = ['generar_mensualidad_masiva']

    @admin.action(description="Generar Cobros del Mes Actual (460 Aptos)")
    def generar_mensualidad_masiva(self, request, queryset):
        mes_actual = str(datetime.now().month).zfill(2)
        anio_actual = datetime.now().year
        valor_estandar = 150000

        aptos = Apartamento.objects.all()
        creados = 0
        for apto in aptos:
            obj, created = CuentaCobro.objects.get_or_create(
                apartamento=apto, mes_referencia=mes_actual, anio=anio_actual,
                defaults={'valor_base': valor_estandar, 'estado': 'Pendiente'}
            )
            if created: creados += 1

        self.message_user(request, f"✅ Proceso completado: {creados} cobros nuevos.", messages.SUCCESS)

    def mostrar_mora_y_deuda(self, obj):
        deuda = CuentaCobro.objects.filter(
            apartamento=obj.apartamento, estado='Pendiente', id__lt=obj.id
        ).aggregate(Sum('valor_base'))['valor_base__sum'] or 0

        if deuda > 0:
            interes = float(deuda) * 0.019
            return f"${deuda:,.2f} (+ ${interes:,.2f} Int.)"
        return "$0.00"
    mostrar_mora_y_deuda.short_description = "Deuda Ant. + Mora"

    def mostrar_multas(self, obj):
        total_multas = Multa.objects.filter(
            apartamento=obj.apartamento, aplicada_en_cobro=False
        ).aggregate(Sum('valor'))['valor__sum'] or 0
        return f"${total_multas:,.2f}"
    mostrar_multas.short_description = "Multas Pend."

    def total_final(self, obj):
        deuda = CuentaCobro.objects.filter(
            apartamento=obj.apartamento, estado='Pendiente', id__lt=obj.id
        ).aggregate(Sum('valor_base'))['valor_base__sum'] or 0

        interes = float(deuda) * 0.019
        multas = Multa.objects.filter(
            apartamento=obj.apartamento, aplicada_en_cobro=False
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total = float(obj.valor_base) + float(deuda) + interes + float(multas)
        return f"${total:,.2f}"
    total_final.short_description = "TOTAL A PAGAR"
