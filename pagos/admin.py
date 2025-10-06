from django.contrib import admin
from .models import Pago, Comprobante

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'monto', 'metodo', 'fecha', 'estado')
    list_filter = ('metodo', 'estado')
    search_fields = ('inscripcion__estudiante__apellidos',)

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('pago', 'archivo')
