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
    tipo = models.IntegerField(("Tipo de Libro"),choices=((1,"Consumidor Final"),(2,"Contribuyente"),(3,"Compras")))
    cliente = models.ForeignKey("empresas.Empresa", related_name="libros", verbose_name=("Cliente"), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} : {self.cliente} : Mes {self.mes}, Ano {self.ano} : {self.tipo}"


class Empresa(models.Model):
    nRegistro = models.CharField(("Numero de Regisro"),unique=True, max_length=12)
    nombre = models.CharField(("Nombre"), max_length=100)
    nit = models.CharField(("NIT"), max_length=18,blank=True, null=True,default="")

    def __str__(self):
        return f"{self.nRegistro} {self.nombre}"


class FacturaCF(models.Model):
    fecha = models.DateField(("Fecha"),blank=True, null=True,auto_now=False, auto_now_add=False)
    claseDocumento = models.CharField("Clase de Documento",choices=(
        ("1","IMPRESO POR IMPRENTA O TIQUETES"),
        ("2","FORMULARIO UNICO")
    ),max_length=1,default="1",blank=True, null=True)
    tipoDocumento = models.CharField("Tipo de Documetno",choices=(
        ("01","FACTURA"),
        ("02","FACTURA DE VENTAS SIMPLIFICADAS"),
        ("10","TIQUETES DE MAQUINA REGISTRADORA"),
        ("11","FACTURA DE EXPORTACION"),
    ),max_length=2,default="01",blank=True, null=True)
    numeroResolucion = models.CharField("Numero de Resolucion",max_length=19,blank=True, null=True)
    numeroSerie = models.CharField("Numero de Serie de Documento",max_length=8,blank=True, null=True)
    numeroControlInternoDel = models.CharField("Numero de Control Interno (DEL)", max_length=8,blank=True, null=True,default="")
    numeroControlInternoAl = models.CharField("Numero de Control Interno (AL)", max_length=8,blank=True, null=True,default="")
    correlativoInicial = models.IntegerField(("NUMERO DE DOCUMENTO(DEL)"),blank=True, null=True)
    correlativoFinal = models.IntegerField(("NUMERO DE DOCUMENTO(AL)"),blank=True, null=True)
    numeroRegistradora = models.CharField("Numero de Maquina Registradora",default="",max_length=14,blank=True, null=True)
    exento = models.DecimalField(("Ventas Exentas"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventasInternasExentas = models.DecimalField(("Ventas Internas Exentas no Sujetas a Proporcionalidad"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventasNSujetas = models.DecimalField(("Ventas No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2)
    locales = models.DecimalField(("Ventas Gravadas Locales"),blank=True, null=True,max_digits=8, decimal_places=2)
    exportacionesCA = models.DecimalField(("Exportaciones Dentro del Area Centroamericana"),blank=True, null=True,max_digits=8, decimal_places=2)
    exportacionesNoCA = models.DecimalField(("Exportaciones Fuera del Area Centroamericana"),blank=True, null=True,max_digits=8, decimal_places=2)
    exportacionesServicios =  models.DecimalField(("Exportaciones de Servicios"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventasZonasFrancas = models.DecimalField(("Ventas a Zonas Francas y DPA(Tasa Cero)"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventaCtaTerceros = models.DecimalField(("Venta Cta Terceros No Domiciliados"),blank=True, null=True,max_digits=8, decimal_places=2)
    ventaTotal = models.DecimalField(("Venta Total"),blank=True, null=True,max_digits=8, decimal_places=2)

    libro = models.ForeignKey("iva.Libro",related_name="facturacf", verbose_name=("Libro"),blank=True, null=True, on_delete=models.CASCADE)
    exportaciones = models.DecimalField(("Exportaciones"),blank=True, null=True, max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.fecha} : {self.correlativoInicial}" 


class FacturaCt(models.Model):
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    claseDocumento = models.CharField("Clase de Documento",choices=(
        ("1","IMPRESO POR IMPRENTA O TIQUETES"),
        ("2","FORMULARIO UNICO")
    ),max_length=1,default="1",blank=True, null=True)
    tipoDocumento = models.CharField("Tipo de Documetno",choices=(
        ("03","COMPROBANTE DE CREDITO FISCAL"),
        ("05","NOTA DE CREDITO"),
        ("06","NOTA DE DEBITO")
    ),max_length=2,default="03",blank=True, null=True)
    numeroResolucion = models.CharField("Numero de Resolucion",max_length=19,blank=True, null=True)
    numeroSerie = models.CharField("Numero de Serie de Documento",max_length=8,blank=True, null=True)
    numeroDocumento = models.CharField("Numero de Documento", max_length=8,blank=True, null=True)
    numeroControlInterno = models.CharField("Numero de Control Interno", max_length=8,blank=True, null=True)
    contribuyente = models.ForeignKey("iva.Empresa",blank=True, null=True, verbose_name=("Contribuyente"), on_delete=models.CASCADE)
    venExentas = models.DecimalField(("Ventas Exentas"),blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    ventasNSujetas = models.DecimalField(("Ventas No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2,default=0.00)
    venGravadas = models.DecimalField(("Ventas Gravadas"),blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    ivaDebFiscal = models.DecimalField(("IVA Debito Fiscal"),blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    vtVentas = models.DecimalField("Ventas a Terceros no Domiciliados",blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    vtIVA = models.DecimalField(("Debito Fiscal Ventas a Terceros"),blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    total = models.DecimalField(("Total"),blank=True, null=True,max_digits=8, decimal_places=2,default=0.00)
    libro = models.ForeignKey("iva.Libro",related_name="facturact",blank=True, null=True, on_delete=models.CASCADE)

    serie = models.IntegerField(("Serie"),blank=True, null=True)
    correlativo = models.IntegerField(("Correlativo"),blank=True, null=True)
    nComprobacion = models.IntegerField(("Numero de Comprobacion"),blank=True, null=True)
    corrIntUni = models.IntegerField(("Correlativo Interno Unico"),blank=True, null=True)
    ivaRetenido = models.DecimalField(("IVA Retenido"),blank=True, null=True,max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.fecha} : {self.correlativo} : {self.libro}"
 

class FacturaCm(models.Model):
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    claseDocumento = models.CharField("Clase de Documento",choices=(
        ("1","IMPRESO POR IMPRENTA O TIQUETES"),
        ("2","FORMULARIO UNICO"),
        ("3","OTROS")
    ),max_length=1,default="1",blank=True, null=True)
    tipoDocumento = models.CharField("Tipo de Documetno",choices=(
        ("03","COMPROBANTE DE CREDITO FISCAL"),
        ("05","NOTA DE CREDITO"),
        ("06","NOTA DE DEBITO"),
        ("11","FACTURA DE EXPORTACION"),
        ("12","DECLARACION DE MERCANCIAS"),
        ("13","MANDAMIENTO DE INGRSO"),
    ),max_length=2,default="03",blank=True, null=True)
    numeroDocumento = models.CharField("Numero de Documento", max_length=50,blank=True, null=True)
    empresa  = models.ForeignKey("iva.Empresa", on_delete=models.CASCADE,blank=True, null=True)
    cExenteInterna = models.DecimalField(("Compras Internas Exentas y/o No Sujetas"),blank=True, null=True,max_digits=8, decimal_places=2)
    cExenteInternaciones = models.DecimalField(("Internaciones Exentas y/o No Sujetas"),blank=True, null=True,max_digits=8, decimal_places=2)
    cExenteImportaciones = models.DecimalField(("Importacion Exentas y/o No Sujetas"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaInterna = models.DecimalField(("Compras Internas Gravadas"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaInternaciones = models.DecimalField(("Internaciones Gravadas de Bienes"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaImportaciones = models.DecimalField(("Importaciones Gravadas de Bienes"),blank=True, null=True,max_digits=8, decimal_places=2)
    cGravadaImportacionesServicios = models.DecimalField(("Importaciones Gravadas de Servicios"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaCdtoFiscal = models.DecimalField(("Credito Fiscal"),blank=True, null=True,max_digits=8, decimal_places=2)
    totalCompra = models.DecimalField(("Total Compra"),blank=True, null=True,max_digits=8, decimal_places=2)
    numeroSerie =  models.CharField("Numero de Serie", max_length=14,blank=True, null=True, default="")
    
    correlativo = models.IntegerField(("Correlativo"),blank=True, null=True)
    retencionPretencion = models.DecimalField(("Retencion Pretencion"),blank=True, null=True,max_digits=8, decimal_places=2)
    anticipoCtaIva =models.DecimalField(("Anticipo Cta IVA"),blank=True, null=True,max_digits=8, decimal_places=2)
    ivaTerceros = models.DecimalField(("Iva Terceros"),blank=True, null=True,max_digits=8, decimal_places=2)
    comprasNSujetas = models.DecimalField(("Compras No Sujetas"),blank=True, null=True, max_digits=8, decimal_places=2)
    libro = models.ForeignKey("iva.Libro",related_name="facturacm", on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.fecha} : {self.correlativo} : {self.empresa}"


class RetencionCompra(models.Model):
    libro = models.ForeignKey("iva.Libro",related_name="retenciones", on_delete=models.CASCADE)
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=False)
    numeroDocumento = models.CharField("Numero de Documento", max_length=50,blank=True, null=True)
    numeroSerie =  models.CharField("Numero de Serie", max_length=14,blank=True, null=True, default="")
    retencion = models.DecimalField(("Retencion"), decimal_places=2, null=True, blank=True, max_digits=9)
    monto_sujeto = models.DecimalField(("Monto Sujeto"), decimal_places=2, null=True, blank=True, max_digits=9)
    empresa = models.ForeignKey("iva.Empresa",blank=True, null=True, verbose_name=("Empresa"), on_delete=models.CASCADE)
    def __str__(self):
            return f"{self.libro} Retenciones"

    class Meta:
        verbose_name = 'RetencionCompra'
        verbose_name_plural = 'Retenciones Compras'
