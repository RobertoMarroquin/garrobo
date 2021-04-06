from django import forms
from .models import *

class TalonarioF(forms.ModelForm):
    def save(self,commit = True, *args, **kwargs):
        tal = super().save(*args, **kwargs)
        if commit:
            tal.save()
            for  mes in range(12):
                mensualidad = Mensualidad(talonario=tal, mes=mes+1)
                mensualidad.save()
        return tal
        
    class Meta:
        model = Talonario
        fields = ("ano","empresa")
        widgets = {
            'ano'   :forms.NumberInput(attrs={'max': 2050,'min':2020}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super(TalonarioF, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(id=empresa.id)


class MensualidadF(forms.ModelForm):
    class Meta:
        model = Mensualidad
        fields = ["talonario","mes",]

    def __init__(self, *args, **kwargs):
        talonario = kwargs.pop('talonario', None)
        super(MensualidadF, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['talonario'].queryset = self.fields['talonario'].queryset.get(id=talonario.id)


class CobroF(forms.ModelForm):
    class Meta:
        model = Cobro
        fields = ["descripcion",
            "monto",
            "iva",
            "mensualidad",
            "fecha_acordada_pago",
        ]
        
    def __init__(self, *args, **kwargs):
        talonario = kwargs.pop('talonario', None)
        super(MensualidadF, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['talonario'].queryset = self.fields['talonario'].queryset.get(id=talonario.id)


