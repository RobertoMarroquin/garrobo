from django.shortcuts import render

#Funcionalidades de las views
def actualizacion_saldos(cuenta, movimiento):
    """ Actualiza todas las cuentas que modifica un movimiento de una partida """
    tipo_cuenta = cuenta.codigo[0]
    tipo_movimiento = "haber" if movimiento.monto_haber > 0 else "deber" 
    #Dependiendo del tipo de cuenta y tipo de movimiento se procedera de distinta manera
    if tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "deber":
        cuenta.saldo  =+ movimiento.monto_deber
    elif tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "haber":
        cuenta.saldo  =- movimiento.monto_haber
    elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "haber":
        cuenta.saldo  =+ movimiento.monto_haber
    elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "deber":
        cuenta.saldo  =- movimiento.monto_deber
    else: return "Error tipos no registrados" 

    #Alterar cuenta padre en bucle hasta llegar a cuentas de mayor
    cuenta_padre = cuenta.cuenta_padre
    cuenta_principal = None
    while cuenta_padre:
        #Alterar saldo hasta llegar a cuentas de mayor
        if tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "deber":
            cuenta_padre.saldo  =+ movimiento.monto_deber
        elif tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "haber":
            cuenta_padre.saldo  =- movimiento.monto_haber
        elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "haber":
            cuenta_padre.saldo  =+ movimiento.monto_haber
        elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "deber":
            cuenta_padre.saldo  =- movimiento.monto_deber
        else: return "Error tipos no registrados" 
        if cuenta_padre.cuenta.principal is not None:
            cuenta_principal = cuenta_padre.cuenta.principal
        #Si la cuenta padre no tiene una cuenta padre propia entonces se saldra del bucle
        cuenta_padre = cuenta_padre.cuenta_padre if cuenta_padre.cuenta_padre is not None else False

    if cuenta_principal is not None:
        #Alterar saldo de cuenta Principal
        if tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "deber":
            cuenta_principal.saldo  =+ movimiento.monto_deber
        elif tipo_cuenta == '1' or tipo_cuenta == '4' and tipo_movimiento == "haber":
            cuenta_principal.saldo  =- movimiento.monto_haber
        elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "haber":
            cuenta_principal.saldo  =+ movimiento.monto_haber
        elif tipo_cuenta == '2' or tipo_cuenta == '3' or tipo_cuenta == '5' or tipo_cuenta == '6' and tipo_movimiento == "deber":
            cuenta_principal.saldo  =- movimiento.monto_deber
        else: return "Error tipos no registrados"

    return "Se Actualizaron todas las cuentas" 