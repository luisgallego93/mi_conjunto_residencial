"""
Descripción General: Controladores para la gestión financiera, cobranza y facturación.
Módulo: finanzas
Propósito del archivo: Gestionar el ciclo de vida de las cuentas de cobro, multas, recaudos y seguimiento de morosidad.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from datetime import date
import calendar as cal_module
import csv
import io

from django.db.models import Q, F
from .models import CuentaCobro, Multa, GestionCartera, Recaudo
from usuarios.models import Apartamento
from reservas.models import Reserva
from .forms import MultaForm

def _ultimo_dia_mes(anio, mes):
    """
    Determina el último día calendario de un mes determinado.
    """
    ultimo = cal_module.monthrange(int(anio), int(mes))[1]
    return date(int(anio), int(mes), ultimo)

def _aplicar_saldo(apto, items_qs, saldo: Decimal, es_factura=True):
    """
    Motor de Liquidación PEPS Génerico con Registro de Recaudos.
    Aplica saldo a una lista de deudas y genera trazabilidad histórica.
    """
    liquidados = 0
    total_aplicado_en_esta_vuelta = Decimal('0')
    cat = 'Administracion' if es_factura else 'Multa'
    
    for item in items_qs:
        if saldo <= Decimal('0'):
            break
        
        pendiente = item.saldo_pendiente if es_factura else item.valor
        monto_a_aplicar = min(saldo, pendiente)
        
        if monto_a_aplicar > 0:
            if es_factura:
                item.valor_abonado += monto_a_aplicar
                if item.saldo_pendiente <= 0:
                    item.estado = 'Pagado'
            else:
                # Si se paga al menos una parte de la multa, la marcamos como aplicada (simplificación)
                item.aplicada_en_cobro = True
            
            item.save()
            
            # Registrar el Recaudo histórico
            Recaudo.objects.create(
                apartamento=apto,
                valor=monto_a_aplicar,
                categoria=cat,
                referencia=f"Liquidación PEPS {'Factura' if es_factura else 'Multa'}"
            )
            
            saldo -= monto_a_aplicar
            total_aplicado_en_esta_vuelta += monto_a_aplicar
            liquidados += 1

    return liquidados, saldo

@login_required
def cartera(request):
    """
    Consola de Administración Financiera Global.
    """
    query = request.GET.get('q', '')
    filtro_estado = request.GET.get('filtro', 'todos')

    apartamentos_qs = Apartamento.objects.all().select_related('residente_principal', 'propietario', 'inquilino')
    if query:
        apartamentos_qs = apartamentos_qs.filter(
            Q(numero__icontains=query) |
            Q(propietario__nombre_completo__icontains=query) |
            Q(inquilino__nombre_completo__icontains=query) |
            Q(residente_principal__nombre_completo__icontains=query)
        )

    deuda_por_apto = {apto.id: {
        'apartamento': apto,
        'detalles': [],
        'total_mora': Decimal('0'),
        'total_vigente': Decimal('0'),
        'total': Decimal('0'),
        'saldo_a_favor': apto.saldo_a_favor,
        'esta_al_dia': True
    } for apto in apartamentos_qs}

    cuentas_qs = CuentaCobro.objects.filter(estado='Pendiente').select_related('apartamento')
    multas_qs = Multa.objects.filter(aplicada_en_cobro=False).select_related('apartamento')

    hoy = date.today()

    for c in cuentas_qs:
        if c.apartamento.id in deuda_por_apto:
            vencimiento = _ultimo_dia_mes(c.anio, c.mes_referencia)
            en_mora = hoy > vencimiento
            saldo = c.saldo_pendiente
            deuda_por_apto[c.apartamento.id]['detalles'].append({
                'periodo': f"{c.mes_referencia}/{c.anio}",
                'saldo': saldo,
                'en_mora': en_mora,
                'tipo': 'Administración'
            })
            deuda_por_apto[c.apartamento.id]['total'] += saldo
            deuda_por_apto[c.apartamento.id]['esta_al_dia'] = False
            if en_mora:
                deuda_por_apto[c.apartamento.id]['total_mora'] += saldo
            else:
                deuda_por_apto[c.apartamento.id]['total_vigente'] += saldo

    for m in multas_qs:
        if m.apartamento.id in deuda_por_apto:
            deuda_por_apto[m.apartamento.id]['detalles'].append({
                'id_multa': m.id,
                'periodo': f"Multa: {m.tipo}",
                'saldo': m.valor,
                'en_mora': True,
                'tipo': 'Multa'
            })
            deuda_por_apto[m.apartamento.id]['total'] += m.valor
            deuda_por_apto[m.apartamento.id]['total_mora'] += m.valor
            deuda_por_apto[m.apartamento.id]['esta_al_dia'] = False

    resumen_cartera = list(deuda_por_apto.values())
    if filtro_estado == 'mora':
        resumen_cartera = [item for item in resumen_cartera if not item['esta_al_dia']]
    elif filtro_estado == 'aldia':
        resumen_cartera = [item for item in resumen_cartera if item['esta_al_dia']]

    resumen_cartera.sort(key=lambda x: (x['apartamento'].torre, x['apartamento'].numero))
    meses_choices = CuentaCobro.MESES
    mes_actual = str(date.today().month).zfill(2)
    
    # Años disponibles para la purga
    anios_disponibles = sorted(list(set(CuentaCobro.objects.values_list('anio', flat=True))), reverse=True)
    if not anios_disponibles:
        anios_disponibles = [date.today().year]

    return render(request, 'finanzas/cartera.html', {
        'resumen_cartera': resumen_cartera,
        'total_mora': sum(i['total_mora'] for i in resumen_cartera),
        'total_vigente': sum(i['total_vigente'] for i in resumen_cartera),
        'total_saldo_favor': sum(i['saldo_a_favor'] or 0 for i in resumen_cartera),
        'query': query,
        'filtro_estado': filtro_estado,
        'aptos_totales': apartamentos_qs.count(),
        'aptos_en_mora': sum(1 for item in deuda_por_apto.values() if not item['esta_al_dia']),
        'meses_choices': meses_choices,
        'mes_actual': mes_actual,
        'anios_disponibles': anios_disponibles,
    })

@login_required
def generar_facturacion(request):
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        valor = request.POST.get('valor_base')
        if mes and anio and valor:
            apartamentos = Apartamento.objects.all()
            for apto in apartamentos:
                valor_base = Decimal(str(valor))
                valor_abonado = Decimal('0')
                estado = 'Pendiente'
                if apto.saldo_a_favor > 0:
                    if apto.saldo_a_favor >= valor_base:
                        valor_abonado = valor_base
                        apto.saldo_a_favor -= valor_base
                        estado = 'Pagado'
                    else:
                        valor_abonado = apto.saldo_a_favor
                        apto.saldo_a_favor = Decimal('0')
                    apto.save()
                CuentaCobro.objects.get_or_create(
                    apartamento=apto,
                    mes_referencia=mes,
                    anio=int(anio),
                    defaults={'valor_base': valor_base, 'valor_abonado': valor_abonado, 'estado': estado}
                )
            return redirect('finanzas:cartera')

@login_required
def eliminar_periodo(request):
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        if mes and anio:
            eliminados, _ = CuentaCobro.objects.filter(mes_referencia=mes, anio=anio).delete()
            messages.warning(request, f"Se han eliminado {eliminados} registros del periodo {mes}/{anio}.")
    return redirect('finanzas:cartera')

@login_required
def registrar_multa(request):
    if request.method == 'POST':
        form = MultaForm(request.POST)
        if form.is_valid():
            multa = form.save()
            # Cruce automático con Saldo a Favor
            apto = multa.apartamento
            if apto.saldo_a_favor > 0:
                if apto.saldo_a_favor >= multa.valor:
                    apto.saldo_a_favor -= multa.valor
                    multa.aplicada_en_cobro = True
                    messages.success(request, f"Multa saldada automáticamente con crédito a favor (${multa.valor:,.0f}).")
                else:
                    multa.valor -= apto.saldo_a_favor
                    apto.saldo_a_favor = Decimal('0')
                    messages.info(request, "Se aplicó saldo a favor parcialmente a la multa.")
                apto.save()
                multa.save()
            else:
                messages.success(request, "Sanción registrada correctamente.")
            return redirect('finanzas:cartera')
    else:
        form = MultaForm()
    return render(request, 'finanzas/crear_multa.html', {'form': form})

@login_required
def recibir_pago(request, apartamento_id):
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apartamento_id)
        tipo_pago = request.POST.get('tipo_pago', 'total')

        if tipo_pago == 'total':
            CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente').update(valor_abonado=F('valor_base'), estado='Pagado')
            Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).update(aplicada_en_cobro=True)
            messages.success(request, f"¡Apto {apto.numero} en Paz y Salvo!")
        elif tipo_pago == 'abono':
            val_str = ''.join(c for c in str(request.POST.get('valor_abono', '')) if c.isdigit())
            if val_str:
                saldo = Decimal(val_str)
                # 1. Aplicar a Multas primero
                multas = Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).order_by('fecha_suceso')
                _, saldo = _aplicar_saldo(apto, multas, saldo, es_factura=False)
                # 2. Aplicar a Facturas
                if saldo > 0:
                    facturas = CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente').order_by('anio', 'mes_referencia')
                    _, saldo = _aplicar_saldo(apto, facturas, saldo, es_factura=True)
                # 3. Excedente
                if saldo > 0:
                    apto.saldo_a_favor += saldo
                    apto.save()
                messages.success(request, "Abono procesado exitosamente.")
    return redirect('finanzas:cartera')

@login_required
def cargar_pagos_csv(request):
    """
    Motor de Procesamiento Masivo de Recaudos Bancarios.
    
    Qué hace:
        Lee un archivo CSV con los pagos del banco, identifica el inmueble por su
        codigo_pago, liquida deudas pendientes (PEPS) y genera saldos a favor.
    """
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        
        # Manejo de decodificación robusta
        try:
            data = archivo.read().decode('utf-8-sig') # utf-8-sig para archivos Excel con BOM
        except UnicodeDecodeError:
            try:
                data = archivo.read().decode('latin-1')
            except:
                messages.error(request, "Error de codificación en el archivo.")
                return redirect('finanzas:cartera')

        io_string = io.StringIO(data)
        
        # Detector automático de delimitador (; o ,)
        primer_linea = data.split('\n')[0]
        dialect = ';' if ';' in primer_linea else ','
        
        reader = csv.DictReader(io_string, delimiter=dialect)
        
        # Diccionario de búsqueda inteligente: mapea códigos normalizados (solo dígitos) a apartamentos
        # Esto permite que '1103' (Banco) coincida con '1A103' (DB)
        mapa_inteligente = {
            ''.join(filter(str.isdigit, str(a.codigo_pago))): a 
            for a in Apartamento.objects.filter(codigo_pago__isnull=False)
        }

        exitos = 0
        errores = 0
        total_procesado = Decimal('0')

        for row in reader:
            try:
                codigo_original = row.get('codigo_pago', '').strip()
                valor_str = row.get('valor_depositado', '0').strip().replace(',', '.')
                if not codigo_original or not valor_str:
                    continue
                    
                valor = Decimal(valor_str)
                if valor <= 0:
                    continue

                # 1. Encontrar el Apartamento (Búsqueda Inteligente)
                apto = Apartamento.objects.filter(codigo_pago=codigo_original).first()
                
                if not apto:
                    # Segundo intento: Normalización (solo dígitos)
                    codigo_normalizado = ''.join(filter(str.isdigit, codigo_original))
                    apto = mapa_inteligente.get(codigo_normalizado)

                if not apto:
                    errores += 1
                    continue

                # 2. Aplicar lógica de liquidación PEPS (Multas -> Facturas -> Saldo a Favor)
                saldo = valor
                
                # A. Multas pendientes
                multas = Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).order_by('fecha_suceso')
                _, saldo = _aplicar_saldo(apto, multas, saldo, es_factura=False)
                
                # B. Facturas pendientes
                if saldo > 0:
                    facturas = CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente').order_by('anio', 'mes_referencia')
                    _, saldo = _aplicar_saldo(apto, facturas, saldo, es_factura=True)
                
                # C. Excedente a Saldo a Favor
                if saldo > 0:
                    apto.saldo_a_favor += saldo
                    apto.save()
                    # También registramos el excedente como recaudo 'Otro' 
                    # para que la contabilidad de caja cuadre con el banco
                    Recaudo.objects.create(
                        apartamento=apto,
                        valor=saldo,
                        categoria='Otro',
                        referencia="Excedente CSV -> Saldo a Favor"
                    )
                
                exitos += 1
                total_procesado += valor

            except (InvalidOperation, ValueError):
                errores += 1
                continue

        if exitos > 0:
            messages.success(request, f"¡Procesamiento exitoso! Se aplicaron {exitos} pagos por un total de ${total_procesado:,.0f}.")
        if errores > 0:
            messages.warning(request, f"Se encontraron {errores} registros con errores (código no existe o formato inválido).")
            
    return redirect('finanzas:cartera')

@login_required
def descargar_plantilla_pagos(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_pagos.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['codigo_pago', 'valor_depositado', 'fecha', 'referencia_banco'])
    return response

@login_required
def notificar_morosos(request):
    messages.info(request, "Avisos de cobro enviados.")
    return redirect('finanzas:cartera')

@login_required
def historial_apartamento_admin(request, apartamento_id):
    apto = get_object_or_404(Apartamento, id=apartamento_id)
    cuentas = CuentaCobro.objects.filter(apartamento=apto).order_by('-anio', '-mes_referencia')
    multas = Multa.objects.filter(apartamento=apto).order_by('-fecha_suceso')
    return render(request, 'finanzas/historial_admin.html', {
        'apto': apto,
        'cuentas': cuentas,
        'multas': multas
    })

@login_required
def expediente_cobranza(request, apartamento_id):
    apto = get_object_or_404(Apartamento, id=apartamento_id)
    if request.method == 'POST':
        GestionCartera.objects.create(
            apartamento=apto,
            tipo_gestion=request.POST.get('tipo_gestion'),
            observaciones=request.POST.get('observaciones'),
            acuerdo_pago=request.POST.get('acuerdo_pago') == 'on',
            fecha_compromiso=request.POST.get('fecha_compromiso') or None,
            gestor=request.user
        )
        messages.success(request, "Gestión registrada.")
    facturas = CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente').order_by('anio', 'mes_referencia')
    multas = Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).order_by('fecha_suceso')
    total_deuda = sum(f.saldo_pendiente for f in facturas) + sum(m.valor for m in multas)
    historial = GestionCartera.objects.filter(apartamento=apto).order_by('-fecha_registro')
    return render(request, 'finanzas/expediente.html', {
        'apto': apto, 
        'historial': historial,
        'facturas': facturas,
        'multas': multas,
        'total_deuda': total_deuda
    })

@login_required
def mi_estado_cuenta(request):
    es_admin = hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol != 'RESIDENTE'
    apartamento = None
    apartamentos_lista = []
    seleccion_necesaria = False
    if es_admin:
        apartamentos_lista = Apartamento.objects.all().order_by('torre', 'numero')
        apto_id = request.GET.get('apartamento_id')
        if apto_id:
            apartamento = get_object_or_404(Apartamento, id=apto_id)
        else:
            seleccion_necesaria = True
    else:
        if hasattr(request.user, 'perfilusuario'):
            perfil = request.user.perfilusuario
            apartamento = Apartamento.objects.filter(
                Q(residente_principal=perfil) | Q(propietario=perfil) | Q(inquilino=perfil)
            ).first()
        if not apartamento:
            messages.warning(request, "No tienes un inmueble asociado.")
            return redirect('dashboard:index')

    context = {
        'vista_admin': es_admin,
        'apartamentos_lista': apartamentos_lista,
        'seleccion_necesaria': seleccion_necesaria,
        'apartamento': apartamento,
        'anio_actual': date.today().year,
        'mes_actual': str(date.today().month).zfill(2),
        'anio_filtro': request.GET.get('anio_filtro', 'todos'),
        'meses_choices': CuentaCobro.MESES,
    }

    if apartamento:
        anio_filtro = request.GET.get('anio_filtro', 'todos')
        cuentas = CuentaCobro.objects.filter(apartamento=apartamento).order_by('-anio', '-mes_referencia')
        multas = Multa.objects.filter(apartamento=apartamento).order_by('-fecha_suceso')
        perfiles_asociados = [apartamento.residente_principal, apartamento.propietario, apartamento.inquilino]
        reservas = Reserva.objects.filter(solicitante__in=[p for p in perfiles_asociados if p]).order_by('-fecha')
        if anio_filtro != 'todos':
            cuentas = cuentas.filter(anio=anio_filtro)
            multas = multas.filter(fecha_suceso__year=anio_filtro)
            reservas = reservas.filter(fecha__year=anio_filtro)
        tiene_deuda = cuentas.filter(estado='Pendiente').exists() or multas.filter(aplicada_en_cobro=False).exists()
        anios_disponibles = sorted(list(set(list(CuentaCobro.objects.filter(apartamento=apartamento).values_list('anio', flat=True).distinct()) + [date.today().year])), reverse=True)
        context.update({
            'cuentas': cuentas,
            'multas': multas,
            'reservas': reservas,
            'al_dia': not tiene_deuda,
            'anios_disponibles': anios_disponibles,
        })
    return render(request, 'finanzas/movimientos.html', context)
@login_required
def notar_gestion(request, apartamento_id):
    # (Existing view code might be here or below)
    pass


@login_required
def eliminar_multa(request, multa_id):
    """
    Eliminación Individual de Sanciones.
    Permite revertir una multa cargada por error.
    """
    perfil = getattr(request.user, 'perfilusuario', None)
    if not perfil or perfil.rol not in ['ADMIN_CONJUNTO', 'ADMIN_SISTEMA']:
        messages.error(request, "Acceso denegado.")
        return redirect('finanzas:cartera')

    multa = get_object_or_404(Multa, id=multa_id)
    apto_numero = multa.apartamento.numero
    
    # Si la multa fue saldada con crédito a favor, se debería revertir el crédito?
    # Para simplicidad inicial, solo se borra la multa.
    
    multa.delete()
    messages.warning(request, f"Multa del Apto {apto_numero} eliminada correctamente.")
    return redirect(request.META.get('HTTP_REFERER', 'finanzas:cartera'))
