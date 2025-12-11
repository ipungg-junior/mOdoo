from django.db import models
from django.contrib.auth import get_user_model
from engine.models import MasterDatabase

User = get_user_model()

class ChoosenDatabase(models.Model):
    name = models.ForeignKey(MasterDatabase, on_delete=models.SET_NULL, null=True, blank=True)


class ChoosenDatabaseConfig(models.Model):
    db_name = models.ForeignKey(ChoosenDatabase, on_delete=models.SET_NULL, null=True, blank=True)
    config_name = models.CharField(max_length=40)
    config_value = models.TextField()

    def __str__(self):
        return f"{self.config_name} - {self.master_database.name}"


class Bank(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class BankBranch(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    branch_name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.bank.name} - {self.branch_name}"


class BankAccount(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=50)
    holder_name = models.CharField(max_length=150)
    branch = models.ForeignKey(BankBranch, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.bank.name} - {self.account_number}"
    
    
class MasterStatus(models.Model):
    code = models.CharField(max_length=22, unique=True)
    display_name = models.CharField(max_length=60)
    description = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return self.code


class Item(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    cost_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class AccountReceivable(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=MasterStatus.objects.values_list('code', 'display_name'), default='UNPAID')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"AR {self.invoice_number} - {self.customer.name}"


class AccountPayable(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    bill_number = models.CharField(max_length=50, unique=True)
    bill_date = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=MasterStatus.objects.values_list('code', 'display_name'), default='UNPAID')
    item_list = models.ManyToManyField(Item, through='AccountPayableItem')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"AP {self.bill_number} - {self.supplier.name}"


class ARPayment(models.Model):
    ar = models.ForeignKey(AccountReceivable, on_delete=models.CASCADE, related_name="payments")
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ar.paid_amount += self.amount
        self.ar.save()

    def __str__(self):
        return f"AR Payment {self.amount} for {self.ar.invoice_number}"


class APPayment(models.Model):
    ap = models.ForeignKey(AccountPayable, on_delete=models.CASCADE, related_name="payments")
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ap.paid_amount += self.amount
        self.ap.remaining_amount = self.ap.amount - self.ap.paid_amount
        self.ap.save()

    def __str__(self):
        return f"AP Payment {self.amount} for {self.ap.bill_number}"
