from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    # models.py
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.position}"