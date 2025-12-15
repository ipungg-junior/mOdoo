# Accounting Module

## Overview
Financial management module for bank accounts, payment processing, and accounting records in the mOdoo ERP system.

## Features
- Bank and branch management
- Bank account tracking with balances
- Payment status and term configurations
- Receivable payments and batch processing
- Multiple payment methods (bank transfer, QRIS, cash, virtual account)

## Models
- `Bank`/`BankBranch`/`BankAccount`: Banking structures
- `AccountingPaymentStatus`/`AccountingPaymentTerm`: Payment configurations
- `AccountingReceivablePayment`: Receivables
- `AccountingBatchPayment`: Batch payments
- Various payment record models (BankTransfer, QRIS, Cash, VirtualAccount)

## Dependencies
- Django auth

## Entry Points
- `modules/accounting/apps.py`: Permission setup
- `modules/accounting/urls.py`: URL routing
- `modules/accounting/views.py`: Page and API views

## Public Interfaces
- API Endpoints:
  - `/api/ar/`: Accounts receivable operations
- Page Views:
  - `/accounting/`: Accounting dashboard
  - `/accounting/create-ar/`: Create receivable

## Version
v0.1.0 - Basic accounting structures