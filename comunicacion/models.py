from django.db import models

class Solicitud(models.Model):
    # Aquí defino las opciones fijas para que el usuario no escriba cualquier cosa
    TIPOS_SOLICITUD = [
        ('PQRS', 'Petición, Queja, Reclamo o Sugerencia'),
        ('MANTENIMIENTO', 'Solicitud de Reparación'),
    ]
    
    ESTADOS_SOLICITUD = [
        ('Abierto', 'Abierto / Pendiente'),
        ('En Proceso', 'En Revisión'),
        ('Cerrado', 'Resuelto / Finalizado'),
    ]

    # He decidido añadir prioridades para clasificar la urgencia de los reportes
    NIVELES_PRIORIDAD = [
        ('Baja', 'Baja - Rutinario'),
        ('Media', 'Media - Importante'),
        ('Alta', 'Alta - Urgente'),
    ]
    
    # Estos son los campos de mi tabla:
    tipo = models.CharField(max_length=20, choices=TIPOS_SOLICITUD)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Se captura la fecha actual sola
    
    # Uso 'choices' para que en mi panel aparezca una lista desplegable
    prioridad = models.CharField(max_length=10, choices=NIVELES_PRIORIDAD, default='Media')
    estado = models.CharField(max_length=20, choices=ESTADOS_SOLICITUD, default='Abierto')

    def __str__(self):
        # Esta función me ayuda a que el registro se vea con su prioridad y título en el panel
        return f"[{self.prioridad}] {self.tipo}: {self.titulo}"