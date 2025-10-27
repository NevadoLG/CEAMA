from django.db import transaction
from pagos.models import Pago, Comprobante

@transaction.atomic
def registrar_pago_con_comprobante(inscripcion, pago_cleaned_data, archivo):
    """
    Crea el Pago y, si hay archivo, crea el Comprobante.
    Además actualiza el estado_pago de la Inscripcion acorde al pago seleccionado.
    """
    pago = Pago.objects.create(
        inscripcion=inscripcion,
        monto=pago_cleaned_data['monto'],
        metodo=pago_cleaned_data['metodo'],
        estado=pago_cleaned_data['estado'], 
    )

    if archivo:
        Comprobante.objects.create(pago=pago, archivo=archivo)

    inscripcion.estado_pago = pago.estado
    inscripcion.save(update_fields=['estado_pago'])

    return pago
