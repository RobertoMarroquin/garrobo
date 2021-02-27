from django import template
from django.db.models import Sum
from django.db.models.functions import Coalesce

from contabilidad.models import *

register = template.Library()


@register.simple_tag(name="parcu")
def partida_cuadrada(partida_id):
    partida = Partida.objects.get(id=partida_id)
    diferencia = partida.movimientos.all().aggregate(dif=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["dif"]
    return True if diferencia >= -0.0099 and diferencia <= 0.0099  else False
    