from django import forms

from .models import Empresa


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        exclude = ['creado']
        fields = '__all__'
        widgets = {
            "nit"   :  forms.TextInput(attrs={'data-mask':"0000-000000-000-0"}),
            "telefono" :forms.TextInput(attrs={'data-mask':"0000-0000"}),
        }

