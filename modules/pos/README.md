# Point of Sale (PoS) Module

## Overview
A comprehensive Point of Sale module for the mOdoo ERP system, designed for fast and efficient retail transactions. Features complete integration with Product and Accounting modules for seamless inventory and financial management.

## Features

### Core Functionality
- **Fast Transaction Processing**: Optimized for cashier speed with minimal clicks
- **Real-time Inventory**: Automatic stock validation and updates
- **Multi-Payment Support**: Cash, Bank Transfer, and E-Wallet options
- **Receipt Generation**: Printable HTML receipts with transaction details
- **Discount & Tax Management**: Flexible pricing adjustments

### User Interface
- **Product Grid Display**: Visual product cards with stock indicators
- **Search & Filter**: Real-time product search and category filtering
- **Interactive Cart**: Dynamic cart management with quantity controls
- **Mobile-Responsive**: Touch-optimized design for tablets and mobile devices
- **One-Click Operations**: Streamlined workflow for maximum efficiency

### Integration Features
- **Product Module Sync**: Automatic product data retrieval and stock management
- **Accounting Integration**: Automatic journal entries for all transactions
- **Financial Tracking**: Complete audit trail with accounting references
- **Inventory Control**: Real-time stock deduction and validation

### Security & Permissions
- **Role-Based Access**: Dedicated cashier user group
- **Transaction Validation**: Stock availability and payment verification
- **Audit Trail**: Complete transaction history with user tracking

## Models

### PoSTransaction
Main transaction model containing:
- `transaction_number`: Auto-generated unique identifier (POS-YYYYMMDD-XXXX)
- `cashier`: User who processed the transaction
- `customer_name`: Optional customer identification
- `subtotal`, `discount_amount`, `tax_amount`, `grand_total`: Financial calculations
- `payment_method`: Cash, Bank Transfer, or E-Wallet
- `cash_received`, `change_amount`: Cash transaction details
- `accounting_journal_id`: Reference to accounting journal entry

### PoSTransactionItem
Individual transaction line items:
- `product_id`: Reference to Product model
- `product_name`, `product_sku`: Product identification
- `unit_price`, `quantity`, `subtotal`: Pricing calculations

## Dependencies
- `modules.product`: Product data and inventory management
- `modules.accounting`: Financial journal entries and payment tracking
- `engine`: Utility functions and base permissions
- Django authentication and ORM

## Entry Points
- `modules/pos/apps.py`: Permission setup and cashier group creation
- `modules/pos/urls.py`: URL routing configuration
- `modules/pos/views.py`: Main views and API endpoints
- `modules/pos/services.py`: Business logic and integration layer

## Public Interfaces

### API Endpoints
All endpoints use JSON request/response format with action-based routing:

#### Product Data Retrieval
```javascript
POST /pos/api/
{
  "action": "get_products"
}
```

#### Transaction Management
```javascript
// Create transaction
POST /pos/api/
{
  "action": "create_transaction",
  "customer_name": "John Doe",
  "items": [
    {
      "product_id": 1,
      "product_name": "Product A",
      "unit_price": 10000,
      "quantity": 2
    }
  ]
}

// Process payment
POST /pos/api/
{
  "action": "process_payment",
  "transaction_id": 123,
  "payment_method": "cash",
  "cash_received": 25000,
  "discount_amount": 0,
  "tax_amount": 0
}
```

### Page Views
- `/pos/`: Main Point of Sale interface

## Transaction Flow

### 1. Product Selection
- Browse product grid or use search/filter
- Click products to add to cart
- Real-time stock validation

### 2. Cart Management
- View items with quantities and subtotals
- Adjust quantities with +/- buttons
- Remove items individually
- Apply discounts and taxes

### 3. Payment Processing
- Select payment method
- Enter cash received (for cash payments)
- Automatic change calculation
- Process payment with validation

### 4. Post-Transaction
- Generate and display receipt
- Update product inventory
- Create accounting journal entries
- Reset for next transaction

## Integration Details

### Product Module Integration
- **Data Retrieval**: Product name, price, stock, category
- **Stock Validation**: Prevents overselling with real-time checks
- **Automatic Updates**: Stock deduction on successful payment
- **Category Filtering**: Product organization and search

### Accounting Module Integration
- **Journal Entries**: Automatic creation for each transaction
  - Debit: Cash/Bank Account
  - Credit: Sales Revenue Account
- **Payment Records**: Detailed transaction tracking
- **Reference Linking**: PoS transactions linked to financial records
- **Audit Trail**: Complete financial transaction history

## Mobile Responsiveness

### Breakpoint Strategy
- **Desktop (> 1024px)**: Full 3-column layout (products, cart, payment)
- **Tablet (768-1024px)**: Adapted grid with side-by-side layout
- **Mobile (< 768px)**: Single column with fixed bottom cart

### Touch Optimizations
- Large product cards for easy tapping
- Prominent quantity control buttons
- Swipe-friendly cart management
- Optimized button sizes for finger navigation

## Security Features

### Permission System
- **Cashier Group**: Dedicated role for PoS operations
- **Transaction Permissions**: Create, view, and manage transactions
- **User Tracking**: All transactions linked to cashier user

### Validation Layers
- **Stock Validation**: Prevents selling out-of-stock items
- **Payment Validation**: Ensures sufficient payment amounts
- **Data Integrity**: Transaction atomicity with rollback on errors

## Performance Optimizations

### Frontend Optimizations
- **Client-Side Cart**: JavaScript state management for instant updates
- **Lazy Loading**: On-demand product and category loading
- **Minimal API Calls**: Combined data retrieval where possible
- **Efficient DOM Updates**: Targeted element updates only

### Backend Optimizations
- **Database Transactions**: Atomic operations with rollback capability
- **Bulk Operations**: Efficient inventory and accounting updates
- **Caching Strategy**: Product data caching for repeated access
- **Query Optimization**: Select related data to minimize database hits

## Error Handling

### User-Friendly Messages
- **Stock Errors**: Clear messages when items are out of stock
- **Payment Errors**: Insufficient funds or invalid payment method alerts
- **Network Errors**: Graceful handling of API failures
- **Validation Errors**: Specific feedback for data entry issues

### System Recovery
- **Transaction Rollback**: Automatic reversal on processing failures
- **State Recovery**: Cart persistence during session interruptions
- **Error Logging**: Comprehensive error tracking for debugging

## Receipt System

### Receipt Features
- **Company Information**: Configurable business details
- **Transaction Details**: Complete itemization with quantities and prices
- **Payment Summary**: Method, amounts, and change calculation
- **Print Optimization**: Monospace font for consistent formatting

### Receipt Format
```
RECEIPT
POS-20251223-0001
2025-12-23 14:30:00

Cashier: John Doe
Customer: Walk-in Customer

Product A x2.............Rp 20,000
Product B x1.............Rp 15,000
-----------------------------------
Subtotal:...............Rp 35,000
Tax:....................Rp 3,500
TOTAL:..................Rp 38,500

Payment: Cash
Cash Received:.........Rp 40,000
Change:................Rp 1,500

Thank you for your business!
```

## Configuration

### Required Setup
1. **Add to INSTALLED_APPS** in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ... existing apps
       'modules.pos',
   ]
   ```

2. **URL Configuration** in main `urls.py`:
   ```python
   urlpatterns = [
       # ... existing patterns
       path('pos/', include('modules.pos.urls')),
   ]
   ```

3. **Run Migrations**:
   ```bash
   python manage.py makemigrations pos
   python manage.py migrate
   ```

4. **Create Cashier Users**:
   - Assign users to 'cashier' group
   - Grant necessary permissions

### Optional Configuration
- **Receipt Customization**: Modify receipt template in `pos.html`
- **Payment Methods**: Extend payment options in models
- **Tax Calculations**: Customize tax logic in services
- **Printer Integration**: Add print API for thermal printers

## Version History

### v1.0.0 - Initial Release
- Complete PoS functionality with Product and Accounting integration
- Mobile-responsive design optimized for tablets
- Comprehensive transaction processing and receipt generation
- Automatic inventory and accounting management
- Role-based security with cashier permissions

## Version
v1.0.0 - Complete Point of Sale system with full ERP integration

## Usage Guide

### For Cashiers
1. **Login** with cashier credentials
2. **Browse Products** using grid view or search
3. **Add Items** to cart by clicking product cards
4. **Manage Cart** with quantity controls and item removal
5. **Apply Discounts/Taxes** as needed
6. **Process Payment** with selected payment method
7. **Print Receipt** and start next transaction

### For Administrators
1. **Configure Products** in Product module
2. **Set up Accounting** charts and journals
3. **Create Cashier Users** and assign permissions
4. **Monitor Transactions** through transaction history
5. **Review Financial Reports** in Accounting module

The PoS module provides a complete retail solution with professional-grade features, seamless integration, and excellent user experience for both cashiers and administrators.