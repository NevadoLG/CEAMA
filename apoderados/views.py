from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Apoderado
from estudiantes.models import Estudiante, Inscripcion
from django.utils import timezone


def _resolver_inscripcion(request):
    """
    Intenta encontrar la Inscripcion por:
    1) inscripcion_id en GET/POST
    2) estudiante_id guardado en sesión (toma la última inscripción de ese estudiante)
    """
    inscripcion_id = request.GET.get("inscripcion_id") or request.POST.get("inscripcion_id")
    if inscripcion_id:
        return (Inscripcion.objects
                .filter(id=inscripcion_id)
                .select_related("estudiante")
                .first())

    est_id = request.session.get("estudiante_id")
    if est_id:
        est = Estudiante.objects.filter(id=est_id).first()
        if est:
            return (Inscripcion.objects
                    .filter(estudiante=est)
                    .order_by("-id")
                    .select_related("estudiante")
                    .first())
    return None


def registrar_apoderado(request):
    """
    Crea o reutiliza un Apoderado, pero:
    - DNI es obligatorio y único
    - Teléfono también debe ser único
    - Si hay duplicados en DNI o teléfono => mensaje rojo y NO se crea ni actualiza
    - Si todo bien, vincula al estudiante y redirige al paso de pago
    """
    inscripcion = _resolver_inscripcion(request)

    if request.method == "POST":
        dni = (request.POST.get("dni") or "").strip()
        data = {
            "nombres":   (request.POST.get("nombres") or "").strip(),
            "apellidos": (request.POST.get("apellidos") or "").strip(),
            "telefono":  (request.POST.get("telefono") or "").strip(),
            "correo":    (request.POST.get("correo") or "").strip(),
            "direccion": (request.POST.get("direccion") or "").strip(),
        }

        # Prebuild redirect URL (preserve inscripcion_id if present)
        redirect_url = reverse("registrar_apoderado") + (
            f"?inscripcion_id={inscripcion.id}" if inscripcion else ""
        )

        # Server-side validations requested:
        # - DNI: exactly 8 numeric digits
        # - Nombres / Apellidos: max 30 chars
        # - Telefono: exactly 9 numeric digits
        # - Correo: max 50 chars (if provided)
        # - Direccion: max 50 chars (if provided)
        if not dni:
            messages.error(request, "El DNI es obligatorio.")
            return redirect(redirect_url)

        if not dni.isdigit() or len(dni) != 8:
            messages.error(request, "El DNI debe tener exactamente 8 dígitos numéricos.")
            return redirect(redirect_url)

        # Rechazar espacios en cualquier posición del DNI
        if any(c.isspace() for c in dni):
            messages.error(request, "El DNI no puede contener espacios en blanco.")
            return redirect(redirect_url)

        if len(data["nombres"]) > 30:
            messages.error(request, "Los nombres no pueden exceder 30 caracteres.")
            return redirect(redirect_url)

        if len(data["apellidos"]) > 30:
            messages.error(request, "Los apellidos no pueden exceder 30 caracteres.")
            return redirect(redirect_url)

        est_nom = ""
        est_ape = ""

        if inscripcion and getattr(inscripcion, "estudiante", None):
            # Caso en que ya existe el estudiante en BD
            est_nom = (inscripcion.estudiante.nombres or "").strip().lower()
            est_ape = (inscripcion.estudiante.apellidos or "").strip().lower()
        else:
            # Caso del flujo por sesión (aún no existe en BD)
            ses_ins = request.session.get("ceama_inscripcion") or {}
            est_nom = (ses_ins.get("nombres") or "").strip().lower()
            est_ape = (ses_ins.get("apellidos") or "").strip().lower()

        apod_nom = data["nombres"].strip().lower()
        apod_ape = data["apellidos"].strip().lower()

        if est_nom and est_ape and apod_nom and apod_ape:
            if est_nom == apod_nom and est_ape == apod_ape:
                messages.error(
                    request,
                    "El apoderado no puede tener exactamente el mismo nombre y apellidos que el estudiante."
                )
                return redirect(redirect_url)

        telefono = data["telefono"]
        if not telefono:
            messages.error(request, "El teléfono es obligatorio.")
            return redirect(redirect_url)

        # Rechazar espacios en el teléfono y asegurar solo dígitos
        if any(c.isspace() for c in telefono):
            messages.error(request, "El teléfono no puede contener espacios en blanco.")
            return redirect(redirect_url)

        if not telefono.isdigit() or len(telefono) != 9:
            messages.error(request, "El teléfono debe contener exactamente 9 dígitos numéricos (sin código de país).")
            return redirect(redirect_url)

        if data["correo"] and len(data["correo"]) > 50:
            messages.error(request, "El correo no puede exceder 50 caracteres.")
            return redirect(redirect_url)

        if data["direccion"] and len(data["direccion"]) > 50:
            messages.error(request, "La dirección no puede exceder 50 caracteres.")
            return redirect(redirect_url)

        # Validaciones básicas
        if not dni:
            messages.error(request, "El DNI es obligatorio.")
            # PRG para limpiar el formulario
            return redirect(reverse("registrar_apoderado") + (
                f"?inscripcion_id={inscripcion.id}" if inscripcion else ""
            ))

        # Check for existing conflicts (telefono) to avoid obvious collisions
        apod_por_dni = Apoderado.objects.filter(dni=dni).first()
        tel_qs = Apoderado.objects.filter(telefono=telefono)
        if apod_por_dni:
            tel_qs = tel_qs.exclude(id=apod_por_dni.id)
        apod_por_tel = tel_qs.first()
        if apod_por_tel:
            messages.error(request, "El teléfono ya ha sido registrado previamente.")
            return redirect(redirect_url)

        # Save apoderado data in session (do NOT persist to DB yet). The actual
        # Apoderado / Estudiante / Inscripcion / Pago objects will be created
        # when the user submits the payment (Registrar pago).
        request.session['ceama_apoderado'] = {
            'dni': dni,
            'nombres': data['nombres'],
            'apellidos': data['apellidos'],
            'telefono': data['telefono'],
            'correo': data['correo'],
            'direccion': data['direccion'],
            'created_at': timezone.now().timestamp(),
        }
        request.session.modified = True

        messages.success(request, 'Datos del apoderado guardados temporalmente. Continúa con el pago.')
        return redirect(reverse('registrar_pago'))

    # GET
    apoderados = Apoderado.objects.all().order_by("-id")
    return render(
        request,
        "apoderados/registrar_apoderado.html",
        {
            "apoderados": apoderados,
            "inscripcion": inscripcion,
        },
    )
