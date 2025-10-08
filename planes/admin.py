from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'area', 'cupo_maximo', 'activo')
    list_filter = ('nivel', 'area', 'activo')
    search_fields = ('nombre',)
