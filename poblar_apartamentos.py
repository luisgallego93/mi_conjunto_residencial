import os
import django

# 1. Configuración del entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_principal.settings')
django.setup()

from usuarios.models import Apartamento

def generar_conjunto_real():
    # Rango de torres: de la A a la W
    torres = [chr(i) for i in range(ord('A'), ord('W') + 1)]
    pisos = range(1, 6)           # Pisos 1, 2, 3, 4, 5
    unidades = range(1, 5)        # Aptos 01, 02, 03, 04 por piso
    
    contador = 0
    print(f"🚀 Iniciando construcción digital de {len(torres)} torres...")

    for letra in torres:
        for piso in pisos:
            for n in unidades:
                # Formato solicitado: A101, A102... W504
                # Usamos f"{letra}{piso}0{n}" para asegurar el cero intermedio
                identificador_apto = f"{letra}{piso}0{n}"
                
                # Creamos el registro en MySQL
                Apartamento.objects.get_or_create(
                    torre=letra,
                    numero=identificador_apto,
                    piso=piso
                )
                contador += 1
    
    print(f"✅ ¡Misión cumplida! Se crearon {contador} apartamentos con éxito.")

if __name__ == '__main__':
    generar_conjunto_real()