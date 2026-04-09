from django.shortcuts import redirect
from django.urls import reverse

class OnboardingMiddleware:
    """
    Middleware que asegura que los residentes completen su perfil y censo familiar
    en su primer ingreso antes de acceder al resto del sistema.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # 1. Excluimos al personal administrativo y de vigilancia
            # Solo los residentes deben pasar por el onboarding
            if not request.user.is_staff:
                try:
                    perfil = request.user.perfilusuario
                    # 2. Si es su primer ingreso y no está ya en la página de completar-perfil
                    if perfil.primer_ingreso:
                        path_censar = reverse('usuarios:completar_perfil')
                        path_logout = reverse('logout')
                        
                        # Lista de rutas permitidas durante el onboarding
                        exempt_paths = [path_censar, path_logout, '/media/', '/static/']
                        
                        if not any(request.path.startswith(p) for p in exempt_paths):
                            return redirect('usuarios:completar_perfil')
                except Exception:
                    # Si no tiene perfil, lo dejamos pasar (podría ser un superuso sin perfil)
                    pass

        return self.get_response(request)
