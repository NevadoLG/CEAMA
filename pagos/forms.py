from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import Pago

PUBLIC_ALLOWED_ESTADOS = {"parcial", "completado"}

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["monto", "metodo", "estado"]
        widgets = {
            "monto": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "inputmode": "decimal",
            }),
            "metodo": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metodo"].choices = Pago._meta.get_field("metodo").choices
        all_estado = Pago._meta.get_field("estado").choices
        self.fields["estado"].choices = [(v, l) for v, l in all_estado if v in PUBLIC_ALLOWED_ESTADOS]
        # Establecer "completado" como valor predeterminado
        if not self.instance.pk:  # Solo para nuevos pagos
            self.initial["estado"] = "completado"

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
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def clean_estado(self):
        estado = self.cleaned_data.get("estado")
        if estado not in PUBLIC_ALLOWED_ESTADOS:
            raise forms.ValidationError("Estado de pago inválido.")
        return estado


class LookupCodeForm(forms.Form):
    code = forms.CharField(
        label="Código de acceso",
        max_length=16,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 9K2F7A1B3C",
        }),
    )


class ReenviarCodigoForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "tu@correo.com"})
    )


class RegularizacionForm(forms.Form):
    """
    Solo valida monto y método. Los archivos se leen por request.FILES['archivos'].
    """
    monto = forms.DecimalField(
        min_value=1,
        max_value=999.99,
        decimal_places=2,
        max_digits=6,
        validators=[MinValueValidator(1), MaxValueValidator(999.99)],
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "max": "999.99",
            "min": "1",
            "step": "0.01",
            "inputmode": "decimal",
        }),
        label="Monto a regularizar",
    )
    metodo = forms.ChoiceField(
        label="Método de pago",
        choices=Pago._meta.get_field("metodo").choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_monto(self):
        """
        Fuerza tope 999.99 si viene más alto.
        """
        val = self.cleaned_data["monto"]
        if val > Decimal("999.99"):
            return Decimal("999.99")
        return val
