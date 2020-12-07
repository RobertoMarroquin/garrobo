#python libs
from datetime import date
import datetime
#django libs
from contabilidad.forms import *
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, CreateView, DeleteView, UpdateView, DetailView, ListView, TemplateView
from django.urls import reverse
from django.db.models import Sum
#self libs
from .models import *
from empresas.models import Empresa

#Vistas Subcuenta

class SubCuentaCV(CreateView):
    model = SubCuenta
    template_name = "contabilidad/modal.html"
    form_class = SubCuentaF

    def get_success_url(self,**kwargs):
        catalogo = SubCuenta.objects.get(id=self.kwargs["catalogo"]).catalogo.id
        return reverse("cont:detalle_catalogo",args=(catalogo,))
    
    def get_initial(self, **kwargs):
        initial = super(SubCuentaCV,self).get_initial()
        initial["catalogo"] =  Catalogo.objects.get(id=self.kwargs["catalogo"]).id
        return initial

    
    def get_form_kwargs(self):
        kwargs = super(SubCuentaCV,self).get_form_kwargs()
        kwargs['catalogo'] = Catalogo.objects.get(id=self.kwargs["catalogo"])
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(SubCuentaCV,self).get_context_data(**kwargs)
        context['catalogo'] = Catalogo.objects.get(id=self.kwargs["catalogo"])
        context["empresa"] = Catalogo.objects.get(id=self.kwargs["catalogo"]).empresa
        context['direccion'] = 'cont:nueva_subcuenta'
        context['titulo'] = 'Crear Subcuenta'
        context["parametro"] = self.kwargs['catalogo']
        return context


class SubCuentaUV(UpdateView):
    model = SubCuenta
    template_name = "contabilidad/modal.html"
    fields = ["nombre","codigo"]

    def get_context_data(self, **kwargs):
        context = super(SubCuentaUV,self).get_context_data(**kwargs)
        subcuenta = SubCuenta.objects.get(id=self.kwargs['pk'])
        context['direccion'] = 'cont:act_subcuenta'
        context['titulo'] = f'Actualizar Subcuenta {subcuenta.nombre}'
        context['parametro'] = self.kwargs['pk'] 
        context['actualizar'] = True 
        return context
    def get_success_url(self,**kwargs):
        catalogo = SubCuenta.objects.get(id=self.kwargs["pk"]).catalogo.id
        return reverse("cont:detalle_catalogo",args=(catalogo,))


#Vistas de Catalogo
class CatalogoCV(CreateView):
    model = Catalogo
    template_name = "contabilidad/modal.html"
    form_class = CatalogoF

    def get_success_url(self,**kwargs):
        return reverse("cont:lista_periodo",args=(self.kwargs["empresa"],))

    def get_context_data(self, **kwargs):
        context = super(CatalogoCV,self).get_context_data(**kwargs)
        context["empresa"] = Empresa.objects.get(id=self.kwargs['empresa'])
        context['direccion'] = 'cont:nuevo_catalogo'
        context['titulo'] = 'Crear Catalogo'
        context["parametro"] = self.kwargs['empresa']
        return context
    
    def get_initial(self, **kwargs):
        initial = super(CatalogoCV,self).get_initial()
        initial['empresa']=self.kwargs['empresa']
        return initial


class CatalogoD(DetailView):
    model = Catalogo
    template_name = 'contabilidad/detalle_catalogo.html'
    context_object_name = 'catalogo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = Catalogo.objects.get(id=self.kwargs['pk']).empresa
        context['catalogo'] =  Catalogo.objects.get(id=self.kwargs['pk'])
        context["subcuentas"] = SubCuenta.objects.filter(catalogo=Catalogo.objects.get(id=self.kwargs['pk'])) 
        return context

                
#Vistas de Movimiento
class MovimientoCV(CreateView):
    model = Movimiento
    template_name = "contabilidad/lmovimiento.html"
    form_class = MovimientoF

    def post(self, request, **kwargs):
        return super(MovimientoCV, self).post(request, **kwargs)

    def form_valid(self, form):
        form.instance.partida_id = Partida.objects.get(id=self.kwargs["partida"]).id
        valid_data = super(MovimientoCV, self).form_valid(form)
        return valid_data

    def get_initial(self,  **kwargs):
        initial = super(MovimientoCV,self).get_initial()
        initial["monto_haber"] = "0.00"
        initial["monto_deber"] = "0.00"
        return initial

    def get_form_kwargs(self):
        kwargs = super(MovimientoCV,self).get_form_kwargs()
        kwargs['catalogo'] = Partida.objects.get(id=self.kwargs["partida"]).libro.periodo.empresa.catalogo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(MovimientoCV, self).get_context_data(**kwargs)
        context['partida'] = Partida.objects.get(id=self.kwargs["partida"])
        context["movimientos"] = Movimiento.objects.filter(partida__id=self.kwargs["partida"]) 
        context["haber_total"] = float("{0:.2f}".format(Movimiento.objects.filter(partida__id=self.kwargs["partida"]).aggregate(Sum('monto_haber'))["monto_haber__sum"]))   if Movimiento.objects.filter(partida__id=self.kwargs["partida"]).exists() else "0.00"
        context["deber_total"] = float("{0:.2f}".format(Movimiento.objects.filter(partida__id=self.kwargs["partida"]).aggregate(Sum('monto_deber'))["monto_deber__sum"]))   if Movimiento.objects.filter(partida__id=self.kwargs["partida"]).exists() else "0.00"
        
        return context

    def get_success_url(self,**kwargs):
        return reverse("cont:movimientos",args=[self.kwargs['partida'],])
    
    
class MovimientoUV(UpdateView):
    model = Movimiento
    template_name = "contabilidad/modal.html"
    fields = [
        "descripcion",
        "monto_haber",
        "monto_deber",
    ]

    def get_context_data(self, **kwargs):
        context = super(MovimientoUV,self).get_context_data(**kwargs)
        movimiento = Movimiento.objects.get(id=self.kwargs['pk'])
        context['direccion'] = 'cont:act_movimiento'
        context['titulo'] = f'Actualizar Movimiento {movimiento.partida.fecha}'
        context['parametro'] = self.kwargs['pk'] 
        context['actualizar'] = True 
        return context

    def get_success_url(self,**kwargs):
        partida = Movimiento.objects.get(id=self.kwargs['pk']).partida.id
        return reverse("cont:movimientos",args=[partida,])


class MovimientoDV(DeleteView):
    model = Movimiento
    template_name = "contabilidad/dmodal.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mov"] = self.kwargs["pk"]
        context["partida"] = Movimiento.objects.get(id=self.kwargs["pk"]).partida.id
        return context
    
    def get_object(self):
        id_m = self.kwargs['pk']
        return get_object_or_404(Movimiento,id=id_m)

    def get_success_url(self,**kwargs):
        partida = Movimiento.objects.get(id=self.kwargs['pk']).partida.id
        return reverse("cont:movimientos",args=[partida,])

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


class PartidaUV(UpdateView):
    model = Partida
    template_name = "contabilidad/modal.html"
    fields = ["fecha","descripcion"]

    def get_context_data(self, **kwargs):
        context = super(PartidaUV,self).get_context_data(**kwargs)
        partida = Partida.objects.get(id=self.kwargs['pk'])
        context['direccion'] = 'cont:act_partida'
        context['titulo'] = f'Actualizar Partida {partida.descripcion} {partida.fecha}'
        context['parametro'] = self.kwargs['pk'] 
        context['actualizar'] = True 
        return context

    def get_success_url(self,**kwargs):
        libro = Partida.objects.get(id=self.kwargs['pk']).libro.id
        return reverse("cont:lista_partida",args=[libro,])


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
        initial['fecha_inicio'] = "{}".format(date(date.today().year, 1, 1).strftime("%dd/%mm/%yy")) if  not Empresa.objects.get(id=self.kwargs['pk']).periodos.exists() else "01/01/{}".format(str(Empresa.objects.get(id=self.kwargs['pk']).periodos.order_by("-ano")[0].ano+1)[-2:])
        initial['fecha_fin'] = "{}".format(date(date.today().year, 12, 31).strftime("%dd/%mm/%yy")) if  not Empresa.objects.get(id=self.kwargs['pk']).periodos.exists() else "31/12/{}".format(str(Empresa.objects.get(id=self.kwargs['pk']).periodos.order_by("-ano")[0].ano+1)[-2:])
        initial["ano"] = "{}".format(date.today().year) if  not Empresa.objects.get(id=self.kwargs['pk']).periodos.exists() else Empresa.objects.get(id=self.kwargs['pk']).periodos.order_by("-ano")[0].ano +1
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
