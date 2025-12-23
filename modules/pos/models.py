from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from engine.utils import format_rupiah


class PoSTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet', 'E-Wallet'),
    ]

    transaction_number = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, blank=True, null=True)

    # Transaction amounts
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    cash_received = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Status and timestamps
    is_completed = models.BooleanField(default=False)
    transaction_date = models.DateTimeField(default=timezone.now)

    # Accounting integration
    accounting_journal_id = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PoS Transaction #{self.transaction_number}"

    def calculate_totals(self):
        """Calculate subtotal, tax, and grand total"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.grand_total = self.subtotal - self.discount_amount + self.tax_amount
        self.save()

    def generate_transaction_number(self):
        """Generate unique transaction number"""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        # Get count of transactions for today
        today_count = PoSTransaction.objects.filter(
            transaction_date__date=today
        ).count() + 1
        self.transaction_number = f"POS-{date_str}-{today_count:04d}"


class PoSTransactionItem(models.Model):
    transaction = models.ForeignKey(PoSTransaction, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()  # Reference to Product model in product module
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)