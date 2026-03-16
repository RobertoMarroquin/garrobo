"""
Módulo de exportación de Libros de IVA a Excel.
Refactorizado para eliminar duplicación de código.
"""
import pandas as pd
import xlsxwriter as xw
import os
from io import BytesIO
from decimal import Decimal as dec

from django.utils.dateformat import DateFormat
from django.db.models import Sum
from django.db.models.functions import Coalesce

from .models import *
from empresas.models import Empresa as Cliente
from garrobo.settings import BASE_DIR


# ============================================================================
# UTILIDADES REUTILIZABLES
# ============================================================================

MESES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}


def get_mes_nombre(mes):
    """Retorna el nombre del mes en español."""
    return MESES.get(mes, "")


def ajuste_numeros(numero):
    """Ajuste de números decimales a 10 caracteres (formato Hacienda)."""
    cadena = str(numero)
    while len(cadena) < 10:
        cadena = "0" + cadena
    return cadena


def safe_nit(empresa):
    """Obtiene el NIT sin guiones o el número de registro si no hay NIT."""
    if empresa.nit:
        return empresa.nit.replace('-', '', 3)
    return empresa.nRegistro.replace('-', '')


def safe_val(value, default=""):
    """Retorna un valor seguro para escritura en Excel."""
    return str(value) if value is not None else default


def _create_writer(direccion):
    """Crea un ExcelWriter con xlsxwriter engine."""
    return pd.ExcelWriter(direccion, engine='xlsxwriter')


def _create_formats(workbook):
    """Crea y retorna los formatos reutilizables del workbook."""
    header_format = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'top',
        'border': 1, 'font_size': 10,
    })
    header_format.set_align("center")
    header_format.set_align("vcenter")

    body_format = workbook.add_format({
        'font_size': 8, 'text_wrap': True,
    })
    body_format.set_align("left")
    body_format.set_align("vcenter")

    foot_format = workbook.add_format({
        'font_size': 8, 'text_wrap': True,
    })
    foot_format.set_align("center")
    foot_format.set_align("vcenter")
    foot_format.set_bottom(3)

    return header_format, body_format, foot_format


def _setup_worksheet(ws, orientation='portrait'):
    """Configura página del worksheet."""
    if orientation == 'landscape':
        ws.set_landscape()
    else:
        ws.set_portrait()
    ws.set_paper(1)
    ws.set_margins(0.26, 0.26, 0.75, 0.75)


def _write_libro_header(ws, libro, tipo_libro, header_format, merge_range="A1:I1"):
    """Escribe el encabezado estándar de un libro."""
    col_end = merge_range.split(':')[1][0]  # Extrae la letra final
    ws.merge_range(f'A1:{col_end}1', f'{libro.cliente.nombre}', header_format)
    ws.merge_range(f'A2:{col_end}2', f'NIT: {libro.cliente.nit}', header_format)
    ws.merge_range(f'A3:{col_end}3', f'Numero de Registro: {libro.cliente.num_registro}', header_format)
    ws.merge_range(f'A4:{col_end}4', f'{tipo_libro}. MES DE {libro.get_mes_display()}/{libro.ano}', header_format)
    ws.merge_range(f'A5:{col_end}5', 'EN DOLARES AMERICANOS', header_format)


def _write_libro_header_interno(ws, libro, tipo_libro, header_format, merge_range="A1:R1"):
    """Escribe el encabezado para reportes internos."""
    col_end = merge_range.split(':')[1][0]
    ws.merge_range(f'A1:{col_end}1', f'{libro.cliente.nombre}', header_format)
    ws.merge_range(f'A2:{col_end}2', f'Registro  {libro.cliente.num_registro}', header_format)
    ws.merge_range(f'A3:{col_end}3', f'NIT  {libro.cliente.nit}', header_format)
    ws.merge_range(f'A4:{col_end}4', f'{tipo_libro} del mes de {libro.get_mes_display()}/{libro.ano}', header_format)


def _create_paginated_sheets(writer, df, df_original, libro, tipo_libro, page_size,
                             orientation='portrait', col_formats=None, merge_range="A1:I1"):
    """Crea hojas paginadas con formato estándar."""
    workbook = writer.book
    bandera = 1

    header_fmt = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'top',
        'border': 1, 'font_size': 9 if orientation == 'portrait' else 8,
    })
    header_fmt.set_align("center")
    header_fmt.set_align("vcenter")

    formato = workbook.add_format()
    formato.set_align("left")

    formato_data = workbook.add_format()
    formato_data.set_align("center")
    formato_data.set_bottom()
    formato_data.set_font_size(7)

    while len(df) >= page_size:
        df[:page_size].to_excel(writer, sheet_name=f"HOJA{bandera}", index=False, startrow=6, header=False)
        ws = writer.sheets[f"HOJA{bandera}"]
        _setup_worksheet(ws, orientation)

        for col_num, value in enumerate(df_original.columns.values):
            ws.write(5, col_num, value, header_fmt)

        if col_formats:
            for args in col_formats:
                ws.set_column(*args)

        ws.set_row(5, 40 if orientation == 'landscape' else 30)
        for row in range(6, 6 + page_size):
            ws.set_row(row, 20, formato_data)

        _write_libro_header(ws, libro, tipo_libro, formato, merge_range)
        bandera += 1
        df = df[page_size:]

    # Última hoja
    df.to_excel(writer, sheet_name=f"HOJA{bandera}", index=False, startrow=6, header=False)
    ws = writer.sheets[f"HOJA{bandera}"]
    _setup_worksheet(ws, orientation)

    for col_num, value in enumerate(df_original.columns.values):
        ws.write(5, col_num, value, header_fmt)

    if col_formats:
        for args in col_formats:
            ws.set_column(*args)

    ws.set_row(5, 40 if orientation == 'landscape' else 30)
    for row in range(6, len(df) + 9):
        ws.set_row(row, 20, formato_data)

    _write_libro_header(ws, libro, tipo_libro, formato, merge_range)

    return ws, header_fmt, formato, formato_data, len(df)


def _safe_aggregate(queryset, field_name):
    """Aggregate seguro con Coalesce para evitar None."""
    key = f"{field_name}__sum"
    result = queryset.aggregate(Sum(field_name)).get(key)
    return round(result, 2) if result is not None else dec('0.00')


# ============================================================================
# EXPORTACIÓN DE LIBROS (FORMATO INTERNO SIMPLE)
# ============================================================================

def export_libroCF(libro_id):
    """Exporta libro de Consumidor Final en formato interno simple."""
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCF.objects.filter(libro=libro).values()
    facturas_limpias = []

    for fact in facturas:
        fecha = DateFormat(fact.get("fecha"))
        facturas_limpias.append({
            "Correlativo Inicial": fact.get("correlativoInicial"),
            "Correlativo Final": fact.get("correlativoFinal"),
            "Fecha": fecha.format('d/m/Y'),
            "Exento": fact.get("exento"),
            "Locales": fact.get("locales"),
            "Exportaciones": fact.get("exportaciones"),
            "Ventas No Sujetas": fact.get("ventasNSujetas"),
            "Ventas Cta Terceros": fact.get("ventaCtaTerceros"),
            "Venta Total": fact.get("ventaTotal"),
        })

    direccion = BASE_DIR / f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_condumidorFinal.xlsx"
    writer = _create_writer(direccion)
    df_facturas = pd.DataFrame(facturas_limpias)
    df = df_facturas.copy()

    col_formats = [(2, 2, 10), (0, 1, 10), (6, 7, 11), (3, 5, 10)]

    ws, header_fmt, formato, formato_data, remaining = _create_paginated_sheets(
        writer, df, df_facturas, libro,
        'LIBRO DE VENTAS A CONSUMIDOR FINAL', 25,
        orientation='portrait', col_formats=col_formats
    )

    # Totales
    resumen = [
        _safe_aggregate(facturas, 'exento'),
        _safe_aggregate(facturas, 'locales'),
        _safe_aggregate(facturas, 'exportaciones'),
        _safe_aggregate(facturas, 'ventaTotal'),
    ]
    iva = float(resumen[1] / dec('1.13'))
    ventSin = float(resumen[1]) - iva

    ws.merge_range(f'A{remaining + 7}:B{remaining + 7}', 'TOTALES', header_fmt)
    ws.write(remaining + 6, 3, f"{resumen[0]}")
    ws.write(remaining + 6, 4, f"{resumen[1]}")
    ws.write(remaining + 6, 5, f"{resumen[2]}")
    ws.write(remaining + 6, 8, f"{resumen[3]}")
    ws.merge_range(f'B{remaining + 8}:D{remaining + 8}', 'Venta', formato_data)
    ws.write(remaining + 8, 4, f"{round(ventSin, 2):.2f}")
    ws.merge_range(f'B{remaining + 9}:D{remaining + 9}', 'IVA 13%', formato_data)
    ws.write(remaining + 7, 4, f"{round(iva, 2):.2f}")

    writer.save()
    return direccion


def export_librocm(libro_id):
    """Exporta libro de Compras en formato interno simple."""
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCm.objects.filter(libro=libro).order_by('fecha').values()
    facturas_limpias = []

    for ci, fact in enumerate(facturas, 1):
        fecha = DateFormat(fact.get("fecha"))
        empresa = Empresa.objects.get(id=int(fact.get("empresa_id")))
        facturas_limpias.append({
            "Correlativo": ci,
            "Fecha": fecha.format('d/m/Y'),
            "Num. de Comprobante": fact.get("correlativo"),
            "Num de Registro": empresa.nRegistro,
            "Empresa": empresa.nombre,
            "Com. Exe. Inter.": fact.get("cExenteInterna"),
            "Com. Exe. Impor.": fact.get("cExenteImportaciones"),
            "Com. Gra. Inter.": fact.get("cGravadaInterna"),
            "Com. Gra. Impor.": fact.get("cGravadaImportaciones"),
            "Compras No Sujetas": fact.get("comprasNSujetas"),
            "IVA Cdto Fiscal": fact.get("ivaCdtoFiscal"),
            "Compra Total": fact.get("totalCompra"),
            "Ret. Percep. 1%": fact.get("retencionPretencion"),
            "Ant. a Cta IVA 2%": fact.get("anticipoCtaIva"),
            "IVA Terceros": fact.get("ivaTerceros"),
        })

    direccion = BASE_DIR / f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras.xlsx"
    writer = _create_writer(direccion)
    df_facturas = pd.DataFrame(facturas_limpias)
    df = df_facturas.copy()

    col_formats = [(0, 0, 6), (1, 3, 9), (4, 4, 17), (5, 9, 8), (10, 14, 7)]

    ws, header_fmt, formato, formato_data, remaining = _create_paginated_sheets(
        writer, df, df_facturas, libro,
        'LIBRO DE COMPRAS', 15,
        orientation='landscape', col_formats=col_formats
    )

    # Totales
    fields_compras = ['cExenteInterna', 'cExenteImportaciones', 'cGravadaInterna',
                      'cGravadaImportaciones', 'comprasNSujetas', 'ivaCdtoFiscal',
                      'totalCompra', 'retencionPretencion', 'anticipoCtaIva', 'ivaTerceros']
    totals = {f: _safe_aggregate(facturas, f) for f in fields_compras}

    ws.merge_range(f'A{remaining + 7}:B{remaining + 7}', 'TOTALES', header_fmt)
    col_map = {5: 'cExenteInterna', 6: 'cExenteImportaciones', 7: 'cGravadaInterna',
               8: 'cGravadaImportaciones', 9: 'comprasNSujetas', 10: 'ivaCdtoFiscal',
               11: 'totalCompra', 12: 'retencionPretencion', 13: 'anticipoCtaIva', 14: 'ivaTerceros'}
    for col, field in col_map.items():
        ws.write(remaining + 6, col, f"{totals[field]}")

    # Totales compras vs N/C
    compras = FacturaCm.objects.filter(libro=libro, cGravadaInterna__gte=dec('0.00'))
    compras_t = _safe_aggregate(compras.values(), 'cGravadaInterna')
    iva_compras_t = _safe_aggregate(compras.values(), 'ivaCdtoFiscal')
    notas_credito = FacturaCm.objects.filter(libro=libro, cGravadaInterna__lt=dec('0.00'))
    notas_credito_t = _safe_aggregate(notas_credito.values(), 'cGravadaInterna') if notas_credito.exists() else '0.00'
    iva_notas_credito_t = _safe_aggregate(notas_credito.values(), 'ivaCdtoFiscal') if notas_credito.exists() else '0.00'

    ws.write(remaining + 7, 4, "Total Compras")
    ws.write(remaining + 8, 4, "Total N/C")
    ws.write(remaining + 7, 7, f"{compras_t}")
    ws.write(remaining + 7, 10, f"{iva_compras_t}")
    ws.write(remaining + 8, 7, f"{notas_credito_t}")
    ws.write(remaining + 8, 10, f"{iva_notas_credito_t}")

    writer.save()
    return direccion


def export_libroct(libro_id):
    """Exporta libro de Contribuyente en formato interno simple."""
    libro = Libro.objects.get(id=libro_id)
    facturas = FacturaCt.objects.filter(libro=libro).values()
    facturas_limpias = []

    for ci, fact in enumerate(facturas, 1):
        fecha = DateFormat(fact.get("fecha"))
        contribuyente = Empresa.objects.get(id=int(fact.get("contribuyente_id")))
        facturas_limpias.append({
            "Correlativo": ci,
            "Fecha": fecha.format('d/m/Y'),
            "Corr. Int. Uni.": fact.get("corrIntUni") if fact.get("corrIntUni") is not None else "",
            "Num. de Comprobante": fact.get("correlativo"),
            "Num de Registro": contribuyente.nRegistro,
            "Contribuyente": contribuyente.nombre,
            "Vent. Exe.": fact.get("venExentas"),
            "Vent. Gra.": fact.get("venGravadas"),
            "Ventas No Sujetas": fact.get("ventasNSujetas"),
            "IVA Dbto Fiscal": fact.get("ivaDebFiscal"),
            "Ventas Terceros": fact.get("vtVentas"),
            "IVA Terceros": fact.get("vtIVA"),
            "Iva Retenido": fact.get("ivaRetenido"),
            "Venta Total": fact.get("total"),
        })

    direccion = BASE_DIR / f"libros_contribuyente/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente.xlsx"
    writer = _create_writer(direccion)
    df_facturas = pd.DataFrame(facturas_limpias)
    df = df_facturas.copy()

    col_formats = [(0, 0, 6), (1, 4, 9), (5, 5, 17), (6, 9, 8), (10, 14, 7)]

    ws, header_fmt, formato, formato_data, remaining = _create_paginated_sheets(
        writer, df, df_facturas, libro,
        'LIBRO DE VENTAS A CONTRIBUYENTES', 15,
        orientation='landscape', col_formats=col_formats
    )

    # Totales
    fields_ct = ['venExentas', 'venGravadas', 'ventasNSujetas', 'ivaDebFiscal',
                 'vtVentas', 'vtIVA', 'ivaRetenido', 'total']
    totals = {f: _safe_aggregate(facturas, f) for f in fields_ct}

    ws.merge_range(f'A{remaining + 7}:B{remaining + 7}', 'TOTALES', header_fmt)
    col_map = {6: 'venExentas', 7: 'venGravadas', 8: 'ventasNSujetas', 9: 'ivaDebFiscal',
               10: 'vtVentas', 11: 'vtIVA', 12: 'ivaRetenido', 13: 'total'}
    for col, field in col_map.items():
        ws.write(remaining + 6, col, f"{totals[field]}")

    # Ventas vs N/C
    ventas = FacturaCt.objects.filter(libro=libro, venGravadas__gte=dec('0.00'))
    ventas_t = _safe_aggregate(ventas.values(), 'venGravadas')
    iva_ventas_t = _safe_aggregate(ventas.values(), 'ivaDebFiscal')
    ventas_positivas = _safe_aggregate(ventas.values(), 'total')
    notas_credito = FacturaCt.objects.filter(libro=libro, venGravadas__lt=dec('0.00'))
    notas_credito_t = _safe_aggregate(notas_credito.values(), 'venGravadas') if notas_credito.exists() else '0.00'
    iva_notas_credito_t = _safe_aggregate(notas_credito.values(), 'ivaDebFiscal') if notas_credito.exists() else '0.00'
    ventas_negativas = _safe_aggregate(notas_credito.values(), 'total') if notas_credito.exists() else '0.00'

    ws.write(remaining + 7, 5, "Total Ventas")
    ws.write(remaining + 8, 5, "Total N/C")
    ws.write(remaining + 7, 7, f"{ventas_t}")
    ws.write(remaining + 7, 9, f"{iva_ventas_t}")
    ws.write(remaining + 8, 7, f"{notas_credito_t}")
    ws.write(remaining + 8, 9, f"{iva_notas_credito_t}")
    ws.write(remaining + 7, 13, f"{ventas_positivas}")
    ws.write(remaining + 8, 13, f"{ventas_negativas}")

    writer.save()
    return direccion


# ============================================================================
# FORMATOS DE HACIENDA
# ============================================================================

def formato_hacienda(libro_id):
    """Genera el formato de Hacienda según el tipo de libro."""
    libro = Libro.objects.get(id=libro_id)
    exporters = {1: consumidor, 2: contribuyente, 3: compras}
    return exporters[libro.tipo](libro)


def formato_interno(libro_id):
    """Genera el formato interno según el tipo de libro."""
    libro = Libro.objects.get(id=libro_id)
    exporters = {1: interno_consumidor, 2: interno_contribuyente, 3: interno_compras}
    return exporters[libro.tipo](libro)


    ws = wb.add_worksheet(sheet_name)
    _setup_worksheet(ws, orientation)
    header_fmt, body_fmt, foot_fmt = _create_formats(wb)
    return writer, wb, ws, header_fmt, body_fmt, foot_fmt


# --- Formato Hacienda: Consumidor Final ---
def consumidor(libro):
    facturas = FacturaCF.objects.filter(libro=libro)
    direccion = BASE_DIR / f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_condumidorFinal_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion)

    row = 0
    for factura in facturas:
        data = [
            factura.fecha.strftime('%d/%m/%Y'),
            factura.claseDocumento,
            factura.tipoDocumento,
            factura.numeroResolucion,
            factura.numeroSerie,
            safe_val(factura.numeroControlInternoDel),
            safe_val(factura.numeroControlInternoAl),
            factura.correlativoInicial,
            factura.correlativoFinal,
            safe_val(factura.numeroRegistradora),
            ajuste_numeros(factura.exento),
            ajuste_numeros(factura.ventasInternasExentas),
            ajuste_numeros(factura.ventasNSujetas),
            ajuste_numeros(factura.locales),
            ajuste_numeros(factura.exportacionesCA),
            ajuste_numeros(factura.exportacionesNoCA),
            ajuste_numeros(factura.exportacionesServicios),
            ajuste_numeros(factura.ventasZonasFrancas),
            ajuste_numeros(factura.ventaCtaTerceros),
            ajuste_numeros(factura.ventaTotal),
            "2",
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    writer.save()
    return direccion


# --- Formato Hacienda: Contribuyente ---
def contribuyente(libro):
    facturas = FacturaCt.objects.filter(libro=libro)
    direccion = BASE_DIR / f"libros_contribuyente/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion)

    row = 0
    for factura in facturas:
        if factura.contribuyente.nRegistro in ("0-0", "0-2", "00-0"):
            continue
        nit = factura.contribuyente.nit.replace('-', '', 3) if factura.contribuyente.nit else factura.contribuyente.nRegistro.replace('-', '')
        data = [
            factura.fecha.strftime('%d/%m/%Y'),
            factura.claseDocumento,
            factura.tipoDocumento,
            factura.numeroResolucion,
            factura.numeroSerie,
            factura.numeroDocumento,
            factura.numeroControlInterno,
            nit,
            factura.contribuyente.nombre,
            ajuste_numeros(factura.venExentas),
            ajuste_numeros(factura.ventasNSujetas),
            ajuste_numeros(factura.venGravadas),
            ajuste_numeros(factura.ivaDebFiscal),
            ajuste_numeros(factura.vtVentas),
            ajuste_numeros(factura.vtIVA),
            ajuste_numeros(factura.total),
            "",  # DUI placeholder
            "1",
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    writer.save()
    return direccion


# --- Formato Hacienda: Compras ---
def compras(libro):
    facturas = FacturaCm.objects.filter(libro=libro)
    direccion = BASE_DIR / f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion)

    row = 0
    for factura in facturas:
        if factura.empresa.nRegistro in ("0-0", "0-2", "00-0"):
            continue
        data = [
            factura.fecha.strftime('%d/%m/%Y'),
            factura.claseDocumento,
            factura.tipoDocumento,
            factura.numeroDocumento,
            safe_nit(factura.empresa),
            factura.empresa.nombre,
            factura.cExenteInterna,
            factura.cExenteInternaciones,
            factura.cExenteImportaciones,
            factura.cGravadaInterna,
            factura.cGravadaInternaciones,
            factura.cGravadaImportaciones,
            factura.cGravadaImportacionesServicios,
            factura.ivaCdtoFiscal,
            factura.totalCompra,
            # ingresar DUI de la empresa cuando se tenga
            factura.empresa.dui.replace('-','',1) if factura.empresa.dui is not None else '',
            # Modificaciones resolucion 04-2024
            factura.tipo_operacion if factura.tipo_operacion is not None else '0',
            factura.clasificacion if factura.clasificacion is not None else '0',
            factura.sector if factura.sector is not None else '0',
            factura.tipo_compra if factura.tipo_compra is not None else '0',
            "3",
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    writer.save()
    return direccion


# ============================================================================
# FORMATOS INTERNOS (CON CABECERA)
# ============================================================================

def _write_retenciones_section(ws, body_fmt, header_fmt, retenciones, row, titulo, campos_extra=None):
    """Escribe una sección de retenciones/percepciones/anticipos en el worksheet."""
    if not retenciones.exists():
        return row
    row += 4
    row += 1
    headers = ['NIT', 'Nombre', 'Fecha', 'Tipo de Documento', 'Numero de Serie',
               'Numero de Documento', 'Monto Sujeto', titulo]
    for col, h in enumerate(headers):
        ws.write(row, col, h, body_fmt)
    row += 1
    for item in retenciones:
        ws.write(row, 0, f"{item.empresa.nit}", body_fmt)
        ws.write(row, 1, f"{item.empresa.nombre}", body_fmt)
        ws.write(row, 2, f"{item.fecha.strftime('%d/%m/%Y')}", body_fmt)
        ws.write(row, 3, f"{item.get_tipoDocumento_display()}", body_fmt)
        ws.write(row, 4, f"{item.numeroSerie}", body_fmt)
        ws.write(row, 5, f"{item.numeroDocumento}", body_fmt)
        ws.write(row, 6, f"{item.monto_sujeto}", body_fmt)
        ws.write(row, 7, f"{item.retencion}", body_fmt)
        row += 1
    return row


def interno_compras(libro):
    """Exporta libro de compras en formato interno con cabecera."""
    facturas = FacturaCm.objects.filter(libro=libro).order_by('fecha')
    direccion = BASE_DIR / f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_compras_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(
        direccion, orientation='landscape')

    _write_libro_header_interno(ws, libro, "Libro de Compras", header_fmt)

    # Cabecera de columnas
    headers = ["Correlativo", "Fecha", "Clase de Doc", "Tipo de Doc", "N de Doc", "Nit",
               "Nombre", "Comp Loc Exen", "Inter Exen", "Impor Exen", "Comp Loc Grav",
               "Inter Grav Bienes", "Impor Grav Bienes", "Impor Grav Servicios",
               "Crdto Fiscal", "Total Compra", "Retencion/Pretencion", "Anticipo Cta Iva",
               "IVA Terceros"]
    for col, h in enumerate(headers):
        ws.write(4, col, h, body_fmt)

    row = 5
    for factura in facturas:
        data = [
            row - 4,
            factura.fecha.strftime('%d/%m/%Y'),
            factura.claseDocumento,
            factura.tipoDocumento,
            factura.numeroDocumento,
            safe_nit(factura.empresa),
            factura.empresa.nombre,
            factura.cExenteInterna, factura.cExenteInternaciones, factura.cExenteImportaciones,
            factura.cGravadaInterna, factura.cGravadaInternaciones,
            factura.cGravadaImportaciones, factura.cGravadaImportacionesServicios,
            factura.ivaCdtoFiscal, factura.totalCompra,
            factura.retencionPretencion, factura.anticipoCtaIva, factura.ivaTerceros,
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    # Totales
    total_fields = ['cExenteInterna', 'cExenteInternaciones', 'cExenteImportaciones',
                    'cGravadaInterna', 'cGravadaInternaciones', 'cGravadaImportaciones',
                    'cGravadaImportacionesServicios', 'ivaCdtoFiscal', 'totalCompra',
                    'retencionPretencion', 'anticipoCtaIva', 'ivaTerceros']
    ws.merge_range(f"A{row + 3}:F{row + 3}", "Totales", body_fmt)
    for i, field in enumerate(total_fields):
        total = facturas.aggregate(total=Coalesce(Sum(field), 0))['total']
        ws.write(row + 2, 7 + i, f"{total}", body_fmt)

    # Anticipos
    anticipos = RetencionCompra.objects.filter(libro=libro, tipoDocumento="2%").exclude(numeroSerie="").order_by('fecha')
    if anticipos.exists():
        row += 4
        headers_ant = ['NIT', 'Nombre', 'Fecha', 'Numero de Serie', 'Numero de Documento', 'Monto Sujeto', 'Anticipo a Cuenta']
        row += 1
        for col, h in enumerate(headers_ant):
            ws.write(row, col, h, body_fmt)
        row += 1
        for anticipo in anticipos:
            ws.write(row, 0, f"{anticipo.empresa.nit}", body_fmt)
            ws.write(row, 1, f"{anticipo.empresa.nombre}", body_fmt)
            ws.write(row, 2, f"{anticipo.fecha.strftime('%d/%m/%Y')}", body_fmt)
            ws.write(row, 3, f"{anticipo.numeroSerie}", body_fmt)
            ws.write(row, 4, f"{anticipo.numeroDocumento}", body_fmt)
            ws.write(row, 5, f"{anticipo.monto_sujeto}", body_fmt)
            ws.write(row, 6, f"{anticipo.retencion}", body_fmt)
            row += 1

    # Retenciones
    retenciones = RetencionCompra.objects.filter(libro=libro).exclude(tipoDocumento="2%").exclude(es_percepcion=True).order_by('fecha')
    row = _write_retenciones_section(ws, body_fmt, header_fmt, retenciones, row, 'Retencion')

    # Percepciones
    percepciones = RetencionCompra.objects.filter(libro=libro, es_percepcion=True).order_by('fecha')
    row = _write_retenciones_section(ws, body_fmt, header_fmt, percepciones, row, 'Percepcion')

    writer.close()
    return direccion


def interno_consumidor(libro):
    """Exporta libro de consumidor final en formato interno con cabecera."""
    facturas = FacturaCF.objects.filter(libro=libro).order_by("correlativoInicial")
    direccion = BASE_DIR / f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_consumidor_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion)

    _write_libro_header_interno(ws, libro, "Libro de Consumidor Final", header_fmt)

    headers = ["Fecha", "Clas de Doc", "Tipo de Doc", "N de Res", "N de Ser",
               "N Con Inter", "N Con Inter", "Corr Ini", "Corr Fin", "N Maq Regis",
               "Ven Exe", "Ven Inter Exen No Suj", "Ven no Suj", "Ven Grav Loc",
               "Expor CA", "Expor No CA", "Zona Franc", "Total"]
    for col, h in enumerate(headers):
        ws.write(4, col, h, body_fmt)

    row = 5
    for factura in facturas:
        data = [
            factura.fecha.strftime('%d/%m/%Y'),
            factura.claseDocumento, factura.tipoDocumento,
            factura.numeroResolucion, factura.numeroSerie,
            safe_val(factura.numeroControlInternoDel),
            safe_val(factura.numeroControlInternoAl),
            factura.correlativoInicial, factura.correlativoFinal,
            safe_val(factura.numeroRegistradora),
            factura.exento, factura.ventasInternasExentas, factura.ventasNSujetas,
            factura.locales, factura.exportacionesCA, factura.exportacionesNoCA,
            factura.ventasZonasFrancas, factura.ventaTotal,
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    # Totales
    total_fields = ['exento', 'ventasInternasExentas', 'ventasNSujetas', 'locales',
                    'exportacionesCA', 'exportacionesNoCA', 'ventasZonasFrancas', 'ventaTotal']
    ws.merge_range(f"A{row + 3}:I{row + 3}", "Totales", body_fmt)
    for i, field in enumerate(total_fields):
        total = facturas.aggregate(total=Coalesce(Sum(field), 0))['total']
        ws.write(row + 2, 10 + i, f"{total}", body_fmt)

    iva_total = facturas.aggregate(iva=Coalesce(Sum('locales'), 0) / dec('1.13'))['iva']
    ws.write(row + 3, 15, "IVA TOTAL:", body_fmt)
    ws.write(row + 3, 17, f"{iva_total}", body_fmt)

    writer.save()
    return direccion


def interno_contribuyente(libro):
    """Exporta libro de contribuyente en formato interno con cabecera."""
    facturas = FacturaCt.objects.filter(libro=libro).order_by('numeroDocumento')
    direccion = BASE_DIR / f"libros_consumidor/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_contribuyente_mh.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion)

    _write_libro_header_interno(ws, libro, "Libro de Contribuyente", header_fmt)

    headers = ["Fecha", "Clase de Doc", "Tipo de Doc", "N de Res", "N de Ser",
               "N de Doc", "N Cont Intr", "NIT Contr", "Nombre Contr",
               "Ven Exen", "Ven No Suje", "Ven Grav", "IVA", "Ven 3ros",
               "IVA 3ros", "Total", "IVA Ret"]
    for col, h in enumerate(headers):
        ws.write(4, col, h, body_fmt)

    row = 5
    for factura in facturas:
        nit = factura.contribuyente.nit if factura.contribuyente.nit else factura.contribuyente.nRegistro
        data = [
            factura.fecha.strftime('%d/%m/%Y'),
            factura.get_claseDocumento_display(), factura.get_tipoDocumento_display(),
            factura.numeroResolucion, factura.numeroSerie,
            factura.numeroDocumento, factura.numeroControlInterno,
            nit, factura.contribuyente.nombre,
            factura.venExentas, factura.ventasNSujetas, factura.venGravadas,
            factura.ivaDebFiscal, factura.vtVentas, factura.vtIVA,
            factura.total, factura.ivaRetenido,
        ]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    # Totales
    total_fields = ['venExentas', 'ventasNSujetas', 'venGravadas', 'ivaDebFiscal',
                    'vtVentas', 'vtIVA', 'total', 'ivaRetenido']
    ws.merge_range(f"A{row + 3}:I{row + 3}", "Totales", body_fmt)
    for i, field in enumerate(total_fields):
        total = facturas.aggregate(total=Coalesce(Sum(field), 0))['total']
        ws.write(row + 2, 9 + i, f"{total}", body_fmt)

    writer.save()
    return direccion


# ============================================================================
# EXPORTACIONES DE RETENCIONES / ANTICIPOS / PERCEPCIONES
# ============================================================================

def _export_retencion_base(libro_id, queryset_filter, filename_suffix, sheet_name, tipo_codigo):
    """Función base para exportar retenciones, anticipos o percepciones."""
    libro = Libro.objects.get(id=libro_id)
    facturas = queryset_filter(libro)
    direccion = BASE_DIR / f"libros_compras/{libro.cliente.nombre}_{libro.mes}_{libro.ano}_{filename_suffix}.xlsx"
    writer, wb, ws, header_fmt, body_fmt, foot_fmt = _create_hacienda_worksheet(direccion, sheet_name)

    row = 0
    for factura in facturas:
        data = [
            safe_nit(factura.empresa),
            factura.fecha.strftime('%d/%m/%Y'),
            factura.tipoDocumento if hasattr(factura, 'tipoDocumento') else "",
            factura.numeroSerie,
            factura.numeroDocumento,
            factura.monto_sujeto,
            factura.retencion,
            tipo_codigo,
        ]
        # Para anticipos, omitir tipo documento (col 2)
        if filename_suffix == 'anticipo_a_cuenta':
            data = [data[0], data[1], data[3], data[4], data[5], data[6], data[7]]
        for col, val in enumerate(data):
            ws.write(row, col, f"{val}", body_fmt)
        row += 1

    writer.save()
    return direccion


def anticipo_cuenta(libro_id):
    """Exporta anticipos a cuenta IVA 2%."""
    def qf(libro):
        return RetencionCompra.objects.filter(
            libro=libro, tipoDocumento="2%"
        ).exclude(numeroSerie="").order_by('fecha')
    return _export_retencion_base(libro_id, qf, 'anticipo_a_cuenta', 'detalle_consumidor', '6')


def retencion_compra(libro_id):
    """Exporta retenciones de compra."""
    def qf(libro):
        return RetencionCompra.objects.filter(
            libro=libro
        ).exclude(tipoDocumento="2%").exclude(es_percepcion=True).order_by('fecha')
    return _export_retencion_base(libro_id, qf, 'retencion_compra', 'Retenciones', '7')


def percepcion_compra(libro_id):
    """Exporta percepciones de compra."""
    def qf(libro):
        return RetencionCompra.objects.filter(
            libro=libro, es_percepcion=True
        ).order_by('fecha')
    return _export_retencion_base(libro_id, qf, 'percepcion_compra', 'Percepciones', '8')