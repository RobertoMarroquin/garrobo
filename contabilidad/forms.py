#django libs
from django import forms
from django.db.models.aggregates import Count
from django.db.models import Sum
from django.forms import widgets
#self libs
from .models import *
from .funciones import actualizacion_saldos
#other Libs
from .plantillaCuentas import pl_cuentas as pl

class DateInput(forms.DateInput):
    input_type = 'date'


#reporte de cuentas
class ReporteCuentasForm(forms.Form):
    cuenta = forms.ModelChoiceField(queryset=SubCuenta.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    fecha_inicio = forms.DateField(widget=DateInput(attrs={'class':'form-control'}))
    fecha_fin = forms.DateField(widget=DateInput(attrs={'class':'form-control'}))
    def __init__(self, *args, **kwargs):
        super(ReporteCuentasForm, self).__init__(*args, **kwargs)
        self.fields['cuenta'].label = 'Cuenta'
        self.fields['fecha_inicio'].label = 'Fecha Inicio'
        self.fields['fecha_fin'].label = 'Fecha Fin'
        
    def clean(self):
        cleaned_data = super(ReporteCuentasForm, self).clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio > fecha_fin:
            raise forms.ValidationError('La fecha de inicio no puede ser mayor a la fecha fin')
        return cleaned_data


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

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super(PeriodoForm, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(id=empresa.id)


class CatalogoF(forms.ModelForm):
    class Meta:
        model = Catalogo
        fields = ["empresa",]

    def save(self,commit = True, *args, **kwargs):
        cat = super().save(*args, **kwargs)
        if commit:
            cat.save()
            pl(cat)
        return cat

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super(CatalogoF, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['empresa'].queryset = self.fields['empresa'].queryset.filter(id=empresa.id)


class CuentaF(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = [
            "catalogo",
            "codigo",
            "nombre",
        ]


class SubCuentaF(forms.ModelForm):
    class Meta:
        model = SubCuenta
        fields = [
            "catalogo",
            "codigo",
            "nombre",
            "cuenta_padre",
        ]
        widgets = {
            "codigo" : forms.TextInput(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        catalogo = kwargs.pop('catalogo', None)
        super(SubCuentaF, self).__init__(*args, **kwargs)
        # restrict the queryset of 'Cuenta'
        self.fields['catalogo'].queryset = self.fields['catalogo'].queryset.filter(id=catalogo.id)
        self.fields['cuenta_padre'].queryset = self.fields['cuenta_padre'].queryset.filter(catalogo=catalogo)


class LibroF(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ["periodo","mes"]


class PartidaF(forms.ModelForm):
    fecha = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=True)
    class Meta:
        model = Partida
        fields = ["fecha", "libro", "descripcion"]


class MovimientoF(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        catalogo = kwargs.pop('catalogo', None)
        partida =  kwargs.pop('partida', None)
        super(MovimientoF, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].label = False
        # restrict the queryset of 'Cuenta'
        self.fields['cuenta'].queryset = self.fields['cuenta'].queryset.filter(catalogo=catalogo,es_mayor=False).annotate(subcuenta_existe=Count('subcuentas')).filter(subcuenta_existe=0).order_by("codigo")


    def save(self,commit = True, *args, **kwargs):
        mov = super().save(*args, **kwargs)
        if commit:
            mov.save()
            #actualizacion_saldos(movimiento=mov,cuenta=mov.cuenta)
        return mov


    class Meta:
        model = Movimiento
        fields = ["cuenta","descripcion","monto_haber","monto_deber",]
        exclude = ["partida",]
        widgets = {
            "cuenta"     :   forms.Select(attrs={"required":"true","autofocus":"true"}),
            "descripcion":  forms.TextInput(attrs={}),
            #"monto_haber":  forms.TextInput(attrs={"class":"money"}),
            #"monto_deber":  forms.TextInput(attrs={"class":"money"}),
        }

