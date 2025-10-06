from django.db import models
from apoderados.models import Apoderado  
from django.conf import settings

class Estudiante(models.Model):
    GRADOS = [
        ("1° Prim", "1° Primaria"),
        ("2° Prim", "2° Primaria"),
        ("3° Prim", "3° Primaria"),
        ("4° Prim", "4° Primaria"),
        ("5° Prim", "5° Primaria"),
        ("6° Prim", "6° Primaria"),
        ("1° Sec", "1° Secundaria"),
        ("2° Sec", "2° Secundaria"),
        ("3° Sec", "3° Secundaria"),
        ("4° Sec", "4° Secundaria"),
        ("5° Sec", "5° Secundaria"),
    ]

    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    edad = models.PositiveIntegerField()
    grado = models.CharField(max_length=10, choices=GRADOS)
    colegio = models.CharField(max_length=150)
    apoderado = models.ForeignKey(Apoderado, on_delete=models.PROTECT, related_name='estudiantes')

class Inscripcion(models.Model):
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)
    curso = models.ForeignKey('docentes.Curso', on_delete=models.PROTECT)
    usuario_registra = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=20, choices=[('pendiente','Pendiente'),('total','Total'),('parcial','Parcial')])

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
