from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apoderados.models import Apoderado  
from django.conf import settings

class VerificacionToken(models.Model):
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.CASCADE,
        related_name='tokens'
    )
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
    edad = models.PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(20)])
    grado = models.CharField(max_length=10, choices=GRADOS)
    colegio = models.CharField(max_length=150)
    apoderado = models.ForeignKey(Apoderado, on_delete=models.PROTECT, related_name='estudiantes', null=True, blank=True)

class Inscripcion(models.Model):
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)
    curso = models.ForeignKey('docentes.Curso', on_delete=models.PROTECT, null=True, blank=True)
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
    # 🔹 Validación de disponibilidad de cupos al guardar
    def save(self, *args, **kwargs):
        from planes.models import Plan  # import interno para evitar ciclos

        with transaction.atomic():
            plan = Plan.objects.select_for_update().get(pk=self.plan_id)
            ocupados = plan.inscripcion_set.exclude(pk=self.pk).count()

            if ocupados >= plan.cupo_maximo:
                raise ValidationError(
                    f"No hay cupos disponibles para el plan: "
                    f"{plan.get_nivel_display()} - {plan.get_area_display()}."
                )

            super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.estudiante.apellidos}, {self.estudiante.nombres}"

class Matricula(models.Model):
    inscripcion = models.ForeignKey('estudiantes.Inscripcion', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('estudiantes.Estudiante', on_delete=models.CASCADE)  # 👈 Esta línea debe existir
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo')
        ]
    )
    monto_referencial = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fecha_creada = models.DateTimeField(auto_now_add=True)
    # usuario_registra eliminado

    def __str__(self):
        return f"Matrícula de {self.estudiante.apellidos}, {self.estudiante.nombres}"