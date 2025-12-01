from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_installed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MasterDatabase(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class ModuleMasterDatabase(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    master_database = models.ForeignKey(MasterDatabase, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.module.name} - {self.master_database.name}"