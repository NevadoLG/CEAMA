from django import forms
from django.core.exceptions import ValidationError
from .models import Apoderado

class ApoderadoForm(forms.ModelForm):
    class Meta:
        model = Apoderado
        fields = ["nombres", "apellidos", "dni", "telefono", "email", "direccion"]

    def clean_telefono(self):
        tel = (self.cleaned_data.get("telefono") or "").strip()
        qs = Apoderado.objects.filter(telefono=tel)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este teléfono ya ha sido registrado previamente.")
        return tel

    def clean_dni(self):
        dni = (self.cleaned_data.get("dni") or "").strip()
        if not dni:
            return dni
        qs = Apoderado.objects.filter(dni=dni)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este DNI ya ha sido registrado previamente.")
        return dni
