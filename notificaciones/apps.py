from django.apps import AppConfig

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        # IMPORTANTE: Aquí es donde se conecta el cable de las señales
        import notificaciones.signals
