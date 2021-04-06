from django.contrib import admin
from .models import *


@admin.register(Talonario)
class TalonarioAdmin(admin.ModelAdmin):
    list_display = ('empresa','ano',"id",)
    search_fields = ('empresa__nombre',"id",)


@admin.register(Mensualidad)
class MensualidadAdmin(admin.ModelAdmin):
    list_display = ('talonario','mes',"id",)
    search_fields = ('talonario__ano','talonario__empresa__nombre','mes'"id",)


@admin.register(Cobro)
class CobroAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "descripcion",
        "monto",
        "iva",
        "activo",
        "cancelado",
        "mensualidad",
    )
    search_fields = ("id",
        "descripcion",
        "monto",
        "iva",
        "activo",
        "cancelado",
        "mensualidad",
        'mensualidad__talonario__ano',
        'mensualidad__talonario__empresa__nombre',
    )
