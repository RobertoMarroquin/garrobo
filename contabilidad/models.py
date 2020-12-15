#django libs
from django.contrib.admin.options import TabularInline
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
#self libs
from empresas.models import Empresa

class Periodo(models.Model):
    """Periodo Contable comprendido generalmente por un año fiscal."""
    fecha_inicio = models.DateField(("Inicio de Periodo"), auto_now=False, auto_now_add=False)
    fecha_fin = models.DateField(("Fin de Periodo"), auto_now=False, auto_now_add=False)
    ano = models.IntegerField(("Año"),default=2020,validators=[MaxValueValidator(2100),MinValueValidator(2010)])
    empresa = models.ForeignKey('empresas.Empresa', related_name='periodos', on_delete=models.CASCADE)
    creado = models.DateField(("Creado"), auto_now=False, auto_now_add=True)
    class Meta:
        """Meta definition for Periodo."""

        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'

    def __str__(self):
        return f'{self.ano} {self.empresa}'

    
class Catalogo(models.Model):
    """Catalogo de cuentas contables de Empresa."""
    empresa = models.OneToOneField('empresas.Empresa', verbose_name=("Empresa"), related_name='catalogo', on_delete=models.CASCADE)
    creado = models.DateField(("Creado"), auto_now=False, auto_now_add=True)
    class Meta:
        verbose_name = 'Catalogo'
        verbose_name_plural = 'Catalogos'

    def __str__(self):
        return f'{self.empresa}'


class Cuenta(models.Model):
    """Cuentas Principales del Catalogo contable."""
    catalogo = models.ForeignKey("contabilidad.Catalogo", related_name="cuentasp",verbose_name=("Catalogo de Cuentas"), on_delete=models.CASCADE)
    codigo = models.CharField(("Codigo"), max_length=2)    
    nombre = models.CharField(("Nombre"), max_length=150)
    creado = models.DateTimeField(("Creado"),auto_now=False, auto_now_add=True)
    saldo = models.FloatField("Saldo",default=0.00)
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ("catalogo","codigo")

    def __str__(self):
        return f"{self.codigo}"


class SubCuenta(models.Model):
    """Subcuentas del catalogo Contable."""
    catalogo = models.ForeignKey("contabilidad.Catalogo", related_name="subcuentas", verbose_name=("Catalogo de Cuentas"), on_delete=models.CASCADE)
    codigo = models.CharField(("Codigo"), max_length=12)    
    nombre = models.CharField(("Nombre"), max_length=150)
    cuenta_padre = models.ForeignKey('contabilidad.SubCuenta',related_name="subcuentas", verbose_name=("Cuenta Padre"),on_delete=models.CASCADE,blank=True, null=True)
    cuenta_principal = models.ForeignKey("contabilidad.Cuenta",related_name="subcuentasp", verbose_name=("Cuenta Principal"), on_delete=models.CASCADE,blank=True, null=True)
    creado = models.DateTimeField(("Creado"),auto_now=False, auto_now_add=True)
    saldo = models.FloatField("Saldo", default=0.00)
    es_mayor = models.BooleanField(("Es Cuenta de Mayor"), default=False)
    class Meta:
        verbose_name = 'SubCuenta'
        verbose_name_plural = 'SubCuentas'
        ordering = ("catalogo","codigo")
    def __str__(self):
        return f'{self.codigo}||{self.nombre}'


meses = ((1,"Enero"),(2,"Febrero"),(3,"Marzo"),(4,"Abril"),(5,"Mayo"),(6,"Junio"),
         (7,"Julio"),(8,"Agosto"),(9,"Septiembre"),(10,"Octubre"),(11,"Noviembre"),(12,"Diciembre"))
class Libro(models.Model):
    """Libro de partidas contables."""
    periodo = models.ForeignKey("contabilidad.Periodo", verbose_name=("Periodo"),related_name="libros", on_delete=models.CASCADE)
    mes = models.IntegerField(("Mes"), choices=meses)
    creado = models.DateTimeField(("Creado"),auto_now=False, auto_now_add=True)
    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'

    def __str__(self):
        return f'{self.get_mes_display()} {self.periodo.ano} {self.periodo.empresa.num_registro}'


class Partida(models.Model):
    """Partidas contables de los libros mayores."""
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    libro = models.ForeignKey('contabilidad.Libro', related_name='partidas', on_delete=models.CASCADE)
    descripcion = models.CharField(("Descripcion"), max_length=200,blank=True, null=True, default="Movimientos diarios")
    creado = models.DateTimeField(("Creado"),auto_now=False, auto_now_add=True)
    class Meta:
        verbose_name = 'Partida' 
        verbose_name_plural = 'Partidas'
        ordering = ['libro','fecha']

    def __str__(self):
        return f'{self.fecha}'


class Movimiento(models.Model):
    """Moviemientos transaccionales  de partidas."""
    partida = models.ForeignKey("contabilidad.Partida", verbose_name=("Partida"),related_name="movimientos", on_delete=models.CASCADE)
    monto_deber = models.FloatField(("Monto Deudor"), blank=True, null=True,default=0.00)
    monto_haber = models.FloatField(("Monto Acreedor"), blank=True, null=True,default=0.00)
    cuenta = models.ForeignKey('contabilidad.Subcuenta',verbose_name="Cuenta", related_name='movimientos', on_delete=models.CASCADE)
    descripcion = models.CharField(("Descripcion"), max_length=200)
    creado = models.DateTimeField(("Creado"),auto_now=False, auto_now_add=True)
    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'

    def __str__(self):
        """Unicode representation of Movimiento."""
        if self.monto_deber or self.monto_deber > 0.00:
            return f"{self.cuenta} - {self.monto_deber} D"
        elif self.monto_haber or self.monto_haber > 0.00:
            return f"{self.cuenta} - {self.monto_haber} H"
        else : return f"{self.cuenta}"

