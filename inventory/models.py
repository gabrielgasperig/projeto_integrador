from django.db import models
from django.conf import settings

class Asset(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome do Ativo")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="Data de Compra")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Preço de Compra")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_assets', verbose_name="Atribuído a")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Hardware(Asset):
    serial_number = models.CharField(max_length=100, unique=True, verbose_name="Número de Série")
    model = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fabricante")

    class Meta:
        verbose_name = "Hardware"
        verbose_name_plural = "Hardwares"

class Software(Asset):
    license_key = models.CharField(max_length=100, unique=True, verbose_name="Chave de Licença")
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name="Versão")
    expiration_date = models.DateField(blank=True, null=True, verbose_name="Data de Expiração")

    class Meta:
        verbose_name = "Software"
        verbose_name_plural = "Softwares"

class Subscription(Asset):
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(verbose_name="Data de Fim")
    renewal_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Custo de Renovação")

    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"