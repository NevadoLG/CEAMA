from django.db import models

class Plan(models.Model):
    NIVELES = [('primaria','Primaria'), ('secundaria','Secundaria')]
    AREAS = [('matematica','Matemática'), ('comunicacion','Comunicación'), ('ambos','Matemática + Comunicación')]

    nombre = models.CharField(max_length=120)  # Ej: "Primaria - Matemática"
    nivel = models.CharField(max_length=15, choices=NIVELES)
    area = models.CharField(max_length=15, choices=AREAS)
    cupo_maximo = models.PositiveIntegerField(default=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()} - {self.get_area_display()})"
