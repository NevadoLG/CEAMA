from django.contrib import admin, messages
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.db import transaction
from django.utils.crypto import get_random_string

from .models import Pago, Comprobante
from .emails import enviar_correo_pago_aprobado
from django.db.models import Sum
from estudiantes.models import Matricula


class ComprobanteInline(admin.TabularInline):
    model = Comprobante
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ("preview", "fecha", "acciones")
    fields = ("preview", "fecha", "acciones")

    @admin.display(description="Archivo / Vista previa")
    def preview(self, obj):
        if not obj.archivo:
            return "—"
        url = obj.archivo.url
        name = obj.archivo.name.split("/")[-1].lower()
        if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height:90px;border-radius:6px;vertical-align:middle" />'
                "</a><br><small>{1}</small>",
                url, name
            )
        return format_html('<a href="{}" target="_blank">Abrir archivo</a>', url)

    @admin.display(description="Acciones")
    def acciones(self, obj):
        back = reverse("admin:pagos_pago_change", args=[obj.pago_id]) + "#inline-group"
        delete_url = reverse("admin:pagos_comprobante_delete", args=[obj.pk]) + f"?next={back}"

        request = getattr(self, "request", None)  
        if request and not request.user.has_perm("pagos.delete_comprobante"):
            return "—"

        return format_html(
            '<a class="button btn btn-sm btn-danger" href="{}">Eliminar</a>',
            delete_url
        )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "estudiante_nombre", "plan_text", "estado_badge",
                    "comprobantes_cell", "abrir_cell", "acciones_cell")
    list_display_links = ("id", "estudiante_nombre")
    list_filter = ("estado", "fecha")
    search_fields = ("inscripcion__estudiante__apellidos", "inscripcion__estudiante__nombres")
    date_hierarchy = "fecha"
    readonly_fields = ("inscripcion", "fecha", "apoderado_info")
    fields = ("inscripcion", "monto", "metodo", "estado", "fecha", "apoderado_info")
    raw_id_fields = ("inscripcion",)
    inlines = [ComprobanteInline]
    actions = ["validar_pago", "marcar_parcial", "rechazar_pago"]

    @admin.display(description="Apoderado")
    def apoderado_info(self, obj):
        est = getattr(obj.inscripcion, "estudiante", None)
        apo = getattr(est, "apoderado", None)
        if not apo:
            return format_html('<span style="opacity:.7">Sin apoderado vinculado</span>')

        nombre_apo = f"{getattr(apo, 'apellidos', '').strip()}, {getattr(apo, 'nombres', '').strip()}".strip(", ")

        dni = getattr(apo, "dni", "") or getattr(apo, "documento", "")
        email = self._apo_email(apo) or "—"
        tel = getattr(apo, "telefono", "") or getattr(apo, "celular", "") or "—"

        link_est = ""
        link_apo = ""
        try:
            url_est = reverse("admin:estudiantes_estudiante_change", args=[est.pk])
            link_est = format_html('<a href="{}">Editar estudiante</a>', url_est)
        except Exception:
            pass
        try:
            url_apo = reverse("admin:apoderados_apoderado_change", args=[apo.pk])
            link_apo = format_html('<a href="{}">Editar apoderado</a>', url_apo)
        except Exception:
            pass

        enlaces = format_html("{} | {}", link_est, link_apo) if (link_est and link_apo) else (link_est or link_apo)

        return format_html(
            '<div style="line-height:1.6">'
            '<b>{nombre}</b><br>'
            'DNI: {dni}<br>'
            'Email: {email}<br>'
            'Tel: {tel}<br>'
            '{enlaces}'
            '</div>',
            nombre=nombre_apo,
            dni=dni or "—",
            email=email,
            tel=tel,
            enlaces=enlaces or "",
        )
    def _apo_email(self, apoderado):
        """Devuelve el email del apoderado probando distintos nombres de campo."""
        if not apoderado:
            return None
        for attr in ("email", "correo", "correo_electronico"):
            val = getattr(apoderado, attr, None)
            if val:
                return val
        return None
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:pk>/aprobar/', self.admin_site.admin_view(self.aprobar_view),
                 name='pagos_pago_aprobar'),
            path('<int:pk>/rechazar/', self.admin_site.admin_view(self.rechazar_view),
                 name='pagos_pago_rechazar'),
        ]
        return custom + urls

    def _redirect_changelist(self, request):
        return HttpResponseRedirect(reverse("admin:pagos_pago_changelist"))

    def _sync_inscripcion(self, pago):
        ins = pago.inscripcion

        if pago.estado == "completado":
            ins.estado_pago = "total"
        elif pago.estado == "parcial":
            ins.estado_pago = "parcial"
        elif pago.estado == "rechazado":
            ins.estado_pago = "pendiente"
        else:
            ins.estado_pago = "pendiente"
        ins.save(update_fields=["estado_pago"])

        total_pagado = (
            ins.pago_set.filter(estado__in=["parcial", "completado"])
            .aggregate(total=Sum("monto"))
            .get("total") or 0
        )

        estudiante = getattr(ins, "estudiante", None)
        if estudiante is None:
            return

        matricula, created = Matricula.objects.get_or_create(
            inscripcion=ins,
            estudiante=estudiante,
            defaults={
                "estado": "activo" if ins.estado_pago == "total" else "inactivo",
                "monto_referencial": total_pagado,
            },
        )

        if not created:
            matricula.estado = "activo" if ins.estado_pago == "total" else "inactivo"
            matricula.monto_referencial = total_pagado
            matricula.save(update_fields=["estado", "monto_referencial"])

    def aprobar_view(self, request, pk):
        pago = Pago.objects.select_related("inscripcion__estudiante__apoderado").filter(pk=pk).first()
        if not pago:
            self.message_user(request, "Pago no encontrado.", level=messages.ERROR)
            return self._redirect_changelist(request)

        pago.estado = pago.estado_solicitado or "completado"
        pago.save(update_fields=["estado"])
        self._sync_inscripcion(pago)

        ins = pago.inscripcion
        if not getattr(ins, "access_code", ""):
            ins.access_code = get_random_string(10).upper()
            ins.save(update_fields=["access_code"])

        apo = getattr(ins.estudiante, "apoderado", None)
        correo = self._apo_email(apo)
        if not correo:
            self.message_user(
                request,
                "Pago aprobado. No se envió correo porque el estudiante no tiene apoderado con email.",
                level=messages.WARNING,
            )
            return self._redirect_changelist(request)

        ok = False
        try:
            ok = enviar_correo_pago_aprobado(pago, raise_errors=False)
        except Exception as e:
            self.message_user(
                request, f"Pago aprobado, pero falló el envío de correo: {e}", level=messages.ERROR
            )
            return self._redirect_changelist(request)

        if ok:
            self.message_user(request, "Pago aprobado. Código generado/enviado.", level=messages.SUCCESS)
        else:
            self.message_user(
                request,
                "Pago aprobado, pero no se pudo enviar el correo (revisa configuración SMTP).",
                level=messages.ERROR,
            )

        return self._redirect_changelist(request)

    def rechazar_view(self, request, pk):
        pago = Pago.objects.select_related("inscripcion__estudiante").filter(pk=pk).first()
        if not pago:
            self.message_user(request, "Pago no encontrado.", level=messages.ERROR)
            return self._redirect_changelist(request)
        pago.estado = "rechazado"
        pago.save(update_fields=["estado"])
        self._sync_inscripcion(pago)
        self.message_user(request, "Pago rechazado.", level=messages.WARNING)
        return self._redirect_changelist(request)

    @admin.display(description="Estudiante")
    def estudiante_nombre(self, obj):
        e = obj.inscripcion.estudiante
        return f"{e.apellidos} {e.nombres}"

    @admin.display(description="Plan")
    def plan_text(self, obj):
        return str(obj.inscripcion.plan)

    @admin.display(description="Estado")
    def estado_badge(self, obj):
        txt = obj.get_estado_display()
        palette = {
            "pendiente": "#b45309",
            "parcial": "#1d4ed8",
            "completado": "#065f46",
            "rechazado": "#991b1b",
        }
        color = palette.get(obj.estado, "#374151")
        badge = format_html(
            '<span style="background:{}20;color:{};padding:2px 8px;'
            'border-radius:12px;font-weight:600;text-transform:capitalize">{}</span>',
            color, color, txt
        )
        note = ""
        if obj.estado == "pendiente" and obj.estado_solicitado in ("parcial", "completado"):
            note = format_html(' <small style="opacity:.7">({} solicitado)</small>',
                               obj.get_estado_solicitado_display())
        return format_html("{}{}", badge, note)

    @admin.display(description="Comprobantes")
    def comprobantes_cell(self, obj):
        qs = obj.comprobantes.all()
        n = qs.count()
        if not n:
            return "—"
        first = qs.first()
        if first and first.archivo:
            open_url = reverse("admin:pagos_pago_change", args=[obj.pk]) + "#inline-group"
            return format_html(
                '<a href="{}"><img src="{}" style="height:24px;border-radius:4px;vertical-align:middle;margin-right:6px"/></a>'
                '<span style="background:#e5e7eb;border-radius:10px;padding:2px 8px;font-weight:600">{}</span>',
                open_url, first.archivo.url, n
            )
        return str(n)

    @admin.display(description="Abrir")
    def abrir_cell(self, obj):
        url = reverse("admin:pagos_pago_change", args=[obj.pk])
        return format_html('<a class="button btn btn-sm" href="{}">Abrir</a>', url)

    @admin.display(description="Acciones")
    def acciones_cell(self, obj):
        if obj.estado in ("rechazado", "parcial", "completado"):
            return "—"
        aprobar = reverse("admin:pagos_pago_aprobar", args=[obj.pk])
        rechazar = reverse("admin:pagos_pago_rechazar", args=[obj.pk])
        return format_html(
            '<a class="button btn btn-success btn-sm" style="margin-right:6px" href="{}">Aprobar</a>'
            '<a class="button btn btn-danger btn-sm" href="{}">Rechazar</a>',
            aprobar, rechazar
        )

    @admin.action(description="Validar pago(s) → COMPLETADO")
    def validar_pago(self, request, queryset):
        with transaction.atomic():
            for pago in queryset:
                pago.estado = pago.estado_solicitado or "completado"
                pago.save(update_fields=["estado"])
                self._sync_inscripcion(pago)
        self.message_user(request, "Pagos validados.", level=messages.SUCCESS)

    @admin.action(description="Marcar pago(s) → PARCIAL")
    def marcar_parcial(self, request, queryset):
        with transaction.atomic():
            for pago in queryset:
                pago.estado = "parcial"
                pago.save(update_fields=["estado"])
                self._sync_inscripcion(pago)
        self.message_user(request, "Pagos marcados como Parcial.", level=messages.INFO)

    @admin.action(description="Rechazar pago(s)")
    def rechazar_pago(self, request, queryset):
        with transaction.atomic():
            for pago in queryset:
                pago.estado = "rechazado"
                pago.save(update_fields=["estado"])
                self._sync_inscripcion(pago)
        self.message_user(request, "Pagos rechazados.", level=messages.WARNING)

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "fecha")

    def has_module_permission(self, request):
        return False
