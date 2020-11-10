#python libs
import datetime
#django libs
from contabilidad.forms import *
from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView, TemplateView
from django.urls import reverse
#self libs
from .models import *
from empresas.models import Empresa


#vistas de Partida

class PartidaCV(CreateView):
    model = Partida
    template_name = "contabilidad/modal.html"
    form_class = PartidaF
    def get_initial(self, **kwargs):
        mes = Libro.objects.get(id=self.kwargs['libro']).mes
        ano = Libro.objects.get(id=self.kwargs['libro']).periodo.ano
        initial = super(PartidaCV,self).get_initial()
        initial['libro'] = Libro.objects.get(id=self.kwargs['libro'])
        initial["fecha"] = Partida.objects.filter(libro__id=self.kwargs['libro']).order_by('-fecha')[0].fecha + datetime.timedelta(days=1) if Partida.objects.filter(libro__id=self.kwargs['libro']).exists() else datetime.datetime.strptime(f"01/{mes}/{ano}",'%d/%m/%Y')
        return initial

    def get_context_data(self, **kwargs):
        context = super(PartidaCV, self).get_context_data(**kwargs)
        context['direccion'] = 'cont:nueva_partida'
        context['titulo']    = 'Crear Partida Nueva'
        context['parametro'] = self.kwargs['libro']
        context['obj_padre'] = Libro.objects.get(id=self.kwargs['libro'])
        return context

    def get_success_url(self,**kwargs):
        return reverse("cont:lista_partida",args=[self.kwargs['libro'],])


class PartidaLV(ListView):
    model = Partida
    template_name = "contabilidad/lpartida.html"
    context_object_name = 'partidas'
    ordering = ['-fecha',]

    def get_context_data(self, **kwargs):
        context = super(PartidaLV, self).get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(id=self.kwargs['libro'])
        return context
        
    def get_queryset(self):
        queryset = super(PartidaLV, self).get_queryset()
        queryset = queryset.filter(libro__id = self.kwargs['libro']).order_by("fecha")
        return queryset

#Vistas de Libro

class LibroCV(CreateView):
    model = Libro
    template_name = "contabilidad/modal.html"
    form_class = LibroF
    
    def get_success_url(self,**kwargs):
        return reverse("cont:lista_libro",args=[self.kwargs['pk'],])

    def get_initial(self, **kwargs):
        initial = super(LibroCV,self).get_initial()
        initial['periodo'] = Periodo.objects.get(id=self.kwargs['pk'])
        return initial

    def get_context_data(self, **kwargs):
        context = super(LibroCV, self).get_context_data(**kwargs)
        context['direccion'] = 'cont:nuevo_libro'
        context['titulo']    = 'Crear Libro Nuevo'
        context['parametro'] = self.kwargs['pk']
        context['obj_padre'] = Periodo.objects.get(id=self.kwargs['pk'])
        return context

class LibroLV(ListView):
    model = Libro
    template_name = "contabilidad/llibro.html"
    context_object_name = 'libros'

    def get_context_data(self, **kwargs):
        context = super(LibroLV,self).get_context_data(**kwargs)
        context["periodo"] = Periodo.objects.get(id=self.kwargs['periodo'])
        return context

    def get_queryset(self):
        queryset = super(LibroLV, self).get_queryset()
        queryset = queryset.filter(periodo__id = self.kwargs['periodo']).order_by('periodo','mes')
        return queryset



#vistas del Periodo 
class PeriodoCV(CreateView):
    model = Periodo
    template_name = "contabilidad/modal.html"
    form_class = PeriodoForm

    def get_success_url(self,**kwargs):
        return reverse("cont:lista_periodo",args=[self.kwargs['pk'],])

    def get_context_data(self, **kwargs):
        context = super(PeriodoCV, self).get_context_data(**kwargs)
        context['direccion'] = 'cont:nuevo_periodo'
        context['titulo']    = 'Crear Periodo Nuevo'
        context['parametro'] = self.kwargs['pk']
        context['obj_padre'] = Empresa.objects.get(id=self.kwargs['pk'])
        return context

    def get_initial(self, **kwargs):
        initial = super(PeriodoCV,self).get_initial()
        initial['empresa'] = Empresa.objects.get(id=self.kwargs['pk'])
        return initial


class PeriodoL(ListView):
    model = Periodo
    context_object_name = 'periodos'
    template_name='contabilidad/lperiodo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa"] = Empresa.objects.get(id=self.kwargs['emp'])
        return context
    
    def get_queryset(self):
        q = super(PeriodoL,self).get_queryset()
        q = q.filter(empresa__id=self.kwargs['emp'])
        return q


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
    cuenta.save()
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
        cuenta_padre.save()
        if cuenta_padre.es_mayor:
            cuenta_principal = cuenta_padre.cuenta_principal
        #Si la cuenta padre no tiene una cuenta padre propia entonces se saldra del bucle
        cuenta_padre = cuenta_padre.cuenta_padre if cuenta_padre.es_mayor ==False else False

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
        cuenta_principal.save()

    return "Se Actualizaron todas las cuentas" 