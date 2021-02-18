#python libs
import os
import csv

#3rd party libs
import pandas as pd

#Self
from .models import Cuenta, SubCuenta, Catalogo
from empresas.models import Empresa
from garrobo.settings import BASE_DIR




# Crear plantilla de cuentas
def  pl_cuentas(catalogo):
    #cuentas principales
    cuentas_principales = [('1','Activo'),('2',"Pasivo"),
    ('3','Patrimonio Neto'),('4','Cuentas de Resultado Deudoras'),
    ('5','Cuentas de Resultado Acreedoras'),('6','Cuentas de Cierre')]
    for cuenta in cuentas_principales:
        nueva_cuenta = Cuenta(codigo=cuenta[0],nombre=cuenta[1],catalogo=catalogo)
        nueva_cuenta.save()
    #Cuentas Secundarias
    cuentas_secundarias =[
        ('11','Activo Corriente'.upper()),('12','Activo No Corriente'.upper()),
        ('21','Pasivo Corriente'.upper()),('22','Pasivo No Corriente'.upper()),
        ('31','Capital, Reservas y Resultados'.upper()),
        ('41','Costos por Operaciones'.upper()),('42','Gastos de Operaciones'.upper()),('43','Gastos no Operacionales'.upper()),
        ('51','Ingresos Operacionales'.upper()),('52','Ingresos no Operacionales'.upper()),
        ('61','Perdidas Y Ganancias'.upper()),
    ]
    for cuenta in cuentas_secundarias:
        cuenta_principal = Cuenta.objects.get(catalogo=catalogo,codigo=cuenta[0][0])
        cuenta_nueva = SubCuenta(codigo=cuenta[0],nombre=cuenta[1],catalogo=catalogo,cuenta_principal=cuenta_principal,es_mayor=True)
        cuenta_nueva.save()
    #subcuentas 3er nivel
    subcuentas = [
        ('1101','Efectivo y Equivalentes'.upper()),
        ('1102','Inversiones Financieras A Corto Plazo'.upper()),
        ('1103','DEUDORES COMERCIALES Y OTRAS CUENTAS POR COBRAR'),
        ('1104','INVENTARIOS'),('1105','PAGOS ANTICIPADOS')
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='11',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('1201','PROPIEDAD, PLANTA Y EQUIPO'),
        ('1202','INTANGIBLES'),
        ('1203','PROPIEDAD DE INVERSION'),
        ('1204','INVERSIONES FINANCIERAS A LARGO PLAZO'),
        ('1205','ACTIVO POR IMPUESTOS DIFERIDOS'),
        ('1206','DEPOSITOS EN GARANTIA Y OTROS ACTIVOS A LARGO PLAZO'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='12',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('2101','DEUDAS FINANCIERAS A CORTO PLAZO'),
        ('2102','DEUDAS COMERCIALES Y OTRAS CUENTAS POR PAGAR A CORTO PLAZO'),
        ('2103','INTERESES POR PAGAR'),
        ('2104','OBLIGACIONES A CORTO PLAZO POR BENEFICIOS A EMPLEADOS'),
        ('2105','IMPUESTOS POR PAGAR'),
        ('2106','DIVIDENDOS POR PAGAR'),
        ('2107','PROVISIONES'),
        ('2108','OBLIGACIONES A CORTO PLAZO POR ARRENDAMIENTOS  FINANCIEROS'),
        ('2109','DEUDAS RELACIONADOS CON ACTIVOS NO CORRIENTES PARA LA VENTA'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='21',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('2201','DEUDAS FINANCIERAS A LARGO PLAZO'),
        ('2202','OBLIGACIONES A LARGO PLAZO POR BENEFICIOS A EMPLEADOS'),
        ('2203','PASIVOS POR IMPUESTOS SOBRE LA RENTA DIFERIDOS'),
        ('2204','PROVISIONES Y OTROS PASIVOS A LARGO PLAZO'),
        ('2205','OBLIGACIONES A LARGO PLAZO POR ARRENDAMIENTOS FINANCIEROS'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='22',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('3101','CAPITAL SOCIAL(CAPITAL EN ACCIONES)'),
        ('3102','OPCIONES Y DERECHOS'),
        ('3103','APORTACINES ADICIONALES'),
        ('3104','RESERVAS'),
        ('3105','RESULTADOS ACUMULADOS'),
        ('3106','RESULTADO DEL EJERCICIO'),
        ('3107','SUPERAVIT POR REVALUACION'),
        ('3108','AJUSTES Y EFECTOS POR VALUACION Y CAMBIOS DE VALOR'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='31',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('4101','COMPRAS'),
        ('4102','COSTO DE SERVICIO'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='41',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('4201','GASTOS DE ADMINISTRACION'),
        ('4202','GASTOS DE VENTAS Y COMERCIALIZACION'),
        ('4203','GASTOS POR DETERIORO Y PERDIDAS EN ENAJENACION DE ACTIVOS DE EXPLOTACION'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='42',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('4301','GASTOS FINANCIEROS')
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='43',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('5101','INGRESOS POR VENTAS'),
        ('5102','OTROS INGRESOS OPERACIONALES'),
        ('5103','INGRESOS POR REVERSION DE DETERIORO Y GANANCIAS EN ENAJENACION DE ACTIVOS'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='51',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('5201','INGRESOS FINANCIEROS'),
        ('5202','INGRESOS POR CAMBIOS EN VALOR RAZONABLE DE INVERSIONES FINANCIERAS'),
        ('5203','REVERSION DEL DETERIORO Y GANACIENAS EN INSTRUMENTOS FINANCIEROS'),
        ('5204','OTROS INGRESOS FINANCIEROS NO OPERACIONALES'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='52',catalogo=catalogo))
        subuenta.save()
    subcuentas = [
        ('6101','PERDIDAS Y GANACIAS'),
    ]
    for sc in subcuentas:
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo='61',catalogo=catalogo))
        subuenta.save()
    #subcuentas 4to nivel
    subcuentas = [
        ('110101','EFECTIVO EN CAJA GENERAL'),('110102','EFECTIVO EN CAJA CHICA'),('110103','EFECTIVO EN BANCOS'),('110104','EQUIVALENTES DE EFECTIVO'),
        ('110201','DEPOSITOS A PLAZO'),('110202','INSTRUMENTOS FINANCIEROS A CORTO PLAZO'),('110203','INSTRUMENTOS FINANCIEROS A CORTO PLAZO CON PARTES RELACONADAS'),('110204','OTRAS INVERSIONES A CORTO PLAZO'),
        ('110301','DEUDORES POR VENTA DE MERCADERIAS'),('110302','ESTIMACION POR CUENTAS INCOBRABLES (CR)'),('110303','ANTICIPOS A EMPLEADSOS'),('110304','CUENTAS Y DOCUMENTOS POR COBRAR A ACCIONISTAS'),('110305','DEUDORES DIVERSOS Y OTRAS CUENTAS POR COBRAR'),('110306','IMPUESTOS POR RECUPERAR'),
        ('110401','PRODUCTOS COMPRADOS PARA LA VENTA'),('110402','INVENTARIOS EN PROCESO'),('110499','DETERIORO DE VALOR DE LOS INVENTARIOS'),
        ('110501','SEGUROS'),('110502','PAPELERIA UTILES Y ENSERES'),('110503','ALQUILERES'),
        ('120101','BIENES INMUEBLES'),('120102','BIENES MUEBLES'),('120103','PROPIEDAD, PLANTA Y EQUIPO EN CURSO'),('120198','DEPRECIACION DE PROPIEDAD, PLANTA Y EQUIPO EN CURSO(CR)'),('120199','DETERIORO PROPIEDAD, PLANTA Y EQUIPO EN CURSO(CR)'),
        ('120201','INVESTIGACION'),('120202','DESARROLLO'),('120203','PROPIEDAD INDUSTRIAL'),('120204','CREDITO MERCANTIL'),('120205','LICENCIAS Y PROGRAMAS'),('120206','DERECHOS Y PATENTES'),('120207','ANTICIPOS PARA LA ADQUISICION DE INSTANGIBLES'),('120298','AMORTIZACION ACUMULADA DE INTANGIBLES(CR)'),('120299','DETERIORO DE VALOR DE ACTIVOS INTANGIBLES(CR)'),
        ('120301','INVERSIONES EN TERRENOS'),('120302','INVERSIONES EN EDIFICACIONES'),('120398','DEPRECIACION ACUMULADA DE PROPIEDAD DE INVERSION(CR)'),('120399','DETERIORO DE VALOR DE PROPIEDAD DE INVERSION(CR)'),
        ('120401','INVERSIONES FINANCIERAS A LARGO PLAZO(INVERSIONES PERMANENTES)'),('120402','OTRAS INVERSIONES FINANCIERAS A LARGO PLAZO'),('1204003','DETERIORO DE VALOR DE LAS INVERSIONES FINANCIERAS A LARGO PLAZO(CR)'),
        ('120501','ACTIVO POR ISR DIFERIDO'),
        ('120601','DEPOSITOS CONSTITUIDOS A LARGO PLAZO'),('120602','FINANZAS CONSTITUIDAS A LARGO PLAZO'),('120603','PAGOS ANTICIPADOS AMORTIZABLES A LARGO PLAZO'),('120604','OTROS ACTIVOS DE LARGO PLAZO'),

        ('210101','DEUDAS CON ENTIDADES DE CREDITOS'),('210102','DEUDAS FINANCIERAS A CORTO PLAZO'),('210103','OTRAS OBLIGACIONES FINANCIERAS A LARGO PLAZO'),
        ('210201','PROVEEDORES'),('210202','ANTICIPO A CLIENTES'),('210203','ACREEDORES DIVERSOS'),('210204','RETENCIONES Y CUOTAS PATRONALES POR PAGAR'),
        ('210301','INTERESES BANCARIOS POR PAGAR'),('210302','INTERESES POR TRANSACCIONES CON PARTES RELACIONADAS'),('210303','OTROS INTERESES POR PPAGAR'),
        ('210401','SUELDOS Y SALARIOS'),('210402','VACACIONES Y AGUINALDOS'),('210403','INDEMNIZACIONES OBLIGATORIAS O CONVENIDAS'),('210404','OTRAS REMUNERACIONES Y PRESENTACIONES POR PAGAR'),
        ('210501','IMPUESTOS MENSUALES POR PAGAR'),('210502','PASIVO POR IMPUESTO SOBRE LA RENTA CORRIENTE ANUAL'),
        ('210601','DIVIDENDOS DECRETADOS POR PAGAR'),
        ('210701','PROVISIONES POR GARANTIAS A CIENTES'),
        ('210801','ARRENDAMIENTOS FINANCIEROS POR PAGAR A CORTO PLAZO'),
        ('210901','CUENTAS POR PAGAR VINCULADAS CON ACTIVO NO CORRIENTE '),
        ('220101','DEUDAS CON ENTIDADES DE CREDITO'),('220102','DEUDAS FINANCIERAS A LARGO PLAZO POR PARTES RELACIONADAS'),('220103','OTRAS OBLIGACIONES POR PAGAR A LARGO PLAZO A PARTES RELACIONADAS'),
        ('220201','PRESTACIONES POR RETIRO'),
        ('220301','PASIVO POR ISR DIFERIDO'),
        ('220401','PROVISIONES POR REESTRUCTURACIONES'),('220402','PROVISIONES PARA DESMANTELAMIENTO DE ACTIVOS'),
        ('220501','ARRENDAMIENTOS FINANCIEROS POR PAGAR A LARGO PLAZO'),

        ('310101','CAPITAL SOCIAL MINIMO'),('310102','CAPITAL SOCIAL VARIABLE'),
        ('310201','OPCIONES SOBRE ACCIONES'),('310202','GARANTIAS'),
        ('310301','APORTACIONES A EMISIONES FUTURAS DE DE ACCIONES'),
        ('310401','RESERVA LEGAL'),
        ('310501','UTILIDADES DE EJERCICIOS ANTERIORES'),('310502','PERDIDAS DE EJERCICIOS ANTERIORES'),
        ('310601','UTILIDAD DEL PRESENTE EJERCICIO'),('310602','PERDIDA DEL PRESENTE EJERCICIO'),
        ('310701','SUPERAVIT POR REVALUACION DE INMUEBLES'),
        ('310801','EFECTOS DE CONVERSION DE A NIIF'),

        ('410101','MERCADERIA PARA LA VENTA'),
        ('410201','GASTOS DE PERSONAL'),('410202','MANTENIMIENTOS'),('410203','SERVICIOS PUBLICOS Y PRIVADOS'),('410204','HONORARIOS'),('410205','DEPRECIACIONES'),('410206','AMORTIZACION DE ACTIVOS INTANGIBLES'),('410207','SEGUROS'),('410208','IMPUESTOS, TASAS, DERECHOS, ARANCELES Y CONTRIBUCIONES'),('410209','GASTOS DE ADMINISTRACION - ATENCIONES A CLIENTES Y EMPLEADOS'),('410210','VIATICOS Y GASTOS DE VIAJE'),('410211','COMBUSTIBLES Y LUBRICANTES'),('410212','PAPELERIA Y UTILES'),('410213','DONACIONES'),
        ('420101','GASTOS DE ADMINISTRACION - GASTOS DE PERSONAL'),('420102','GASTOS DE ADMINISTRACION - MANTENIMIENTOS'),('420103','GASTOS DE ADMINISTRACION - SERVICIOS PUBLICOS Y PRIVADOS'),('420104','GASTOS DE ADMINISTRACION - HONORARIOS'),('420105','GASTOS DE ADMINISTRACION - DEPRECIACIONES'),('420106','AMORTIZACION DE ACTIVOS INSTANGIBLES'),('420107','GASTOS DE ADMINISTRACION - SEGUROS'),('410108','GASTOS DE ADMINISTRACION - IMPUESTOS, TASAS, DERECHOS, ARANCELES Y CONTRIBUCIONES'),('420109','GASTOS DE ADMINISTRACION - ATENCIONES A CLIENTES Y EMPLEADOS'),('420110','GASTOS DE ADMINISTRACION - VIATICOS Y GASTOS DE VIAJE'),('420111','COMBUSTIBLES Y LUBRICANTES'),('420112','PAPELERIA Y UTILES'),('420113','DONACIONES'),('420199','OTROS GASTOS'),
        ('420201','GASTOS DE PERSONAL'),('420202','MANTENIMIENTOS'),('420203','SERVICIOS PUBLICOS Y PRIVADOS'),('420204','HONORARIOS'),('420205','DEPRECIACIONES'),('420206','AMORTIZACIONES'),('420207','SEGUROS'),('420208','IMPUESTOS, TASAS, DERECHOS, ARANCELES Y CONTRIBUCIONES'),('420209','ATENCIONES A CLIENTES Y EMPLEADOS'),('420210','VIATICOS Y GASTOS DE VIAJE'),('420211','COMBUSTIBLES Y LUBRICANTES'),('420212','PAPELERIA Y UTILES'),('420213','DONACIONES'),
        ('420301','DETERIORO DE VALOR DE ACTIVOS'),('420302','PERDIDAS POR ENAJENACION DE ACTIVOS DE EXPLOTACION'),
        ('430101','INTERESES POR PRESTAMOS'),('430102','COMISIONES, HONORARIOS Y OTROS GASTOS POR PRESTAMOS'),('430103','DIFERENCIAS DE CAMBIO'),

        ('510101','INGRESOS POR VENTAS'),
        ('510201','INGRESOS POR ARRENDAMIENTOS'),
        ('510301','REVERSION DEL DETERIORO DEL VALOR DE LOS ACTIVOS'),('510302','GANANCIAS POR ENAJENAMIENTO DE ACTIVOS DE EXPLOTACION'),
        ('520101','INTERESES SOBRE DEPOSITOS BANCARIOS'),('520102','COMISIONES RECIBIDAS'),('520103','OTROS INGRESOS FINANCIEROS'),
        ('520201','INGRESOS POR CAMBIOS EN VALOR RAZONABLE DE INVERSIONES PARA LA VENTA'),
        ('520301','REVERSION DE DETERIORO DE INSTRUMENTOS FINANCIEROS'),('520302','GANANCIA POR ENAJENACIONES DE INSTRUMENTOS FINANCIEROS'),
        ('520401','OTROS INGRESOS NO OPERACIONALES'),
    ]
    for sc in subcuentas:
        cod = sc[0][0:4]
        subuenta = SubCuenta(codigo=sc[0],nombre=sc[1],catalogo=catalogo,cuenta_padre=SubCuenta.objects.get(codigo=cod,catalogo=catalogo))
        subuenta.save()


def pl_cuentas2(archivo,empresa_id=1):
    catalogo = Catalogo.objects.get_or_create(empresa_id=empresa_id)[0]
    with open(os.path.join(BASE_DIR,archivo)) as f:
        documento = csv.reader(f,delimiter=',',dialect='excel')
        next(documento, None)
        documento = list(documento)
        for linea in documento:
            codigo, nombre = list(linea)
            codigo = str(codigo)
            if len(codigo) == 1:
                cuenta = Cuenta.objects.get_or_create(
                    catalogo_id=catalogo.id,
                    codigo=codigo,
                    nombre=nombre
                    )
                cuenta[0].save()
                
            elif len(codigo) == 2:
                cuenta = SubCuenta.objects.get_or_create(
                    catalogo=catalogo,
                    codigo=codigo,
                    nombre=nombre,
                    cuenta_principal=(Cuenta.objects.get(catalogo_id=catalogo.id,codigo=codigo[0]))
                    )
                cuenta[0].save()

            else:
                cuenta = SubCuenta.objects.get_or_create(
                    catalogo=catalogo,
                    codigo=codigo,
                    nombre=nombre,
                    cuenta_padre=(SubCuenta.objects.get(catalogo_id=catalogo.id,codigo=codigo[0:-2]))
                    )
                cuenta[0].save()
