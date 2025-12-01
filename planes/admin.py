from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'descripcion_short', 'activo')
    list_filter = ('nivel','activo')
    search_fields = ('nombre',)
    def descripcion_short(self, obj):
        return (obj.descripcion[:60] + '...') if obj.descripcion and len(obj.descripcion) > 60 else (obj.descripcion or '')
    descripcion_short.short_description = 'Descripción'
