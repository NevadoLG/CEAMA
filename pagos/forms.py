from django import forms
from .models import Pago, Comprobante

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo', 'estado']   # usamos tus choices del modelo
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'metodo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),  # pendiente | parcial | total (según tu modelo)
        }

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['archivo']  # PDF o imagen (según tu FileField/ImageField)
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
