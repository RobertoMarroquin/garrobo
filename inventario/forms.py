from django import forms
from .models import *


class LocacionF(forms.ModelForm):
    class Meta:
        model = Locacion
        fields = ["nombre","direccion"]


class EstadoF(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ["codigo","nombre"]


class CatalogoF(forms.ModelForm):
    class Meta:
        model = CatalogoProducto
    fields = ["empresa"]


class ProductoF(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["coodigo",
        "nombre",
        "catalogo"]


class DetallePF(forms.ModelForm):
    class Meta:
        model = DetalleProducto
        fields = ['producto',
        'ubicacion',
        'existencia',
        'fecha_entrada',
        'perecedero',
        'fecha_caducidad'
        ]

