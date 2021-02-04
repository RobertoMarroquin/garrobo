from django.db import models
from empresas.models import Empresa


class Locacion(models.Model):
    nombre = models.CharField(("Nombre"), max_length=200)
    direccion = models.TextField(("Direccion"))
    creado = models.DateTimeField(("Creado"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = ("Locacion")
        verbose_name_plural = ("Locaciones")

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    codigo = models.CharField(("Codigo"), max_length=50)
    nombre = models.CharField(("Nombre"), max_length=50) 
    creado = models.DateTimeField(("Creado"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = ("Estado")
        verbose_name_plural = ("Estados")

    def __str__(self):
        return self.name


class CatalogoProducto(models.Model):
    empresa = models.OneToOneField("empresas.Empresa", related_name="catalogo_productos", verbose_name=("Empresa"), on_delete=models.CASCADE)
    creado = models.DateTimeField(("Creado"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = ("Catalogo")
        verbose_name_plural = ("Catalogos")

    def __str__(self):
        return self.empresa


class Producto(models.Model):
    codigo = models.CharField(("Codigo"), max_length=50)
    nombre = models.CharField(("Nombre"), max_length=150)
    catalogo = models.ForeignKey("inventario.Catalogo", verbose_name=("Catalogo"),related_name="produtos",on_delete=models.CASCADE)
    creado = models.DateTimeField(("Creado"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre


class DetalleProducto(models.Model):
    producto = models.ForeignKey('inventario.Producto', related_name='detalles', verbose_name=("Producto") ,on_delete=models.CASCADE)
    ubicacion = models.CharField(("inventario.Ubicacion"), max_length=50, blank=True, null=True)
    existencia = models.IntegerField(("Existencias"), blank=True, null=True)
    fecha_entrada = models.DateField(("Fecha de entrada"), auto_now=False, auto_now_add=False,blank=True, null=True)
    perecedero = models.BooleanField("Perecedero")
    fecha_caducidad = models.DateField(("Fecha de Caducidad"), auto_now=False, auto_now_add=False,blank=True, null=True)
    creado = models.DateTimeField(("Creado"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = ("Detalle Producto")
        verbose_name_plural = ("Detalle de Productos")

    def __str__(self):
        return f"{self.producto} {self.ubicacion} {self.cantidad}"

    