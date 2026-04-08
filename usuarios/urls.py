from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('residentes/', views.directorio_residentes, name='directorio_residentes'),
    path('apartamentos/', views.directorio_apartamentos, name='directorio_apartamentos'),
]
