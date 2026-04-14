"""
Descripción General: Middleware de seguridad y flujos de usuario.
Módulo: usuarios
Propósito del archivo: Garantizar que los residentes completen su información básica (Onboarding) antes de usar el sistema.
"""

from django.shortcuts import redirect
from django.urls import reverse

class OnboardingMiddleware:
    """
    Middleware que asegura que los residentes completen su perfil y censo familiar
    en su primer ingreso antes de acceder al resto del sistema.
    """
    def __init__(self, get_response):
        """Inicialización del middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Lógica de redirección para el wizard de bienvenida.

        Qué hace:
            Si el usuario es un residente (no staff) y tiene marcada la bandera
            'primer_ingreso', lo redirige obligatoriamente al formulario de censo.
        """
        if request.user.is_authenticated:
            # Los administradores y vigilancia no pasan por este flujo
            if not request.user.is_staff:
                try:
                    perfil = request.user.perfilusuario
                    # Si es su primer ingreso, forzamos el registro de datos
                    if perfil.primer_ingreso:
                        path_censar = reverse('usuarios:completar_perfil')
                        path_logout = reverse('logout')

                        # Rutas excluidas de la redirección para permitir el registro
                        exempt_paths = [path_censar, path_logout, '/media/', '/static/']

                        if not any(request.path.startswith(p) for p in exempt_paths):
                            return redirect('usuarios:completar_perfil')
                except Exception:
                    # En caso de error o ausencia de perfil, se permite el acceso por defecto
                    pass

        return self.get_response(request)
