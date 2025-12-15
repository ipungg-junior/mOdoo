# Product Management Module

## Overview
Product and category management module with transaction handling and inventory tracking for the mOdoo ERP system.

## Features
- Product CRUD operations (create, read, update, delete)
- Category management
- Transaction processing with inventory adjustment
- Payment status and terms
- Dashboard with total amounts and income tracking

## Models
- `Category`: Product categories
- `Product`: Product details with pricing and inventory
- `Transaction`: Sales transactions
- `TransactionItem`: Transaction line items
- `PaymentStatus`/`PaymentTerm`: Payment configurations

## Dependencies
- `engine` (MasterDatabase, format_rupiah utility)
- Django models and auth

## Entry Points
- `modules/product/apps.py`: Permission setup
- `modules/product/urls.py`: URL routing
- `modules/product/views.py`: Page and API views

## Public Interfaces
- API Endpoints:
  - `/api/product/`: Product operations
  - `/api/category/`: Category operations
  - `/api/transaction/`: Transaction operations
- Page Views:
  - `/product/`: Main dashboard
  - `/product/create-product/`: Product creation
  - `/product/transaction/`: Transaction management

## Version
v0.1.0 - Basic product CRUD with transactions