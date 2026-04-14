"""
Descripción General: Despachador central de rutas del proyecto "Mi Conjunto Residencial".
Módulo: configuracion_principal
Propósito del archivo: Orquestar la navegación global integrando los módulos de finanzas, seguridad, comunicación y administración.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel Administrativo de Django
    path('admin/', admin.site.urls),

    # Sistema de Autenticación y Cuentas
    path('accounts/', include('django.contrib.auth.urls')),

    # Módulos Funcionales del Conjunto
    path('pqrs/', include('comunicacion.urls')),
    path('reservas/', include('reservas.urls')),
    path('finanzas/', include('finanzas.urls')),
    path('visitantes/', include('visitantes.urls')),
    path('correspondencia/', include('correspondencia.urls')),
    path('directorio/', include('usuarios.urls')),
    path('documentos/', include('documentos.urls')),

    # Portal de Inicio (Dashboard)
    path('', include('dashboard.urls')),
]

# Configuración de Archivos Estáticos y Multimedia (Modo Desarrollo)
# IMPORTANTE: En producción, estos archivos deben ser servidos por un servidor web (Nginx/Apache).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
