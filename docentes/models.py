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
class Profesor(models.Model):
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"

class Aula(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "Aula 101"
    capacidad = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.nombre

class Horario(models.Model):
    DIAS = [
        ('lun','Lunes'),('mar','Martes'),('mie','Miércoles'),
        ('jue','Jueves'),('vie','Viernes'),('sab','Sábado'),('dom','Domingo'),
    ]
    dia = models.CharField(max_length=3, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        unique_together = [('dia','hora_inicio','hora_fin')]

    def __str__(self):
        return f"{self.get_dia_display()} {self.hora_inicio}–{self.hora_fin}"

class Asignacion(models.Model):
    profesor = models.ForeignKey('docentes.Profesor', on_delete=models.PROTECT)
    curso = models.ForeignKey('docentes.Curso', on_delete=models.PROTECT)
    aula = models.ForeignKey('docentes.Aula', on_delete=models.PROTECT)
    horario = models.ForeignKey('docentes.Horario', on_delete=models.PROTECT)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            # Un profesor no puede tener dos clases en el mismo horario
            models.UniqueConstraint(fields=['profesor','horario'], name='uniq_profesor_horario'),
            # Un aula no puede tener dos clases en el mismo horario
            models.UniqueConstraint(fields=['aula','horario'], name='uniq_aula_horario'),
        ]

    def __str__(self):
        return f"{self.profesor} → {self.curso} ({self.horario} / {self.aula})"