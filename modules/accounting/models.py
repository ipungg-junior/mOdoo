from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    
    
# Base model for payment status
class AccountingPaymentStatus(models.Model):
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True, null=True)
    
    def get_display_name(self):
        return self.display_name

    def __str__(self):
        return self.display_name


# Base model for payment term
class AccountingPaymentTerm(models.Model):
    name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, blank=True, null=True)
    
    def get_display_name(self):
        return self.display_name

    def __str__(self):
        return self.display_name


# Record for receivable payments (invoice payments)
class AccountingReceivablePayment(models.Model):
    INCOME_VARIANT = [
        ('tr', 'Transaction'),
        ('etc', 'Other'),
    ]
    receivable_from = models.CharField(max_length=3, choices=INCOME_VARIANT, default='etc', null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    status = models.ForeignKey(AccountingPaymentStatus, on_delete=models.SET_NULL, null=True)
    term = models.ForeignKey(AccountingPaymentTerm, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date}"
    
    
# Record for batch payments
class AccountingBatchPayment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('ar', 'Accounted Receivable'),
        ('ap', 'Accounted Payable'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('bt', 'Bank Transfer'),
        ('qr', 'QRIS'),
        ('cs', 'Cash'),
        ('va', 'Virtual Account'),
    ]
    batch_number = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_type = models.CharField(max_length=2, choices=PAYMENT_TYPE_CHOICES)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Batch Payment: {self.batch_name} - Total: {self.total_amount}"
    

# Record for bank transfers
class AccountingBankTransferRecord(models.Model):
    batch_payment = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=100)
    bank_account_name = models.CharField(max_length=100)
    transfer_amount = models.IntegerField()
    transfer_date = models.DateField()
    reference_number = models.CharField(max_length=100)

    def __str__(self):
        return f"Transfer of {self.transfer_amount} on {self.transfer_date}"
    
# Record for QRIS payments
class AccountingQRISPaymentRecord(models.Model):
    batch_payment = models.CharField(max_length=100)
    qris_code = models.CharField(max_length=100)
    payment_amount = models.IntegerField()
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100)

    def __str__(self):
        return f"QRIS Payment of {self.payment_amount} on {self.payment_date}"

# Record for cash payments
class AccountingCashPaymentRecord(models.Model):
    batch_payment = models.CharField(max_length=100)
    cash_received_by = models.CharField(max_length=100)
    payment_amount = models.IntegerField()
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100)

    def __str__(self):
        return f"Cash Payment of {self.payment_amount} on {self.payment_date}"
    
# Record for virtual account payments
class AccountingVirtualAccountPaymentRecord(models.Model):
    batch_payment = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    virtual_account_number = models.CharField(max_length=100)
    payment_amount = models.IntegerField()
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100)

    def __str__(self):
        return f"Virtual Account Payment of {self.payment_amount} on {self.payment_date}"