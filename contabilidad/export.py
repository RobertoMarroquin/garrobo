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
    

def cuenta_largo(tamano,cadena):
    if len(cadena) == tamano:
        return True
    else:
        return False


def imprimir_diario_mayor(libro_id):
    libro = Libro.objects.get(id=libro_id)
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    todos = Movimiento.objects.filter(cuenta__catalogo = catalogo, partida__libro__periodo  = libro.periodo)
    #lista de codigos de los movimientos involucrados
    codigos = list(Movimiento.objects.filter(partida__libro__id=libro_id).distinct().values("cuenta__codigo"))
    cuentas_mayores = list(catalogo.subcuentas.filter(es_mayor=True))
    cuentas = []
    for cuenta in cuentas_mayores:
        lista = list(cuenta.subcuentas.all())
        for i in lista:
            cuentas.append(i)
    cuentas_mayores += cuentas
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
        BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_DIARIO_MAYOR.xlsx", 
        engine='xlsxwriter')
    wb = writer.book
    #Creacion de hoja
    ws = wb.add_worksheet("mayor")
    #Configuracion de pagina
    ws.set_landscape()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
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
    #Seteado de tamano
    ws.set_column(1,1,20)
    ws.set_column(2,3,3)
    ws.set_column(4,7,10)
    #Encabezado de hoja
    ws.merge_range("A1:H1",f"{catalogo.empresa.nombre}",header_format)
    ws.merge_range("A2:H2", f"Libro Diario Mayor del mes de {libro.get_mes_display()} de {libro.periodo.ano}",header_format)
    ws.merge_range("A3:D3","Cuenta",header_format)
    ws.write("E3","Saldo Anterior",header_format)
    ws.write("F3","Haber",header_format)
    ws.write("G3","Deber",header_format)
    ws.write("H3","Saldo Actual",header_format)
    #Listado de cuentas con movimientos
    lista_cuentas = []
    for i in cuentas_mayores:
        lista_cuentas += get_ruta_cuenta(i.id)
    lista_cuentas = sorted(set(lista_cuentas))
    #Escritura de cuerpo
    row = 3
    for i in lista_cuentas:
        largo = len(i)
        ws.write(row, 0,i)
        row_aux = row
        ws.set_row(row_aux,35)
        #Nombre de cuenta
        if largo == 1:
            ws.write(row_aux,1,Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper())
            
        else:
            ws.write(row_aux,1,SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre)
        #bordes
        bordes = wb.add_format()
        if largo == 1:
            bordes.set_bottom(2)
        elif largo == 2:
            bordes.set_bottom(1)
        elif largo == 4:
            bordes.set_bottom(3)
        #Montos
        if i[0] in ("1",'4','6'):
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            ws.write(row_aux,4,"${0:.2f}".format(total_anterior),bordes) 
            ws.write(row_aux,5, "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"]),bordes)
            ws.write(row_aux,6, "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"]),bordes)
            ws.write(row_aux,7, "${0:.2f}".format(total_actual),bordes)
        else:
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            ws.write(row_aux,4,"${0:.2f}".format(total_anterior),bordes)
            ws.write(row_aux,5,"${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"]),bordes)
            ws.write(row_aux,6,"${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"]),bordes)
            ws.write(row_aux,7,"${0:.2f}".format(total_actual),bordes)
        #Resumen de cuentas
        if largo == 4:
            for partida in Partida.objects.filter(libro=libro):
                totales = partida.movimientos.filter(cuenta__codigo__startswith=i).aggregate(haber=Coalesce(Sum("monto_haber"),0),deber=Coalesce(Sum("monto_deber"),0))
                haber = totales["haber"]
                deber = totales["deber"]
                if haber>0 or deber>0: 
                    row+=1
                    ws.set_row(row,20)
                    ws.write(row,1,f"{partida.fecha.strftime('%d/%m/%Y')}")
                    ws.write(row,5,"${0:.2f}".format(haber))
                    ws.write(row,6,"${0:.2f}".format(deber))
        row+=1
    writer.save()
    return writer.book


def imprimir_auxiliar(libro_id):
    libro = Libro.objects.get(id=libro_id)
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    todos = Movimiento.objects.filter(cuenta__catalogo = catalogo, partida__libro__periodo  = libro.periodo)
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
        BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_AUXILIAR.xlsx", 
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
    for i in ("A","B","C","D","E","F","G","H"):
        ws[f"{i}2"].border = Border(bottom=Side(border_style="thin", color="000000"))
        ws[f"{i}2"].alignment = Alignment(vertical="center")
    ws["A3"],ws["E3"],ws["F3"],ws["G3"],ws["H3"] = "Cuentas","Saldo Anterior","Haber","Deber","Saldo Actual"
    row = 4
    for i in lista_cuentas:
        ws[f"A{row}"] = i
        largo = len(i)
        row_aux = row
        rd = ws.row_dimensions[row]
        rd.height = 30
        cd = ws.column_dimensions["B"]
        cd.width = 25
        cd = ws.column_dimensions["A"]
        cd.width = 12
        cd = ws.column_dimensions["C"]
        cd.width = 5
        cd = ws.column_dimensions["D"]
        cd.width = 5
        cd = ws.column_dimensions["E"]
        cd.width = 10
        cd = ws.column_dimensions["F"]
        cd.width = 10
        cd = ws.column_dimensions["G"]
        cd.width = 10
        cd = ws.column_dimensions["H"]
        cd.width = 10
        for x in ("A","B","C","D","E","F","G","H"):
            ws[f"{x}2"].alignment = Alignment(horizontal='justify',vertical='center',wrap_text=True,shrink_to_fit=True)
        if largo == 1:
            ws[f"B{row}"] = Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper()
            ws[f"A{row}"].border = Border(bottom=Side(style='thin'))
            ws[f"B{row}"].border = Border(bottom=Side(style='thin'))
            ws[f"E{row}"].border = Border(bottom=Side(style='dashDotDot'))
            ws[f"F{row}"].border = Border(bottom=Side(style='dashDotDot'))
            ws[f"G{row}"].border = Border(bottom=Side(style='dashDotDot'))
            ws[f"H{row}"].border = Border(bottom=Side(style='dashDotDot'))

        else:
            ws[f"B{row}"] = SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre
        row+=1
        for movimiento in movimientos.filter(cuenta__codigo = i):
            ws[f"A{row}"] = f"{movimiento.partida.fecha.strftime('%d/%m/%Y')}"
            ws[f"B{row}"] = movimiento.descripcion
            ws[f"F{row}"] = "${0:.2f}".format(movimiento.monto_haber)
            ws[f"G{row}"] = "${0:.2f}".format(movimiento.monto_deber)

            if movimiento.cuenta.codigo[0] in ("2",'3','5'):
                celda = (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_haber")-Sum("monto_deber"))["monto_anterior"]) if (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_haber")-Sum("monto_deber"))["monto_anterior"]) is not None else 0.00
                ws[f"E{row}"] = "${0:.2f}".format(celda)
                celda = (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_haber")-Sum("monto_deber"))["monto_actual"]) if (todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_haber")-Sum("monto_deber"))["monto_actual"]) is not None else 0.00
                ws[f"H{row}"] = "${0:.2f}".format(celda + movimiento.monto_haber - movimiento.monto_deber)
            else:
                celda = todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_deber")-Sum("monto_haber"))["monto_anterior"] if todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_anterior = Sum("monto_deber")-Sum("monto_haber"))["monto_anterior"] is not None else 0.00
                ws[f"E{row}"] = "${0:.2f}".format(celda)
                celda = todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_deber")-Sum("monto_haber"))["monto_actual"] if todos.filter(partida__fecha__lte=movimiento.partida.fecha,creado__lt=movimiento.creado,cuenta=movimiento.cuenta).aggregate(monto_actual = Sum("monto_deber")-Sum("monto_haber"))["monto_actual"] is not None else 0.00 
                ws[f"H{row}"] = "${0:.2f}".format(celda + movimiento.monto_deber - movimiento.monto_haber)
            rd = ws.row_dimensions[row]
            rd.height = 15    
            row+=1
        if i[0] in ("1",'4','6'):
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            ws[f"E{row_aux}"] = "${0:.2f}".format(total_anterior)
            ws[f"F{row_aux}"] = "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"])
            ws[f"G{row_aux}"] = "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"])
            ws[f"H{row_aux}"] = "${0:.2f}".format(total_actual)

        else:
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            ws[f"E{row_aux}"] = "${0:.2f}".format(total_anterior)
            ws[f"F{row_aux}"] = "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"])
            ws[f"G{row_aux}"] = "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"])
            ws[f"H{row_aux}"] = "${0:.2f}".format(total_actual)
    writer.save()
    return BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_auxiliar.xlsx"


def imprimir_mayor(libro_id):
    libro = Libro.objects.get(id=libro_id)
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    todos = Movimiento.objects.filter(cuenta__catalogo = catalogo, partida__libro__periodo  = libro.periodo)
    #lista de codigos de los movimientos involucrados
    codigos = list(Movimiento.objects.filter(partida__libro__id=libro_id).distinct().values("cuenta__codigo"))
    cuentas_mayores = list(catalogo.subcuentas.filter(es_mayor=True))
    cuentas = []
    for cuenta in cuentas_mayores:
        lista = list(cuenta.subcuentas.all())
        for i in lista:
            cuentas.append(i)
    cuentas_mayores += cuentas
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
        BASE_DIR/f"libros_contables/{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_LIBRO_MAYOR.xlsx", 
        engine='xlsxwriter')
    wb = writer.book
    #Creacion de hoja
    ws = wb.add_worksheet("mayor")
    #Configuracion de pagina
    ws.set_landscape()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
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
    #Seteado de tamano
    ws.set_column(1,1,20)
    ws.set_column(2,3,3)
    ws.set_column(4,7,10)
    #Encabezado de hoja
    ws.merge_range("A1:H1",f"{catalogo.empresa.nombre}",header_format)
    ws.merge_range("A2:H2", f"Libro Diario Mayor del mes de {libro.get_mes_display()} de {libro.periodo.ano}",header_format)
    ws.merge_range("A3:D3","Cuenta",header_format)
    ws.write("E3","Saldo Anterior",header_format)
    ws.write("F3","Haber",header_format)
    ws.write("G3","Deber",header_format)
    ws.write("H3","Saldo Actual",header_format)
    #Listado de cuentas con movimientos
    lista_cuentas = []
    for i in cuentas_mayores:
        lista_cuentas += get_ruta_cuenta(i.id)
    lista_cuentas = sorted(set(lista_cuentas))
    #Escritura de cuerpo
    row = 3
    for i in lista_cuentas:
        largo = len(i)
        ws.write(row, 0,i)
        row_aux = row
        ws.set_row(row_aux,30)
        #Nombre de cuenta
        if largo == 1:
            ws.write(row_aux,1,Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper())
            
        else:
            ws.write(row_aux,1,SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre)
        #Montos
        if i[0] in ("1",'4','6'):
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            ws.write(row_aux,4,"${0:.2f}".format(total_anterior)) 
            ws.write(row_aux,5, "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"]))
            ws.write(row_aux,6, "${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"]))
            ws.write(row_aux,7, "${0:.2f}".format(total_actual))

        else:
            total_actual =  Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lte=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            total_anterior = Movimiento.objects.filter(cuenta__codigo__startswith=i,partida__libro__mes__lt=libro.mes,partida__libro__periodo = libro.periodo).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            ws.write(row_aux,4,"${0:.2f}".format(total_anterior))
            ws.write(row_aux,5,"${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0))["total"]))
            ws.write(row_aux,6,"${0:.2f}".format(movimientos.filter(cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0))["total"]))
            ws.write(row_aux,7,"${0:.2f}".format(total_actual))
        row+=1
    writer.save()
    return writer.book


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


def imprimir_estado_resultado(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass


def imprimir_balance_general(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    catalogo = Catalogo.objects.get(empresa=periodo.empresa)
    movimientos = Movimiento.objects.exclude(cuenta__codigo__startswith="4").exclude(cuenta__codigo__startswith="6").exclude(cuenta__codigo__startswith="5").filter(partida__libro__periodo=periodo)
    #lista de cuentas
    lista_cuentas = movimientos.values("cuenta__codigo")
    lista_cuentas = list(lista_cuentas)
    lista_limpia = []
    for cuenta in lista_cuentas:
        lista_limpia.append(cuenta['cuenta__codigo'])
    lista_cuentas = sorted(set(lista_limpia))
    lista_todas_cuentas = []
    for cuenta in lista_cuentas:
        ruta = get_ruta_cuenta(SubCuenta.objects.get(catalogo=catalogo.id,codigo=cuenta).id)
        lista_todas_cuentas += ruta
    lista_todas_cuentas = lista_cuentas + lista_todas_cuentas
    lista_todas_cuentas = sorted(set(lista_todas_cuentas))
    mas_larga = 0
    for cuenta in lista_cuentas:
        if len(cuenta) > mas_larga:
            mas_larga = len(cuenta) 
    #Apertura de Libro Excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_contables/{periodo.empresa.nombre}_{periodo.ano}_Balance_General.xlsx", 
        engine='xlsxwriter')
    wb = writer.book
    #Creacion de hoja
    ws = wb.add_worksheet("Balance General")
    #Configuracion de pagina
    ws.set_portrait()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
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
    ws.set_column(1,1,40)
    ws.set_column(0,0,5)
    #Escritura de cuerpo
    row = 3
    #Inicio de pocision de montos
    inicio = 3
    
    for i in lista_todas_cuentas:
        largo = len(i)
        if largo <= 4:
            if largo == 1:
                row += 1
            #ws.write(row, 0,i)
            row_aux = row
            ws.set_row(row_aux,35)
            cell_format = wb.add_format()
            cell_format.set_text_wrap()
            cell_format.set_font_size(10)
            #Nombre de cuenta
            if largo == 1:
                ws.write(row_aux,1,Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper(),cell_format)
                
            else:
                ws.write(row_aux,1,SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre,cell_format)
            #bordes
            ws.set_row(row_aux,20)
            bordes = wb.add_format()
            if largo == 1:
                bordes.set_bottom(2)
            elif largo == 2:
                bordes.set_bottom(1)
            elif largo == 4:
                bordes.set_bottom(3)
            #Montos
            if i[0] in ("1",'4','6'):
                total_cuenta = Movimiento.objects.filter(partida__libro__periodo=periodo,cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
            else:
                total_cuenta = Movimiento.objects.filter(partida__libro__periodo=periodo,cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
            if largo == 1:
                if total_cuenta > 0:
                    ws.write(row_aux,inicio+2,"${0:.2f}".format(total_cuenta),bordes)
                else:
                    ws.write(row_aux,inicio+2,"$({0:.2f})".format(total_cuenta),bordes)
            elif largo == 2:
                if total_cuenta > 0:
                    ws.write(row_aux,inicio+1,"${0:.2f}".format(total_cuenta),bordes)
                else:
                    ws.write(row_aux,inicio+1,"$({0:.2f})".format(total_cuenta),bordes)
            elif largo == 4:
                if total_cuenta > 0:
                    ws.write(row_aux,inicio,"${0:.2f}".format(total_cuenta),bordes)
                else:
                    ws.write(row_aux,inicio,"$({0:.2f})".format(total_cuenta),bordes)
            
            row+=1
    ws.merge_range("A1:G1",f"{catalogo.empresa.nombre}",header_format)
    ws.merge_range("A2:G2",f"BALANCE GENERAL AL 31 DE DICIEMBRE DE {periodo.ano}",header_format)
    writer.save()
    return writer.book



def imprimir_auxiliar_balance_general(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    catalogo = Catalogo.objects.get(empresa=periodo.empresa)
    movimientos = Movimiento.objects.exclude(cuenta__codigo__startswith="4").exclude(cuenta__codigo__startswith="6").exclude(cuenta__codigo__startswith="5").filter(partida__libro__periodo=periodo)
    #lista de cuentas
    lista_cuentas = movimientos.values("cuenta__codigo")
    lista_cuentas = list(lista_cuentas)
    lista_limpia = []
    for cuenta in lista_cuentas:
        lista_limpia.append(cuenta['cuenta__codigo'])
    lista_cuentas = sorted(set(lista_limpia))
    lista_todas_cuentas = []
    for cuenta in lista_cuentas:
        ruta = get_ruta_cuenta(SubCuenta.objects.get(catalogo=catalogo.id,codigo=cuenta).id)
        lista_todas_cuentas += ruta
    lista_todas_cuentas = lista_cuentas + lista_todas_cuentas
    lista_todas_cuentas = sorted(set(lista_todas_cuentas))
    mas_larga = 0
    for cuenta in lista_cuentas:
        if len(cuenta) > mas_larga:
            mas_larga = len(cuenta) 
    #Apertura de Libro Excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_contables/{periodo.empresa.nombre}_{periodo.ano}_Anexos_Balance_General.xlsx", 
        engine='xlsxwriter')
    wb = writer.book
    #Creacion de hoja
    ws = wb.add_worksheet("Anexos Balance Gnral")
    #Configuracion de pagina
    ws.set_portrait()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
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
    ws.set_column(1,1,40)
    ws.set_column(0,0,5)
    #Escritura de cuerpo
    row = 3
    #Inicio de pocision de montos
    if mas_larga == 12:
        inicio = 4
    elif mas_larga == 10:
        inicio = 3
    elif mas_larga == 8:
        inicio = 2
    elif mas_larga == 6:
        inicio = 1
    elif mas_larga == 4:
        inicio = 0
    else:
        inicio = 0

    for i in lista_todas_cuentas:
        largo = len(i)
        if largo == 1:
            row += 1
        #ws.write(row, 0,i)
        row_aux = row
        ws.set_row(row_aux,35)
        cell_format = wb.add_format()
        cell_format.set_text_wrap()
        cell_format.set_font_size(10)
        #Nombre de cuenta
        if largo == 1:
            ws.write(row_aux,1,Cuenta.objects.get(catalogo=catalogo,codigo=i).nombre.upper(),cell_format)
            
        else:
            ws.write(row_aux,1,SubCuenta.objects.get(catalogo=catalogo,codigo=i).nombre,cell_format)
        #bordes
        ws.set_row(row_aux,20)
        bordes = wb.add_format()
        if largo == 1:
            bordes.set_bottom(2)
        elif largo == 2:
            bordes.set_bottom(1)
        elif largo == 4:
            bordes.set_bottom(3)
        #Montos
        if i[0] in ("1",'4','6'):
            total_cuenta = Movimiento.objects.filter(partida__libro__periodo=periodo,cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_deber"),0)-Coalesce(Sum("monto_haber"),0))["total"]
        else:
            total_cuenta = Movimiento.objects.filter(partida__libro__periodo=periodo,cuenta__codigo__startswith=i).aggregate(total=Coalesce(Sum("monto_haber"),0)-Coalesce(Sum("monto_deber"),0))["total"]
        if largo == 1:
            if total_cuenta > 0:
                ws.write(row_aux,inicio+5,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio+5,"$({0:.2f})".format(total_cuenta),bordes)
        elif largo == 2:
            if total_cuenta > 0:
                ws.write(row_aux,inicio+4,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio+4,"$({0:.2f})".format(total_cuenta),bordes)
        elif largo == 4:
            if total_cuenta > 0:
                ws.write(row_aux,inicio+3,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio+3,"$({0:.2f})".format(total_cuenta),bordes)
        elif largo == 6:
            if total_cuenta > 0:  
                ws.write(row_aux,inicio+2,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio+2,"$({0:.2f})".format(total_cuenta),bordes)
        elif largo == 8:
            if total_cuenta > 0:
                ws.write(row_aux,inicio+1,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio+1,"$({0:.2f})".format(total_cuenta),bordes)
        elif largo == 10:
            if total_cuenta > 0:
                ws.write(row_aux,inicio,"${0:.2f}".format(total_cuenta),bordes)
            else:
                ws.write(row_aux,inicio,"$({0:.2f})".format(total_cuenta),bordes)
        row+=1
    ws.merge_range("A1:J1",f"{catalogo.empresa.nombre}",header_format)
    ws.merge_range("A2:J2",f"ANEXOS AL BALANCE GENERAL AL 31 DE DICIEMBRE DE {periodo.ano}",header_format)
    writer.save()
    return writer.book


def imprimir_estado_cambio_patrimonio(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass


def imprimir_estado_flujo_efectivo(periodo_id):
    periodo = Periodo.objects.get(id=periodo_id)
    pass
