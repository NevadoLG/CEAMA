from django.db import models
from django.utils import timezone

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
    ]
    ESTADO_SOLICITADO_CHOICES = [
        ('parcial', 'Parcial'),
        ('completado', 'Completado'),
    ]

    inscripcion = models.ForeignKey('estudiantes.Inscripcion', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    metodo = models.CharField(
        max_length=20,
        choices=[('transferencia', 'Transferencia'), ('yape', 'Yape'), ('plin', 'Plin')]
    )
    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', db_index=True)

    estado_solicitado = models.CharField(
        max_length=20,
        choices=ESTADO_SOLICITADO_CHOICES,
        default='parcial',
        help_text="Lo que el apoderado indicó (parcial o completado). No cambia a menos que lo edites."
    )

    def aprobar(self):
        """Usado por el Admin: pasa el estado real a lo que solicitó el apoderado."""
        self.estado = self.estado_solicitado
        self.save(update_fields=['estado'])

    def rechazar(self):
        self.estado = 'rechazado'
        self.save(update_fields=['estado'])


class Comprobante(models.Model):
    pago = models.ForeignKey('Pago', on_delete=models.CASCADE, related_name='comprobantes')
    archivo = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
