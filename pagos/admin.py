from django.contrib import admin
from .models import Pago, Comprobante

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'inscripcion', 'monto', 'metodo', 'estado', 'fecha')
    list_filter = ('metodo', 'estado', 'fecha')
    search_fields = ('inscripcion__estudiante__apellidos', 'inscripcion__estudiante__nombres')

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'pago', 'archivo')
