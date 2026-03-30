from django.db import models

#
class ZonaComun(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField()

    def __str__(self):
        return self.nombre

#
class Reserva(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente de aprobación'),
        ('Aprobada', 'Reserva Confirmada'),
        ('Cancelada', 'Reserva Cancelada'),
        ('Finalizada', 'Uso completado'),
    ]

    
    zona = models.ForeignKey(ZonaComun, on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    residente_nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')

    def __str__(self):
        return f"{self.residente_nombre} en {self.zona}"