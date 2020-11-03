#django libs
from django import forms
#self libs
from .models import *


class PeriodoForm(forms.ModelForm):
    fecha_inicio = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=True)
    
    fecha_fin = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=True)
    
    class Meta:
        model = Periodo
        fields = (
            "empresa",
            "fecha_inicio",
            "fecha_fin",
            "ano",
        )


class Catalogo(forms.ModelForm):
    class Meta:
        model = Catalogo
        fields = ["empresa",]


class Cuenta(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = [ 
            "catalogo", 
            "codigo", 
            "nombre", 
        ]


class SubCuenta(forms.ModelForm):
    class Meta:
        model = SubCuenta
        fields = [
            "catalogo", 
            "codigo", 
            "nombre", 
            "cuenta_padre",
        ]


class Libro(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ["periodo","mes"]


class Partida(forms.ModelForm):
    fecha = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=True)
    class Meta:
        model = Partida
        fields = ["fecha", "libro", "descripcion"]


class Movimiento(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ["monto_haber","monto_deber","cuenta","descripcion"]
