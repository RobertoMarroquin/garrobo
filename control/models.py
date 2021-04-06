from django.db import models
from empresas.models import Empresa
# Create your models here.

class Talonario(models.Model):
    empresa = models.ForeignKey('empresas.Empresa', related_name='talonarios', on_delete=models.CASCADE)
    ano = models.IntegerField(("Año"))

    class Meta:
        verbose_name = 'Talonario'
        verbose_name_plural = 'Talonarios'

    def __str__(self):
        return f'{self.empresa.nombre}-{self.ano}'

meses = ((1,"Enero"),(2,"Febrero"),(3,"Marzo"),(4,"Abril"),(5,"Mayo"),(6,"Junio"),
         (7,"Julio"),(8,"Agosto"),(9,"Septiembre"),(10,"Octubre"),(11,"Noviembre"),(12,"Diciembre"))


class Mensualidad(models.Model):
    talonario = models.ForeignKey("control.Talonario", verbose_name=("Talonario"),related_name="mensualidades", on_delete=models.CASCADE)
    mes = models.IntegerField(("Mes"), choices =meses)

    class Meta:
        verbose_name = ("Mensualidad")
        verbose_name_plural = ("Mensualidads")

    def __str__(self):
        return f"{self.get_mes_display()}-{self.talonario}"


class Cobro(models.Model):
    descripcion = models.TextField("Descripcion", default="Mensualidad")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    iva =  models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(("Estado"))
    cancelado = models.BooleanField(("Cancelado"))
    mensualidad = models.ForeignKey(Mensualidad,related_name="cobros", on_delete=models.CASCADE)
    fecha_acordada_pago = models.DateField(("Fecha Acordada de pago"), auto_now=False, auto_now_add=False)
    fecha_real_pago = models.DateField(("Fecha De Pago"), auto_now=False, auto_now_add=False)
    
    def __str__(self):
        return f'{self.descripcion}:{self.monto}'

 