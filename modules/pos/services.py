import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from .models import PoSTransaction, PoSTransactionItem
from engine.utils import format_rupiah


class PoSService:

    @staticmethod
    def process_get(request, json_request):
        """Handle GET requests for PoS operations"""
        action = json_request.get('action')

        if action == 'get_products':
            return PoSService.get_products(request)
        elif action == 'get_transaction':
            return PoSService.get_transaction(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown GET action: {action}'}, status=400)

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for PoS operations"""
        action = json_request.get('action')

        if action == 'create_transaction':
            return PoSService.create_transaction(request, json_request)
        elif action == 'process_payment':
            return PoSService.process_payment(request, json_request)
        elif action == 'cancel_transaction':
            return PoSService.cancel_transaction(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def get_products(request):
        """Get products for PoS interface"""
        try:
            # Import here to avoid circular imports
            from modules.product.models import Product, Category

            products = Product.objects.select_related('category').filter(is_active=True).order_by('name')

            product_data = []
            for product in products:
                product_data.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'formatted_price': str(format_rupiah(product.price)),
                    'stock': product.qty,
                    'category': {
                        'id': product.category.id if product.category else None,
                        'name': product.category.name if product.category else 'No Category'
                    } if product.category else None,
                    'description': product.description or '',
                })

            return JsonResponse({
                'success': True,
                'data': {
                    'products': product_data
                }
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    @staticmethod
    def get_transaction(request, data):
        """Get transaction details"""
        transaction_id = data.get('transaction_id')

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = PoSTransaction.objects.get(id=transaction_id)
            items = PoSTransactionItem.objects.filter(transaction=transaction)

            transaction_data = {
                'id': transaction.id,
                'transaction_number': transaction.transaction_number,
                'customer_name': transaction.customer_name,
                'subtotal': float(transaction.subtotal),
                'discount_amount': float(transaction.discount_amount),
                'tax_amount': float(transaction.tax_amount),
                'grand_total': float(transaction.grand_total),
                'payment_method': transaction.payment_method,
                'cash_received': float(transaction.cash_received),
                'change_amount': float(transaction.change_amount),
                'is_completed': transaction.is_completed,
                'transaction_date': transaction.transaction_date.isoformat(),
                'items': []
            }

            for item in items:
                transaction_data['items'].append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'product_sku': item.product_sku,
                    'unit_price': float(item.unit_price),
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal)
                })

            return JsonResponse({
                'success': True,
                'data': transaction_data
            })

        except PoSTransaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    @staticmethod
    def create_transaction(request, data):
        """Create a new PoS transaction"""
        try:
            with db_transaction.atomic():
                # Create transaction
                pos_transaction = PoSTransaction()
                pos_transaction.cashier = request.user
                pos_transaction.customer_name = data.get('customer_name', '')
                pos_transaction.generate_transaction_number()
                pos_transaction.save()

                # Add items
                items = data.get('items', [])
                for item in items:
                    pos_item = PoSTransactionItem()
                    pos_item.transaction = pos_transaction
                    pos_item.product_id = item['product_id']
                    pos_item.product_name = item['product_name']
                    pos_item.product_sku = item.get('product_sku', '')
                    pos_item.unit_price = item['unit_price']
                    pos_item.quantity = item['quantity']
                    pos_item.save()

                # Calculate totals
                pos_transaction.calculate_totals()

                return JsonResponse({
                    'success': True,
                    'message': 'Transaction created successfully',
                    'data': {
                        'transaction_id': pos_transaction.id,
                        'transaction_number': pos_transaction.transaction_number
                    }
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    @staticmethod
    def process_payment(request, data):
        """Process payment for PoS transaction"""
        transaction_id = data.get('transaction_id')
        payment_method = data.get('payment_method', 'cash')
        cash_received = data.get('cash_received', 0)
        discount_amount = data.get('discount_amount', 0)
        discount_percentage = data.get('discount_percentage', 0)
        tax_amount = data.get('tax_amount', 0)

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            with db_transaction.atomic():
                transaction = PoSTransaction.objects.get(id=transaction_id)

                if transaction.is_completed:
                    return JsonResponse({'success': False, 'message': 'Transaction already completed'}, status=400)

                # Apply discounts and tax
                transaction.discount_amount = discount_amount
                transaction.discount_percentage = discount_percentage
                transaction.tax_amount = tax_amount
                transaction.payment_method = payment_method
                transaction.cash_received = cash_received

                # Recalculate totals
                transaction.calculate_totals()

                # Validate payment
                if payment_method == 'cash' and cash_received < transaction.grand_total:
                    return JsonResponse({
                        'success': False,
                        'message': f'Insufficient payment. Required: {format_rupiah(transaction.grand_total)}, Received: {format_rupiah(cash_received)}'
                    }, status=400)

                # Calculate change
                if payment_method == 'cash':
                    transaction.change_amount = cash_received - transaction.grand_total

                # Validate stock availability
                for item in transaction.items.all():
                    from modules.product.models import Product
                    try:
                        product = Product.objects.get(id=item.product_id)
                        if product.qty < item.quantity:
                            return JsonResponse({
                                'success': False,
                                'message': f'Insufficient stock for {product.name}. Available: {product.qty}, Required: {item.quantity}'
                            }, status=400)
                    except Product.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': f'Product {item.product_name} not found'
                        }, status=400)

                # Deduct stock
                for item in transaction.items.all():
                    from modules.product.models import Product
                    product = Product.objects.get(id=item.product_id)
                    product.qty -= item.quantity
                    product.save()

                # Create accounting journal entry
                journal_id = PoSService.create_accounting_journal(transaction)
                transaction.accounting_journal_id = journal_id

                # Mark as completed
                transaction.is_completed = True
                transaction.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Payment processed successfully',
                    'data': {
                        'transaction_id': transaction.id,
                        'transaction_number': transaction.transaction_number,
                        'change_amount': float(transaction.change_amount),
                        'receipt_data': PoSService.generate_receipt_data(transaction)
                    }
                })

        except PoSTransaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    @staticmethod
    def create_accounting_journal(transaction):
        """Create accounting journal entry for the transaction"""
        try:
            # Import accounting models
            from modules.accounting.models import AccountingBatchPayment, AccountingBankTransferRecord

            # Create batch payment record
            batch_payment = AccountingBatchPayment()
            batch_payment.batch_number = f"POS-{transaction.transaction_number}"
            batch_payment.total_amount = transaction.grand_total
            batch_payment.payment_type = 'ar'  # Accounts Receivable
            batch_payment.payment_date = transaction.transaction_date.date()
            batch_payment.payment_method = transaction.payment_method
            batch_payment.save()

            # Create payment record based on method
            if transaction.payment_method == 'cash':
                from modules.accounting.models import AccountingCashPaymentRecord
                cash_record = AccountingCashPaymentRecord()
                cash_record.batch_payment = batch_payment.batch_number
                cash_record.cash_received_by = transaction.cashier.username
                cash_record.payment_amount = transaction.grand_total
                cash_record.payment_date = transaction.transaction_date.date()
                cash_record.reference_number = transaction.transaction_number
                cash_record.save()

            elif transaction.payment_method == 'bank_transfer':
                bank_record = AccountingBankTransferRecord()
                bank_record.batch_payment = batch_payment.batch_number
                bank_record.bank_name = 'Default Bank'  # Could be made configurable
                bank_record.bank_account_number = 'Default Account'
                bank_record.bank_account_name = transaction.cashier.username
                bank_record.transfer_amount = transaction.grand_total
                bank_record.transfer_date = transaction.transaction_date.date()
                bank_record.reference_number = transaction.transaction_number
                bank_record.save()

            return batch_payment.batch_number

        except Exception as e:
            # Log error but don't fail the transaction
            print(f"Failed to create accounting journal: {e}")
            return None

    @staticmethod
    def generate_receipt_data(transaction):
        """Generate receipt data for printing"""
        items = []
        for item in transaction.items.all():
            items.append({
                'name': item.product_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal)
            })

        return {
            'transaction_number': transaction.transaction_number,
            'date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'cashier': transaction.cashier.username,
            'customer': transaction.customer_name or 'Walk-in Customer',
            'items': items,
            'subtotal': float(transaction.subtotal),
            'discount_amount': float(transaction.discount_amount),
            'tax_amount': float(transaction.tax_amount),
            'grand_total': float(transaction.grand_total),
            'payment_method': transaction.get_payment_method_display(),
            'cash_received': float(transaction.cash_received),
            'change_amount': float(transaction.change_amount)
        }

    @staticmethod
    def cancel_transaction(request, data):
        """Cancel a PoS transaction"""
        transaction_id = data.get('transaction_id')

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = PoSTransaction.objects.get(id=transaction_id)

            if transaction.is_completed:
                return JsonResponse({'success': False, 'message': 'Cannot cancel completed transaction'}, status=400)

            # Delete transaction (will cascade to items)
            transaction.delete()

            return JsonResponse({
                'success': True,
                'message': 'Transaction cancelled successfully'
            })

        except PoSTransaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)