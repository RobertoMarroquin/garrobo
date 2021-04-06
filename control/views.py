#python libs
from datetime import date, datetime, timedelta
import datetime
#django libs
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, CreateView, DeleteView, UpdateView, DetailView, ListView, TemplateView
from django.urls import reverse
from django.db.models import Sum
from django.http.response import FileResponse, HttpResponse
from django.core.serializers import serialize
from django.contrib.auth.models import User
#self libs
from .models import *
from .forms import *
from empresas.models import Empresa

#Views Talonario
class TalonarioCV(CreateView):
    model = Talonario
    template_name = "control/talonarioc.html"
    form_class = TalonarioF

    def get_initial(self, **kwargs):
        initial = super(TalonarioCV, self).get_initial(**kwargs)
        initial["empresa"] = self.kwargs['empresa']
        return initial

    def get_context_data(self, **kwargs):
        context = super(TalonarioCV, self).get_context_data(**kwargs)
        context["empresa"] = Empresa.objects.get(id=self.kwargs['empresa'])
        context['direccion'] = 'control:nuevoTalonario'
        context['titulo'] = 'Crear Talonario'
        context["parametro"] = self.kwargs['empresa']
        #context["talonarios"] = context["empresa"].talonarios.all()
        return context

    def get_form_kwargs(self):
        kwargs = super(TalonarioCV,self).get_form_kwargs()
        kwargs['empresa'] = Empresa.objects.get(id=self.kwargs['empresa'])
        return kwargs

    def get_success_url(self,**kwargs):
        return reverse("control:talonarioLista",args=(self.kwargs["empresa"],))


class TalonarioLV(ListView):
    model = Talonario
    form_class = TalonarioF
    template_name = "control/talonariol.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa"] = Empresa.objects.get(id=self.kwargs['empresa'])
        context["talonarios"] = context["empresa"].talonarios
        return context
    


#Views Mensualidad

class MensualidadCV(CreateView):
    model = Mensualidad
    template_name = "control/mensualidadc.html"
    form_class = MensualidadF

    def get_form_kwargs(self):
        kwargs = super(MensualidadCV,self).get_form_kwargs()
        kwargs['talonario'] = Talonario.objects.get(id=self.kwargs['talonario'])
        return kwargs

    def get_success_url(self,**kwargs):
        return reverse("control:lista_Mensualidad",args=(self.kwargs["talonario"],))


class MensualidadLV(ListView):
    model = Mensualidad
    context_object_name = 'mensualidades'
    template_name='control/mensualidadl.html'

    def get_context_data(self, **kwargs):
        context = super(MensualidadLV,self).get_context_data()
        context['talonario'] = Talonario.objects.get(id=self.kwargs['talonario'])
        return context
    

#Views Cobros 
class CobroCV(CreateView):
    model = Cobro
    template_name = "control/cobroc.html"
    
    def get_form_kwargs(self):
        kwargs = super(CobroCV,self).get_form_kwargs()
        kwargs['mensualidad'] = Mensualidad.objects.get(id=self.kwargs['mensualidad'])
        return kwargs

    def get_success_url(self,**kwargs):
        return reverse("control:lista_cobros",args=(self.kwargs["mensualidad"],))
    

class CobroLV(ListView):
    model = Cobro
    template_name = "control/cobrol.html"

    def get_context_data(self, **kwargs):
        context = super(MensualidadCV,self).get_context_data()
        context['mensualida'] = Talonario.objects.get(id=self.kwargs['mensualidad'])
        return context
    