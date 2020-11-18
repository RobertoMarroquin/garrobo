from django.db import models

# Create your models here.
class Libro(models.Model):
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=True)
    mes = models.IntegerField(("Mes"),choices = (
        (1,"Enero"),(2,"Febrero"),(3,"Marzo"),(4,"Abril"),
        (5,"Mayo"),(6,"Junio"),(7,"Julio"),(8,"Agosto"),
        (9,"Septiembre"),(10,"Octubre"),(11,"Noviembre"),(12,"Diciembre"),
    ))
    ano = models.IntegerField(("Ano"))
    tipo = models.IntegerField(("Tipo de Libro"))
    cliente = models.ForeignKey("empresas.Empresa", verbose_name=("Cliente"), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} : {self.cliente} : Mes {self.mes}, Ano {self.ano} : {self.tipo}"


class Empresa(models.Model):
    nRegistro = models.CharField(("Numero de Regisro"),unique=True, max_length=12)
    nombre = models.CharField(("Nombre"), max_length=100)
    nit = models.CharField(("NIT"), max_length=18,blank=True, null=True)

    def __str__(self):
        return f"{self.nRegistro} {self.nombre}"


class FacturaConsumidorFinal(models.Model):
    correlativoInicial = models.IntegerField(("Correlativo Inicial"))
    correlativoFinal = models.IntegerField(("Correlativo Final"))
    fecha = models.DateField(("Fecha"),blank=True, null=True,auto_now=False, auto_now_add=False)
    exento = models.DecimalField(("Exento"),blank=True, null=True,max_digits=8, decimal_places=2)
    locales = models.DecimalField(("Locales"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventaTotal = models.DecimalField(("Venta Total"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventaCtaTerceros = models.DecimalField(("Venta Cta Terceros"),blank=True, null=True,max_digits=8, decimal_places=2)
    libro = models.ForeignKey("iva.Libro", verbose_name=("Libro"),blank=True, null=True, on_delete=models.CASCADE)
    exportaciones = models.DecimalField(("Exportaciones"),blank=True, null=True, max_digits=8, decimal_places=2)
    ventasNSujetas = models.DecimalField(("Ventas No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.fecha} : {self.correlativoInicial}" 


class FacturaContribuyente(models.Model):
    correlativo = models.IntegerField(("Correlativo"))
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    nComprobacion = models.IntegerField(("Numero de Comprobacion"),blank=True, null=True)
    serie = models.IntegerField(("Serie"),blank=True, null=True)
    corrIntUni = models.IntegerField(("Correlativo Interno Unico"),blank=True, null=True)
    contribuyente = models.ForeignKey("empresas.Empresa",blank=True, null=True, verbose_name=("Contribuyente"), on_delete=models.CASCADE)
    venExentas = models.DecimalField(("Ventas Exentas"),blank=True, null=True,max_digits=8, decimal_places=2)
    venGravadas = models.DecimalField(("Ventas Gravadas"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaDebFiscal = models.DecimalField(("IVA Debito Fiscal"),blank=True, null=True,max_digits=8, decimal_places=2)
    vtVentas = models.DecimalField("Ventas Terceros Ventas",blank=True, null=True,max_digits=8, decimal_places=2)
    vtIVA = models.DecimalField(("Ventas Terceros IVA"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaRetenido = models.DecimalField(("IVA Retenido"),blank=True, null=True,max_digits=8, decimal_places=2)
    total = models.DecimalField(("Total"),blank=True, null=True,max_digits=8, decimal_places=2)
    libro = models.ForeignKey("iva.Libro",blank=True, null=True, on_delete=models.CASCADE)
    ventasNSujetas = models.DecimalField(("Ventas No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.fecha} : {self.correlativo} : {self.libro}"
 

class FacturaCompras(models.Model):
    correlativo = models.IntegerField(("Correlativo"))
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    empresa  = models.ForeignKey("empresas.Empresa", on_delete=models.CASCADE,blank=True, null=True)
    cExenteInterna = models.DecimalField(("Compra Exenta Interna"),blank=True, null=True,max_digits=8, decimal_places=2)
    cExenteImportaciones = models.DecimalField(("Compra Exenta Importaciones"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaInterna = models.DecimalField(("Compra Gravada Interna"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaImportaciones = models.DecimalField(("Compra Gravada Importaciones"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaCdtoFiscal = models.DecimalField(("IVA Cdto Fiscal"),blank=True, null=True,max_digits=8, decimal_places=2)
    totalCompra = models.DecimalField(("Total Compra"),blank=True, null=True,max_digits=8, decimal_places=2)
    retencionPretencion = models.DecimalField(("Retencion Pretencion"),blank=True, null=True,max_digits=8, decimal_places=2)
    anticipoCtaIva =models.DecimalField(("Anticipo Cta IVA"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaTerceros = models.DecimalField(("Iva Terceros"),blank=True, null=True,max_digits=8, decimal_places=2)
    comprasNSujetas = models.DecimalField(("Compras No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2)
    libro = models.ForeignKey("iva.Libro", on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.fecha} : {self.correlativo} : {self.empresa}"
