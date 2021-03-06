from django import forms
from .models import *

class EmpresaF(forms.ModelForm):
    nit  = forms.CharField(widget=forms.TextInput(attrs={"data-mask":"0000-000000-000-0"}),
            required=False)
    class Meta:
        model = Empresa
        fields = ['nRegistro','nombre','nit',]
        


class LibroForm(forms.ModelForm):
    
    class Meta:
        model = Libro
        fields = ('mes','ano','tipo','cliente')
        widgets = {
            'ano'       :forms.NumberInput(attrs={'max': 2050,'min':2000}),
            'tipo'      :forms.HiddenInput(),
            'cliente'   :forms.HiddenInput(),
            }


class ContribuyenteForm(forms.ModelForm):
    fecha = forms.DateField(input_formats=["%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=False)
    falsoContribuyente = forms.CharField(widget=forms.TextInput(attrs={"":""}),
            required=True,label="Contribuyente")
    class Meta:
        model = FacturaCt
        fields = (  "correlativo",
                    "fecha",
                    "contribuyente",
                    'falsoContribuyente',
                    "venExentas",
                    "venGravadas",
                    "ventasNSujetas",
                    "ivaDebFiscal",
                    "vtVentas",
                    "vtIVA",
                    "ivaRetenido",
                    "total",
                    "libro"
                    )
        widgets = {
            "correlativo"   :  forms.TextInput(attrs={"required":"true","autofocus":"true"}),
            "contribuyente" :  forms.HiddenInput,
            "venExentas"    :  forms.NumberInput(attrs={"value":"0.00"}),
            "venGravadas"   :  forms.NumberInput(attrs={"value":"0.00"}),
            "ivaDebFiscal"  :  forms.NumberInput(attrs={"value":"0.00"}),
            "vtVentas"      :  forms.NumberInput(attrs={"value":"0.00"}),
            "vtIVA"         :  forms.NumberInput(attrs={"value":"0.00"}),
            "ivaRetenido"   :  forms.NumberInput(attrs={"value":"0.00"}),
            "total"         :  forms.NumberInput(attrs={"value":"0.00","readonly":"true"}),
            "ventasNSujetas":  forms.NumberInput(attrs={"value":"0.00"}),
            "libro"         :  forms.HiddenInput,
        }


class ConsumidorFinalForm(forms.ModelForm):
    fecha = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=False)
    class Meta:
        model = FacturaCF
        fields =(
            "correlativoInicial",
            "correlativoFinal",
            "fecha" ,
            "exento",
            "locales" ,
            "exportaciones",
            "ventasNSujetas",
            "ventaTotal",
            "ventaCtaTerceros",
            "libro", 
        )
        widgets = {
            "correlativoInicial"    : forms.NumberInput(attrs={"autofocus":"true"}),
            "correlativoFinal"      : forms.NumberInput(attrs={"":""}),
            "exento"                : forms.NumberInput(attrs={"value":"0.00"}),
            "locales"               : forms.NumberInput(attrs={"value":"0.00"}),
            "ventaTotal"            : forms.NumberInput(attrs={"value":"0.00","readonly":"true"}),
            "ventaCtaTerceros"      : forms.NumberInput(attrs={"value":"0.00"}),
            "exportaciones"         : forms.NumberInput(attrs={"value":"0.00"}),
            "ventasNSujetas"        : forms.NumberInput(attrs={"value":"0.00"}),
            "libro"                 : forms.HiddenInput(attrs={"":""}),
        }


class ComprasForm(forms.ModelForm):
    fecha = forms.DateField(input_formats=["%d/%m/%Y","%d/%m/%y"],
            widget=forms.DateInput(attrs={"data-mask":"00/00/00"}),
            required=False)
    falsaEmpresa = forms.CharField(widget=forms.TextInput(attrs={"":""}),
            required=True,label="Proveedor")
    class Meta:
        model = FacturaCm
        fields =(
        "correlativo",       
        "fecha",              
        "empresa",
        "falsaEmpresa",           
        "cExenteInterna",     
        "cExenteImportaciones", 
        "cGravadaInterna",     
        "cGravadaImportaciones",
        "comprasNSujetas",
        "ivaCdtoFiscal",     
        "totalCompra",        
        "retencionPretencion",
        "anticipoCtaIva",     
        "ivaTerceros",
        "libro",   
        )    

        widgets = {
        "correlativo"          : forms.NumberInput(attrs={"autofocus":"true"}),
        "empresa"              : forms.HiddenInput(attrs={"readonly":"true"}),
        "cExenteInterna"       : forms.NumberInput(attrs={"value":"0.00"}),
        "cExenteImportaciones" : forms.NumberInput(attrs={"value":"0.00"}),
        "cGravadaInterna"      : forms.NumberInput(attrs={"value":"0.00"}),
        "cGravadaImportaciones": forms.NumberInput(attrs={"value":"0.00"}),
        "ivaCdtoFiscal"        : forms.NumberInput(attrs={"value":"0.00"}),
        "totalCompra"          : forms.NumberInput(attrs={"value":"0.00","readonly":"true"}),
        "retencionPretencion"  : forms.NumberInput(attrs={"value":"0.00"}),
        "anticipoCtaIva"       : forms.NumberInput(attrs={"value":"0.00"}),
        "ivaTerceros"          : forms.NumberInput(attrs={"value":"0.00"}),
        "comprasNSujetas"      : forms.NumberInput(attrs={"value":"0.00"}),
        "libro"                : forms.HiddenInput(attrs={"":""}),
        }