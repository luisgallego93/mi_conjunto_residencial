from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum
from collections import defaultdict

from .models import CuentaCobro, Multa
from usuarios.models import Apartamento
from .forms import MultaForm

@login_required
def cartera(request):
    query = request.GET.get('q', '')
    
    # 1. Obtener todas las cuentas y multas pendientes
    cuentas = CuentaCobro.objects.filter(estado='Pendiente').select_related('apartamento', 'apartamento__residente_principal')
    multas = Multa.objects.filter(aplicada_en_cobro=False).select_related('apartamento', 'apartamento__residente_principal')
    
    if query:
        cuentas = cuentas.filter(apartamento__numero__icontains=query) | cuentas.filter(apartamento__residente_principal__nombre_completo__icontains=query)
        multas = multas.filter(apartamento__numero__icontains=query) | multas.filter(apartamento__residente_principal__nombre_completo__icontains=query)

    # 2. Agrupar la deuda por Apartamento en Python
    deuda_por_apto = {}
    
    for c in cuentas:
        apto_id = c.apartamento.id
        if apto_id not in deuda_por_apto:
            deuda_por_apto[apto_id] = {
                'apartamento': c.apartamento,
                'detalles': [],
                'total': 0
            }
        deuda_por_apto[apto_id]['detalles'].append(f"Admin {c.mes_referencia}/{c.anio}")
        deuda_por_apto[apto_id]['total'] += c.valor_base
        
    for m in multas:
        apto_id = m.apartamento.id
        if apto_id not in deuda_por_apto:
            deuda_por_apto[apto_id] = {
                'apartamento': m.apartamento,
                'detalles': [],
                'total': 0
            }
        deuda_por_apto[apto_id]['detalles'].append(f"Multa: {m.tipo}")
        deuda_por_apto[apto_id]['total'] += m.valor
        
    resumen_cartera = list(deuda_por_apto.values())
    # Ordenar por el número de torre y luego de apartamento
    resumen_cartera.sort(key=lambda x: (x['apartamento'].torre, x['apartamento'].numero))
    
    total_mora = sum(c['total'] for c in resumen_cartera)
    
    return render(request, 'finanzas/cartera.html', {
        'resumen_cartera': resumen_cartera, 
        'total_mora': total_mora, 
        'query': query
    })

@login_required
def generar_facturacion(request):
    if request.method == 'POST':
        mes = request.POST.get('mes')
        anio = request.POST.get('anio')
        valor = request.POST.get('valor_base')
        
        if mes and anio and valor:
            apartamentos = Apartamento.objects.all()
            creados = 0
            for apto in apartamentos:
                _, created = CuentaCobro.objects.get_or_create(
                    apartamento=apto,
                    mes_referencia=mes,
                    anio=anio,
                    defaults={'valor_base': valor, 'estado': 'Pendiente'}
                )
                if created: creados += 1
            messages.success(request, f"Se generaron {creados} cuentas de cobro para {mes}/{anio}.")
        else:
            messages.error(request, "Faltan datos para la generación masiva.")
            
    return redirect('finanzas:cartera')

@login_required
def registrar_multa(request):
    if request.method == 'POST':
        form = MultaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sanción registrada correctamente. Ha sido sumada a la cartera.")
            return redirect('finanzas:cartera')
    else:
        form = MultaForm()
    return render(request, 'finanzas/crear_multa.html', {'form': form})

@login_required
def recibir_pago(request, apartamento_id):
    if request.method == 'POST':
        apto = get_object_or_404(Apartamento, id=apartamento_id)
        # Saldar todas las facturas y multas del apartamento
        facturas = CuentaCobro.objects.filter(apartamento=apto, estado='Pendiente')
        facturas.update(estado='Pagado')
        
        multas = Multa.objects.filter(apartamento=apto, aplicada_en_cobro=False)
        multas.update(aplicada_en_cobro=True)
        
        messages.success(request, f"¡Pago exitoso! La cartera del apartamento {apto.numero} ha quedado en paz y salvo.")
    return redirect('finanzas:cartera')

@login_required
def notificar_morosos(request):
    # Buscar todos los que deben y tienen correo
    cuentas = CuentaCobro.objects.filter(estado='Pendiente')
    aptos_con_deuda = set([c.apartamento for c in cuentas])
    
    enviados = 0
    for apto in aptos_con_deuda:
        residente = apto.residente_principal
        if residente and residente.email_personal:
            # En un entorno real enviaría el email
            # send_mail(
            #     'Estado de Cuenta Vencido - Mi Conjunto',
            #     f'Hola {residente.nombre_completo}, tu apartamento {apto.numero} registra facturas pendientes.',
            #     'no-reply@miconjunto.com',
            #     [residente.email_personal],
            #     fail_silently=True,
            # )
            enviados += 1
            
    messages.info(request, f"Función Simulada: Se habrían enviado {enviados} correos a los morosos con emails registrados en su Ficha.")
    return redirect('finanzas:cartera')

