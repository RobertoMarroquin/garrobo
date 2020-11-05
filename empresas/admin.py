from django.contrib import admin
from .models import Empresa
# Register your models here.
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    '''Admin View for Empresa'''

    list_display = (
        "nombre",
        "razon_social",
        "num_registro",
        "nit",
        "direccion",
        "giro1",
        "giro2",
        "giro3",
        "telefono",
        "contabilidad",
        "creado",
    )