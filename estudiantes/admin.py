from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse 
import csv 
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
        'estado',
        'estado_pago',
        'fecha'
    )
    list_filter = ('estado_pago', 'estado')
    search_fields = (
        'estudiante__nombres',
        'estudiante__apellidos',
    )
    ordering = ('-fecha',)
    autocomplete_fields = ('estudiante',)
    readonly_fields = ('fecha',)
    # Remove curso and plan from the Inscripcion CRUD: Asignacion already
    # embeds course/plan information and Matricula holds confirmed plan.
    exclude = ('curso', 'plan')

class AsignacionInline(admin.TabularInline):
    model = Matricula.asignaciones.through
    extra = 0
    verbose_name = "Asignación"
    verbose_name_plural = "Asignaciones"
    can_delete = False


class AsignacionFilter(SimpleListFilter):
    title = 'Asignación'
    parameter_name = 'asignacion'

    def lookups(self, request, model_admin):
        asigns = Asignacion.objects.all().order_by('plan__nombre')
        return [(str(a.id), str(a)) for a in asigns]

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            return queryset.filter(asignaciones__id=val)
        return queryset

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'estado', 'monto_referencial', 'cursos_del_plan', 'fecha_creada')
    list_filter = (AsignacionFilter, 'estado',)
    search_fields = ('inscripcion__estudiante__apellidos', 'inscripcion__estudiante__nombres')
    ordering = ('-fecha_creada',)
    filter_horizontal = ('asignaciones',)
    inlines = [AsignacionInline]
    actions = ['exportar_matriculas_csv']
    def exportar_matriculas_csv(self, request, queryset):
        """
        Exporta a CSV las matrículas seleccionadas (respeta filtros del admin).
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="matriculas_ceama.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Nombre del estudiante",
            "Estado de matrícula",
            "Monto referencial",
            "Fecha de creación",
            "Asignaciones (curso / docente / aula / horario)",
        ])

        for m in queryset:
            est = m.estudiante
            nombre_estudiante = f"{est.apellidos}, {est.nombres}"
            monto = f"{m.monto_referencial:.2f}" if m.monto_referencial is not None else ""
            fecha = m.fecha_creada.strftime("%Y-%m-%d %H:%M") if m.fecha_creada else ""
            asignaciones_texto = "; ".join(str(a) for a in m.asignaciones.all())

            writer.writerow([
                nombre_estudiante,
                m.estado,
                monto,
                fecha,
                asignaciones_texto,
            ])
        return response
    exportar_matriculas_csv.short_description = "Exportar listado a CSV"
    def cursos_del_plan(self, obj):
        cursos = obj.cursos_plan
        if not cursos:
            return "—"
        return ", ".join(c.nombre for c in cursos)
    cursos_del_plan.short_description = "Cursos del plan"