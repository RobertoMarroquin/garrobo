from .models import *
from django.db.models.aggregates import Count
from django.db.models.functions import Coalesce
from django.db.models import Sum


def cierre(periodo):
    periodo = Periodo.objects.get(id=periodo)
    if periodo.cerrado:
        return periodo.cerrado
    else:
        empresa = Empresa.objects.get(id=periodo.empresa.id)
        libro = Libro.objects.get_or_create(periodo=periodo,mes=12)
        catalogo = Catalogo.objects.get(empresa=empresa)
        partida = Partida.objects.get_or_create(libro=libro[0], fecha=f"{periodo.ano}-12-31", descripcion="Cierre de Periodo")

        if not partida[1]:
            partida[0].delete()
            partida = Partida.objects.get_or_create(libro=libro[0], fecha=f"{periodo.ano}-12-31", descripcion="Cierre de Periodo")

        total4 = Movimiento.objects.exclude(partida=partida[0]).filter(partida__libro__periodo=periodo,cuenta__codigo__startswith="4").aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
        total5 = Movimiento.objects.exclude(partida=partida[0]).filter(partida__libro__periodo=periodo,cuenta__codigo__startswith="5").aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
        valor6 = total5 - total4
        cuenta = SubCuenta.objects.get(catalogo=catalogo,codigo="6101")

        monto4 = Movimiento.objects.exclude(partida=partida[0]).filter(partida__libro__periodo=periodo,cuenta__codigo__startswith="4").aggregate(total_haber=Coalesce(Sum("monto_haber"),0), total_deber=Coalesce(Sum("monto_deber"),0))
        monto5 = Movimiento.objects.exclude(partida=partida[0]).filter(partida__libro__periodo=periodo,cuenta__codigo__startswith="5").aggregate(total_deber=Coalesce(Sum("monto_deber"),0), total_haber=Coalesce(Sum("monto_haber"),0))
        
        #Movimientos para cierre
        Movimiento.objects.get_or_create(partida=partida[0],monto_deber=0, monto_haber=total5,cuenta=cuenta,descripcion="Cierre contable cuenta 5")
        Movimiento.objects.get_or_create(partida=partida[0],monto_deber=total4, monto_haber=0,cuenta=cuenta,descripcion="Cierre contable cuenta 4")
        
        #Movimientos de cuentas 4 y 5
        lista_movs = Movimiento.objects.exclude(partida=partida[0]).filter(cuenta__catalogo=catalogo, cuenta__codigo__startswith ="5", partida__libro__periodo=periodo) | Movimiento.objects.exclude(partida=partida[0]).filter(cuenta__catalogo=catalogo, cuenta__codigo__startswith ="4", partida__libro__periodo=periodo)
        lista_movs = lista_movs.values("cuenta__codigo")
        lista_cuenta = []
        for mov in lista_movs:
            lista_cuenta.append(mov["cuenta__codigo"])
        lista_cuenta = set(lista_cuenta)
        for cuenta in lista_cuenta:

            subcuenta = SubCuenta.objects.get(catalogo=catalogo, codigo=cuenta)
            liquidacion_haber = Movimiento.objects.exclude(partida=partida[0]).filter(cuenta__catalogo=catalogo, cuenta__codigo=cuenta).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"]
            liquidacion_deber = Movimiento.objects.exclude(partida=partida[0]).filter(cuenta__catalogo=catalogo, cuenta__codigo=cuenta).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"]
            if liquidacion_haber > 0:
                mov_haber = Movimiento.objects.get_or_create(partida=partida[0],monto_deber=liquidacion_haber,monto_haber=0,cuenta=subcuenta,descripcion=f"liquidacion haber de cuenta {cuenta}")
            if liquidacion_deber > 0:
                mov_deber = Movimiento.objects.get_or_create(partida=partida[0],monto_haber=liquidacion_deber,monto_deber=0,cuenta=subcuenta,descripcion=f"liquidacion deber de cuenta {cuenta}")

        periodo.cerrado = True
        periodo.save()
        return periodo.cerrado
        