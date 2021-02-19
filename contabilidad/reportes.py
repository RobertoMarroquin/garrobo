#third party Libs
from datetime import datetime
import numpy as np
import pandas as pd
import openpyxl as ox
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Alignment
import xlsxwriter as xw
import matplotlib.pyplot as plt

#python libs
from decimal import Decimal as dec
import os

#django libs
from django.utils.dateformat import DateFormat
from django.db.models import Sum
from django.db.models.functions import Coalesce

#self libs
from .models import *
from empresas.models import Empresa
from garrobo.settings import BASE_DIR

def get_ruta_cuenta(cuenta_id):
    cuenta = SubCuenta.objects.get(id=cuenta_id)
    cuentas = []
    cuentas.append(cuenta.codigo)
    while cuenta.cuenta_padre is not None:
        cuentas.append(cuenta.cuenta_padre.codigo)
        cuenta = cuenta.cuenta_padre
    if cuenta.es_mayor:
        cuentas.append(cuenta.cuenta_principal.codigo)
    return cuentas

def rep_anexos_balanace(libro_id):
    libro = Libro.objects.get(id=libro_id)
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    if libro.mes in (1,3,5,7,8,10,12):
        movs = Movimiento.objects.filter(partida__libro__periodo=libro.periodo,partida__fecha__lte=f"{libro.periodo.ano}-{libro.mes}-31")
    elif libro.mes in (4,6,9,11):
        movs = Movimiento.objects.filter(partida__libro__periodo=libro.periodo,partida__fecha__lte=f"{libro.periodo.ano}-{libro.mes}-30")
    else:
        if libro.periodo.ano%4 ==0:
            movs = Movimiento.objects.filter(partida__libro__periodo=libro.periodo,partida__fecha__lte=f"{libro.periodo.ano}-{libro.mes}-29")
        else:
            movs = Movimiento.objects.filter(partida__libro__periodo=libro.periodo,partida__fecha__lte=f"{libro.periodo.ano}-{libro.mes}-28")
    
    #Separacion activos de pasivos
    movs_activos = movs.filter(cuenta__codigo__startswith="1") | movs.filter(cuenta__codigo__startswith="4")
    movs_pasivos = movs.filter(cuenta__codigo__startswith="2") | movs.filter(cuenta__codigo__startswith="3") | movs.filter(cuenta__codigo__startswith="5") 
    
    #listas de cuentas activo
    cuentas_activo = movs_activos.values("cuenta__id")
    lista_cuentas_activo = []
    for i in cuentas_activo:
        lista_cuentas_activo += get_ruta_cuenta(i["cuenta__id"])
    lista_cuentas_activo = sorted(set(lista_cuentas_activo))
    
    #listas de cuentas pasivo
    cuentas_pasivo = movs_pasivos.values("cuenta__id")
    lista_cuentas_pasivo = []
    for i in cuentas_pasivo:
        lista_cuentas_pasivo += get_ruta_cuenta(i["cuenta__id"])
    lista_cuentas_pasivo = sorted(set(lista_cuentas_pasivo))
    
    #Creacion de libro
    #Ceacion de objeto Excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.get_mes_display()}_{libro.periodo.ano}_Balance_comprobacion.xlsx",
        engine='xlsxwriter')
    wb = writer.book
    #Creacion de hoja
    ws = wb.add_worksheet("Balance-Activos")
    ws2 = wb.add_worksheet("Balance-Pasivos")
    #Configuracion de pagina
    ws.set_portrait()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
    ws2.set_portrait()
    ws2.set_paper(1)
    ws2.set_margins(0.26,0.26,0.75,0.75)
    #formato de cabecera
    header_format = wb.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'border': 1,
    "font_size":10,
    })
    header_format.set_align("center")
    header_format.set_align("vcenter")
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("center")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #Escritura de cabecera  Activo
    ws.merge_range("A1:J1",f"{catalogo.empresa.nombre}",header_format)
    ws.merge_range("A2:J2",f"BALANCE GENERAL AL MES DE {libro.get_mes_display()} DE {libro.periodo.ano}")
    ws.merge_range("A3:J3",f"ACTIVO")

    ws.merge_range("A5:B5","Cuentas",body_format)
    ws.merge_range("D5:I5","Parciales",body_format)
    ws.write("J5","Totales",body_format)
    #Escritura de cabecera  PASIVO
    ws2.merge_range("A1:J1",f"{catalogo.empresa.nombre}",header_format)
    ws2.merge_range("A2:J2",f"BALANCE GENERAL AL MES DE {libro.get_mes_display()} DE {libro.periodo.ano}")
    ws2.merge_range("A3:J3",f"PASIVO")

    ws2.merge_range("A5:B5","Cuentas",body_format)
    ws2.merge_range("D5:I5","Parciales",body_format)
    ws2.write("J5","Totales",body_format)

    #Estructura de tablas
    ws.set_column(0,0,10)
    ws.set_column(1,1,25)
    ws.set_column(2,2,3)
    ws.set_column(3,10,10)
    ws2.set_column(0,0,10)
    ws2.set_column(1,1,25)
    ws2.set_column(2,2,3)
    ws2.set_column(3,10,10)
    #Lista de activos
    row = 5
    for i in lista_cuentas_activo:
        ws.set_row(row,25)
        largo = len(i)
        if largo == 1:
            cuenta = Cuenta.objects.get(catalogo=catalogo,codigo=i)
        else:
            cuenta = SubCuenta.objects.get(catalogo=catalogo,codigo=i)
        ws.write(row,0,cuenta.codigo,body_format)
        ws.write(row,1,cuenta.nombre,body_format)
        #Totalizacion de cuentas
        if i[0] in ("2",'5','3'):
            total = movs.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))['total']
        else:
            total = movs.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))['total']

        if total >= 0:
            total = "{0:.2f}".format(total)
        else:
            total = "({0:.2f})".format(total)

        if largo == 1:
            ws.write(f"J{row+1}",f"${total}",body_format)
        elif largo == 2:
            ws.write(f"I{row+1}",f"${total}",body_format)
        elif largo == 4:
            ws.write(f"H{row+1}",f"${total}",body_format)
        elif largo == 6:
            ws.write(f"G{row+1}",f"${total}",body_format)
        elif largo == 8:
            ws.write(f"F{row+1}",f"${total}",body_format)
        elif largo == 10:
            ws.write(f"E{row+1}",f"${total}",body_format)
        elif largo == 12:
            ws.write(f"D{row+1}",f"${total}",body_format)
        row +=1

    activo = movs.filter(cuenta__codigo__startswith="1") | movs.filter(cuenta__codigo__startswith="5")
    activo = activo.aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
    ws.merge_range(f"A{row+2}:J{row+2}","",foot_format)
    ws.merge_range(f"A{row+3}:H{row+3}","Total Activo",foot_format)
    ws.merge_range(f"I{row+3}:J{row+3}","${0:.2f}".format(activo),foot_format)
    writer.save()
    #Lista de Pasivo
    row = 5
    for i in lista_cuentas_activo:
        ws2.set_row(row,25)
        largo = len(i)
        if largo == 1:
            cuenta = Cuenta.objects.get(catalogo=catalogo,codigo=i)
        else:
            cuenta = SubCuenta.objects.get(catalogo=catalogo,codigo=i)
        ws2.write(row,0,cuenta.codigo,body_format)
        ws2.write(row,1,cuenta.nombre,body_format)
        #Totalizacion de cuentas
        if i[0] in ("2",'5','3'):
            total = movs.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))['total']
        else:
            total = movs.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))['total']

        if total >= 0:
            total = "{0:.2f}".format(total)
        else:
            total = "({0:.2f})".format(total)

        if largo == 1:
            ws2.write(f"J{row+1}",f"${total}",body_format)
        elif largo == 2:
            ws2.write(f"I{row+1}",f"${total}",body_format)
        elif largo == 4:
            ws2.write(f"H{row+1}",f"${total}",body_format)
        elif largo == 6:
            ws2.write(f"G{row+1}",f"${total}",body_format)
        elif largo == 8:
            ws2.write(f"F{row+1}",f"${total}",body_format)
        elif largo == 10:
            ws2.write(f"E{row+1}",f"${total}",body_format)
        elif largo == 12:
            ws2.write(f"D{row+1}",f"${total}",body_format)
        row +=1
    pasivo = movs.filter(cuenta__codigo__startswith="2") | movs.filter(cuenta__codigo__startswith="3") | movs.filter(cuenta__codigo__startswith="5") 
    pasivo = pasivo.aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
    
    ws2.merge_range(f"A{row+2}:J{row+2}","",foot_format)
    ws2.merge_range(f"A{row+3}:H{row+3}","Total Pasivo",foot_format)
    ws2.merge_range(f"I{row+3}:J{row+3}","${0:.2f}".format(pasivo),foot_format)
    writer.save()
    return BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.get_mes_display()}_{libro.periodo.ano}_Balance_comprobacion.xlsx"