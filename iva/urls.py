from django.urls import path
from django.urls.conf import include
from .views  import *

app_name = "iva"

urlpatterns = [
    #---------------------------------------------------------------------------#
    #--------------------------------Libro--------------------------------------#    
    path('nuevo/libro/<int:empresa>/<int:tipo>/', LibroCV.as_view(), name='nuevo_libro'),
    path("libros/<int:empresa>/<int:tipo>/", LibroLV.as_view(), name="lista_libro"),
    #---------------------------------------------------------------------------#
    #--------------------------------Factura------------------------------------# 
    path("libro/<int:libro>/cons_final/", FacturaCFCV.as_view(), name="nueva_fcf"),
    path("libro/<int:libro>/contribuyente/", FacturaCtCV.as_view(), name="nueva_fct"),
    path("libro/<int:libro>/compra/", FacturaCmCV.as_view(), name="nueva_fcm"),
    #---------------------------------------------------------------------------#
    #--------------------------------Empresa------------------------------------# 
    path("nueva/empresa/", EmpresaCV.as_view(), name="nueva_empresa"), 
    path("empresa/<slug:nReg>/", EmpresaDetail.as_view(), name="detalle"),  
    #---------------------------------------------------------------------------#
    #--------------------------------Cliente------------------------------------# 
    path("iva/detalle/empresa/<int:pk>/", EmpresaDV.as_view(), name="detalle_cliente"),
    #---------------------------------------------------------------------------#
    #------------------------------Exportacion----------------------------------# 
    path("libro/<int:id_libro>/<int:tipo>/", ExportarView.as_view(), name="export"),

]
