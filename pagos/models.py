from django.db import models

class Pago(models.Model):
    inscripcion = models.ForeignKey('estudiantes.Inscripcion', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=[('transferencia','Transferencia'),('yape','Yape'),('plin','Plin')])
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=[('pendiente','Pendiente'),('completado','Completado')])

class Comprobante(models.Model):
    pago = models.OneToOneField('pagos.Pago', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='comprobantes/', blank=True, null=True)
