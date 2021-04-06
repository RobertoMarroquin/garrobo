from django.urls import path
from django.urls.conf import include
from .views  import *

app_name = "control"

urlpatterns = [
    ##---------------------------------Talonario--------------------------------##
    path("empresa/<int:empresa>/talonarios/", TalonarioLV.as_view(), name="talonarioLista"),
    path("nuevo/talonario/<int:empresa>/", TalonarioCV.as_view(), name="nuevoTalonario"),
    ##--------------------------------Mensualidad-------------------------------##
    path("empresa/talonario/<int:talonario>/", MensualidadLV.as_view(), name="mensualidades"),
    path("nuevo/mensualidad/<int:talonario>/", MensualidadCV.as_view(), name="nueva_mensualidad"),
    ##-----------------------------------Cobro----------------------------------##
    path("empresa/talonario/mesualidad/<int:mensualidad>/", CobroLV.as_view(), name=""),
    path("nuevo/cobro/<int:mensualidad>", CobroCV.as_view(), name="nuevo_cobro"),
    
]
