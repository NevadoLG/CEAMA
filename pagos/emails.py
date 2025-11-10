from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.crypto import get_random_string

def _abs(path: str) -> str:
    base = getattr(settings, "SITE_BASE_URL", "").rstrip("/")
    return f"{base}{path}"

def _get_apo_email(apoderado):
    if not apoderado:
        return None
    for attr in ("email", "correo", "correo_electronico"):
        v = getattr(apoderado, attr, None)
        if v:
            return v
    return None


def enviar_correo_codigo(inscripcion):
    """
    (Uso opcional) Envía solo el código de acceso con el enlace de seguimiento.
    La vista de registrar_pago YA NO debería llamarlo, pero lo dejamos por
    compatibilidad si en algún punto lo necesitas.
    """
    est = getattr(inscripcion, "estudiante", None)
    apod = getattr(est, "apoderado", None)
    correo = getattr(apod, "email", None)
    if not correo:
        return

    code = getattr(inscripcion, "access_code", "")
    path = reverse("pagos_regularizar_seguimiento", args=[code]) if code else "#"
    url = _abs(path)

    subject = "CEAMA – Código de acceso para pagos"
    body = (
        "Hola,\n\n"
        f"Tu código de acceso es: {code}\n"
        f"Puedes ver/regularizar pagos aquí:\n{url}\n\n"
        "CEAMA"
    )
    send_mail(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", None), [correo], fail_silently=True)


def enviar_correo_pago_aprobado(pago, raise_errors=False) -> bool:
    """Envía el correo de aprobación. Devuelve True si envió, False si no."""
    ins = pago.inscripcion
    est = ins.estudiante
    apo = getattr(est, "apoderado", None)
    to = _get_apo_email(apo)
    if not to:
        return False

    # Garantiza código
    if not getattr(ins, "access_code", ""):
        ins.access_code = get_random_string(10).upper()
        ins.save(update_fields=["access_code"])

    url = _abs(reverse("pagos_regularizar_seguimiento", args=[ins.access_code]))

    sujeto = "CEAMA – Confirmación de pago"
    texto = (
        f"Hola {getattr(apo, 'nombres', '')},\n\n"
        f"Tu pago fue aprobado como {pago.get_estado_display()}.\n\n"
        f"Estudiante: {est.apellidos}, {est.nombres}\n"
        f"Plan: {ins.plan}\n"
        f"Monto: S/ {pago.monto}\n"
        f"Código de acceso: {ins.access_code}\n"
        f"Seguimiento: {url}\n\n"
        f"Si no reconoces este mensaje, ignóralo."
    )
    html = (
        f"<p>Hola <b>{getattr(apo, 'nombres', '')}</b>,</p>"
        f"<p>Tu pago fue <b>aprobado</b> como <b>{pago.get_estado_display()}</b>.</p>"
        f"<ul>"
        f"<li><b>Estudiante:</b> {est.apellidos}, {est.nombres}</li>"
        f"<li><b>Plan:</b> {ins.plan}</li>"
        f"<li><b>Monto:</b> S/ {pago.monto}</li>"
        f"<li><b>Código de acceso:</b> <code>{ins.access_code}</code></li>"
        f"</ul>"
        f'<p>Puedes ver/regularizar pagos aquí: <a href="{url}">{url}</a></p>'
    )

    try:
        msg = EmailMultiAlternatives(
            sujeto,
            texto,
            settings.DEFAULT_FROM_EMAIL,
            [to],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:
        if raise_errors:
            raise
        return False

