from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

from estudiantes.models import Inscripcion, Estudiante, Matricula
from .forms import (
    PagoForm,
    LookupCodeForm,
    ReenviarCodigoForm,
    RegularizacionForm,
)
from .models import Pago, Comprobante
from decimal import Decimal

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
            .filter(estudiante__apoderado__email__iexact=email)
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

    if not inscripcion:
        return HttpResponseBadRequest("Falta inscripcion_id o no se pudo derivar desde la sesión.")

    pagos_previos = inscripcion.pago_set.select_related().order_by("-id")
    last_pago = pagos_previos.first()

    # Obtener matrícula y asignaciones relacionadas (si existen)
    matricula = (
        Matricula.objects
        .filter(inscripcion=inscripcion)
        .prefetch_related(
            'asignaciones__curso',
            'asignaciones__profesor',
            'asignaciones__aula',
            'asignaciones__horario',
            'asignaciones__horario__dias',
        )
        .first()
    )
    asignaciones = list(matricula.asignaciones.all()) if matricula else []

    if request.method == "GET":
        pagado = request.GET.get("ok") == "1"
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
            },
        )

    pago_form = PagoForm(request.POST)
    archivos = request.FILES.getlist("archivos")

    if pago_form.is_valid():
        if len(archivos) == 0:
            pago_form.add_error(None, "Debes adjuntar al menos un comprobante (PDF o imagen).")
        elif len(archivos) > MAX_FILES:
            pago_form.add_error(None, f"Solo se permiten {MAX_FILES} comprobantes por pago.")
        else:
            registrar_pago_con_comprobantes(inscripcion, pago_form.cleaned_data, archivos)
            messages.success(
                request,
                "Pago registrado. Queda pendiente de confirmación por administración."
            )
            return redirect(f"{reverse('registrar_pago')}?inscripcion_id={inscripcion.id}&ok=1")

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