# estudiantes/models.py
from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apoderados.models import Apoderado
from docentes.models import Asignacion
from django.db.models import Count


class VerificacionToken(models.Model):
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.pk} de estudiante {self.estudiante_id}"
    class Meta:
        verbose_name = "Token de verificación"
        verbose_name_plural = "Tokens de verificación"


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
    edad = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(20)]
    )
    grado = models.CharField(max_length=10, choices=GRADOS)
    colegio = models.CharField(max_length=150)
    apoderado = models.ForeignKey(
        Apoderado,
        on_delete=models.PROTECT,
        related_name='estudiantes',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class Inscripcion(models.Model):
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)
    curso = models.ForeignKey('docentes.Curso', on_delete=models.PROTECT, null=True, blank=True)
    # Asignación seleccionada (la clase / grupo al que se quiere inscribir)
    asignacion = models.ForeignKey('docentes.Asignacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='inscripciones')
    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmada'),
            ('anulada', 'Anulada'),
        ],
        default='pendiente',
    )

    estado_pago = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('parcial', 'Parcial'),
            ('total', 'Total'),
        ],
        default='pendiente',
    )

    plan = models.ForeignKey('planes.Plan', on_delete=models.CASCADE, default=1)
    verificada = models.BooleanField(default=False)
    # Indica si la inscripción es provisional (pendiente de aprobación de pago).
    provisional = models.BooleanField(default=True, db_index=True)

    # Ya no se genera automáticamente; se rellenará al aprobar el pago en el admin
    access_code = models.CharField(
        max_length=16,
        unique=True,
        blank=True,
        null=True,
        help_text="Código de acceso para seguimiento/regularización del pago."
    )

    def save(self, *args, **kwargs):
        """
        Guardamos la inscripción sin forzar control de cupos aquí. La lógica de
        reserva y verificación de cupos se realiza en el flujo de pago para que
        la inscripción pueda permanecer provisional hasta la aprobación.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estudiante.apellidos}, {self.estudiante.nombres}"
    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"


class Matricula(models.Model):
    inscripcion = models.ForeignKey('estudiantes.Inscripcion', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)
    asignaciones = models.ManyToManyField(
        'docentes.Asignacion',
        blank=True,
        related_name='matriculas'
    )
    estado = models.CharField(
        max_length=20,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='inactivo',
    )
    monto_referencial = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fecha_creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Matrícula de {self.estudiante.apellidos}, {self.estudiante.nombres}"
    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
    @property
    def cursos_plan(self):
        if not self.inscripcion or not self.inscripcion.plan:
            return []
        return self.inscripcion.plan.cursos_base()
    def asignar_automaticamente_grupos(self):
        if self.estado != 'activo':
            return
        cursos = list(self.cursos_plan)
        if not cursos:
            return
        asignaciones_actuales = list(self.asignaciones.all())
        cursos_ya_asignados = {a.curso_id for a in asignaciones_actuales}

        for curso in cursos:
            if curso.id in cursos_ya_asignados:
                continue
            # elegir una asignacion del curso con cupos disponibles
            asignacion = (
                Asignacion.objects
                .filter(curso=curso)
                .annotate(num_matriculas=Count('matriculas'))
                .filter(num_matriculas__lt=models.F('cupo_maximo'))
                .order_by('num_matriculas', 'id')
                .first()
            )

            if asignacion:
                self.asignaciones.add(asignacion)