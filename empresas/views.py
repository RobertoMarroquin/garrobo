#Django Libs
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView, TemplateView
from django.http import HttpResponse, FileResponse,HttpResponseRedirect
#Self Libs
from .models import Empresa
from .forms import EmpresaForm

#CreateViews

class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresas"] = Empresa.objects.all()
        return context
    

class EmpresaCV(CreateView):
    model = Empresa
    template_name = "empresas/modal.html"
    form_class = EmpresaForm

    def get_success_url(self,**kwargs):
        return reverse("home")

    def get_context_data(self, **kwargs):
        context = super(EmpresaCV,self).get_context_data(**kwargs)
        context['direccion'] = 'emp:nueva_empresa'
        context['titulo'] = 'Crear Empresa'
        return context
    
    def get_initial(self, **kwargs):
        initial = super(EmpresaCV,self).get_initial()
        return initial



class EmpresaUV(UpdateView):
    model = Empresa
    template_name = "empresas/modal.html"
    fields = [
        "razon_social",
        "direccion",
        "giro1",
        "giro2",
        "giro3",
        "telefono",
        "contabilidad",
    ]

    def get_context_data(self, **kwargs):
        context = super(EmpresaUV,self).get_context_data(**kwargs)
        registro = Empresa.objects.get(id=self.kwargs['pk']).num_registro
        context['direccion'] = 'emp:act_empresa'
        context['titulo'] = f'Actualizar Empresa {registro}'
        context['parametro'] = self.kwargs['pk'] 
        context['actualizar'] = True 
        return context

    def get_success_url(self,**kwargs):
        return reverse("home")
        #57588994