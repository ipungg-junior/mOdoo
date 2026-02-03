from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_installed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    
class TaxType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"
    
    
class Tax(models.Model):
    name = models.CharField(max_length=100)
    tax_type = models.ForeignKey(TaxType, on_delete=models.DO_NOTHING, null=True, blank=True)
    rate = models.SmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name}"