#third party Libs
import numpy as np
import pandas as pd
import openpyxl as ox
import xlsxwriter as xw
import matplotlib.pyplot as plt

#python libs
from decimal import Decimal as dec
import os

#django libs
from django.utils.dateformat import DateFormat
from django.db.models import Sum

#self libs
from .models import *
from empresas.models import Empresa
from garrobo.settings import BASE_DIR

def imprimir_auxiliar(libro_id):
    libro = Libro.objects.get(id=libro_id)
    partidas = libro.partidas.all()
    catalogo = libro.periodo.empresa.catalogo
    #Listado de movimientos por libro
    movimientos = Movimiento.objects.filter(partida__libro__id=libro_id).order_by("cuenta__codigo")
    movimientos_por_cuenta = {}
    #listado de movimientas clasiciados por cuenta mayos
    for subcuenta in catalogo.subcuentas.all().filter(es_mayor=True):
        movimientos_por_cuenta.update({subcuenta.codigo:[]})
        movimientos_por_cuenta[subcuenta.codigo] = (movimientos.filter(cuenta__codigo__startswith=subcuenta.codigo).order_by("cuenta__codigo"))
    
    #totalizacion de montos de haber y deber
    totales = []
    for cuenta in movimientos_por_cuenta.items():
        totales.append((cuenta[0],cuenta[1].aggregate(monto_haber=Sum("monto_haber"), monto_deber=Sum("monto_deber"))))
    
    #Creacion de Data Frame
    df_movimientos = pd.DataFrame(movimientos.values("id","partida_id","monto_deber","monto_haber","cuenta_id","cuenta__codigo","descripcion","partida__libro__id"))
    print(df_movimientos)
    
    #Trabajo sobre excel
    writer = pd.ExcelWriter(
        BASE_DIR/f"/{libro.periodo.empresa.nombre}_{libro.mes}_{libro.periodo.ano}_auxiliar.xlsx", 
        engine='xlsxwriter')

    workbook  = writer.book
    df = df_movimientos
    df.to_excel(writersheet_name="Auxiliar",index=False,startrow=6,header=False)
    #Formato de Pagina
    worksheet = writer.sheets["Auxiliar"]
    worksheet.set_landscape()
    worksheet.set_paper(1)
    worksheet.set_margins(0.26,0.26,0.75,0.75)

    #formato de cabecera
    header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'border': 1,
    "font_size":9, 
    })
    

##-------------------------------------------------------------------------------------------------------------------##    
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
