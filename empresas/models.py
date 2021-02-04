from django.db import models

# Create your models here.

class Empresa(models.Model):
    nombre = models.CharField('Nombre', max_length=200)
    razon_social = models.CharField('Razon Social', max_length=200, blank=True, null=True)
    num_registro = models.CharField(("Registro"), max_length=12,unique=True)
    nit = models.CharField("NIT", max_length=17, unique=True)
    direccion = models.CharField(("Direccion"), max_length=250,blank=True, null=True)
    giro1 = models.CharField(("Actividad Economica 1"), max_length=200, blank=True, null=True)
    giro2 = models.CharField(("Actividad Economica 2"), max_length=200, blank=True, null=True)
    giro3 = models.CharField(("Actividad Economica 3"), max_length=200, blank=True, null=True)
    telefono = models.CharField(("Telefono"), max_length=50, blank=True, null=True)
    contabilidad = models.BooleanField(("Contabilidad"),default=False)
    creado = models.DateTimeField("Creado", auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ["nombre",]

    def __str__(self):
        return f"{self.num_registro} | {self.nombre}"
