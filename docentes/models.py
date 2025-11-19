from django.db import models
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=[('primaria','Primaria'),('secundaria','Secundaria')])
    plan = models.CharField(max_length=50, choices=[
        ('matematica', 'Matemática'),
        ('comunicacion', 'Comunicación'),
        ('ambos', 'Matemática + Comunicación')
    ])
    # Nota: la capacidad se gestiona por `Asignacion` (grupos), no por `Curso`.
    def __str__(self):
        return f"{self.nombre} ({self.get_nivel_display()})"

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
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    # Los días ahora se modelan con una relación ManyToMany a Dia
    # Esto permite horarios que se repiten varios días (ej: lun/mie/vie 16:00-19:00)
    dias = models.ManyToManyField('docentes.Dia', related_name='horarios')

    def __str__(self):
        dias_list = ','.join([d.codigo for d in self.dias.all()])
        return f"{dias_list} {self.hora_inicio}–{self.hora_fin}"

class Asignacion(models.Model):
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

    # Grado asociado a esta asignación (para filtrar en el registro)
    grado = models.CharField(max_length=10, choices=GRADOS, null=True, blank=True)

    profesor = models.ForeignKey('docentes.Profesor', on_delete=models.PROTECT)
    curso = models.ForeignKey('docentes.Curso', on_delete=models.PROTECT)
    aula = models.ForeignKey('docentes.Aula', on_delete=models.PROTECT)
    horario = models.ForeignKey('docentes.Horario', on_delete=models.PROTECT)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    # Capacidad por grupo/asignación
    cupo_maximo = models.PositiveIntegerField(default=30)

    class Meta:
        constraints = [
            # Un profesor no puede tener dos clases en el mismo horario
            models.UniqueConstraint(fields=['profesor','horario'], name='uniq_profesor_horario'),
            # Un aula no puede tener dos clases en el mismo horario
            models.UniqueConstraint(fields=['aula','horario'], name='uniq_aula_horario'),
        ]

    def __str__(self):
        return f"{self.profesor} → {self.curso} ({self.horario} / {self.aula})"


class Dia(models.Model):
    DIAS = [
        ('lun','Lunes'),('mar','Martes'),('mie','Miércoles'),
        ('jue','Jueves'),('vie','Viernes'),('sab','Sábado'),('dom','Domingo'),
    ]
    codigo = models.CharField(max_length=3, choices=DIAS, unique=True)

    def __str__(self):
        return self.get_codigo_display()