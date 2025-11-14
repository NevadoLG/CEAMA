from django.contrib import admin
from .models import Estudiante, Inscripcion, Matricula
from docentes.models import Asignacion

class MatriculaInline(admin.StackedInline):
    model = Matricula
    extra = 0
    can_delete = False
    readonly_fields = ('fecha_creada',)
    verbose_name_plural = "Matrículas asociadas"


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'grado', 'edad', 'colegio', 'apoderado')
    search_fields = ('apellidos', 'nombres', 'colegio', 'apoderado__nombres')
    list_filter = ('grado',)
    ordering = ('apellidos', 'nombres')
    inlines = [MatriculaInline]


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'estudiante',
        'plan',
        'curso',
        'estado_pago',
        'fecha'
    )
    list_filter = ('estado_pago', 'plan', 'curso')
    search_fields = (
        'estudiante__nombres',
        'estudiante__apellidos',
    )
    ordering = ('-fecha',)
    autocomplete_fields = ('estudiante', 'curso', 'plan')

class AsignacionInline(admin.TabularInline):
    model = Matricula.asignaciones.through
    extra = 0
    verbose_name = "Asignación"
    verbose_name_plural = "Asignaciones"
    can_delete = False

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'estado', 'monto_referencial', 'fecha_creada')
    list_filter = ('estado',)
    search_fields = ('inscripcion__estudiante__apellidos', 'inscripcion__estudiante__nombres')
    ordering = ('-fecha_creada',)
    filter_horizontal = ('asignaciones',)
    inlines = [AsignacionInline]

