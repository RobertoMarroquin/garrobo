from django.urls import path
from django.urls.conf import include
from .views  import *

app_name= 'cont'

urlpatterns = [
    #---------------------------------------------------------------------------------#
    #------------------------------------periodo--------------------------------------#
    path("nuevo/periodo/<int:pk>/", PeriodoCV.as_view(), name="nuevo_periodo"),
    path("empresa/<int:emp>/periodos/", PeriodoL.as_view(), name="lista_periodo"),
    #---------------------------------------------------------------------------------#
    #-------------------------------------libro---------------------------------------#
    path("nuevo/libro/<int:pk>/", LibroCV.as_view(), name="nuevo_libro"),
    path("empresa/periodo/<int:periodo>/", LibroLV.as_view(), name="lista_libro"),
    #---------------------------------------------------------------------------------#
    #------------------------------------Partida--------------------------------------#
    path("nueva/partida/<int:libro>/", PartidaCV.as_view(), name="nueva_partida"),
    path("empresa/periodo/libro/<int:libro>/", PartidaLV.as_view(), name="lista_partida"),

]
