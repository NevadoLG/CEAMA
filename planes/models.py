from django.db import models

class Plan(models.Model):
    NIVELES = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria')
    ]
    AREAS = [
        ('matematica', 'Matemática'),
        ('comunicacion', 'Comunicación'),
        ('ambos', 'Matemática + Comunicación')
    ]

    nombre = models.CharField(max_length=120)  # Ej: "Primaria - Matemática"
    nivel = models.CharField(max_length=15, choices=NIVELES)
    area = models.CharField(max_length=15, choices=AREAS)
    cupo_maximo = models.PositiveIntegerField(default=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()} - {self.get_area_display()})"

    # 🔹 Funciones de ayuda (no afectan migraciones)
    def cupos_ocupados(self):
        return self.inscripcion_set.count()

    def cupos_disponibles(self):
        return max(self.cupo_maximo - self.cupos_ocupados(), 0)
    
    def cursos_base(self):
        from docentes.models import Curso
        qs = Curso.objects.filter(nivel=self.nivel)
        if self.area == 'matematica':
            qs = qs.filter(plan='matematica')
        elif self.area == 'comunicacion':
            qs = qs.filter(plan='comunicacion')
        else:  
            qs = qs.filter(plan__in=['matematica', 'comunicacion'])
        return qs

