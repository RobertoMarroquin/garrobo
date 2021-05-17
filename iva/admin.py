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
        "id",
        "fecha",
        "numeroControlInternoDel",
        "numeroControlInternoAl",
        "claseDocumento",
        "tipoDocumento",
        "numeroResolucion",
        "numeroSerie",
        "correlativoInicial",
        "correlativoFinal",
        "numeroRegistradora",
        "exento",
        "ventasInternasExentas",
        "ventasNSujetas",
        "locales",
        "exportacionesCA",
        "exportacionesNoCA",
        "exportacionesServicios",
        "ventasZonasFrancas",
        "ventaCtaTerceros",
        "ventaTotal",
    )
    search_fields = ["id","correlativoInicial","correlativoFinal","fecha",]


@admin.register(FacturaCt)
class FacturaCtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contribuyente",
        "fecha",
        "numeroDocumento",
        "claseDocumento",
        "tipoDocumento",
        "numeroResolucion",
        "numeroSerie",
        "numeroControlInterno",
        "venExentas",
        "ventasNSujetas",
        "venGravadas",
        "ivaDebFiscal",
        "vtVentas",
        "vtIVA",
        "total",
        "ivaRetenido",
        "correlativo"
    )
    search_fields = ["id","fecha","contribuyente__nombre","contribuyente__nit","contribuyente__nRegistro"]
    

@admin.register(FacturaCm)
class FacturaCmAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "empresa",
        "fecha",
        "numeroDocumento",
        "claseDocumento",
        "tipoDocumento",
        "cExenteInterna",
        "cExenteInternaciones",
        "cExenteImportaciones",
        "cGravadaInterna",
        "cGravadaInternaciones",
        "cGravadaImportaciones",
        "cGravadaImportacionesServicios",
        "ivaCdtoFiscal",
        "totalCompra",
        "retencionPretencion",
        "anticipoCtaIva",
        "ivaTerceros",
        "correlativo",
    )
    search_fields = ["id","numeroDocumento","correlativo","fecha","empresa__nit","empresa__nombre","empresa__nRegistro","id"]


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    '''Admin View for Empresa'''

    list_display = ('id','nombre','nRegistro','nit')
    search_fields = list_display


@admin.register(RetencionCompra)
class RetencionCompraAdmin(admin.ModelAdmin):
    '''Admin View for RetencionCompra'''

    list_display = ("libro",
            "fecha",
            "numeroDocumento",
            "numeroSerie",
            "retencion",
            "monto_sujeto",
            "empresa",)
    list_filter = ('fecha',)
    search_fields = (
        "fecha",
        "numeroDocumento",
        "numeroSerie",
        "retencion",
        "monto_sujeto",
        "empresa__nit"
    )
    