from django.db import models

class Plan(models.Model):
    NIVELES = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria')
    ]

    nombre = models.CharField(max_length=120)  # Ej: "Primaria - Matemática"
    nivel = models.CharField(max_length=15, choices=NIVELES)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True)
    # Relación a Cursos: un Plan puede contener varios Cursos, y un Curso
    # puede pertenecer a varios Planes.
    cursos = models.ManyToManyField('docentes.Curso', related_name='planes', blank=True)

    def __str__(self):
        if self.descripcion:
            return f"{self.nombre} ({self.get_nivel_display()}) — {self.descripcion}"
        return f"{self.nombre} ({self.get_nivel_display()})"

    # Nota: la capacidad se gestiona por `Asignacion` (grupos), no por `Plan`.
    
    def cursos_base(self):
        from docentes.models import Curso
        qs = Curso.objects.all()
        return qs

