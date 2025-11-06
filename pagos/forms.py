from decimal import Decimal, InvalidOperation
from django import forms
from .models import Pago

# --- Widget múltiple compatible con Django 3.2/4.0/4.1 ---
class MultiFileInput(forms.ClearableFileInput):
    # Esto es lo que habilita input type="file" multiple en versiones que lo requieren
    allow_multiple_selected = True

PUBLIC_ALLOWED_ESTADOS = {"parcial", "completado"}

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        # 'estado' aquí es lo que el apoderado SOLICITA (parcial/completado);
        # el pago REAL siempre se registra en 'pendiente'
        fields = ["monto", "metodo", "estado"]
        widgets = {
            "monto": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.01", "min": "0", "inputmode": "decimal"
            }),
            "metodo": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_choices = getattr(Pago, "ESTADO_CHOICES", Pago._meta.get_field("estado").choices)
        # Solo mostramos al apoderado: Parcial / Completado
        self.fields["estado"].choices = [(v, l) for v, l in all_choices if v in PUBLIC_ALLOWED_ESTADOS]

    def clean_monto(self):
        raw = self.data.get("monto", "")
        if isinstance(raw, str):
            raw = raw.replace(",", ".")
        try:
            val = Decimal(str(raw))
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Monto inválido. Usa números como 123.45.")
        if val < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return val

    def clean_estado(self):
        estado = self.cleaned_data.get("estado")
        if estado not in PUBLIC_ALLOWED_ESTADOS:
            raise forms.ValidationError("Estado de pago inválido.")
        return estado


class ComprobanteForm(forms.Form):
    # IMPORTANTE: usar el widget MultiFileInput (no ClearableFileInput directo)
    archivos = forms.FileField(
        required=False,                   # opcional
        widget=MultiFileInput(attrs={"multiple": True})
    )

    def clean_archivos(self):
        """
        Siempre devolver una lista de archivos (vacía o con elementos).
        Esto evita el error 'no se ha enviado ningún fichero' cuando no adjuntan.
        """
        return self.files.getlist("archivos")
