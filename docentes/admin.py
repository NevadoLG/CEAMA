from django.contrib import admin
from .models import Curso, Profesor, Aula, Horario, Asignacion

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'plan', 'cupo_maximo')
    list_filter = ('nivel', 'plan')
    search_fields = ('nombre',)

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
    list_display = ('dia','hora_inicio','hora_fin')
    list_filter = ('dia',)

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('profesor','curso','aula','horario','fecha_inicio','fecha_fin')
    list_filter = ('curso','profesor','aula','horario')
    search_fields = ('profesor__apellidos','profesor__nombres','curso__nombre')
