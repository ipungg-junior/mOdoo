from django.db import models
from django.contrib.auth.models import User


class MasterPosition(models.Model):
    name = models.CharField(max_length=30, unique=True, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    position = models.ForeignKey(MasterPosition, on_delete=models.CASCADE, null=True, blank=True)
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.position.name if self.position else 'No Position'}"