from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pago
from estudiantes.models import Matricula, Estudiante, Inscripcion
from django.core.exceptions import ObjectDoesNotExist

@receiver(post_save, sender=Pago)
def pago_post_save(sender, instance: Pago, created, **kwargs):
    """
    - On creation: try to reserve the asignacion (add to Matricula) if Inscripcion has asignacion.
    - On state change to 'rechazado': if inscripcion is provisional, rollback (delete inscripcion, matricula, estudiante if appropriate).
    - On state change to 'parcial' or 'completado': finalize provisional inscription.
    """
    pago = instance
    ins = pago.inscripcion

    # If created, attempt reservation
    if created:
        asign = getattr(ins, 'asignacion', None)
        if asign is None:
            # nothing to reserve
            return
        # Reserve atomically: lock the related curso row to avoid race conditions
        curso = asign.curso
        try:
            with transaction.atomic():
                # Lock the asignacion row to prevent concurrent reservations
                from docentes.models import Asignacion
                Asignacion.objects.select_for_update().get(pk=asign.pk)
                # count current ocupados for this asignacion
                ocupados = asign.matriculas.count()
                if ocupados >= asign.cupo_maximo:
                    # no cupos -> mark pago as rechazado
                    pago.estado = 'rechazado'
                    pago.save(update_fields=['estado'])
                    return
                # obtain or create matricula for this inscripcion
                matricula, _ = Matricula.objects.get_or_create(
                    inscripcion=ins,
                    estudiante=ins.estudiante,
                )
                # idempotent add
                matricula.asignaciones.add(asign)
                matricula.save()
        except Exception:
            # If reservation fails unexpectedly, mark pago as rechazado to be safe
            pago.estado = 'rechazado'
            pago.save(update_fields=['estado'])
            return

    # Handle state transitions: finalize or rollback
    if pago.estado in ('parcial', 'completado'):
        # finalize: mark inscription as not provisional
        if getattr(ins, 'provisional', False):
            ins.provisional = False
            ins.save(update_fields=['provisional'])
            # activate matricula if exists
            try:
                matricula = Matricula.objects.filter(inscripcion=ins).first()
                if matricula:
                    matricula.estado = 'activo'
                    matricula.save(update_fields=['estado'])
            except Exception:
                pass

    if pago.estado == 'rechazado':
        # rollback provisional inscription
        if getattr(ins, 'provisional', False):
            try:
                with transaction.atomic():
                    # remove asignacion reservation from matricula if present
                    matricula = Matricula.objects.filter(inscripcion=ins).first()
                    if matricula:
                        # remove asignaciones related to this inscripcion
                        if ins.asignacion_id:
                            matricula.asignaciones.remove(ins.asignacion_id)
                        # delete matricula
                        matricula.delete()
                    # keep reference to estudiante and apoderado before deleting inscripcion
                    est = ins.estudiante
                    ap = getattr(est, 'apoderado', None)
                    # delete inscripcion
                    ins.delete()
                    # if estudiante has no other inscripciones, delete estudiante
                    if not est.inscripcion_set.exists():
                        est.delete()
                        # if apoderado exists and has no other estudiantes, delete apoderado
                        if ap and not ap.estudiantes.exists():
                            ap.delete()
            except Exception:
                # best-effort rollback; don't raise
                pass
