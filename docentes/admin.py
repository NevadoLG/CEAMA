from django.contrib import admin
from .models import Curso, Profesor, Aula, Horario, Asignacion, Dia
from django.db.models import Count

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion_short')
    list_filter = ()
    search_fields = ('nombre',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    def descripcion_short(self, obj):
        return (obj.descripcion[:60] + '...') if obj.descripcion and len(obj.descripcion) > 60 else (obj.descripcion or '')
    descripcion_short.short_description = 'Descripción'
    
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
    list_display = ('plan','profesores_list','aula','horario','grado','fecha_inicio','fecha_fin', 'cupos', 'precio')
    list_filter = ('plan','profesores','aula','horario','grado')
    search_fields = ('profesores__apellidos','profesores__nombres','plan__nombre')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(num_matriculas=Count('matriculas'))
    def profesores_list(self, obj):
        profs = ', '.join(str(p) for p in obj.profesores.all())
        return profs or '—'
    profesores_list.short_description = 'Profesor(es)'
    def cupos(self, obj):
        maximo = getattr(obj, 'cupo_maximo', None)
        usados = getattr(obj, 'num_matriculas', 0)
        return f"{usados}/{maximo if maximo is not None else '—'}"

    cupos.short_description = "Cupos usados"


@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    list_display = ('codigo',)
    search_fields = ('codigo',)