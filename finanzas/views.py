from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from datetime import date
import calendar as cal_module
import csv
import io

from .models import CuentaCobro, Multa, GestionCartera
from usuarios.models import Apartamento, PerfilUsuario
from reservas.models import Reserva
from .forms import MultaForm


def _ultimo_dia_mes(anio, mes):
    """Fecha del último día del mes — es la fecha de vencimiento de la factura."""
    ultimo = cal_module.monthrange(int(anio), int(mes))[1]
    return date(int(anio), int(mes), ultimo)


def _aplicar_saldo(facturas_qs, saldo: Decimal):
    """
    Aplica `saldo` a las facturas pendientes de más antigua a más reciente.
    Usa `valor_abonado` para no destruir `valor_base` (valor original facturado).
    Retorna la cantidad de meses completamente liquidados.
    """
    meses_liquidados = 0
    for factura in facturas_qs:
        if saldo <= Decimal('0'):
            break
        pendiente = factura.saldo_pendiente
        if saldo >= pendiente:
            # Pago completo de este mes
            factura.valor_abonado = factura.valor_base
            factura.estado = 'Pagado'
            factura.save()
            saldo -= pendiente
            meses_liquidados += 1
        else:
            # Abono parcial — solo acumular el abono, NO modificar valor_base
            factura.valor_abonado += saldo
            factura.save()
            saldo = Decimal('0')
    return meses_liquidados, saldo


@login_required
def cartera(request):
    """
    Lista todos los apartamentos con facturas o multas pendientes.
    Asegura que todos los meses (Jan, Feb, Mar, etc) sean visibles.
    """
    query = request.GET.get('q', '')
    hoy = date.today()

    # Traer todas las facturas pendientes
    cuentas_qs = CuentaCobro.objects.filter(estado='Pendiente').select_related(
        'apartamento', 'apartamento__residente_principal'
    ).order_by('anio', 'mes_referencia')
    
    # Traer todas las multas no facturadas
    multas_qs = Multa.objects.filter(aplicada_en_cobro=False).select_related(
        'apartamento', 'apartamento__residente_principal'
    )

    if query:
        cuentas_qs = (
            cuentas_qs.filter(apartamento__numero__icontains=query) |
            cuentas_qs.filter(apartamento__residente_principal__nombre_completo__icontains=query)
        )
        multas_qs = (
            multas_qs.filter(apartamento__numero__icontains=query) |
            multas_qs.filter(apartamento__residente_principal__nombre_completo__icontains=query)
        )

    # Agrupar datos por apartamento
    deuda_por_apto = {}

    for c in cuentas_qs:
        apto_id = c.apartamento.id
        if apto_id not in deuda_por_apto:
            deuda_por_apto[apto_id] = {
                'apartamento': c.apartamento,
                'detalles': [],
                'total_mora': Decimal('0'),
                'total_vigente': Decimal('0'),
                'total': Decimal('0'),
            }
        
        # Lógica de Mora: Vencida al último día del mes
        vencimiento = _ultimo_dia_mes(c.anio, c.mes_referencia)
        en_mora = hoy > vencimiento
        saldo = c.saldo_pendiente

        deuda_por_apto[apto_id]['detalles'].append({
            'periodo': f"{c.mes_referencia}/{c.anio}",
            'saldo': saldo,
            'en_mora': en_mora,
            'tipo': 'Administración'
        })
        
        deuda_por_apto[apto_id]['total'] += saldo
        if en_mora:
            deuda_por_apto[apto_id]['total_mora'] += saldo
        else:
            deuda_por_apto[apto_id]['total_vigente'] += saldo

    for m in multas_qs:
        apto_id = m.apartamento.id
        if apto_id not in deuda_por_apto:
            deuda_por_apto[apto_id] = {
                'apartamento': m.apartamento,
                'detalles': [],
                'total_mora': Decimal('0'),
                'total_vigente': Decimal('0'),
                'total': Decimal('0'),
            }
        deuda_por_apto[apto_id]['detalles'].append({
            'periodo': f"Multa: {m.tipo}",
            'saldo': m.valor,
            'en_mora': True,
            'tipo': 'Multa'
        })
        deuda_por_apto[apto_id]['total'] += m.valor
        deuda_por_apto[apto_id]['total_mora'] += m.valor

    # Ordenar por Torre y Apto
    resumen_cartera = list(deuda_por_apto.values())
    resumen_cartera.sort(key=lambda x: (x['apartamento'].torre, x['apartamento'].numero))

    total_mora = sum(item['total_mora'] for item in resumen_cartera)
    total_vigente = sum(item['total_vigente'] for item in resumen_cartera)
    
    return render(request, 'finanzas/cartera.html', {
        'resumen_cartera': resumen_cartera,
        'total_mora': total_mora,
        'total_vigente': total_vigente,
        'query': query,
    })


@login_required
def generar_facturacion(request):
    """
    Genera cuentas de cobro para TODOS los apartamentos para el mes/año indicado.
    Usa get_or_create: no duplica ni borra registros existentes.
    """
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        valor = request.POST.get('valor_base')

        if mes and anio and valor:
            apartamentos = Apartamento.objects.all()
            creados = 0
            ya_existian = 0
            for apto in apartamentos:
                # Cada factura debe representar solo el valor del mes actual.
                # El tablero de Cartera se encargará de sumar los meses independientes.
                _, created = CuentaCobro.objects.get_or_create(
                    apartamento=apto,
                    mes_referencia=mes,
                    anio=int(anio),
                    defaults={'valor_base': Decimal(str(valor)), 'valor_abonado': Decimal('0'), 'estado': 'Pendiente'}
                )
                if created:
                    creados += 1
                else:
                    ya_existian += 1

            if creados > 0:
                messages.success(request, f"✅ Generación Exitosa: Se crearon {creados} nuevas facturas para {mes}/{anio}. "
                                          f"({ya_existian} apartamentos ya tenían factura para este periodo y no fueron duplicados).")
            else:
                messages.warning(request, f"Atención: Las {ya_existian} facturas para el periodo {mes}/{anio} ya se encuentran en el sistema. No se realizaron cambios.")
        else:
            messages.error(request, "Faltan datos: mes, año y valor son obligatorios.")

    return redirect('finanzas:cartera')


@login_required
def registrar_multa(request):
    if request.method == 'POST':
        form = MultaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sanción registrada correctamente.")
            return redirect('finanzas:cartera')
    else:
        form = MultaForm()
    return render(request, 'finanzas/crear_multa.html', {'form': form})


@login_required
def recibir_pago(request, apartamento_id):
    """
    Registra un pago manual para un apartamento.
    - Pago Total: salda absolutamente todo (facturas + multas).
    - Abono Parcial: aplica el monto de más antiguo a más reciente.
      Usa valor_abonado para no destruir valor_base (el valor original facturado).
    """
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apartamento_id)
        tipo_pago = request.POST.get('tipo_pago', 'total')

        if tipo_pago == 'total':
            facturas = CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente')
            for f in facturas:
                f.valor_abonado = f.valor_base
                f.estado = 'Pagado'
                f.save()
            Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).update(aplicada_en_cobro=True)
            messages.success(request, f"✅ Pago total registrado. El apartamento {apto.numero} quedó en Paz y Salvo.")

        elif tipo_pago == 'abono':
            # Limpieza robusta: eliminar todo lo que no sea dígito
            raw_valor = request.POST.get('valor_abono', '')
            valor_str = ''.join(c for c in str(raw_valor) if c.isdigit())
            
            if not valor_str:
                messages.error(request, f"El valor ingresado ({raw_valor}) no es válido. Ingrese solo números.")
                return redirect('finanzas:cartera')

            saldo = Decimal(valor_str)
            if saldo <= 0:
                messages.error(request, "El valor del abono debe ser mayor a $0.")
                return redirect('finanzas:cartera')

            facturas = CuentaCobro.objects.filter(
                apartamento=apto, estado='Pendiente'
            ).order_by('anio', 'mes_referencia')

            meses_pagados, saldo_restante = _aplicar_saldo(facturas, saldo)

            if meses_pagados > 0:
                messages.success(request, f"Abono aplicado. {meses_pagados} mes(es) liquidado(s) para Apto {apto.numero}.")
            else:
                messages.info(request, f"Abono de ${saldo:,.0f} registrado en la factura más antigua del Apto {apto.numero}.")

    return redirect('finanzas:cartera')


@login_required
def notificar_morosos(request):
    cuentas = CuentaCobro.objects.filter(estado='Pendiente')
    aptos_con_deuda = set(c.apartamento for c in cuentas)
    enviados = sum(
        1 for apto in aptos_con_deuda
        if apto.residente_principal and apto.residente_principal.email_personal
    )
    messages.info(request, f"Simulación: Se habrían enviado {enviados} correos a morosos con email registrado.")
    return redirect('finanzas:cartera')


@login_required
def descargar_plantilla_pagos(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_pagos_banco.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['codigo_pago', 'valor_depositado'])
    writer.writerow(['14501', '485000'])  # Fila de ejemplo
    return response

@login_required
def eliminar_periodo(request):
    """
    Elimina todas las facturas de un periodo (mes/año) específico.
    Útil para corregir errores de digitación en la generación masiva.
    """
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        
        if mes and anio:
            eliminados, _ = CuentaCobro.objects.filter(
                mes_referencia=mes, 
                anio=int(anio)
            ).delete()
            
            if eliminados > 0:
                messages.success(request, f"Se han eliminado {eliminados} facturas del periodo {mes}/{anio} correctamente.")
            else:
                messages.warning(request, f"No se encontraron facturas para el periodo {mes}/{anio}.")
        else:
            messages.error(request, "Debe especificar mes y año para eliminar.")
            
    return redirect('finanzas:cartera')


def decodificar_codigo_banco(codigo):
    """
    Decodifica el código bancario numérico al formato interno de la BD.
    Formato: TTAAA  → TT = número ordinal torre (A=1, B=2 ... N=14), AAA = número apto
    Ejemplos: '14501' → Torre N, Apto 501
    """
    codigo = str(codigo).strip()
    if len(codigo) < 4:
        return None, None
    num_apto = codigo[-3:]
    num_torre_str = codigo[:-3]
    try:
        num_torre = int(num_torre_str)
        if num_torre < 1 or num_torre > 26:
            return None, None
        letra_torre = chr(ord('A') + num_torre - 1)
        return letra_torre, num_apto
    except ValueError:
        return None, None


@login_required
def cargar_pagos_csv(request):
    """
    Procesa el archivo plano del banco.
    Columnas requeridas: codigo_pago, valor_depositado
    Soporta delimitadores ; y , y codificación UTF-8/ISO.
    """
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']

        if not archivo.name.endswith('.csv'):
            messages.error(request, "Solo se admiten archivos .csv")
            return redirect('finanzas:cartera')

        try:
            # Intentar utf-8-sig primero (elimina BOM de Excel), luego latin-1
            try:
                decoded_file = archivo.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                archivo.seek(0)
                decoded_file = archivo.read().decode('latin-1')

            primera_linea = decoded_file.split('\n')[0]
            delimitador = ';' if primera_linea.count(';') >= primera_linea.count(',') else ','

            reader = csv.DictReader(io.StringIO(decoded_file), delimiter=delimitador)

            pagos_aplicados = 0
            codigos_no_encontrados = []

            for fila_num, row in enumerate(reader, start=2):
                cod_pago = row.get('codigo_pago', '').strip()
                val_deposito = row.get('valor_depositado', '').strip()

                if not cod_pago and not val_deposito:
                    continue

                if not cod_pago:
                    continue

                apto = None

                # Intento 1: búsqueda directa por codigo_pago
                try:
                    apto = Apartamento.objects.get(codigo_pago__iexact=cod_pago)
                except Apartamento.DoesNotExist:
                    pass

                # Intento 2: decodificar código bancario numérico
                if apto is None:
                    letra_torre, num_apto = decodificar_codigo_banco(cod_pago)
                    if letra_torre and num_apto:
                        try:
                            apto = Apartamento.objects.get(torre=letra_torre, numero=f"{letra_torre}{num_apto}")
                        except Apartamento.DoesNotExist:
                            try:
                                apto = Apartamento.objects.get(torre=letra_torre, numero__endswith=num_apto)
                            except (Apartamento.DoesNotExist, Apartamento.MultipleObjectsReturned):
                                pass

                if apto is None:
                    codigos_no_encontrados.append(f"'{cod_pago}' (fila {fila_num})")
                    continue

                # Parsear valor — solo dígitos (admite formatos: 485000 / 485.000 / $485,000)
                val_limpio = ''.join(c for c in val_deposito if c.isdigit())
                try:
                    saldo_disponible = Decimal(val_limpio) if val_limpio else Decimal('0')
                except InvalidOperation:
                    saldo_disponible = Decimal('0')

                # Aplicar el pago a las facturas pendientes
                facturas = CuentaCobro.objects.filter(
                    apartamento=apto, estado='Pendiente'
                ).order_by('anio', 'mes_referencia')

                meses_liquidados, saldo_restante = _aplicar_saldo(facturas, saldo_disponible)

                if meses_liquidados > 0:
                    pagos_aplicados += 1

                # Aplicar saldo restante a multas si sobra
                if saldo_restante > 0:
                    Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False).update(aplicada_en_cobro=True)

            # Resultado final
            if pagos_aplicados == 0 and codigos_no_encontrados:
                lista = ', '.join(codigos_no_encontrados[:5])
                extra = f' y {len(codigos_no_encontrados)-5} más' if len(codigos_no_encontrados) > 5 else ''
                messages.error(request, f"No se procesó ningún pago. Códigos no encontrados: {lista}{extra}. "
                                        f"Formato esperado: TT+AAA (ej: 14501 = Torre N, Apto 501).")
            elif codigos_no_encontrados:
                lista = ', '.join(codigos_no_encontrados[:5])
                messages.warning(request, f"Procesado: {pagos_aplicados} apto(s) actualizados. "
                                           f"No encontrados: {lista}.")
            elif pagos_aplicados > 0:
                messages.success(request, f"✅ {pagos_aplicados} apartamento(s) actualizados. "
                                           f"Los meses cubiertos quedaron en 'Pagado'; abonos parciales se registraron sin borrar el saldo original.")
            else:
                messages.info(request, "Archivo procesado. No había facturas pendientes para los códigos del archivo.")

        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")

    return redirect('finanzas:cartera')


@login_required
def expediente_cobranza(request, apartamento_id):
    apto = get_object_or_404(Apartamento, id=apartamento_id)

    facturas_pendientes = CuentaCobro.objects.filter(
        apartamento=apto, estado='Pendiente'
    ).order_by('-anio', '-mes_referencia')

    multas_pendientes = Multa.objects.filter(
        apartamento=apto, aplicada_en_cobro=False
    ).order_by('-fecha_suceso')

    total_deuda = (
        sum(f.saldo_pendiente for f in facturas_pendientes) +
        sum(m.valor for m in multas_pendientes)
    )

    historial = GestionCartera.objects.filter(
        apartamento=apto
    ).select_related('gestor').order_by('-fecha_registro')

    if request.method == 'POST':
        tipo = request.POST.get('tipo_gestion')
        obs = request.POST.get('observaciones')
        acuerdo = request.POST.get('acuerdo_pago') == 'on'
        fecha_comp = request.POST.get('fecha_compromiso')
        evidencia = request.FILES.get('evidencia')

        GestionCartera.objects.create(
            apartamento=apto,
            tipo_gestion=tipo,
            observaciones=obs,
            acuerdo_pago=acuerdo,
            fecha_compromiso=fecha_comp if fecha_comp else None,
            estado_acuerdo='Pendiente' if acuerdo else None,
            evidencia=evidencia,
            gestor=request.user
        )
        messages.success(request, "Gestión registrada en el expediente.")
        return redirect('finanzas:expediente_cobranza', apartamento_id=apto.id)

    return render(request, 'finanzas/expediente.html', {
        'apto': apto,
        'facturas': facturas_pendientes,
        'multas': multas_pendientes,
        'total_deuda': total_deuda,
        'historial': historial,
    })
@login_required
def mi_estado_cuenta(request):
    """
    Vista para que el RESIDENTE consulte su historial de pagos y deudas.
    Cruza información de Administración, Multas y Reservas.
    """
    try:
        perfil = request.user.perfilusuario
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Tu usuario no tiene un perfil de residente asociado.")
        return redirect('dashboard:index')

    apartamento = None
    from usuarios.models import Apartamento as AptoModel
    from django.db.models import Q
    # Buscar por nueva arquitectura (propietario o inquilino) o por campo legado
    apartamento = AptoModel.objects.filter(
        Q(propietario=perfil) | Q(inquilino=perfil) | Q(residente_principal=perfil)
    ).first()

    if not apartamento:
        messages.warning(request, "No tienes un apartamento asignado. Contacta a la administración.")
        return render(request, 'finanzas/movimientos.html', {'movimientos': [], 'al_dia': True})

    # 1. Cuentas de Cobro
    cuentas = CuentaCobro.objects.filter(apartamento=apartamento).order_by('-anio', '-mes_referencia')
    
    # 2. Multas
    multas = Multa.objects.filter(apartamento=apartamento).order_by('-fecha_suceso')
    
    # 3. Reservas Pagadas o Aprobadas
    reservas = Reserva.objects.filter(solicitante=perfil).order_by('-fecha')

    # Determinar si está al día
    deuda_pendiente = cuentas.filter(estado='Pendiente').exists() or multas.filter(aplicada_en_cobro=False).exists()

    from datetime import date
    hoy = date.today()
    mes_actual = str(hoy.month).zfill(2)
    anio_actual = hoy.year

    context = {
        'apartamento': apartamento,
        'cuentas': cuentas,
        'multas': multas,
        'reservas': reservas,
        'al_dia': not deuda_pendiente,
        'mes_actual': mes_actual,
        'anio_actual': anio_actual,
    }
    return render(request, 'finanzas/movimientos.html', context)
