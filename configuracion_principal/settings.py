"""
Descripción General: Configuración central del ecosistema Django para el Conjunto "Sauces de Ciudad del Valle".
Módulo: configuracion_principal
Propósito del archivo: Centralizar los parámetros técnicos, seguridad, conexión a base de datos y definición de servicios externos (correo, multimedia).
"""

import os
from pathlib import Path

# --- 1. RUTAS DEL SISTEMA ---
# BASE_DIR apunta a la raíz del proyecto para referencias relativas confiables.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- 2. SEGURIDAD Y ENTORNO ---
# IMPORTANTE: Cambiar DEBUG a False y generar una SECRET_KEY nueva antes de desplegar en servidor público.
SECRET_KEY = 'django-insecure-93p(3p@_5o$5j_oshoe+#b7mdbm_08!&$2hjx$ra#zypt%h%16'
DEBUG = True
ALLOWED_HOSTS = []

# --- 3. COMPONENTES DEL ECOSISTEMA (APPS) ---
INSTALLED_APPS = [
    # Módulos Core del Conjunto
    'dashboard',
    'usuarios',
    'finanzas',
    'reservas',
    'visitantes',
    'correspondencia',
    'comunicacion',
    'documentos',
    'notificaciones.apps.NotificacionesConfig',

    # Django Built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

# --- 4. INTERCEPTORES (MIDDLEWARE) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.OnboardingMiddleware', # Fuerza actualización de datos personales
]

ROOT_URLCONF = 'configuracion_principal.urls'

# --- 5. MOTOR DE PLANTILLAS (UX/UI) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Directorio global de fragmentos HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'configuracion_principal.wsgi.application'

# --- 6. PERSISTENCIA DE DATOS (MYSQL) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_residencial_pro',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# --- 7. POLÍTICAS DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- 8. LOCALIZACIÓN Y TIEMPO (COLOMBIA) ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- 9. RECURSOS ESTÁTICOS Y MULTIMEDIA ---
# STATIC: CSS, JS, Imágenes de Marca
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# MEDIA: Documentos subidos, comprobantes, fotos de visitantes
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- 10. POLÍTICAS DE ACCESO (AUTH) ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'login'

# --- 11. COMUNICACIÓN ELECTRÓNICA (SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'luisgallegop93@gmail.com'
EMAIL_HOST_PASSWORD = 'Cielo-Azul-99#Mx'
DEFAULT_FROM_EMAIL = 'Mi Conjunto Gestión Integral <luisgallegop93@gmail.com>'

# --- 12. CONFIGURACIÓN TÉCNICA ADICIONAL ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
