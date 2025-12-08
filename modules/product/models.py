from django.db import models
from django.contrib.auth.models import User
from engine.models import MasterDatabase

class ChoosenDatabase(models.Model):
    name = models.ForeignKey(MasterDatabase, on_delete=models.SET_NULL, null=True, blank=True)


class ChoosenDatabaseConfig(models.Model):
    db_name = models.ForeignKey(ChoosenDatabase, on_delete=models.SET_NULL, null=True, blank=True)
    config_name = models.CharField(max_length=40)
    config_value = models.TextField()

    def __str__(self):
        return f"{self.config_name} - {self.master_database.name}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name
    
    
class Transaction(models.Model):
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    STATUS_CHOICES = [
        ('lunas', 'Lunas'),
        ('belum_lunas', 'Belum Lunas'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='belum_lunas')
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction of {self.product.name} by {self.user.username} on {self.transaction_date}"
    
    
class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=60)
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} at {self.price_per_item} each"