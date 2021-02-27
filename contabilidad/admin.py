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
    search_fields = ["fecha_inicio",
        "fecha_fin",
        "ano",
        "empresa__nombre",
        "creado",
        "id",
        "cerrado",]


class CatalogoAdmin(admin.ModelAdmin):
    list_display = ("empresa",
        "creado","id"
    )
    search_fields = ["empresa__nombre",
        "creado","id"]

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
    search_fields = ["catalogo__empresa__nombre",
        "codigo",
        "nombre",
        "creado",
        "saldo",]


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
    search_fields = ["id","catalogo__empresa__nombre",
        "codigo",
        "nombre",
        "cuenta_padre__nombre",
        "cuenta_principal__nombre",
        "creado",
        "saldo",
        "es_mayor",
    ]


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
        'get_nombre_empresa',
        "libro",
        "descripcion",
        "id",
    )
    search_fields = ["fecha",
        "libro__mes",
        "descripcion",
        "libro__periodo__empresa__nombre",
        ]

    def get_nombre_empresa(self, obj):
        return obj.libro.periodo.empresa.nombre
    get_nombre_empresa.short_description = 'Empresa'
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
    search_fields = ["id",
        "partida__fecha",
        "monto_deber",
        "monto_haber",
        "cuenta__nombre",
        "cuenta__codigo",
        "get_catalogo",
        "descripcion",
    ]
    def get_catalogo(self, obj):
        return obj.cuenta.catalogo
    get_catalogo.short_description = "Catalogo"
    get_catalogo.admin_order_field = "cuenta"

