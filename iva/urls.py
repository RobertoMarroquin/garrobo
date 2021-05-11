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
    path("nueva/empresa/<int:libro>", EmpresaCV.as_view(), name="nueva_empresa2"),
    path("empresa/<slug:nReg>/", EmpresaDetail.as_view(), name="detalle"), 
    #---------------------------------------------------------------------------#
    #--------------------------------Cliente------------------------------------# 
    path("iva/detalle/empresa/<int:pk>/", EmpresaDV.as_view(), name="detalle_cliente"),
    #---------------------------------------------------------------------------#
    #------------------------------Exportacion----------------------------------# 
    path("libro/<int:id_libro>/<int:tipo>/", ExportarView.as_view(), name="export"),
    path("libro/<int:libro>/", IvaLibros.as_view(), name="iva_hacienda"),
    path("libro/interno/<int:libro>/", IvaInterno.as_view(), name="iva_interno"),
    path("empresa/libro/anticipo/<int:libro>/", AnticipoCta.as_view(), name="anticipo"),
    #---------------------------------------------------------------------------#
    #---------------------------Facturas Hacienda-------------------------------# 
    path("empresa/libro/contribuyente/<int:libro>/", FacturasContribuyenteCV.as_view(), name="haciendact"),
    path("empresa/libro/consumidor/<int:libro>/", FacturasConsudmidorCV.as_view(), name="haciendacf"),
    path("empresa/libro/compras/<int:libro>/", FacturaComprasCV.as_view(), name="haciendacm"),
    path("empresa/libro/compras/retencion/<int:libro>/", RetencionCompraCV.as_view(), name="retencion"),
    
]
