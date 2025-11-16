from django import forms
from .models import vehiculo


# creating a ModelForm for vehiculo
class vehiculoForm(forms.ModelForm):
    class Meta:
        model = vehiculo
        fields = [
            "placa",
            "marca",
            "color_vehiculo",
            "modelo",
        ]
        labels = {
            "placa": "Número de placa",
            "marca": "Marca del vehículo",
            "modelo": "Modelo del vehículo",
            "color_vehiculo": "Color del vehículo",
        }
        widgets = {
            "placa": forms.TextInput(attrs={'class': 'form-control'}),
            "marca": forms.TextInput(attrs={'class': 'form-control'}),
            "modelo": forms.NumberInput(attrs={'class': 'form-control'}),
            "color_vehiculo": forms.Select(attrs={'class': 'form-control'}),
        }