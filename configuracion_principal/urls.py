from django.contrib import admin
from django.urls import path, include

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
