from django.urls import path
from django.urls.conf import include
from .views  import *

app_name='emp'

urlpatterns = [
    path("nueva/empresa/", EmpresaCV.as_view(), name="nueva_empresa"),
    path("actualizar/empresa/<int:pk>", EmpresaUV.as_view(), name="act_empresa"),
]
