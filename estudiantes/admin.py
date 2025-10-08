from django.contrib import admin
from .models import Estudiante, Inscripcion, Matricula


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
        'usuario_registra',
        'estado_pago',
        'fecha'
    )
    list_filter = ('estado_pago', 'plan', 'curso')
    search_fields = (
        'estudiante__nombres',
        'estudiante__apellidos',
        'usuario_registra__username'
    )
    ordering = ('-fecha',)
    autocomplete_fields = ('estudiante', 'curso', 'plan')


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'estado', 'monto_referencial', 'fecha_creada', 'usuario_registra')
    list_filter = ('estado',)
    search_fields = ('inscripcion__estudiante__apellidos', 'inscripcion__estudiante__nombres')
    ordering = ('-fecha_creada',)

