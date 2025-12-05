from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from estudiantes.models import Inscripcion, Estudiante, Matricula
from apoderados.models import Apoderado
from planes.models import Plan
from docentes.models import Asignacion
from types import SimpleNamespace
from django.db import transaction
from django.db.models import F
from .forms import (
    PagoForm,
    LookupCodeForm,
    ReenviarCodigoForm,
    RegularizacionForm,
)
from .models import Pago, Comprobante
from decimal import Decimal
from django.utils import timezone

# Session TTL for temporary inscripcion/apoderado data (seconds). 24 hours.
SESSION_TTL_SECONDS = 24 * 3600

MAX_FILES = 3
MAX_MB = 5  
ALLOWED_CT = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

def registrar_pago_con_comprobantes(inscripcion, cleaned_data, archivos):
    """
    Crea un pago con los datos dados y adjunta comprobantes.
    Retorna el Pago creado.
    """
    pago = Pago.objects.create(
        inscripcion=inscripcion,
        monto=cleaned_data["monto"],
        metodo=cleaned_data["metodo"],
        estado="pendiente",
        estado_solicitado=cleaned_data.get("estado", "parcial"),
    )
    for f in archivos:
        Comprobante.objects.create(pago=pago, archivo=f)
    return pago

def reenviar_codigo(request):
    form = ReenviarCodigoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()

        ins = (
            Inscripcion.objects
            .filter(estudiante__apoderado__correo__iexact=email)
            .order_by("-id")
            .first()
        )
        if not ins:
            messages.error(request, "No encontramos inscripciones asociadas a ese correo.")
        else:
            if not getattr(ins, "access_code", None):
                from django.utils.crypto import get_random_string
                ins.access_code = get_random_string(10).upper()
                ins.save(update_fields=["access_code"])

            from django.core.mail import send_mail
            path = reverse("pagos_regularizar_seguimiento", args=[ins.access_code])
            base = getattr(settings, "SITE_BASE_URL", "").rstrip("/")
            url = f"{base}{path}"

            subject = "CEAMA – Código de acceso para pagos"
            body = (
                "Hola,\n\n"
                f"Tu código de acceso es: {ins.access_code}\n"
                f"Puedes ver/regularizar pagos aquí:\n{url}\n\n"
                "CEAMA"
            )
            send_mail(
                subject,
                body,
                getattr(settings, "DEFAULT_FROM_EMAIL", None),
                [email],
                fail_silently=True,
            )

            messages.success(request, "Te enviamos el código a tu correo.")
            return redirect("pagos_regularizar_lookup")

    return render(request, "pagos/reenviar_codigo.html", {"form": form})

def regularizar_lookup(request):
    form = LookupCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"].strip().upper()
        return redirect("pagos_regularizar_seguimiento", code=code)
    return render(request, "pagos/regularizar_lookup.html", {"form": form})

def regularizar_seguimiento(request, code: str):
    ins = get_object_or_404(Inscripcion, access_code=code)
    pagos = ins.pago_set.select_related().order_by("-id")
    hay_pendiente = pagos.filter(estado="pendiente").exists()

    puede_subir = (getattr(ins, "estado_pago", "pendiente") != "total") and (not hay_pendiente)

    if request.method == "POST":
        if not puede_subir:
            return HttpResponseBadRequest("Ya existe un comprobante pendiente de validación o el pago está completado.")

        form = RegularizacionForm(request.POST) 
        archivos = request.FILES.getlist("archivos")

        # Validaciones de archivos (servidor)
        if not archivos:
            form.add_error(None, "Adjunta al menos un comprobante (PDF o imagen).")
        elif len(archivos) > MAX_FILES:
            form.add_error(None, f"Solo se permiten {MAX_FILES} archivos.")
        else:
            for f in archivos:
                if f.content_type not in ALLOWED_CT:
                    form.add_error(None, "Solo PDF o imágenes (JPG/PNG/WEBP/GIF).")
                    break
                if f.size > MAX_MB * 1024 * 1024:
                    form.add_error(None, f"Cada archivo debe pesar ≤ {MAX_MB} MB.")
                    break

        if form.is_valid():
            pago = Pago.objects.create(
                inscripcion=ins,
                monto=form.cleaned_data["monto"],
                metodo=form.cleaned_data["metodo"],
                estado="pendiente",
                estado_solicitado="completado",
            )
            for f in archivos:
                Comprobante.objects.create(pago=pago, archivo=f)

            messages.success(
                request,
                "Comprobante enviado. Queda pendiente de validación por administración."
            )
            return redirect("pagos_regularizar_seguimiento", code=code)
    else:
        form = RegularizacionForm()

    return render(
        request,
        "pagos/regularizar_seguimiento.html",
        {
            "inscripcion": ins,
            "pagos": pagos,
            "puede_subir": puede_subir,   
            "hay_pendiente": hay_pendiente,
            "form": form,
            "MAX_FILES": MAX_FILES,
        },
    )

def registrar_pago(request):
    inscripcion = None
    inscripcion_id = request.GET.get("inscripcion_id") or request.POST.get("inscripcion_id")
    if inscripcion_id:
        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
    else:
        estudiante_id = request.session.get("estudiante_id")
        if estudiante_id:
            est = get_object_or_404(Estudiante, id=estudiante_id)
            inscripcion = Inscripcion.objects.filter(estudiante=est).order_by("-id").first()

    # If no persisted inscripcion provided, check for session-based data
    ses_ins = request.session.get('ceama_inscripcion')
    ses_apod = request.session.get('ceama_apoderado')

    # If neither a persisted inscripcion nor session data exist, it's an error
    if not inscripcion and not (ses_ins and ses_apod):
        return HttpResponseBadRequest("Falta inscripcion_id o no se pudo derivar desde la sesión.")

    # If session data exists, verify TTL (created_at) and expire if older than TTL
    if ses_ins and isinstance(ses_ins, dict):
        created = ses_ins.get('created_at')
        if not created:
            # Treat as expired if no timestamp
            request.session.pop('ceama_inscripcion', None)
            request.session.pop('ceama_apoderado', None)
            messages.error(request, 'Los datos temporales expiraron. Por favor reingresa el formulario.')
            return redirect(reverse('registrar_estudiante'))
        now_ts = timezone.now().timestamp()
        if now_ts - float(created) > SESSION_TTL_SECONDS:
            request.session.pop('ceama_inscripcion', None)
            request.session.pop('ceama_apoderado', None)
            request.session.modified = True
            messages.error(request, 'Los datos temporales expiraron (más de 24 horas). Por favor reingresa el formulario.')
            return redirect(reverse('registrar_estudiante'))

    if inscripcion:
        pagos_previos = inscripcion.pago_set.select_related().order_by("-id")
        last_pago = pagos_previos.first()

        # Obtener matrícula y asignaciones relacionadas (si existen)
        matricula = (
            Matricula.objects
            .filter(inscripcion=inscripcion)
            .prefetch_related(
                'asignaciones__plan',
                'asignaciones__profesores',
                'asignaciones__aula',
                'asignaciones__horario',
                'asignaciones__horario__dias',
            )
            .first()
        )
        asignaciones = list(matricula.asignaciones.all()) if matricula else []
    else:
        pagos_previos = []
        last_pago = None
        matricula = None
        asignaciones = []

    if request.method == "GET":
        pagado = request.GET.get("ok") == "1"

        # If we have session data but no persisted inscripcion, build a preview
        session_preview = None
        if not inscripcion and ses_ins:
            session_preview = {
                'inscripcion': ses_ins,
                'apoderado': ses_apod,
            }
            # fetch asignacion details for display if provided
            asignacion_obj = None
            if ses_ins.get('asignacion_id'):
                try:
                    asignacion_obj = Asignacion.objects.select_related(
                        'plan', 'aula', 'horario'
                    ).prefetch_related('horario__dias', 'profesores').get(pk=ses_ins['asignacion_id'])
                    session_preview['asignacion_obj'] = asignacion_obj
                except Asignacion.DoesNotExist:
                    session_preview['asignacion_obj'] = None

            # Build lightweight preview objects so the template can render similarly
            # to a persisted Inscripcion + Matricula.
            if session_preview:
                # dummy pago_set with all() -> empty list
                class _DummyPagoSet:
                    def all(self_inner):
                        return []

                estudiante_ns = SimpleNamespace(
                    apellidos=ses_ins.get('apellidos', ''),
                    nombres=ses_ins.get('nombres', ''),
                )
                # plan: prefer asignacion.plan if available, else try plan_id from session
                plan_obj = None
                if asignacion_obj and getattr(asignacion_obj, 'plan', None):
                    plan_obj = asignacion_obj.plan
                else:
                    plan_id = ses_ins.get('plan_id')
                    if plan_id:
                        plan_obj = Plan.objects.filter(pk=plan_id).first()

                ins_preview = SimpleNamespace(
                    estudiante=estudiante_ns,
                    plan=plan_obj,
                    estado_pago=ses_ins.get('estado_pago', 'pendiente'),
                    pago_set=_DummyPagoSet(),
                )

                # expose these into the locals used by the template
                inscripcion = ins_preview
                asignaciones = [asignacion_obj] if asignacion_obj else []

        return render(
            request,
            "pagos/registrar_pago.html",
            {
                "inscripcion": inscripcion,
                "matricula": matricula,
                "asignaciones": asignaciones,
                "pago_form": PagoForm(),
                "pagado": pagado,
                "last_pago": last_pago,
                "MAX_FILES": MAX_FILES,
                "session_preview": session_preview,
            },
        )

    pago_form = PagoForm(request.POST)
    archivos = request.FILES.getlist("archivos")

    if pago_form.is_valid():
        if not archivos:
            pago_form.add_error(None, "Debes adjuntar al menos un comprobante (PDF o imagen).")
        elif len(archivos) > MAX_FILES:
            pago_form.add_error(None, f"Solo se permiten {MAX_FILES} comprobantes por pago.")
        else:
            for f in archivos:
                if f.content_type not in ALLOWED_CT:
                    pago_form.add_error(None, "Solo PDF o imágenes (JPG/PNG/WEBP/GIF).")
                    break
                if f.size > MAX_MB * 1024 * 1024:
                    pago_form.add_error(None, f"Cada archivo debe pesar ≤ {MAX_MB} MB.")
                    break
        if pago_form.is_valid():
            if inscripcion:
                registrar_pago_con_comprobantes(inscripcion, pago_form.cleaned_data, archivos)
                messages.success(
                    request,
                    "Pago registrado. Queda pendiente de confirmación por administración."
                )
                return redirect(f"{reverse('registrar_pago')}?inscripcion_id={inscripcion.id}&ok=1")

            if not ses_ins or not ses_apod:
                pago_form.add_error(None, "Falta información del estudiante o apoderado. Reinicia el proceso.")
            else:
                try:
                    with transaction.atomic():
                        # Apoderado: reuse by DNI if exists
                        apod = None
                        if ses_apod.get('dni'):
                            apod = Apoderado.objects.filter(dni=ses_apod['dni']).first()
                        if apod:
                            # update contact fields if changed
                            apod.nombres = ses_apod.get('nombres') or apod.nombres
                            apod.apellidos = ses_apod.get('apellidos') or apod.apellidos
                            apod.telefono = ses_apod.get('telefono') or apod.telefono
                            apod.correo = ses_apod.get('correo') or apod.correo
                            apod.direccion = ses_apod.get('direccion') or apod.direccion
                            apod.save(update_fields=['nombres','apellidos','telefono','correo','direccion'])
                        else:
                            apod = Apoderado.objects.create(
                                dni=ses_apod.get('dni'),
                                nombres=ses_apod.get('nombres'),
                                apellidos=ses_apod.get('apellidos'),
                                telefono=ses_apod.get('telefono'),
                                correo=ses_apod.get('correo'),
                                direccion=ses_apod.get('direccion'),
                            )

                        # Determine plan similarly to previous logic
                        plan = None
                        plan_id = ses_ins.get('plan_id')
                        asignacion_id = ses_ins.get('asignacion_id')
                        if plan_id:
                            plan = Plan.objects.filter(pk=plan_id).first()
                        if not plan and asignacion_id:
                            try:
                                asig_tmp = Asignacion.objects.select_related('plan').get(pk=asignacion_id)
                                plan = getattr(asig_tmp, 'plan', None)
                            except Asignacion.DoesNotExist:
                                plan = None
                        if not plan:
                            plan = Plan.objects.first()

                        # Create Estudiante
                        estudiante = Estudiante.objects.create(
                            nombres=ses_ins.get('nombres'),
                            apellidos=ses_ins.get('apellidos'),
                            grado=ses_ins.get('grado'),
                            colegio=ses_ins.get('colegio'),
                            edad=ses_ins.get('edad'),
                            apoderado=apod,
                        )

                        # Create Inscripcion and Matricula
                        inscripcion = Inscripcion.objects.create(estudiante=estudiante, plan=plan)
                        matricula = Matricula.objects.create(inscripcion=inscripcion, estudiante=estudiante)

                        # Reserve asignacion if provided
                        if asignacion_id:
                            asignacion = Asignacion.objects.select_for_update().get(pk=asignacion_id)
                            # Check cupo (assume cupo_maximo and relation via matriculas)
                            current = asignacion.matriculas.count()
                            if getattr(asignacion, 'cupo_maximo', None) is not None and current >= asignacion.cupo_maximo:
                                raise ValueError('La asignación seleccionada ya no tiene cupos disponibles.')
                            # add to matricula
                            matricula.asignaciones.add(asignacion)
                            inscripcion.asignacion = asignacion
                            inscripcion.save(update_fields=['asignacion'])

                        # Create Pago and attach comprobantes
                        pago = registrar_pago_con_comprobantes(inscripcion, pago_form.cleaned_data, archivos)

                    # If we reach here, transaction committed successfully
                    # Clear session data used for the flow
                    request.session.pop('ceama_inscripcion', None)
                    request.session.pop('ceama_apoderado', None)
                    request.session.modified = True

                    messages.success(request, "Pago registrado. Queda pendiente de confirmación por administración.")
                    return redirect(f"{reverse('registrar_pago')}?inscripcion_id={inscripcion.id}&ok=1")
                except Exception as e:
                    pago_form.add_error(None, f"No se pudo completar el registro: {e}")

    return render(
        request,
        "pagos/registrar_pago.html",
        {
            "inscripcion": inscripcion,
            "matricula": matricula,
            "asignaciones": asignaciones,
            "pago_form": pago_form,
            "pagado": False,
            "last_pago": last_pago,
            "MAX_FILES": MAX_FILES,
        },
        status=400,
    )
def clean_monto(self):
    val = self.cleaned_data["monto"]
    if val > Decimal("999.99"):
        return Decimal("999.99")
    return val