from django.contrib import admin
from .models import Curso

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'plan', 'cupo_maximo')
    list_filter = ('nivel', 'plan')
    search_fields = ('nombre',)
