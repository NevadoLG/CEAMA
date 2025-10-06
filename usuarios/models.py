from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('docente', 'Docente'),
        ('asistente', 'Asistente'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='admin')
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        # Muestra el username y el rol legible
        return f"{self.username} ({self.get_rol_display()})"
