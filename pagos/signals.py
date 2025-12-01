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
    ins = getattr(pago, 'inscripcion', None)
    if ins is None:
        # Defensive: if for any reason the Pago lacks an Inscripcion, bail out.
        return
    # If created, attempt reservation on the Asignacion referenced by the Inscripcion
    if created:
        asign = getattr(ins, 'asignacion', None)
        if asign is None:
            # nothing to reserve
            return
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
                # idempotent add: use the asignacion instance itself
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
            try:
                ins.provisional = False
                ins.save(update_fields=['provisional'])
            except Exception:
                # If saving inscripcion fails, continue without raising
                pass
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
                        # remove asignacion reservation related to this inscripcion
                        try:
                            asign_id = getattr(ins, 'asignacion_id', None)
                            if asign_id:
                                # remove by id or by instance; use id for safety
                                matricula.asignaciones.remove(asign_id)
                        except Exception:
                            # ignore if not present
                            pass
                        # delete matricula
                        matricula.delete()
                    # keep reference to estudiante and apoderado before deleting inscripcion
                    est = getattr(ins, 'estudiante', None)
                    ap = getattr(est, 'apoderado', None) if est is not None else None
                    # delete inscripcion
                    try:
                        ins.delete()
                    except Exception:
                        pass
                    # if estudiante has no other inscripciones, delete estudiante
                    if est is not None:
                        try:
                            if not est.inscripcion_set.exists():
                                est.delete()
                                # if apoderado exists and has no other estudiantes, delete apoderado
                                if ap and not ap.estudiantes.exists():
                                    ap.delete()
                        except Exception:
                            pass
            except Exception:
                # best-effort rollback; don't raise
                pass
