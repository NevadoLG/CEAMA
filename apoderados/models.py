from django.db import models

class Apoderado(models.Model):
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    telefono = models.CharField(max_length=15, unique=True)
    correo = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
