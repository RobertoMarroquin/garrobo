#third party Libs
from datetime import datetime
import numpy as np
import pandas as pd
import openpyxl as ox
from openpyxl.styles.borders import Border, Side
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
    

def cuenta_largo(tamano,cadena):
    if len(cadena) == tamano:
        return True
    else:
        return False


def imprimir_auxiliar(libro_id):
    libro = Libro.objects.get(id=libro_id)
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    todos = Movimiento.objects.filter(cuenta__catalogo = catalogo)
    #lista de codigos de los movimientos involucrados
    codigos = list(Movimiento.objects.filter(partida__libro__id=libro_id).distinct().values("cuenta__codigo"))
    cuentas_mayores = list(catalogo.subcuentas.filter(es_mayor=True))
    #diccionario de codigos
    dic_c = {}
    for codigo in codigos:
        dic_c[codigo["cuenta__codigo"]] = list(movimientos.filter(cuenta__codigo=codigo["cuenta__codigo"]).values(
            "id",
            "partida_id",
            "partida__fecha",
            "monto_deber",
            "monto_haber",
            "cuenta_id",
            "cuenta__codigo",
            "descripcion",
            )
        )
    #Ceacion de objeto Excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"./{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_auxiliar.xlsx", 
        engine='openpyxl')
    wb = writer.book
    ws = wb.create_sheet("auxiliar")
    dfs = []
    
    for i in dic_c.items():
        df = pd.DataFrame(i[1])
        dfs.append(df)
    lista_cuentas = []    
    for i in movimientos:
        lista_cuentas += get_ruta_cuenta(i.cuenta.id)
    for i in cuentas_mayores:
        lista_cuentas += get_ruta_cuenta(i.id)
    lista_cuentas = sorted(set(lista_cuentas))
    ws.merge_cells('A1:H1')
    ws["A1"] = catalogo.empresa.nombre
    ws.merge_cells('A2:H2')
    ws["A2"] = f"Libro Auxiliar del mes de {libro.get_mes_display()} de {libro.periodo.ano}"
    ws["A2"].border = Border(bottom=Side(border_style="thin", color="000000"))
    ws["A3"],ws["E3"],ws["F3"],ws["G3"],ws["H3"] = "Cuentas","Monto Anterior","Haber","Deber","Monto Actual"
    row = 4
    for i in lista_cuentas:
        ws[f"A{row}"] = i
        largo = len(i)
        row_aux = row
        rd = ws.row_dimensions[row]
        rd.height = 15
        cd = ws.column_dimensions["B"]
        cd.width = 30
        cd = ws.column_dimensions["A"]
        cd.width = 12
        cd = ws.column_dimensions["C"]
        cd.width = 5
        cd = ws.column_dimensions["D"]
        cd.width = 5
        if largo == 1:
            ws[f"B{row}"] = Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper()
            ws[f"A{row}"].border = Border(bottom=Side(style='thin'))
            ws[f"B{row}"].border = Border(bottom=Side(style='thin'))
        else:
            ws[f"B{row}"] = SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre
        row+=1
        for movimiento in movimientos.filter(cuenta__codigo = i):
            ws[f"A{row}"] = f"{movimiento.partida.fecha.strftime('%d/%m/%Y')}"
            ws[f"B{row}"] = movimiento.descripcion
            if movimiento.cuenta.codigo[0] in ("2",'3','5'):
                celda = (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_haber")-Sum("monto_deber"))["monto_anterior"]) if (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_haber")-Sum("monto_deber"))["monto_anterior"]) is not None else 0.00
                ws[f"E{row}"] = "{0:.2f}".format(celda)
                ws[f"F{row}"] = "{0:.2f}".format(movimiento.monto_haber)
                ws[f"G{row}"] = "{0:.2f}".format(movimiento.monto_deber)
                celda = (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_haber")-Sum("monto_deber"))["monto_actual"]) if (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_haber")-Sum("monto_deber"))["monto_actual"]) is not None else 0.00
                ws[f"H{row}"] = "{0:.2f}".format(celda + movimiento.monto_haber - movimiento.monto_deber)
            else:
                celda = todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_deber")-Sum("monto_haber"))["monto_anterior"] if todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_deber")-Sum("monto_haber"))["monto_anterior"] is not None else 0.00
                ws[f"E{row}"] = "{0:.2f}".format(celda)
                ws[f"F{row}"] = "{0:.2f}".format(movimiento.monto_haber)
                ws[f"G{row}"] = "{0:.2f}".format(movimiento.monto_deber)
                celda = todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_deber")-Sum("monto_haber"))["monto_actual"] if todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_deber")-Sum("monto_haber"))["monto_actual"] is not None else 0.00 
                ws[f"H{row}"] = "{0:.2f}".format(celda + movimiento.monto_deber - movimiento.monto_haber)
            rd.height = 15    
            row+=1
        if i[0] in ("1",'4','6'):
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            ws[f"E{row_aux}"] = "{0:.2f}".format(total_anterior)
            ws[f"F{row_aux}"] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"])
            ws[f"G{row_aux}"] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"])
            ws[f"H{row_aux}"] = "{0:.2f}".format(total_actual)

        else:
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            ws[f"E{row_aux}"] = "{0:.2f}".format(total_anterior)
            ws[f"F{row_aux}"] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"])
            ws[f"G{row_aux}"] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"])
            ws[f"H{row_aux}"] = "{0:.2f}".format(total_actual)
    writer.save()
    

#-------------------------------------------------------------------------------------------#
def imprimir_balance(libro_id):
    libro = Libro.objects.get(id=libro_id)
    partidas = libro.partidas.all()
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    #lista de codigos de los movimientos involucrados
    codigos = list(Movimiento.objects.filter(partida__libro__id=libro_id).distinct().values("cuenta__codigo"))
    #diccionario de codigos
    dic_c = {}
    for codigo in codigos:
        dic_c[codigo["cuenta__codigo"]] = list(movimientos.filter(cuenta__codigo=codigo["cuenta__codigo"]).values(
            "id",
            "partida_id",
            "partida__fecha",
            "monto_deber",
            "monto_haber",
            "cuenta_id",
            "cuenta__codigo",
            "descripcion",
            "creado",
            )
        )
    #Ceacion de objeto Excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"./{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_auxiliar.xlsx", 
        engine='openpyxl')
    wb = writer.book
    ws = wb.create_sheet("auxiliar")
    dfs = []
    for i in dic_c.items():
        df = pd.DataFrame(i[1])
        dfs.append(df)
    lista_cuentas = []    
    for i in movimientos:
        lista_cuentas += get_ruta_cuenta(i.cuenta.id)
    lista_cuentas = sorted(set(lista_cuentas))
    row = 2
    
    for i in lista_cuentas:
        ws[f"A{row}"] = i
        largo = len(i)
        row_aux = row
        if largo == 1:
            ws[f"B{row}"] = Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper()
            ws[f"A{row}"].border = Border(bottom=Side(style='thin'))
            ws[f"B{row}"].border = Border(bottom=Side(style='thin'))
        else:
            ws[f"B{row}"] = SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre
        row+=1
        for movimiento in movimientos.filter(cuenta__codigo = i):
            #ws.insert_rows(row+1,amount=1)
            ws[f"C{row}"] = movimiento.partida.fecha
            if largo == 1:
                ws[f"D{row}"] = "{0:.2f}".format(movimiento.monto_haber)
                ws[f"E{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 2:
                ws[f"F{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"G{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 4:
                ws[f"H{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"I{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 6:    
                ws[f"J{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"K{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 8:
                ws[f"L{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"M{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 10:
                ws[f"N{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"O{row}"] = "{0:.2f}".format(movimiento.monto_deber) 
            elif largo == 12:
                ws[f"P{row}"] = "{0:.2f}".format(movimiento.monto_haber) 
                ws[f"Q{row}"] = "{0:.2f}".format(movimiento.monto_deber)

            row+=1
        #print(f"{row - row_aux}"
        if largo == 1  :
            ws[f'D{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'E{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'D{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'E{row_aux}'].border = Border(bottom=Side(style='thin'))

        elif largo == 2 :
            ws[f'F{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'G{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'F{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'G{row_aux}'].border = Border(bottom=Side(style='thin'))

        elif largo == 4 :
            ws[f'H{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'I{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'H{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'I{row_aux}'].border = Border(bottom=Side(style='thin'))
        
        elif largo == 6 :
            ws[f'J{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'K{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'J{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'K{row_aux}'].border = Border(bottom=Side(style='thin'))

        elif largo == 8 :
            ws[f'L{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'M{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'L{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'M{row_aux}'].border = Border(bottom=Side(style='thin'))
        
        elif largo == 10 :
            ws[f'N{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'O{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'N{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'O{row_aux}'].border = Border(bottom=Side(style='thin'))

        elif largo == 12 :
            ws[f'P{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_haber'))["total"])
            ws[f'Q{row_aux}'] = "{0:.2f}".format(movimientos.filter(cuenta__codigo__startswith = i).aggregate(total=Sum('monto_deber'))["total"])
            ws[f'P{row_aux}'].border = Border(bottom=Side(style='thin'))
            ws[f'Q{row_aux}'].border = Border(bottom=Side(style='thin'))

    writer.save()


#-------------------------------------------------------------------------------------------#    
def imprimir_mayor(libro_id):
    libro = Libro.objects.get(id=libro_id)
    pass


def imprimir_estado_resultado(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass


def imprimir_balance_general(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass


def imprimir_estado_cambio_patrimonio(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass


def imprimir_estado_flujo_efectivo(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass
