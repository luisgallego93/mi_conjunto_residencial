from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Login and authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),
    
    # App URLs
    path('pqrs/', include('comunicacion.urls')),
    path('reservas/', include('reservas.urls')),
    path('finanzas/', include('finanzas.urls')),
    path('visitantes/', include('visitantes.urls')),
    path('correspondencia/', include('correspondencia.urls')),
    path('directorio/', include('usuarios.urls')),
    path('documentos/', include('documentos.urls')),
    
    # Dashboard URLs loaded correctly using include
    path('', include('dashboard.urls')),
]

# --- Servir archivos de MEDIA en modo desarrollo (PDFs, imágenes, comprobantes) ---
# En producción se configura Nginx/Apache para esto. En desarrollo lo hace Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
