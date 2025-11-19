from django.contrib import admin
from .models import Curso, Profesor, Aula, Horario, Asignacion, Dia
from django.db.models import Count

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'plan', 'total_matriculados', 'capacidad_total')
    list_filter = ('nivel', 'plan')
    search_fields = ('nombre',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(num_matriculas_total=Count('asignacion__matriculas', distinct=True))

    def total_matriculados(self, obj):
        return getattr(obj, 'num_matriculas_total', 0)
    total_matriculados.short_description = "Matriculados"

    def capacidad_total(self, obj):
        # suma las capacidades definidas en las asignaciones del curso
        return sum(a.cupo_maximo for a in obj.asignacion_set.all())
    capacidad_total.short_description = "Capacidad total"
@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'telefono', 'correo', 'activo')
    list_filter = ('activo',)
    search_fields = ('apellidos','nombres','correo')

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('nombre','capacidad')
    search_fields = ('nombre',)

@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('dias_summary','hora_inicio','hora_fin')
    list_filter = ('dias',)
    def dias_summary(self, obj):
        return ", ".join([d.get_codigo_display() for d in obj.dias.all()])
    dias_summary.short_description = "Días"
    # Mostrar selector M2M amigable
    filter_horizontal = ('dias',)

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('profesor','curso','aula','horario','fecha_inicio','fecha_fin', 'cupos')
    list_filter = ('curso','profesor','aula','horario')
    search_fields = ('profesor__apellidos','profesor__nombres','curso__nombre')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(num_matriculas=Count('matriculas'))
    def cupos(self, obj):
        maximo = getattr(obj, 'cupo_maximo', None)
        usados = getattr(obj, 'num_matriculas', 0)
        return f"{usados}/{maximo if maximo is not None else '—'}"

    cupos.short_description = "Cupos usados"


@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    list_display = ('codigo',)
    search_fields = ('codigo',)