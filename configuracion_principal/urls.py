from django.contrib import admin
from django.urls import path
from dashboard import views as dash_views # Asegúrate que apunte a DASHBOARD

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dash_views.index, name='dashboard'), # Página principal
    path('informes/', dash_views.informes, name='informes'), # Página de informes
]