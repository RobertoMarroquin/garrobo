from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Locacion)
class LocacionAdmin(admin.ModelAdmin):

    list_display = ( "id",
            "nombre",
            "direccion",
            "creado",)
    search_fields = (
            "nombre",
            "direccion",
            "creado",)


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):

    list_display = ( "id",
        "codigo",
        "nombre",
        "creado",
    )
    search_fields = (
        "codigo",
        "nombre",
        "creado",
    )


@admin.register(CatalogoProducto)
class CatalogoProductoAdmin(admin.ModelAdmin):

    list_display = ( "id",
        "empresa",
        "creado",
    )
    search_fields = (
        "empresa",
        "creado",
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):

    list_display = ( "id",
        "codigo",
        "nombre",
        "catalogo",
        "creado",
    )
    search_fields = (
        "codigo",
        "nombre",
        "catalogo",
        "creado",
    )


@admin.register(DetalleProducto)
class DetalleProductoAdmin(admin.ModelAdmin):

    list_display = ( "id",
        "producto",
        "ubicacion",
        "existencia",
        "fecha_entrada",
        "perecedero",
        "fecha_caducidad",
        "creado",
    )
    search_fields = (
        "producto",
        "ubicacion",
        "existencia",
        "fecha_entrada",
        "perecedero",
        "fecha_caducidad",
        "creado",
    )


