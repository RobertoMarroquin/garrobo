from django import template
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce


from contabilidad.models import *

register = template.Library()


@register.simple_tag(name="parcu")
def partida_cuadrada(partida_id):
    partida = Partida.objects.get(id=partida_id)
    diferencia = partida.movimientos.all().aggregate(dif=Coalesce(Sum("monto_haber",output_field=FloatField()),0,output_field=FloatField())-Coalesce(Sum("monto_deber",output_field=FloatField()),0,output_field=FloatField()))["dif"]
    return True if diferencia >= -0.0099 and diferencia <= 0.0099  else False
    