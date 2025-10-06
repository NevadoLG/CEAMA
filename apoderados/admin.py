from django.contrib import admin
from .models import Apoderado

@admin.register(Apoderado)
class ApoderadoAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'telefono', 'correo', 'direccion')
    search_fields = ('apellidos', 'nombres', 'telefono')
