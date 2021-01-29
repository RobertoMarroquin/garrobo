from django.urls import path
from django.urls.conf import include
from .views  import *

app_name= 'cont'

urlpatterns = [
    #---------------------------------------------------------------------------------#
    #------------------------------------periodo--------------------------------------#
    path("nuevo/periodo/<int:pk>/", PeriodoCV.as_view(), name="nuevo_periodo"),
    path("empresa/<int:emp>/periodos/", PeriodoL.as_view(), name="lista_periodo"),
    path("cierre/<int:id_periodo>", Cierre.as_view(), name="cierre"),#cierre contable y exportacion de balance general
    #---------------------------------------------------------------------------------#
    #-------------------------------------libro---------------------------------------#
    path("nuevo/libro/<int:pk>/", LibroCV.as_view(), name="nuevo_libro"),
    path("empresa/periodo/<int:periodo>/", LibroLV.as_view(), name="lista_libro"),
    #---------------------------------------------------------------------------------#
    #------------------------------------Partida--------------------------------------#
    path("nueva/partida/<int:libro>/", PartidaCV.as_view(), name="nueva_partida"),
    path("empresa/periodo/libro/<int:libro>/", PartidaLV.as_view(), name="lista_partida"),
    path("actualizar/partida/<int:pk>", PartidaUV.as_view(), name="act_partida"),
    #----------------------------------------------------------------------------------#
    #-----------------------------------Movimiento-------------------------------------#
    path("empresa/periodo/libro/partida/<int:partida>/", MovimientoCV.as_view(), name="movimientos"),
    path("actualizar/movimiento<int:pk>", MovimientoUV.as_view(), name="act_movimiento"),
    path("borrar/movimiento/<int:pk>", MovimientoDV.as_view(), name="del_movimiento"),
    #----------------------------------------------------------------------------------#
    #------------------------------------Catalogo--------------------------------------#
    path("nuevo/catalogo/<int:empresa>/", CatalogoCV.as_view(), name="nuevo_catalogo"),
    path("empresa/<int:pk>/catalogo/", CatalogoD.as_view(), name="detalle_catalogo"),
    #----------------------------------------------------------------------------------#
    #------------------------------------Subcuenta-------------------------------------#
    path("actualizar/subcuenta/<int:pk>", SubCuentaUV.as_view(), name="act_subcuenta"),
    path("nueva/subcuenta/<int:catalogo>", SubCuentaCV.as_view(), name="nueva_subcuenta"),
    #----------------------------------------------------------------------------------#
    #-----------------------------------Exportacion------------------------------------#
    path("auxiliar/<int:id_libro>", Auxiliar.as_view(), name="auxiliar"),
    path("diario_mayor/<int:id_libro>", DiarioMayorView.as_view(), name="diario"),
    path("libro_mayor/<int:id_libro>", LibroMayorView.as_view(), name="mayor"),
    #----------------------------------------------------------------------------------#
    #----------------------------------------------------------------------------------#
]
