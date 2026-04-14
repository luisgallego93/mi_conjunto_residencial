import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion_principal.settings')
django.setup()

from usuarios.models import Usuario

def test_views():
    c = Client()
    user = Usuario.objects.filter(is_superuser=True).first()
    if not user:
        print("No superuser found")
        return
    c.force_login(user)

    urls = [
        ('finanzas:cartera', {}),
        ('reservas:lista_reservas', {}),
    ]

    for url_name, kwargs in urls:
        try:
            url = reverse(url_name, kwargs=kwargs)
            response = c.get(url)
            print(f"URL: {url} -> Status: {response.status_code}")
            if response.status_code != 200:
                print(f"ERROR content: {response.content.decode()[:1000]}")
        except Exception as e:
            print(f"URL {url_name} CRASHED: {e}")

if __name__ == "__main__":
    test_views()
