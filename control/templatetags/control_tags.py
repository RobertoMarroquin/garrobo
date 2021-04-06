from django import template
from django.db.models import Sum
from django.db.models.functions import Coalesce

from control.models import *

register = template.Library()


@register.simple_tag(name="totalTal")
def totalTal(talonario_id):
    talonario = Talonario.objects.get(id=talonario_id)
    cobros  = Cobro.objects.filter(mensualidad__talonario = talonario,cancelado=True)
    total = cobros.aggregate(total=Coalesce(Sum("monto"),0))
    return total["total"]


@register.simple_tag(name="ulCo")
def ulCo(talonario_id):
    talonario = Talonario.objects.get(id=talonario_id)
    if Cobro.objects.filter(mensualidad__talonario = talonario,cancelado=True).exists():
        cobro  = Cobro.objects.filter(mensualidad__talonario = talonario,cancelado=True).order_by("-id")[0].fecha_real_pago
    else: cobro = "no hay pagos"
    return cobro


@register.simple_tag(name="cobros")
def cobrosMonto(mes_id):
    mes = Mensualidad.objects.get(id=mes_id)
    if mes.cobros.all().exists():
        monto = mes.cobros.all().aggregate(total=Coalesce(Sum("monto"),0))["total"]
    else:
        monto = 0.00
    return monto


@register.simple_tag(name="cancelado")
def cancelado(mes_id):
    mes = Mensualidad.objects.get(id=mes_id)
    return True if mes.cobros.all().filter(cancelado=False).exists() else False

    