from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha",
        "mes",
        "ano",
        "tipo",
        "cliente",
    )
    search_fields = ["id","fecha","mes","ano","cliente__nombre",]

@admin.register(FacturaCF)
class FacturaCFAdmin(admin.ModelAdmin):
    list_display = (
        "correlativoInicial",
        "correlativoFinal",
        "fecha",
        "exento",
        "locales",
        "ventaTotal",
        "ventaCtaTerceros",
        "libro",
        "exportaciones",
        "ventasNSujetas",
    )
    search_fields = ["id","correlativoInicial","correlativoFinal","fecha",]


@admin.register(FacturaCt)
class FacturaCtAdmin(admin.ModelAdmin):
    list_display = (
        "correlativo",
        "fecha",
        "nComprobacion",
        "serie",
        "corrIntUni",
        "contribuyente",
        "venExentas",
        "venGravadas",
        "ivaDebFiscal",
        "vtVentas",
        "vtIVA",
        "ivaRetenido",
        "total",
        "libro",
        "ventasNSujetas",
    )
    search_fields = ["id","correlativo","fecha","contribuyente__nombre","contribuyente__nit","contribuyente__nRegistro"]
    

@admin.register(FacturaCm)
class FacturaCmAdmin(admin.ModelAdmin):
    list_display = (
        "correlativo",
        "fecha",
        "empresa",
        "cExenteInterna",
        "cExenteImportaciones",
        "cGravadaInterna",
        "cGravadaImportaciones",
        "ivaCdtoFiscal",
        "totalCompra",
        "retencionPretencion",
        "anticipoCtaIva",
        "ivaTerceros",
        "comprasNSujetas",
        "libro",
    )
    search_fields = ["correlativo","fecha","empresa__nit","empresa__nombre","empresa__nRegistro","id"]


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    '''Admin View for Empresa'''

    list_display = ('id','nombre','nRegistro','nit')
    search_fields = list_display
    