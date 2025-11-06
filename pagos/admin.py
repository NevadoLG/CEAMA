from django.contrib import admin, messages
from django.urls import reverse, path
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.db import transaction

from .models import Pago, Comprobante


# =========================
#  Inline de Comprobantes
# =========================
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
        return format_html('<a class="button btn btn-sm btn-danger" href="{}">Eliminar</a>', delete_url)


# =======================
#  Admin de Pago
# =======================
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "estudiante_nombre",
        "plan_text",
        "estado_badge",
        "comprobantes_cell",
        "abrir_cell",
        "acciones_cell",
    )
    list_display_links = ("id", "estudiante_nombre")
    list_filter = ("estado", "fecha")
    search_fields = (
        "inscripcion__estudiante__apellidos",
        "inscripcion__estudiante__nombres",
    )
    date_hierarchy = "fecha"
    save_on_top = True

    readonly_fields = ("inscripcion", "fecha")
    fields = ("inscripcion", "monto", "metodo", "estado", "fecha")

    raw_id_fields = ("inscripcion",)
    inlines = [ComprobanteInline]

    actions = ["validar_pago", "marcar_parcial", "rechazar_pago"]

    # --- URLs personalizadas ---
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("<int:pk>/aprobar/", self.admin_site.admin_view(self.aprobar_view),
                 name="pagos_pago_aprobar"),
            path("<int:pk>/rechazar/", self.admin_site.admin_view(self.rechazar_view),
                 name="pagos_pago_rechazar"),
        ]
        return custom + urls

    def _redirect_changelist(self, request):
        return HttpResponseRedirect(reverse("admin:pagos_pago_changelist"))

    def _sync_inscripcion(self, pago):
        """Sincroniza estado_pago de Inscripcion."""
        ins = pago.inscripcion
        if hasattr(ins, "estado_pago"):
            if pago.estado == "completado":
                ins.estado_pago = "total"
            elif pago.estado == "parcial":
                ins.estado_pago = "parcial"
            elif pago.estado == "rechazado":
                ins.estado_pago = "pendiente"
            else:
                ins.estado_pago = "pendiente"
            ins.save(update_fields=["estado_pago"])

    # --- Vistas personalizadas ---
    def aprobar_view(self, request, pk):
        pago = Pago.objects.select_related("inscripcion__estudiante").filter(pk=pk).first()
        if not pago:
            self.message_user(request, "Pago no encontrado.", level=messages.ERROR)
            return self._redirect_changelist(request)
        # Aprueba según lo solicitado (parcial o completado)
        pago.estado = pago.estado_solicitado
        pago.save(update_fields=["estado"])
        self._sync_inscripcion(pago)
        self.message_user(
            request,
            f"Pago aprobado como {pago.get_estado_display()}.",
            level=messages.SUCCESS
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

    # --- Columnas ---
    @admin.display(description="Estudiante")
    def estudiante_nombre(self, obj):
        e = obj.inscripcion.estudiante
        return f"{e.apellidos} {e.nombres}"

    @admin.display(description="Plan")
    def plan_text(self, obj):
        return str(obj.inscripcion.plan)

    @admin.display(description="Estado")
    def estado_badge(self, obj):
        # badge principal
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

        # nota sutil SOLO cuando está pendiente (lo que el apoderado solicitó)
        note = ""
        if obj.estado == "pendiente" and obj.estado_solicitado in ("parcial", "completado"):
            note = format_html(
                ' <small style="opacity:.7">({} solicitado)</small>',
                obj.get_estado_solicitado_display()
            )

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

    # --- Acciones masivas ---
    @admin.action(description="Validar pago(s) → COMPLETADO / PARCIAL según solicitud")
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


# ===================
#  Admin Comprobante
# ===================
@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ("id", "pago", "mini", "fecha")
    readonly_fields = ("mini", "fecha")
    fields = ("pago", "archivo", "mini", "fecha")

    @admin.display(description="Vista")
    def mini(self, obj):
        if not obj.archivo:
            return "—"
        url = obj.archivo.url
        if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-height:60px;border-radius:6px"/></a>',
                url, url
            )
        return format_html('<a href="{}" target="_blank">Abrir</a>', url)
