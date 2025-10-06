from django.contrib import admin
from .models import Estudiante, Inscripcion

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'grado', 'edad', 'colegio', 'apoderado')
    search_fields = ('apellidos', 'nombres', 'colegio')
    list_filter = ('grado',)

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'usuario_registra', 'fecha', 'estado_pago')
    list_filter = ('estado_pago', 'curso')
    search_fields = ('estudiante__apellidos', 'estudiante__nombres')
