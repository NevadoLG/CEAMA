from django.db import models
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=[('primaria','Primaria'),('secundaria','Secundaria')])
    plan = models.CharField(max_length=50, choices=[
        ('matematica', 'Matemática'),
        ('comunicacion', 'Comunicación'),
        ('ambos', 'Matemática + Comunicación')
    ])
    cupo_maximo = models.PositiveIntegerField(default=30)
# Create your models here.
