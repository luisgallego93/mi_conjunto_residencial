from django.urls import path
from . import views

app_name = 'documentos'

urlpatterns = [
    path('', views.lista_documentos, name='lista'),
    path('subir/', views.subir_documento, name='subir'),
]
