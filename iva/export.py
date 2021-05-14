import numpy as np
import pandas as pd
import openpyxl as ox
import xlsxwriter as xw
import matplotlib.pyplot as plt
import os

from decimal import Decimal as dec

from django.utils.dateformat import DateFormat
from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import *
from empresas.models import Empresa as Cliente
from garrobo.settings import BASE_DIR

def export_libroCF(libro_id):
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCF.objects.filter(libro=libro).values()
    facturas_limpias = []
    #Creacion de de lista para dataFrame
    for fact in facturas:
        factura_dict = {}
        fecha = DateFormat(fact.get("fecha"))

        factura_dict.update({
            "Correlativo Inicial":fact.get("correlativoInicial"),
            "Correlativo Final":fact.get("correlativoFinal"),
            "Fecha": fecha.format('d/m/Y'),
            "Exento":fact.get("exento"),
            "Locales":fact.get("locales"),
            "Exportaciones":fact.get("exportaciones"),
            "Ventas No Sujetas":fact.get("ventasNSujetas"),
            "Ventas Cta Terceros": fact.get("ventaCtaTerceros"),
            "Venta Total":fact.get("ventaTotal"),
        })
        facturas_limpias.append(factura_dict)
    #Creacion de objeto Excel para posterior salida
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_condumidorFinal.xlsx",
        engine='xlsxwriter')

    df_facturas = pd.DataFrame(facturas_limpias)

    workbook  = writer.book
    df = df_facturas
    if libro.mes == 1 : mes = "ENERO"
    elif libro.mes == 2 : mes = "FEBRERO"
    elif libro.mes == 3 : mes = "MARZO"
    elif libro.mes == 4 : mes = "ABRIL"
    elif libro.mes == 5 : mes = "MAYO"
    elif libro.mes == 6 : mes = "JUNIO"
    elif libro.mes == 7 : mes = "JULIO"
    elif libro.mes == 8 : mes = "AGOSTO"
    elif libro.mes == 9 : mes = "SEPTIEMBRE"
    elif libro.mes == 10 : mes = "OCTUBRE"
    elif libro.mes == 11 : mes = "NOVIEMBRE"
    elif libro.mes == 12 : mes = "DICIEMBRE"

    bandera = 1
    #Si hay mas de 25 registros se creara una hoja por cada 20
    while len(df) >=25:
        df[:25].to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
        worksheet = writer.sheets[f"HOJA{bandera}"]
        #Configuracion de pagina
        worksheet.set_portrait()
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
        header_format.set_align("center")
        header_format.set_align("vcenter")
        #Ecritura de cabecera
        for col_num, value in enumerate(df_facturas.columns.values):
            worksheet.write(5, col_num, value, header_format)
        formato = workbook.add_format()
        formato.set_align("left")
        formato_data = workbook.add_format()
        formato_data.set_align("center")
        formato_data.set_bottom()
        formato_data.set_font_size(7)
        worksheet.set_column(2,2,10)
        worksheet.set_column(0,1,10)
        worksheet.set_column(6,7,11)
        worksheet.set_column(3,5,10)
        worksheet.set_row(5,30)
        for row in range(6,31):
            worksheet.set_row(row,20,formato_data)
        #Excritura de formato de libro
        worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
        worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
        worksheet.merge_range('A3:I3',f'Numero de Registro: {libro.cliente.num_registro}',formato)
        worksheet.merge_range('A4:I4',f'LIBRO DE VENTAS A CONSUMIDOR FINAL. MES DE {libro.get_mes_display()}/{libro.ano}',formato)
        worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
        bandera+=1
        df=df[25:]
    df.to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
    worksheet = writer.sheets[f"HOJA{bandera}"]
    #Configuracion de pagina
    worksheet.set_portrait()
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
    header_format.set_align("center")
    header_format.set_align("vcenter")
    #Ecritura de cabecera
    for col_num, value in enumerate(df_facturas.columns.values):
        worksheet.write(5, col_num, value, header_format)
    formato = workbook.add_format()
    formato.set_align("left")
    formato_data = workbook.add_format()
    formato_data.set_align("center")
    formato_data.set_bottom()
    formato_data.set_font_size(7)
    worksheet.set_column(2,2,10)
    worksheet.set_column(0,1,10)
    worksheet.set_column(6,7,11)
    worksheet.set_column(3,5,10)
    worksheet.set_row(5,30)
    for row in range(6,len(df)+9):
        worksheet.set_row(row,20,formato_data)
    #Excritura de formato de libro
    worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
    worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
    worksheet.merge_range('A3:I3',f'Numero de Registro: {libro.cliente.num_registro}',formato)
    worksheet.merge_range('A4:I4',f'LIBRO DE VENTAS A CONSUMIDOR FINAL. MES DE {libro.get_mes_display()}/{libro.ano}',formato)
    worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
    resumen  = [
        facturas.aggregate(Sum('exento')),
        facturas.aggregate(Sum("locales")),
        facturas.aggregate(Sum("exportaciones")),
        facturas.aggregate(Sum("ventaTotal")),
        ]
    iva = float(resumen[1].get("locales__sum") / dec(1.13))
    ventSin = float(resumen[1].get("locales__sum")) - iva
    resumen.append({"iva":iva})
    resumen.append({"ventasSinIva":ventSin})
    worksheet.merge_range(f'A{len(df)+7}:B{len(df)+7}','TOTALES',header_format)
    worksheet.write(len(df)+6,3,f"{round(resumen[0].get('exento__sum'),2)}")
    worksheet.write(len(df)+6,4,f"{round(resumen[1].get('locales__sum'),2)}")
    worksheet.write(len(df)+6,5,f"{round(resumen[2].get('exportaciones__sum'),2)}")
    worksheet.write(len(df)+6,8,f"{round(resumen[3].get('ventaTotal__sum'),2)}")
    worksheet.merge_range(f'B{len(df)+8}:D{len(df)+8}','Venta',formato_data)
    worksheet.write(len(df)+8,4,f"{round(resumen[5].get('ventasSinIva'),2):.2f}")
    worksheet.merge_range(f'B{len(df)+9}:D{len(df)+9}','IVA 13%',formato_data)
    worksheet.write(len(df)+7,4,f"{round(resumen[4].get('iva'),2):.2f}")
    writer.save()
    return BASE_DIR/f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_condumidorFinal.xlsx"
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def export_librocm(libro_id):
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCm.objects.filter(libro=libro).order_by('fecha').values()
    facturas_limpias = []
    ci = 1
    #Creacion de de lista para dataFrame
    for fact in facturas:
        factura_dict = {}
        fecha = DateFormat(fact.get("fecha"))
        empresa = int(fact.get("empresa_id"))
        empresa = Empresa.objects.get(id=empresa)
        factura_dict.update({
            "Correlativo":ci,
            "Fecha": fecha.format('d/m/Y'),
            "Num. de Comprobante":fact.get("correlativo"),
            "Num de Registro":empresa.nRegistro,
            "Empresa":empresa.nombre,
            "Com. Exe. Inter.":fact.get("cExenteInterna"),
            "Com. Exe. Impor.":fact.get("cExenteImportaciones"),
            "Com. Gra. Inter.":fact.get("cGravadaInterna"),
            "Com. Gra. Impor.":fact.get("cGravadaImportaciones"),
            "Compras No Sujetas":fact.get("comprasNSujetas"),
            "IVA Cdto Fiscal":fact.get("ivaCdtoFiscal"),
            "Compra Total":fact.get("totalCompra"),
            "Ret. Percep. 1%":fact.get("retencionPretencion"),
            "Ant. a Cta IVA 2%":fact.get("anticipoCtaIva"),
            "IVA Terceros": fact.get("ivaTerceros"),
        })
        facturas_limpias.append(factura_dict)
        ci+=1
    #Creacion de objeto Excel para posterior salida
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras.xlsx",
        engine='xlsxwriter')

    df_facturas = pd.DataFrame(facturas_limpias)

    workbook  = writer.book
    df = df_facturas
    if libro.mes == 1 : mes = "ENERO"
    elif libro.mes == 2 : mes = "FEBRERO"
    elif libro.mes == 3 : mes = "MARZO"
    elif libro.mes == 4 : mes = "ABRIL"
    elif libro.mes == 5 : mes = "MAYO"
    elif libro.mes == 6 : mes = "JUNIO"
    elif libro.mes == 7 : mes = "JULIO"
    elif libro.mes == 8 : mes = "AGOSTO"
    elif libro.mes == 9 : mes = "SEPTIEMBRE"
    elif libro.mes == 10 : mes = "OCTUBRE"
    elif libro.mes == 11 : mes = "NOVIEMBRE"
    elif libro.mes == 12 : mes = "DICIEMBRE"
    bandera = 1
    #Si hay mas de 10 registros se creara una hoja por cada 20
    while len(df) >=15:
        df[:15].to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
        worksheet = writer.sheets[f"HOJA{bandera}"]
        #Configuracion de pagina
        worksheet.set_landscape()
        worksheet.set_paper(1)
        worksheet.set_margins(0.26,0.26,0.75,0.75)
        #formato de cabecera
        header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'border': 1,
        "font_size":8,
        })
        header_format.set_align("center")
        header_format.set_align("vcenter")
        #Ecritura de cabecera
        for col_num, value in enumerate(df_facturas.columns.values):
            worksheet.write(5, col_num, value, header_format)
        formato = workbook.add_format()
        formato.set_align("left")
        formato_data = workbook.add_format()
        formato_data.set_align("center")
        formato_data.set_bottom()
        formato_data.set_font_size(7)
        worksheet.set_column(0,0,6)
        worksheet.set_column(1,3,9)
        worksheet.set_column(4,4,17)
        worksheet.set_column(5,9,8)
        worksheet.set_column(10,14,7)
        worksheet.set_row(5,40)
        for row in range(6,21):
            worksheet.set_row(row,20,formato_data)
        #Excritura de formato de libro
        worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
        worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
        worksheet.merge_range('A3:I3',f'Numero de Registro: {libro.cliente.num_registro}',formato)
        worksheet.merge_range('A4:I4',f'LIBRO DE COMPRAS. MES DE {libro.get_mes_display()}/{libro.ano}',formato)
        worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
        bandera+=1
        df=df[15:]
    df.to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
    worksheet = writer.sheets[f"HOJA{bandera}"]
    #Configuracion de pagina
    worksheet.set_landscape()
    worksheet.set_paper(1)
    worksheet.set_margins(0.26,0.26,0.75,0.75)
    #formato de cabecera
    header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'border': 1,
    "font_size":8,
    })
    header_format.set_align("center")
    header_format.set_align("vcenter")
    #Ecritura de cabecera
    for col_num, value in enumerate(df_facturas.columns.values):
        worksheet.write(5, col_num, value, header_format)
    formato = workbook.add_format()
    formato.set_align("left")
    formato_data = workbook.add_format()
    formato_data.set_align("center")
    formato_data.set_bottom()
    formato_data.set_font_size(7)
    worksheet.set_column(0,0,6)
    worksheet.set_column(1,3,9)
    worksheet.set_column(4,4,17)
    worksheet.set_column(5,9,8)
    worksheet.set_column(10,14,7)
    worksheet.set_row(5,40)
    for row in range(6,len(df)+9):
        worksheet.set_row(row,20,formato_data)
    #Excritura de formato de libro
    worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
    worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
    worksheet.merge_range('A3:I3',f'Numero de Registro: {libro.cliente.num_registro}',formato)
    worksheet.merge_range('A4:I4',f'LIBRO DE COMPRAS. MES DE {libro.get_mes_display()}/{libro.ano}',formato)
    worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
    total_comexin = round(facturas.aggregate(Sum('cExenteInterna')).get("cExenteInterna__sum"),2)
    total_comexim = round(facturas.aggregate(Sum('cExenteImportaciones')).get("cExenteImportaciones__sum"),2)
    total_comgrin = round(facturas.aggregate(Sum('cGravadaInterna')).get("cGravadaInterna__sum"),2)
    total_comgrim = round(facturas.aggregate(Sum('cGravadaImportaciones')).get("cGravadaImportaciones__sum"),2)
    total_ivacrdt = round(facturas.aggregate(Sum('ivaCdtoFiscal')).get("ivaCdtoFiscal__sum"),2)
    total_compras = round(facturas.aggregate(Sum('totalCompra')).get("totalCompra__sum"),2)
    total_retperc = round(facturas.aggregate(Sum('retencionPretencion')).get("retencionPretencion__sum"),2)
    total_antciva = round(facturas.aggregate(Sum('anticipoCtaIva')).get("anticipoCtaIva__sum"),2)
    total_ivaterc = round(facturas.aggregate(Sum('ivaTerceros')).get("ivaTerceros__sum"),2)
    total_nosujet = round(facturas.aggregate(Sum('comprasNSujetas')).get("comprasNSujetas__sum"),2)
    #Escritura lde totales
    worksheet.merge_range(f'A{len(df)+7}:B{len(df)+7}','TOTALES',header_format)
    worksheet.write(len(df)+6,5,f"{total_comexin}")
    worksheet.write(len(df)+6,6,f"{total_comexim}")
    worksheet.write(len(df)+6,7,f"{total_comgrin}")
    worksheet.write(len(df)+6,8,f"{total_comgrim}")
    worksheet.write(len(df)+6,9,f"{total_nosujet}")
    worksheet.write(len(df)+6,10,f"{total_ivacrdt}")
    worksheet.write(len(df)+6,11,f"{total_compras}")
    worksheet.write(len(df)+6,12,f"{total_retperc}")
    worksheet.write(len(df)+6,13,f"{total_antciva}")
    worksheet.write(len(df)+6,14,f"{total_ivaterc}")
    worksheet.write(len(df)+7,4,"Total Compras")
    worksheet.write(len(df)+8,4,"Total N/C")
    compras = FacturaCm.objects.filter(libro=libro,cGravadaInterna__gte=dec(0.00))
    compras_t = round(compras.aggregate(Sum('cGravadaInterna')).get('cGravadaInterna__sum'),2)
    iva_compras_t = round(compras.aggregate(Sum('ivaCdtoFiscal')).get('ivaCdtoFiscal__sum'),2)
    notas_credito = FacturaCm.objects.filter(libro=libro,cGravadaInterna__lt=dec(0.00))
    notas_credito_t = round(notas_credito.aggregate(Sum('cGravadaInterna')).get('cGravadaInterna__sum'),2) if len(notas_credito) > 0 else '0.00'
    iva_notas_credito_t = round(notas_credito.aggregate(Sum('ivaCdtoFiscal')).get('ivaCdtoFiscal__sum'),2) if len(notas_credito) > 0 else '0.00'
    worksheet.write(len(df)+7,7,f"{compras_t}")
    worksheet.write(len(df)+7,10,f"{iva_compras_t}")
    worksheet.write(len(df)+8,7,f"{notas_credito_t}")
    worksheet.write(len(df)+8,10,f"{iva_notas_credito_t}")
    writer.save()
    return BASE_DIR/f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras.xlsx"
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def export_libroct(libro_id):
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCt.objects.filter(libro=libro).values()
    facturas_limpias = []
    ci = 1
    #Creacion de de lista para dataFrame
    for fact in facturas:
        factura_dict = {}
        fecha = DateFormat(fact.get("fecha"))
        contribuyente = int(fact.get("contribuyente_id"))
        contribuyente = Empresa.objects.get(id=contribuyente)
        factura_dict.update({
            "Correlativo":ci,
            "Fecha": fecha.format('d/m/Y'),
            "Corr. Int. Uni.":fact.get("corrIntUni") if fact.get("corrIntUni") is not None else "",
            "Num. de Comprobante":fact.get("correlativo"),
            "Num de Registro":contribuyente.nRegistro,
            "Contribuyente":contribuyente .nombre,
            "Vent. Exe.":fact.get("venExentas"),
            "Vent. Gra.":fact.get("venGravadas"),
            "Ventas No Sujetas":fact.get("ventasNSujetas"),
            "IVA Dbto Fiscal":fact.get("ivaDebFiscal"),
            "Ventas Terceros":fact.get("vtVentas"),
            "IVA Terceros":fact.get("vtIVA"),
            "Iva Retenido":fact.get("ivaRetenido"),
            "Venta Total": fact.get("total"),
        })
        facturas_limpias.append(factura_dict)
        ci+=1
    #Creacion de objeto Excel para posterior salida
    writer = pd.ExcelWriter(
        BASE_DIR/f"libros_contribuyente/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente.xlsx",
        engine='xlsxwriter')

    df_facturas = pd.DataFrame(facturas_limpias)

    workbook  = writer.book
    df = df_facturas
    if libro.mes == 1 : mes = "ENERO"
    elif libro.mes == 2 : mes = "FEBRERO"
    elif libro.mes == 3 : mes = "MARZO"
    elif libro.mes == 4 : mes = "ABRIL"
    elif libro.mes == 5 : mes = "MAYO"
    elif libro.mes == 6 : mes = "JUNIO"
    elif libro.mes == 7 : mes = "JULIO"
    elif libro.mes == 8 : mes = "AGOSTO"
    elif libro.mes == 9 : mes = "SEPTIEMBRE"
    elif libro.mes == 10 : mes = "OCTUBRE"
    elif libro.mes == 11 : mes = "NOVIEMBRE"
    elif libro.mes == 12 : mes = "DICIEMBRE"
    bandera = 1
    #Si hay mas de 10 registros se creara una hoja por cada 20
    while len(df) >=15:
        df[:15].to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
        worksheet = writer.sheets[f"HOJA{bandera}"]
        #Configuracion de pagina
        worksheet.set_landscape()
        worksheet.set_paper(1)
        worksheet.set_margins(0.26,0.26,0.75,0.75)
        #formato de cabecera
        header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'border': 1,
        "font_size":8,
        })
        header_format.set_align("center")
        header_format.set_align("vcenter")
        #Ecritura de cabecera
        for col_num, value in enumerate(df_facturas.columns.values):
            worksheet.write(5, col_num, value, header_format)
        formato = workbook.add_format()
        formato.set_align("left")
        formato_data = workbook.add_format()
        formato_data.set_align("center")
        formato_data.set_bottom()
        formato_data.set_font_size(7)
        worksheet.set_column(0,0,6)
        worksheet.set_column(1,3,9)
        worksheet.set_column(4,4,17)
        worksheet.set_column(5,9,8)
        worksheet.set_column(10,14,7)
        worksheet.set_row(5,40)
        for row in range(6,21):
            worksheet.set_row(row,20,formato_data)
        #Excritura de formato de libro
        worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
        worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
        worksheet.merge_range('A3:I3',f'NNUMERO DE REGISTRO: {libro.cliente.num_registro}',formato)
        worksheet.merge_range('A4:I4',f'LIBRO DE VENTAS A CONTRIBUYENTE. MES DE {libro.get_mes_display}/{libro.ano}',formato)
        worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
        bandera+=1
        df=df[15:]
    df.to_excel(writer,sheet_name=f"HOJA{bandera}",index=False,startrow=6,header=False)
    worksheet = writer.sheets[f"HOJA{bandera}"]
    #Configuracion de pagina
    worksheet.set_landscape()
    worksheet.set_paper(1)
    worksheet.set_margins(0.26,0.26,0.75,0.75)
    #formato de cabecera
    header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'border': 1,
    "font_size":8,
    })
    header_format.set_align("center")
    header_format.set_align("vcenter")
    #Ecritura de cabecera
    for col_num, value in enumerate(df_facturas.columns.values):
        worksheet.write(5, col_num, value, header_format)
    formato = workbook.add_format()
    formato.set_align("left")
    formato_data = workbook.add_format()
    formato_data.set_align("center")
    formato_data.set_bottom()
    formato_data.set_font_size(7)
    worksheet.set_column(0,0,6)
    worksheet.set_column(1,4,9)
    worksheet.set_column(5,5,17)
    worksheet.set_column(6,9,8)
    worksheet.set_column(10,14,7)
    worksheet.set_row(5,40)
    for row in range(6,len(df)+9):
        worksheet.set_row(row,20,formato_data)
    #Excritura de formato de libro
    worksheet.merge_range('A1:I1',f'{libro.cliente.nombre}',formato)
    worksheet.merge_range('A2:I2',f'NIT: {libro.cliente.nit}',formato)
    worksheet.merge_range('A3:I3',f'NUMERO DE REGISTRO: {libro.cliente.num_registro}',formato)
    worksheet.merge_range('A4:I4',f'LIBRO DE VENTAS A CONTRIBUYENTES. MES DE {libro.get_mes_display()}/{libro.ano}',formato)
    worksheet.merge_range('A5:I5','EN DOLARES AMERICANOS',formato)
    total_venexe = round(facturas.aggregate(Sum('venExentas')).get("venExentas__sum"),2)
    total_vengra = round(facturas.aggregate(Sum('venGravadas')).get("venGravadas__sum"),2)
    total_ivadbt = round(facturas.aggregate(Sum('ivaDebFiscal')).get("ivaDebFiscal__sum"),2)
    total_vtsven = round(facturas.aggregate(Sum('vtVentas')).get("vtVentas__sum"),2)
    total_vtsiva = round(facturas.aggregate(Sum('vtIVA')).get("vtIVA__sum"),2)
    total_ivaret = round(facturas.aggregate(Sum('ivaRetenido')).get("ivaRetenido__sum"),2)
    total_ventas = round(facturas.aggregate(Sum('total')).get("total__sum"),2)
    total_vennsu = round(facturas.aggregate(Sum('ventasNSujetas')).get("ventasNSujetas__sum"),2)
    worksheet.merge_range(f'A{len(df)+7}:B{len(df)+7}','TOTALES',header_format)

    worksheet.write(len(df)+6,6,f"{total_venexe}")
    worksheet.write(len(df)+6,7,f"{total_vengra}")
    worksheet.write(len(df)+6,8,f"{total_vennsu}")
    worksheet.write(len(df)+6,9,f"{total_ivadbt}")
    worksheet.write(len(df)+6,10,f"{total_vtsven}")
    worksheet.write(len(df)+6,11,f"{total_vtsiva}")
    worksheet.write(len(df)+6,12,f"{total_ivaret}")
    worksheet.write(len(df)+6,13,f"{total_ventas}")
    ventas = FacturaCt.objects.filter(libro=libro,venGravadas__gte=dec(0.00))
    ventas_t = round(ventas.aggregate(Sum('venGravadas')).get('venGravadas__sum'),2)
    iva_ventas_t = round(ventas.aggregate(Sum('ivaDebFiscal')).get('ivaDebFiscal__sum'),2)
    notas_credito = FacturaCt.objects.filter(libro=libro,venGravadas__lt=dec(0.00))
    notas_credito_t = round(notas_credito.aggregate(Sum('venGravadas')).get('venGravadas__sum'),2) if len(notas_credito) > 0 else '0.00'
    iva_notas_credito_t = round(notas_credito.aggregate(Sum('ivaDebFiscal')).get('ivaDebFiscal__sum'),2) if len(notas_credito) > 0 else '0.00'
    ventas_positivas = round(ventas.aggregate(Sum('total')).get('total__sum'),2)
    ventas_negativas = round(notas_credito.aggregate(Sum('total')).get('total__sum'),2) if len(notas_credito) > 0 else '0.00'
    worksheet.write(len(df)+7,7,f"{ventas_t}")
    worksheet.write(len(df)+7,9,f"{iva_ventas_t}")
    worksheet.write(len(df)+8,7,f"{notas_credito_t}")
    worksheet.write(len(df)+8,9,f"{iva_notas_credito_t}")
    worksheet.write(len(df)+7,13,f"{ventas_positivas}")
    worksheet.write(len(df)+8,13,f"{ventas_negativas}")
    worksheet.write(len(df)+7,5,"Total Ventas")
    worksheet.write(len(df)+8,5,"Total N/C")
    writer.save()
    return BASE_DIR/f"libros_contribuyente/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente.xlsx"
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def formato_hacienda(libro_id):
    libro = Libro.objects.get(id=libro_id)
    
    if libro.tipo == 1:
        direccion = consumidor(libro)
    elif libro.tipo == 2:
        direccion = contribuyente(libro)
    elif libro.tipo == 3:
        direccion = compras(libro)

    return direccion


def formato_interno(libro_id):
    libro = Libro.objects.get(id=libro_id)
    
    if libro.tipo == 1:
        direccion = interno_consumidor(libro)
    elif libro.tipo == 2:
        direccion = interno_contribuyente(libro)
    elif libro.tipo == 3:
        direccion = interno_compras(libro)

    return direccion
    
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def compras(libro):
    facturas = FacturaCm.objects.filter(libro=libro)
    direccion = BASE_DIR/f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #tabla de facturas
    row = 0
    for factura in facturas:
        if factura.empresa.nRegistro not in ("0-0","0-2","00-0"):
            ws.write(row,0 ,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
            ws.write(row,1 ,f"{factura.claseDocumento}",body_format)
            ws.write(row,2 ,f"{factura.tipoDocumento}",body_format)
            ws.write(row,3 ,f"{factura.numeroDocumento}",body_format)
            ws.write(row,4 ,f"{factura.empresa.nit.replace('-','',3) if factura.empresa.nit is not None else factura.empresa.nRegistro.replace('-','')}",body_format)
            ws.write(row,5 ,f"{factura.empresa.nombre}",body_format)
            ws.write(row,6 ,f"{factura.cExenteInterna}",body_format)
            ws.write(row,7 ,f"{factura.cExenteInternaciones}",body_format)
            ws.write(row,8 ,f"{factura.cExenteImportaciones}",body_format)
            ws.write(row,9 ,f"{factura.cGravadaInterna}",body_format)
            ws.write(row,10,f"{factura.cGravadaInternaciones}",body_format)
            ws.write(row,11,f"{factura.cGravadaImportaciones}",body_format)
            ws.write(row,12,f"{factura.cGravadaImportacionesServicios}",body_format)
            ws.write(row,13,f"{factura.ivaCdtoFiscal}",body_format)
            ws.write(row,14,f"{factura.totalCompra}",body_format)
            ws.write(row,15,f"3",body_format)
            row+=1
    
    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def consumidor(libro):
    facturas = FacturaCF.objects.filter(libro=libro)
    direccion = BASE_DIR/f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_condumidorFinal_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #tabla de facturas
    row = 0
    for factura in facturas:
        ws.write(row,0, f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
        ws.write(row,1, f"{factura.claseDocumento}",body_format)
        ws.write(row,2, f"{factura.tipoDocumento}",body_format)
        ws.write(row,3, f"{factura.numeroResolucion}",body_format)
        ws.write(row,4, f"{factura.numeroSerie}",body_format)
        ws.write(row,5, f"{factura.numeroControlInternoDel if factura.numeroControlInternoDel is not None else ''}",body_format)
        ws.write(row,6, f"{factura.numeroControlInternoAl if factura.numeroControlInternoAl is not None else ''}",body_format)
        ws.write(row,7, f"{factura.correlativoInicial}",body_format)
        ws.write(row,8, f"{factura.correlativoFinal}",body_format)
        ws.write(row,9 ,f"{factura.numeroRegistradora if factura.numeroRegistradora is not None else ''}",body_format)
        ws.write(row,10,f"{ajuste_numeros(factura.exento)}",body_format)
        ws.write(row,11,f"{ajuste_numeros(factura.ventasInternasExentas)}",body_format)
        ws.write(row,12,f"{ajuste_numeros(factura.ventasNSujetas)}",body_format)
        ws.write(row,13,f"{ajuste_numeros(factura.locales)}",body_format)
        ws.write(row,14,f"{ajuste_numeros(factura.exportacionesCA)}",body_format)
        ws.write(row,15,f"{ajuste_numeros(factura.exportacionesNoCA)}",body_format)
        ws.write(row,16,f"{ajuste_numeros(factura.exportacionesServicios)}",body_format)
        ws.write(row,17,f"{ajuste_numeros(factura.ventasZonasFrancas)}",body_format)
        ws.write(row,18,f"{ajuste_numeros(factura.ventaCtaTerceros)}",body_format)
        ws.write(row,19,f"{ajuste_numeros(factura.ventaTotal)}",body_format)
        ws.write(row,20,f"2",body_format)
        row+=1

    writer.save()
    return direccion
    
#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def contribuyente(libro):
    facturas = FacturaCt.objects.filter(libro=libro)
    direccion = BASE_DIR/f"libros_contribuyente/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #tabla de facturas
    row = 0
    for factura in facturas:
        if factura.contribuyente.nRegistro not in ("0-0","0-2","00-0") :
            ws.write(row,0 ,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
            ws.write(row,1 ,f"{factura.claseDocumento}",body_format)
            ws.write(row,2 ,f"{factura.tipoDocumento}",body_format)
            ws.write(row,3 ,f"{factura.numeroResolucion}",body_format)
            ws.write(row,4 ,f"{factura.numeroSerie}",body_format)
            ws.write(row,5 ,f"{factura.numeroDocumento}",body_format)
            ws.write(row,6 ,f"{factura.numeroControlInterno}",body_format)
            ws.write(row,7 ,f"{factura.contribuyente.nit.replace('-','',3) if factura.contribuyente.nit is not None else factura.contribuyente.nRegistro}",body_format)
            ws.write(row,8 ,f"{factura.contribuyente.nombre}",body_format)
            ws.write(row,9 ,f"{ajuste_numeros(factura.venExentas)}",body_format)
            ws.write(row,10,f"{ajuste_numeros(factura.ventasNSujetas)}",body_format)
            ws.write(row,11,f"{ajuste_numeros(factura.venGravadas)}",body_format)
            ws.write(row,12,f"{ajuste_numeros(factura.ivaDebFiscal)}",body_format)
            ws.write(row,13,f"{ajuste_numeros(factura.vtVentas)}",body_format)
            ws.write(row,14,f"{ajuste_numeros(factura.vtIVA)}",body_format)
            ws.write(row,15,f"{ajuste_numeros(factura.total)}",body_format)
            ws.write(row,16,f"1",body_format)
            row+=1

    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def interno_compras(libro):
    facturas = FacturaCm.objects.filter(libro=libro).order_by('fecha')
    direccion = BASE_DIR/f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #Cabecera
    ws.merge_range("A1:R1",f"{libro.cliente.nombre}",header_format)
    ws.merge_range("A2:R2",f"Registro  {libro.cliente.num_registro}",header_format)
    ws.merge_range("A3:R3",f"NIT  {libro.cliente.nit}",header_format)
    ws.merge_range("A4:R4",f"Libro de Compras del mes de {libro.get_mes_display()}/{libro.ano}",header_format)
    
    #tabla de facturas
    ws.write(4,0 ,"Correlativo",body_format)
    ws.write(4,1 ,"Fecha",body_format)
    ws.write(4,2 ,"Clase de Doc",body_format)
    ws.write(4,3 ,"Tipo de Doc",body_format)
    ws.write(4,4 ,"N de Doc",body_format)
    ws.write(4,5 ,"Nit",body_format)
    ws.write(4,6 ,"Nombre",body_format)
    ws.write(4,7 ,"Comp Loc Exen",body_format)
    ws.write(4,8 ,"Inter Exen",body_format)
    ws.write(4,9 ,"Impor Exen",body_format)
    ws.write(4,10 ,"Comp Loc Grav",body_format)
    ws.write(4,11 ,"Inter Grav Bienes",body_format)
    ws.write(4,12,"Impor Grav Bienes",body_format)
    ws.write(4,13,"Impor Grav Servicios",body_format)
    ws.write(4,14,"Crdto Fiscal",body_format)
    ws.write(4,15,"Total Compra",body_format)
    ws.write(4,16,"Retencion/Pretencion",body_format)
    ws.write(4,17,"Anticipo Cta Iva",body_format)
    ws.write(4,18,"IVA Terceros",body_format)
    
    row = 5
    for factura in facturas:
        ws.write(row,0 ,f"{row-4}",body_format)
        ws.write(row,1 ,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
        ws.write(row,2 ,f"{factura.claseDocumento}",body_format)
        ws.write(row,3 ,f"{factura.tipoDocumento}",body_format)
        ws.write(row,4 ,f"{factura.numeroDocumento}",body_format)
        ws.write(row,5 ,f"{factura.empresa.nit.replace('-','',3) if factura.empresa.nit is not None else factura.empresa.nRegistro.replace('-','')}",body_format)
        ws.write(row,6 ,f"{factura.empresa.nombre}",body_format)
        ws.write(row,7 ,f"{factura.cExenteInterna}",body_format)
        ws.write(row,8 ,f"{factura.cExenteInternaciones}",body_format)
        ws.write(row,9 ,f"{factura.cExenteImportaciones}",body_format)
        ws.write(row,10 ,f"{factura.cGravadaInterna}",body_format)
        ws.write(row,11,f"{factura.cGravadaInternaciones}",body_format)
        ws.write(row,12,f"{factura.cGravadaImportaciones}",body_format)
        ws.write(row,13,f"{factura.cGravadaImportacionesServicios}",body_format)
        ws.write(row,14,f"{factura.ivaCdtoFiscal}",body_format)
        ws.write(row,15,f"{factura.totalCompra}",body_format)
        ws.write(row,16,f"{factura.retencionPretencion}",body_format)
        ws.write(row,17,f"{factura.anticipoCtaIva}",body_format)
        ws.write(row,18,f"{factura.ivaTerceros}",body_format)
        
        row+=1
    ws.merge_range(f"A{row+3}:F{row+3}","Totales",body_format)
    ws.write(row+2,6,f"{facturas.aggregate(total= Coalesce(Sum('cExenteInterna'),0))['total']}",body_format)
    ws.write(row+2,7,f"{facturas.aggregate(total= Coalesce(Sum('cExenteInternaciones'),0))['total']}",body_format)
    ws.write(row+2,8,f"{facturas.aggregate(total= Coalesce(Sum('cExenteImportaciones'),0))['total']}",body_format)
    ws.write(row+2,9 ,f"{facturas.aggregate(total=Coalesce(Sum('cGravadaInterna'),0))['total']}",body_format)
    ws.write(row+2,10,f"{facturas.aggregate(total=Coalesce(Sum('cGravadaInternaciones'),0))['total']}",body_format)
    ws.write(row+2,11,f"{facturas.aggregate(total=Coalesce(Sum('cGravadaImportaciones'),0))['total']}",body_format)
    ws.write(row+2,12,f"{facturas.aggregate(total=Coalesce(Sum('cGravadaImportacionesServicios'),0))['total']}",body_format)
    ws.write(row+2,13,f"{facturas.aggregate(total=Coalesce(Sum('ivaCdtoFiscal'),0))['total']}",body_format)
    ws.write(row+2,14,f"{facturas.aggregate(total=Coalesce(Sum('totalCompra'),0))['total']}",body_format)
    ws.write(row+2,15,f"{facturas.aggregate(total=Coalesce(Sum('retencionPretencion'),0))['total']}",body_format)
    ws.write(row+2,16,f"{facturas.aggregate(total=Coalesce(Sum('anticipoCtaIva'),0))['total']}",body_format)
    ws.write(row+2,17,f"{facturas.aggregate(total=Coalesce(Sum('ivaTerceros'),0))['total']}",body_format)

    
    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def interno_consumidor(libro):
    facturas = FacturaCF.objects.filter(libro=libro).order_by("correlativoInicial")
    direccion = BASE_DIR/f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_consumidor_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #Cabecera
    ws.merge_range("A1:R1",f"{libro.cliente.nombre}",header_format)
    ws.merge_range("A2:R2",f"Registro  {libro.cliente.num_registro}",header_format)
    ws.merge_range("A3:R3",f"NIT  {libro.cliente.nit}",header_format)
    ws.merge_range("A4:R4",f"Libro de Consumidor Final del Mes de {libro.get_mes_display()}/{libro.ano}",header_format)
    #tabla de facturas
    ws.write(4,0,f"Fecha",body_format)
    ws.write(4,1,f"Clas de Doc",body_format)
    ws.write(4,2,f"Tipo de Doc",body_format)
    ws.write(4,3,f"N de Res",body_format)
    ws.write(4,4,f"N de Ser",body_format)
    ws.write(4,5,f"N Con Inter",body_format)
    ws.write(4,6,f"N Con Inter",body_format)
    ws.write(4,7 ,f"Corr Ini",body_format)
    ws.write(4,8 ,f"Corr Fin",body_format)
    ws.write(4,9 ,f"N Maq Regis",body_format)
    ws.write(4,10 ,f"Ven Exe",body_format)
    ws.write(4,11,f"Ven Inter Exen No Suj",body_format)
    ws.write(4,12,f"Ven no Suj",body_format)
    ws.write(4,13,f"Ven Grav Loc",body_format)
    ws.write(4,14,f"Expor CA",body_format)
    ws.write(4,15,f"Expor No CA",body_format)
    ws.write(4,16,f"Zona Franc",body_format)
    ws.write(4,17,f"Total",body_format)
    row = 5
    for factura in facturas:
        ws.write(row,0,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
        ws.write(row,1,f"{factura.claseDocumento}",body_format)
        ws.write(row,2,f"{factura.tipoDocumento}",body_format)
        ws.write(row,3,f"{factura.numeroResolucion}",body_format)
        ws.write(row,4,f"{factura.numeroSerie}",body_format)
        ws.write(row,5,f"{factura.numeroControlInternoDel if factura.numeroControlInternoDel is not None else ''}",body_format)
        ws.write(row,6 ,f"{factura.numeroControlInternoAl if factura.numeroControlInternoAl is not None else ''}",body_format)
        ws.write(row,7 ,f"{factura.correlativoInicial}",body_format)
        ws.write(row,8 ,f"{factura.correlativoFinal}",body_format)
        ws.write(row,9 ,f"{factura.numeroRegistradora if factura.numeroRegistradora is not None else ''}",body_format)
        ws.write(row,10 ,f"{factura.exento}",body_format)
        ws.write(row,11,f"{factura.ventasInternasExentas}",body_format)
        ws.write(row,12,f"{factura.ventasNSujetas}",body_format)
        ws.write(row,13,f"{factura.locales}",body_format)
        ws.write(row,14,f"{factura.exportacionesCA}",body_format)
        ws.write(row,15,f"{factura.exportacionesNoCA}",body_format)
        ws.write(row,16,f"{factura.ventasZonasFrancas}",body_format)
        ws.write(row,17,f"{factura.ventaTotal}",body_format)
        row+=1
    ws.merge_range(f"A{row+3}:I{row+3}","Totales",body_format)
    ws.write(row+2,10,f"{facturas.aggregate(total=Coalesce(Sum('exento'),0))['total']}",body_format)
    ws.write(row+2,11,f"{facturas.aggregate(total=Coalesce(Sum('ventasInternasExentas'),0))['total']}",body_format)
    ws.write(row+2,12,f"{facturas.aggregate(total=Coalesce(Sum('ventasNSujetas'),0))['total']}",body_format)
    ws.write(row+2,13,f"{facturas.aggregate(total=Coalesce(Sum('locales'),0))['total']}",body_format)
    ws.write(row+2,14,f"{facturas.aggregate(total=Coalesce(Sum('exportacionesCA'),0))['total']}",body_format)
    ws.write(row+2,15,f"{facturas.aggregate(total=Coalesce(Sum('exportacionesNoCA'),0))['total']}",body_format)
    ws.write(row+2,16,f"{facturas.aggregate(total=Coalesce(Sum('ventasZonasFrancas'),0))['total']}",body_format)
    ws.write(row+2,17,f"{facturas.aggregate(total=Coalesce(Sum('ventaTotal'),0))['total']}",body_format)

    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def interno_contribuyente(libro):
    facturas = FacturaCt.objects.filter(libro=libro).order_by('numeroDocumento')
    direccion = BASE_DIR/f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente_mh.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
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
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #formato de pie
    foot_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)
    #tabla de facturas
    ws.merge_range("A1:R1",f"{libro.cliente.nombre}",header_format)
    ws.merge_range("A2:R2",f"Registro  {libro.cliente.num_registro}",header_format)
    ws.merge_range("A3:R3",f"NIT  {libro.cliente.nit}",header_format)
    ws.merge_range("A4:R4",f"Libro de Contribuyente del Mes de {libro.get_mes_display()}/{libro.ano}",header_format)

    ws.write(4,0,f"Fecha",body_format)
    ws.write(4,1,f"Clase de Doc",body_format)
    ws.write(4,2,f"Tipo de Doc",body_format)
    ws.write(4,3,f"N de Res",body_format)
    ws.write(4,4,f"N de Ser",body_format)
    ws.write(4,5,f"N de Doc",body_format)
    ws.write(4,6,f"N Cont Intr",body_format)
    ws.write(4,7,f"NIT Contr",body_format)
    ws.write(4,8,f"Nombre Contr",body_format)
    ws.write(4,9,f" Ven Exen",body_format)
    ws.write(4,10,f"Ven No Suje",body_format)
    ws.write(4,11,f"Ven Grav",body_format)
    ws.write(4,12,f"IVA",body_format)
    ws.write(4,13,f"Ven 3ros",body_format)
    ws.write(4,14,f"IVA 3ros",body_format)
    ws.write(4,15,f"Total",body_format)
    ws.write(4,16,f"IVA Ret",body_format)
    
    row = 5
    for factura in facturas:
        ws.write(row,0 ,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
        ws.write(row,1 ,f"{factura.get_claseDocumento_display()}",body_format)
        ws.write(row,2 ,f"{factura.get_tipoDocumento_display()}",body_format)
        ws.write(row,3 ,f"{factura.numeroResolucion}",body_format)
        ws.write(row,4 ,f"{factura.numeroSerie}",body_format)
        ws.write(row,5 ,f"{factura.numeroDocumento}",body_format)
        ws.write(row,6 ,f"{factura.numeroControlInterno}",body_format)
        ws.write(row,7 ,f"{factura.contribuyente.nit if factura.contribuyente.nit is not None else factura.contribuyente.nRegistro}",body_format)
        ws.write(row,8 ,f"{factura.contribuyente.nombre}",body_format)
        ws.write(row,9 ,f"{factura.venExentas}",body_format)
        ws.write(row,10,f"{factura.ventasNSujetas}",body_format)
        ws.write(row,11,f"{factura.venGravadas}",body_format)
        ws.write(row,12,f"{factura.ivaDebFiscal}",body_format)
        ws.write(row,13,f"{factura.vtVentas}",body_format)
        ws.write(row,14,f"{factura.vtIVA}",body_format)
        ws.write(row,15,f"{factura.total}",body_format)
        ws.write(row,16,f"{factura.ivaRetenido}",body_format)
        row+=1

    ws.merge_range(f"A{row+3}:I{row+3}","Totales",body_format)
    ws.write(row+2,9 ,f"{facturas.aggregate(total=Coalesce(Sum('venExentas'),0))['total']}",body_format)
    ws.write(row+2,10,f"{facturas.aggregate(total=Coalesce(Sum('ventasNSujetas'),0))['total']}",body_format)
    ws.write(row+2,11,f"{facturas.aggregate(total=Coalesce(Sum('venGravadas'),0))['total']}",body_format)
    ws.write(row+2,12,f"{facturas.aggregate(total=Coalesce(Sum('ivaDebFiscal'),0))['total']}",body_format)
    ws.write(row+2,13,f"{facturas.aggregate(total=Coalesce(Sum('vtVentas'),0))['total']}",body_format)
    ws.write(row+2,14,f"{facturas.aggregate(total=Coalesce(Sum('vtIVA'),0))['total']}",body_format)
    ws.write(row+2,15,f"{facturas.aggregate(total=Coalesce(Sum('total'),0))['total']}",body_format)
    ws.write(row+2,16,f"{facturas.aggregate(total=Coalesce(Sum('ivaRetenido'),0))['total']}",body_format)

    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
def anticipo_cuenta(libro_id):
    libro = Libro.objects.get(id=libro_id)
    facturas = RetencionCompra.objects.filter(libro=libro).exclude(numeroSerie="").order_by('fecha')
    direccion = BASE_DIR/f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_anticipo_a_cuenta.xlsx"
    writer = pd.ExcelWriter(
        direccion,
        engine='xlsxwriter')
    wb = writer.book
    ws = wb.add_worksheet("detalle_consumidor")
    #configuraciones de pagina
    ws.set_portrait()
    ws.set_paper(1)
    ws.set_margins(0.26,0.26,0.75,0.75)
    #formato de cuerpo
    body_format =  wb.add_format({
        "font_size":8,
        'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")
    #tabla de facturas
    row = 0
    for factura in facturas:
        ws.write(row,0 ,f"{factura.empresa.nit.replace('-','',3) if factura.empresa.nit is not None else factura.empresa.nRegistro.replace('-','')}",body_format)
        ws.write(row,1 ,f"{factura.fecha.strftime('%d/%m/%Y')}",body_format)
        ws.write(row,2 ,f"{factura.numeroSerie}",body_format)
        ws.write(row,3 ,f"{factura.numeroDocumento}",body_format)
        ws.write(row,4 ,f"{factura.monto_sujeto}",body_format)
        ws.write(row,5 ,f"{factura.retencion}",body_format)
        ws.write(row,6 ,f"6",body_format)
        row+=1
    writer.save()
    return direccion

#------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------#
#ajuste de numeros decimales a 10 caracteres Hacienda cagandose en la gente
def ajuste_numeros(numero):
    cadena = str(numero)
    while len(cadena) < 10 :
        cadena = "0" + cadena
    return cadena