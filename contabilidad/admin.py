from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    '''Admin View for Periodo'''

    list_display = ("fecha_inicio",
        "fecha_fin",
        "ano",
        "empresa",
        "creado",
        "id",
        "cerrado",
    )


class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("empresa",
        "creado","id"
    )

admin.site.register(Catalogo, CatalogoAdmin)

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    '''Admin View for Cuenta'''
    list_display = ("catalogo",
        "codigo",
        "nombre",
        "creado",
        "saldo",
    )


@admin.register(SubCuenta)
class SubCuentaAdmin(admin.ModelAdmin):
    '''Admin View for SubCuenta'''
    list_display = ("id","catalogo",
        "codigo",
        "nombre",
        "cuenta_padre",
        "cuenta_principal",
        "creado",
        "saldo",
        "es_mayor",
    )


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    '''Admin View for Libro'''
    list_display = (
        "mes",
        "periodo",
    )
    search_fields = ["mes","periodo__empresa__nombre","periodo__empresa__num_registro"]

class MovimientoInline(admin.TabularInline):
    '''Tabular Inline View for Movimiento'''

    model = Movimiento
    min_num = 0
    max_num = 20
    extra = 1
    raw_id_fields = ["partida",]
    


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    '''Admin View for Partida'''
    list_display = ("fecha",
        "libro",
        "descripcion",
        "id",
    )
    inlines = [MovimientoInline,]


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    '''Admin View for Movimiento'''
    list_display = ("id",
        "partida",
        "monto_deber",
        "monto_haber",
        "cuenta",
        "get_catalogo",
        "descripcion",
    )
    def get_catalogo(self, obj):
        return obj.cuenta.catalogo
    get_catalogo.short_description = "Catalogo"
    get_catalogo.admin_order_field = "cuenta"
