from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Apoderado
from estudiantes.models import Estudiante, Inscripcion


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

        # Validaciones básicas
        if not dni:
            messages.error(request, "El DNI es obligatorio.")
            # PRG para limpiar el formulario
            return redirect(reverse("registrar_apoderado") + (
                f"?inscripcion_id={inscripcion.id}" if inscripcion else ""
            ))

        telefono = data["telefono"]

        # ¿Existe alguien con ese DNI?
        apod_por_dni = Apoderado.objects.filter(dni=dni).first()

        # ¿Existe alguien con ese teléfono? (excluye al del DNI si es la misma persona)
        tel_qs = Apoderado.objects.filter(telefono=telefono)
        if apod_por_dni:
            tel_qs = tel_qs.exclude(id=apod_por_dni.id)
        apod_por_tel = tel_qs.first()

        if apod_por_tel:
            messages.error(request, "El teléfono ya ha sido registrado previamente.")
            return redirect(reverse("registrar_apoderado") + (
                f"?inscripcion_id={inscripcion.id}" if inscripcion else ""
            ))

        # Si el DNI ya existe, actualizamos sus datos (sin romper la unicidad de tel)
        if apod_por_dni:
            apod_por_dni.nombres   = data["nombres"]
            apod_por_dni.apellidos = data["apellidos"]
            apod_por_dni.telefono  = data["telefono"]
            apod_por_dni.correo    = data["correo"]
            apod_por_dni.direccion = data["direccion"]
            apod_por_dni.save(update_fields=["nombres", "apellidos", "telefono", "correo", "direccion"])
            apoderado = apod_por_dni
            created = False
        else:
            # Crear nuevo apoderado (DNI y Tel únicos)
            apoderado = Apoderado.objects.create(dni=dni, **data)
            created = True

        # Vincular a la inscripción si la tenemos
        estudiante = inscripcion.estudiante if inscripcion else None
        if estudiante:
            if getattr(estudiante, "apoderado_id", None) != apoderado.id:
                estudiante.apoderado = apoderado
                estudiante.save(update_fields=["apoderado"])

            messages.success(
                request,
                ("Apoderado creado. " if created else "Apoderado reutilizado/actualizado. ") +
                "Continúa con el pago."
            )
            # Redirigir al paso de pago (conservando la inscripción)
            url_pago = reverse("registrar_pago")
            if inscripcion:
                url_pago = f"{url_pago}?inscripcion_id={inscripcion.id}"
            return redirect(url_pago)

        messages.warning(
            request,
            "Apoderado registrado, pero no se pudo ubicar la inscripción del estudiante."
        )
        # PRG para limpiar
        return redirect(reverse("registrar_apoderado"))

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
