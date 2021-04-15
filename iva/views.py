#Django Libs
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View, CreateView, DeleteView, UpdateView, DetailView, ListView, TemplateView
from django.db.models import Sum
from django.core.serializers import serialize


#Self Libs
from .forms import (ComprasForm, ConsumidorFinalForm, 
                    ContribuyenteForm, EmpresaF, 
                    LibroForm, FacturaConsumidorF, 
                    FacturaComprasF, FacturaContribuyenteF)
from .models import *
from empresas.models import Empresa as Cliente
from .export import *

#Factura CF
class FacturaCFCV(CreateView):
    model = FacturaCF
    template_name = "iva/lfcf.html"
    form_class = ConsumidorFinalForm
    def get_context_data(self, **kwargs):
        facturas = Libro.objects.get(id=self.kwargs["libro"]).facturacf
        context = super(FacturaCFCV,self).get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(id=self.kwargs["libro"])
        context['direccion'] = 'cont:nueva_fcf'
        context['titulo'] = 'Crear Factura Consumidor Final'
        context["parametro"] = self.kwargs['libro']
        context["totales"] = [
            facturas.all().aggregate(total_exento=Sum('exento'))["total_exento"],
            facturas.all().aggregate(total_local=Sum('locales'))["total_local"],
            facturas.all().aggregate(total_exportacion=Sum('exportaciones'))["total_exportacion"],
            facturas.all().aggregate(total_ventasNSujetas=Sum('ventasNSujetas'))["total_ventasNSujetas"],
            facturas.all().aggregate(total_venta=Sum('ventaTotal'))["total_venta"],
            facturas.all().aggregate(total_ventaCtaTerceros=Sum('ventaCtaTerceros'))["total_ventaCtaTerceros"],
        ]
        return context

    def get_initial(self, **kwargs):
        initial = super(FacturaCFCV,self).get_initial()
        initial["libro"] = Libro.objects.get(id=self.kwargs["libro"]).id
        return initial

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:nueva_fcf",args=[libro.id])


#Factura Ct
class FacturaCtCV(CreateView):
    model = FacturaCt
    template_name = "iva/lfct.html"
    form_class = ContribuyenteForm

    def get_context_data(self, **kwargs):
        facturas = Libro.objects.get(id=self.kwargs["libro"]).facturact
        context = super(FacturaCtCV,self).get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(id=self.kwargs["libro"])
        context['direccion'] = 'cont:nueva_fct'
        context['titulo'] = 'Crear Factura Contribuyente'
        context["parametro"] = self.kwargs['libro']
        context["totales"] = [
            facturas.all().aggregate(total=Sum('venExentas'))["total"],
            facturas.all().aggregate(total=Sum('venGravadas'))["total"],
            facturas.all().aggregate(total=Sum('ventasNSujetas'))["total"],
            facturas.all().aggregate(total=Sum('ivaDebFiscal'))["total"],
            facturas.all().aggregate(total=Sum('vtVentas'))["total"],
            facturas.all().aggregate(total=Sum('vtIVA'))["total"],
            facturas.all().aggregate(total=Sum('ivaRetenido'))["total"],
            facturas.all().aggregate(total=Sum('total'))["total"],
        ]
        return context

    def get_initial(self, **kwargs):
        initial = super(FacturaCtCV,self).get_initial()
        initial["libro"] = Libro.objects.get(id=self.kwargs["libro"]).id
        return initial

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:nueva_fct",args=[libro.id])


#Factura Cm
class FacturaCmCV(CreateView):
    model = FacturaCm
    template_name = "iva/lfcm.html"
    form_class = ComprasForm

    def get_context_data(self, **kwargs):
        facturas = Libro.objects.get(id=self.kwargs["libro"]).facturacm
        context = super(FacturaCmCV,self).get_context_data(**kwargs)
        context["libro"] = Libro.objects.get(id=self.kwargs["libro"])
        context['direccion'] = 'cont:nueva_fcm'
        context['titulo'] = 'Crear Factura Compra'
        context["parametro"] = self.kwargs['libro']
        context["totales"] = [
            facturas.all().aggregate(total=Sum('cExenteInterna'))["total"],
            facturas.all().aggregate(total=Sum('cExenteImportaciones'))["total"],
            facturas.all().aggregate(total=Sum('cGravadaInterna'))["total"],
            facturas.all().aggregate(total=Sum('cGravadaImportaciones'))["total"],
            facturas.all().aggregate(total=Sum('comprasNSujetas'))["total"],
            facturas.all().aggregate(total=Sum('ivaCdtoFiscal'))["total"],
            facturas.all().aggregate(total=Sum('totalCompra'))["total"],
            facturas.all().aggregate(total=Sum('retencionPretencion'))["total"],
            facturas.all().aggregate(total=Sum('anticipoCtaIva'))["total"],
            facturas.all().aggregate(total=Sum('ivaTerceros'))["total"],
        ]
        return context

    def get_initial(self, **kwargs):
        initial = super(FacturaCmCV,self).get_initial()
        initial["libro"] = Libro.objects.get(id=self.kwargs["libro"]).id
        return initial

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:nueva_fcm",args=[libro.id])


#Libros vistas
class LibroCV(CreateView):
    model = Libro
    template_name = "iva/modal.html"
    form_class = LibroForm

    def get_context_data(self, **kwargs):
        context = super(LibroCV,self).get_context_data(**kwargs)
        context["empresa"] = Cliente.objects.get(id=self.kwargs["empresa"])
        context['direccion'] = 'iva:nuevo_libro'
        context['titulo'] = 'Crear Libro'
        context["tipo"] = self.kwargs["tipo"]
        context["parametro"] = self.kwargs['empresa']
        context["parametro2"] = self.kwargs['tipo']

        return context

    def get_initial(self, **kwargs):
        initial = super(LibroCV,self).get_initial()
        initial["cliente"] = Cliente.objects.get(id=self.kwargs["empresa"]).id
        initial["tipo"] = self.kwargs["tipo"]
        return initial

    def get_success_url(self,**kwargs):
        return reverse("iva:lista_libro",args=[self.kwargs["empresa"],self.kwargs["tipo"]])


class LibroLV(ListView):
    model = Libro
    template_name = "iva/llibro.html"
    context_object_name = 'libros'

    def get_context_data(self, **kwargs):
        context = super(LibroLV,self).get_context_data(**kwargs)
        context["cliente"] = Cliente.objects.get(id=self.kwargs['empresa'])
        context["tipo"] = self.kwargs["tipo"]
        return context

    def get_queryset(self):
        queryset = super(LibroLV, self).get_queryset()
        queryset = queryset.filter(cliente__id = self.kwargs['empresa'],tipo=self.kwargs["tipo"]).order_by('ano','mes')
        return queryset


class EmpresaDV(DetailView):
    model = Cliente
    template_name = "iva/detalle_cliente.html"
    context_object_name = "cliente"


#Empresa Vistas
class EmpresaCV(CreateView):
    model = Empresa
    template_name = "iva/empresa.html"
    form_class = EmpresaF

    def get_context_data(self, **kwargs):
        context = super(EmpresaCV,self).get_context_data(**kwargs)
        context['direccion'] = 'cont:nuevo_empresa'
        context['titulo'] = 'Crear Empresa'
        return context

class EmpresaCV2(CreateView):
    model = Empresa
    template_name = "iva/empresa.html"
    form_class = EmpresaF

    def get_context_data(self, **kwargs):
        context = super(EmpresaCV,self).get_context_data(**kwargs)
        context['libro'] = self.kwargs["libro"]
        context['direccion'] = 'cont:nuevo_empresa'
        context['titulo'] = 'Crear Empresa'
        return context
    
    def get_success_url(self,**kwargs):
        libro = Libro.objects.get(id=self.kwargs["libro"])
        direccion = ""
        if libro.tipo == 1:
            direccion = reverse("iva:haciendacf",args=[self.kwargs["libro"],])
        elif libro.tipo == 2:
            direccion = reverse("iva:haciendact",args=[self.kwargs["libro"],])
        else:
            direccion = reverse("iva:haciendacm",args=[self.kwargs["libro"],])
        return direccion
    


class EmpresaDetail(DetailView):
    model = Empresa
    template_name='empresaJson.html'
    def get(self,request,*args, **kwarg ):
        empresa = Empresa.objects.get(nRegistro = self.kwargs['nReg'])
        empresa = serialize('json',[empresa,])
        return HttpResponse(empresa,'application/json')

#Exportacion
class ExportarView(View):
    def get(self, request, *args, **kwargs):
        tipo = self.kwargs.get('tipo')
        id_libro = self.kwargs.get('id_libro')
        libro = Libro.objects.get(id=id_libro)
        if tipo == 1:
            tipol = "Consumidor"
            libroEx = export_libroCF(id_libro)
        elif tipo == 2:
            tipol = "Contibuyente"
            libroEx = export_libroct(id_libro)
        elif tipo == 3:
            tipol = "Compras"
            libroEx = export_librocm(id_libro)
        # create the HttpResponse object ...
        response = FileResponse(open(libroEx, 'rb'))
        return response


#Exportciones de Libros de IVA Segun formato de Hacienda
class IvaLibros(View):
    def get(self, request, *args, **kwargs):
        libro = Libro.objects.get(id=self.kwargs["libro"])
        direccion = formato_hacienda(libro.id)
        response = FileResponse(open(direccion, 'rb'))
        return response


class IvaInterno(View):
    def get(self, request, *args, **kwargs):
        libro = Libro.objects.get(id=self.kwargs["libro"])
        direccion = formato_interno(libro.id)
        response = FileResponse(open(direccion, 'rb'))
        return response

#Iva Libros Pantallas de usuario y formularios
#Contribuyente
class FacturasContribuyenteCV(CreateView):
    model = FacturaCt
    template_name = "iva/haciendact.html"
    form_class = FacturaContribuyenteF

    def form_valid(self, form):
        form.instance.libro_id = self.kwargs["libro"]
        valid_data = super(FacturasContribuyenteCV, self).form_valid(form)
        return valid_data

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:haciendact",args=[libro.id])

    def get_context_data(self, **kwargs):
        context = super(FacturasContribuyenteCV,self).get_context_data(**kwargs)
        libro = Libro.objects.get(id=self.kwargs["libro"])
        context["libro"] = Libro.objects.get(id=libro.id)
        context["facturas"] = FacturaCt.objects.filter(libro=libro.id)
        return context
    
    def get_initial(self, **kwargs):
        initial = super(FacturasContribuyenteCV,self).get_initial()
        libro = Libro.objects.get(id=self.kwargs["libro"])

        if libro.facturact.last() :
            factura = libro.facturact.last()
            initial["numeroResolucion"] = factura.numeroResolucion
            initial["numeroSerie"] = factura.numeroSerie
        else:
            initial["numeroResolucion"] = ""
            initial["numeroSerie"] = ""

        return initial


#Consumidor Final
class FacturasConsudmidorCV(CreateView):
    model = FacturaCF
    template_name = "iva/haciendacf.html"
    form_class = FacturaConsumidorF
    
    def form_valid(self, form):
        form.instance.libro_id = self.kwargs["libro"]
        valid_data = super(FacturasConsudmidorCV, self).form_valid(form)
        return valid_data

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:haciendacf",args=[libro.id])

    def get_context_data(self, **kwargs):
        context = super(FacturasConsudmidorCV,self).get_context_data(**kwargs)
        libro = Libro.objects.get(id=self.kwargs["libro"])
        context["libro"] = Libro.objects.get(id=libro.id)
        context["facturas"] = FacturaCF.objects.filter(libro=libro.id)
        return context
    
    def get_initial(self, **kwargs):
        initial = super(FacturasConsudmidorCV,self).get_initial()
        libro = Libro.objects.get(id=self.kwargs["libro"])
        
        if libro.facturacf.last() :
            factura = libro.facturacf.last()
            initial["numeroResolucion"] = factura.numeroResolucion
            initial["numeroSerie"] = factura.numeroSerie
        else:
            initial["numeroResolucion"] = ""
            initial["numeroSerie"] = ""

        return initial
    

#Compras
class FacturaComprasCV(CreateView):
    model = FacturaCm
    template_name = "iva/haciendacm.html"
    form_class = FacturaComprasF

    def form_valid(self, form):
        form.instance.libro_id = self.kwargs["libro"]
        valid_data = super(FacturaComprasCV, self).form_valid(form)
        return valid_data

    def get_success_url(self,**kwargs):
        libro=Libro.objects.get(id=self.kwargs["libro"])
        return reverse("iva:haciendacm",args=[libro.id])

    def get_context_data(self, **kwargs):
        context = super(FacturaComprasCV,self).get_context_data(**kwargs)
        libro = Libro.objects.get(id=self.kwargs["libro"])
        context["libro"] = Libro.objects.get(id=libro.id)
        context["facturas"] = FacturaCm.objects.filter(libro=libro.id)
        return context
#----------------------------------------------#
