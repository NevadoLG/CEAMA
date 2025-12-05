from django.db import models
from django.core.validators import MinValueValidator
class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    # Eliminamos el campo `nivel` para simplificar el modelo.
    descripcion = models.TextField(blank=True)
    # Curso ahora es una entidad independiente que representa la materia.
    # Las relaciones con Plan se modelan desde `planes.Plan.cursos` (ManyToMany).
    # Nota: la capacidad se gestiona por `Asignacion` (grupos), no por `Curso`.
    def __str__(self):
        if self.descripcion:
            return f"{self.nombre} — {self.descripcion}"
        return self.nombre
    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

# Create your models here.
class Profesor(models.Model):
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"

class Aula(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "Aula 101"
    capacidad = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"

class Horario(models.Model):
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    # Los días ahora se modelan con una relación ManyToMany a Dia
    # Esto permite horarios que se repiten varios días (ej: lun/mie/vie 16:00-19:00)
    dias = models.ManyToManyField('docentes.Dia', related_name='horarios')

    def __str__(self):
        dias_list = ','.join([d.codigo for d in self.dias.all()])
        return f"{dias_list} {self.hora_inicio}–{self.hora_fin}"
    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"

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

    # Permitir múltiples profesores por asignación
    profesores = models.ManyToManyField('docentes.Profesor', related_name='asignaciones')
    # Ahora Asignacion referencia a Plan (una asignación utiliza UN plan)
    # Temporalmente permitimos NULL para poder introducir la columna y
    # rellenarla con una migración de datos antes de exigir NOT NULL.
    plan = models.ForeignKey('planes.Plan', on_delete=models.PROTECT, related_name='asignaciones', null=True, blank=True)
    aula = models.ForeignKey('docentes.Aula', on_delete=models.PROTECT)
    horario = models.ForeignKey('docentes.Horario', on_delete=models.PROTECT)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    # Capacidad por grupo/asignación
    cupo_maximo = models.PositiveIntegerField(default=30)
    precio = models.DecimalField(
            "Precio",
            max_digits=7,
            decimal_places=2,
            default=0,
            validators=[MinValueValidator(0)],
            help_text="Costo en soles de esta asignación (por alumno).",
        )
    def __str__(self):
        profs = ', '.join(str(p) for p in self.profesores.all())
        return f"{profs} → {getattr(self.plan, 'nombre', 'Plan?')} ({self.horario} / {self.aula})"

    class Meta:
        verbose_name = "Asignación"
        verbose_name_plural = "Asignaciones"
        constraints = [
            models.UniqueConstraint(
                fields=['aula', 'horario'],
                name='uniq_aula_horario'
            ),
        ]


class Dia(models.Model):
    DIAS = [
        ('lun','Lunes'),('mar','Martes'),('mie','Miércoles'),
        ('jue','Jueves'),('vie','Viernes'),('sab','Sábado'),('dom','Domingo'),
    ]
    codigo = models.CharField(max_length=3, choices=DIAS, unique=True)

    def __str__(self):
        return self.get_codigo_display()
    class Meta:
        verbose_name = "Día"
        verbose_name_plural = "Días"