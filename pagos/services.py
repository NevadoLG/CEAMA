from django.db import transaction
from .models import Pago, Comprobante

def _mapear_estado_inscripcion_desde_pago(estado_pago_real: str) -> str:
    if estado_pago_real == 'completado':
        return 'total'
    if estado_pago_real == 'parcial':
        return 'parcial'
    return 'pendiente'

@transaction.atomic
def registrar_pago_con_comprobantes(inscripcion, pago_data, archivos_list):
    """
    Crea un Pago nuevo SIEMPRE en 'pendiente' y coloca lo que el apoderado eligió
    (parcial/completado) en estado_solicitado.
    """
    pago = Pago.objects.create(
        inscripcion=inscripcion,
        monto=pago_data['monto'],
        metodo=pago_data['metodo'],
        estado='pendiente',
        estado_solicitado=pago_data['estado'],  # lo que eligió el apoderado
    )

    for f in (archivos_list or []):
        Comprobante.objects.create(pago=pago, archivo=f)

    # Al registrar, la inscripción queda pendiente hasta que el admin apruebe/rechace
    inscripcion.estado_pago = _mapear_estado_inscripcion_desde_pago(pago.estado)
    inscripcion.save(update_fields=['estado_pago'])

    return pago
