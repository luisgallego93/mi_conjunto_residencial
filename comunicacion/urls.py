from django.urls import path
from . import views

app_name = 'comunicacion'

urlpatterns = [
    path('', views.lista_pqrs, name='lista_pqrs'),
    path('crear/', views.crear_pqrs, name='crear_pqrs'),
    path('ver/<int:pqrs_id>/', views.ver_pqrs, name='ver_pqrs'),
]
