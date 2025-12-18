import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Product, Category, Transaction, TransactionItem, PaymentTerm, PaymentStatus
from django.contrib.auth.models import User
from engine.utils import format_rupiah
from datetime import datetime

# Import accounting models for receivable creation
try:
    from modules.accounting.models import AccountingReceivablePayment, AccountingPaymentStatus, AccountingPaymentTerm
except ImportError:
    # Handle case where accounting module is not available
    AccountingReceivablePayment = None
    AccountingPaymentStatus = None
    AccountingPaymentTerm = None



class CategoryService:

    @staticmethod
    def process_get(request, json_request):
        """Handle GET requests for category operations"""
        action = json_request.get('action')
        
        if action == 'list':
            return CategoryService.list_categories(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown GET action: {action}'}, status=400)

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for category operations"""
        action = json_request.get('action')

        if action == 'list':
            return CategoryService.list_categories(request)
        elif action == 'create':
            return CategoryService.create_category(request, json_request)
        elif action == 'update':
            return CategoryService.update_category(request, json_request)
        elif action == 'delete':
            return CategoryService.delete_category(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def list_categories(request):
        """List all categories"""
        categories = Category.objects.all().order_by('name')
        category_data = []

        for category in categories:
            category_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'created_at': category.created_at.isoformat() if category.created_at else None,
                'updated_at': category.updated_at.isoformat() if category.updated_at else None,
            })

        return JsonResponse({
            'success': True,
            'data': category_data
        })

    @staticmethod
    def create_category(request, data):
        """Create a new category"""
        name = data.get('name')
        description = data.get('description', '')

        if not name:
            return JsonResponse({'success': False, 'message': 'Category name is required'}, status=400)

        try:
            category = Category(
                name=name,
                description=description
            )

            category.full_clean()  # Validate
            category.save()

            return JsonResponse({
                'success': True,
                'message': 'Category created successfully',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description
                }
            })

        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def update_category(request, data):
        """Update an existing category"""
        category_id = data.get('id')
        name = data.get('name')
        description = data.get('description')

        if not category_id:
            return JsonResponse({'success': False, 'message': 'Category ID is required'}, status=400)

        try:
            category = Category.objects.get(id=category_id)

            if name is not None:
                category.name = name
            if description is not None:
                category.description = description

            category.full_clean()  # Validate
            category.save()

            return JsonResponse({
                'success': True,
                'message': 'Category updated successfully',
                'data': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description
                }
            })

        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def delete_category(request, data):
        """Delete a category"""
        category_id = data.get('id')

        if not category_id:
            return JsonResponse({'success': False, 'message': 'Category ID is required'}, status=400)

        try:
            category = Category.objects.get(id=category_id)

            # Check if category is being used by products
            if Product.objects.filter(category=category).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot delete category that is being used by products'
                }, status=400)

            category.delete()

            return JsonResponse({
                'success': True,
                'message': 'Category deleted successfully'
            })

        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Category not found'}, status=404)


class ProductService:

    @staticmethod
    def process_get(request, json_request):
        """Handle GET requests for product operations"""
        action = json_request.get('action')

        if action == 'list':
            return ProductService.list_products(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown GET action: {action}'}, status=400)

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for product operations"""
        action = json_request.get('action')

        if action == 'list':
            return ProductService.list_products(request)
        elif action == 'create':
            return ProductService.create_product(request, json_request)
        elif action == 'update':
            return ProductService.update_product(request, json_request)
        elif action == 'delete':
            return ProductService.delete_product(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def get_product_total_amount(request):
        """Get total amount of products"""
        all_products = Product.objects.all()
        total_amount = 0
        for product in all_products:
            if product.qty == None or product.qty == 0:
                pass
            else:
                total_amount += product.qty * product.price
        return total_amount

    @staticmethod
    def list_products(request):
        """List all products with category information"""
        products = Product.objects.select_related('category').all()
        product_data = []
        for product in products:
            product_data.append({
                'id': product.id,
                'name': product.name,
                'qty': product.qty,
                'description': product.description,
                'category': {
                    'id': product.category.id if product.category else None,
                    'name': product.category.name if product.category else None
                } if product.category else None,
                'price': str(format_rupiah(product.price)),
                'raw_price': float(product.price),  # Add raw price for calculations
                'is_active': product.is_active,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None,
            })

        return JsonResponse({
            'success': True,
            'data': {
                'total_amount': format_rupiah(ProductService.get_product_total_amount(request)),
                'income_today': format_rupiah(TransactionService.list_transaction(request).get('data', {}).get('total_transaction_today', 0)),
                'product_list': product_data}
        })

    @staticmethod
    def create_product(request, data):
        
        """Create a new product"""
        # Handle both JSON and FormData
        if hasattr(data, 'get'):  # JSON/FormData
            name = data.get('name')
            qty = data.get('qty')
            price = data.get('price')
            description = data.get('description', '')
            category_id = data.get('category_id')
            is_active = data.get('is_active', True)
            if is_active in ['false', 'False', False, 0, '0']:
                is_active = False
            else:
                is_active = True

        if not name or price is None:
            return JsonResponse({'success': False, 'message': 'Name and price are required'}, status=400)
        
        if qty is None:
            qty = 0

        try:
            # Convert price to float if it's a string
            if isinstance(price, str):
                price = float(price)

            product = Product(
                name=name,
                qty=qty,
                description=description,
                price=price,
                is_active=is_active
            )

            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    product.category = category
                except Category.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Category not found'}, status=400)
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Invalid category ID'}, status=400)

            product.full_clean()  # Validate
            product.save()

            return JsonResponse({
                'success': True,
                'message': 'Product created successfully',
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'qty': product.qty,
                    'description': product.description,
                    'category': {
                        'id': product.category.id if product.category else None,
                        'name': product.category.name if product.category else None
                    } if product.category else None,
                    'price': str(product.price),
                    'is_active': product.is_active
                }
            })

        except ValidationError as e:
            print(e)
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except ValueError as e:
            print(e)
            return JsonResponse({'success': False, 'message': f'Invalid price format: {str(e)}'}, status=400)

    @staticmethod
    def update_product(request, data):
        """Update an existing product"""
        product_id = data.get('id')
        name = data.get('name')
        qty = data.get('qty')
        price = data.get('price')
        description = data.get('description')
        category_id = data.get('category_id')
        is_active = data.get('is_active')

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)

            # Update fields if provided
            if name is not None:
                product.name = name
            if price is not None:
                product.price = price
            if qty is not None:
                product.qty = qty
            if description is not None:
                product.description = description
            if is_active is not None:
                product.is_active = is_active

            # Handle category
            if category_id is not None:
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                        product.category = category
                    except Category.DoesNotExist:
                        return JsonResponse({'success': False, 'message': 'Category not found'}, status=400)
                else:
                    product.category = None

            product.full_clean()  # Validate
            product.save()

            return JsonResponse({
                'success': True,
                'message': 'Product updated successfully',
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'qty': product.qty,
                    'description': product.description,
                    'category': {
                        'id': product.category.id if product.category else None,
                        'name': product.category.name if product.category else None
                    } if product.category else None,
                    'price': str(product.price),
                    'is_active': product.is_active
                }
            })

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def delete_product(request, data):
        """Delete a product"""
        product_id = data.get('id')

        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
            product.delete()

            return JsonResponse({
                'success': True,
                'message': 'Product deleted successfully'
            })

        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        

class TransactionService:

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for product operations"""
        action = json_request.get('action')

        if action == 'list':
            # Extract filters and pagination parameters
            filters = {
                'id': json_request.get('filter_id', '').strip(),
                'customer_name': json_request.get('filter_customer_name', '').strip(),
                'status': json_request.get('filter_status', '').strip(),
                'payment_term': json_request.get('filter_payment_term', '').strip(),
                'due_date': json_request.get('filter_due_date', '').strip(),
                'transaction_date': json_request.get('filter_transaction_date', '').strip(),
            }
            # Remove empty filters
            filters = {k: v for k, v in filters.items() if v}

            page = int(json_request.get('page', 1))
            per_page = int(json_request.get('per_page', 10))

            return TransactionService.list_transaction(request, filters, page, per_page)
        elif action == 'create':
            # return TransactionService.create_transaction(request, json_request)
            return TransactionService.create_transaction_v2(request, json_request)
        elif action == 'update':
            return TransactionService.update_transaction(request, json_request)
        elif action == 'delete':
            return TransactionService.delete_transaction(request, json_request)
        elif action == 'get_income_today':
            return TransactionService.income_today(request)
        elif action == 'get_payment_terms':
            return TransactionService.get_payment_terms(request)
        elif action == 'change_status_transaction':
            return TransactionService.change_status_transaction(request, json_request)
        elif action == 'get_transaction_chart':
            return TransactionService.get_transaction_chart(request)
        elif action == 'get_daily_totals':
            return TransactionService.get_daily_totals(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def change_status_transaction(request, json_request):
        try:
            transaction_id = json_request.get('transactionId')
            transaction = Transaction.objects.get(id=transaction_id)
            if transaction.tmp_status.name == 'paid':
                transaction.tmp_status = PaymentStatus.objects.get(name='unpaid')
            else:
                transaction.tmp_status = PaymentStatus.objects.get(name='paid')
            
            today = timezone.now().date()
            transaction.paid_date = today       
            transaction.save()

            return JsonResponse({
                'success': True,
                'message': 'Transaction status changed successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    # Get transaction with tmp_status paid today
    @staticmethod
    def _get_paid_transaction_today():
        """Get total paid transaction for today"""
        today = timezone.now().date()
        paid_today = Transaction.objects.filter(
            transaction_date__date=today,
            tmp_status__name='paid'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        return paid_today

    # Get pending payment
    @staticmethod
    def _get_pending_payment():
        unpaid = Transaction.objects.filter(tmp_status__name='unpaid').aggregate(total=Sum('total_price'))['total'] or None
        return unpaid
    
    @staticmethod
    def _get_income_today(request):
        """Get total income for today"""
        today = timezone.now().date()
        total_income = Transaction.objects.filter(
            transaction_date__date=today
        ).aggregate(total=Sum('total_price'))['total'] or 0
        return total_income
    
    @staticmethod
    def income_today(request):
        """Return income today as JSON response"""
        total_income = TransactionService._get_income_today(request)
        return JsonResponse({
            'success': True,
            'data': {
                'income_today': format_rupiah(total_income)
            }
        })

    @staticmethod
    def get_payment_terms(request):
        """Return payment terms as JSON response"""
        payment_terms = [{'name': term.name, 'display_name': term.display_name} for term in PaymentTerm.objects.all()]
        return JsonResponse({
            'success': True,
            'data': {'payment_terms': payment_terms}
        })

    @staticmethod
    def list_transaction(request, filters=None, page=1, per_page=10):
        """List transactions with filtering and pagination"""
        from django.core.paginator import Paginator
        from django.db.models import Q

        # Start with base queryset
        transactions_query = Transaction.objects.select_related('tmp_status', 'payment_term').order_by('-transaction_date')

        # Apply filters if provided
        if filters:
            query_conditions = Q()

            if filters.get('id'):
                query_conditions &= Q(id__icontains=filters['id'])

            if filters.get('customer_name'):
                query_conditions &= Q(customer_name__icontains=filters['customer_name'])

            if filters.get('status'):
                query_conditions &= Q(tmp_status__name__icontains=filters['status'])

            if filters.get('payment_term'):
                query_conditions &= Q(payment_term__name__icontains=filters['payment_term'])

            if filters.get('due_date'):
                query_conditions &= Q(due_date__date=filters['due_date'])

            if filters.get('transaction_date'):
                query_conditions &= Q(transaction_date__date=filters['transaction_date'])

            transactions_query = transactions_query.filter(query_conditions)

        # Apply pagination
        paginator = Paginator(transactions_query, per_page)
        page_obj = paginator.get_page(page)

        transaction_data = []

        # Calculate total transaction today
        from django.utils import timezone
        today = timezone.now().date()
        total_today = Transaction.objects.filter(
            transaction_date__date=today
        ).aggregate(total=Sum('total_price'))['total'] or 0

        for transaction in page_obj.object_list:
            # Get transaction items
            items = TransactionItem.objects.filter(transaction=transaction)
            items_data = []
            for item in items:
                items_data.append({
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'price_per_item': str(format_rupiah(item.price_per_item)),
                    'raw_price_per_item': float(item.price_per_item),  # Add raw price for editing
                    'subtotal': str(format_rupiah(item.price_per_item * item.quantity))
                })

            transaction_data.append({
                'id': transaction.id,
                'customer_name': transaction.customer_name or 'N/A',
                'total_price': str(format_rupiah(transaction.total_price)) if transaction.total_price else '0,00',
                'status': transaction.tmp_status.get_display_name() if transaction.tmp_status else 'N/A',
                'status_value': transaction.tmp_status.name if transaction.tmp_status else 'unpaid',
                'payment_term': transaction.payment_term.get_display_name() if transaction.payment_term else 'N/A',
                'due_date': transaction.due_date.strftime('%Y-%m-%d') if transaction.due_date else None,
                'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S') if transaction.transaction_date else None,
                'items': items_data,
                'items_count': len(items_data)
            })

        return JsonResponse({
            'success': True,
            'data': {
                'transactions': transaction_data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'per_page': per_page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                    'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None
                },
                'volume_transaction': str(format_rupiah(total_today)),
                'cash_on_hand': str(format_rupiah(TransactionService._get_paid_transaction_today())),
                'pending_payment': str(format_rupiah(TransactionService._get_pending_payment()))
            }
        })

    @staticmethod
    def create_transaction(request, data):
        """Create a new transaction"""
        all_items = data.get('items', [])
        name = data.get('name', '')
        payment_status = data.get('payment_status', 'false')
        
        print(f'Creating transaction for {name} with items: {all_items} and payment status: {payment_status}')
        
        if not all_items:
            return JsonResponse({'success': False, 'message': 'Transaction items are required'}, status=400)
        
        try:
            total_price = 0
            
            # convert payment status to boolean
            if payment_status in ['true', 'True', True, 1, '1']:
                payment_status = 'lunas'
            else:
                payment_status = 'belum_lunas'
                
            transaction = Transaction(
                customer_name=name,
                status=payment_status,
            )
            transaction.full_clean()  # Validate
            transaction.save()

            failed_items = []

            for item in all_items:
                product_id = item.get('product_id')
                quantity = item.get('qty', 0)

                try:
                    product = Product.objects.get(id=product_id)
                    if product.qty < int(quantity) or int(quantity) <= 0:
                        failed_items.append({
                            'product_id': product_id,
                            'available_qty': product.qty,
                            'requested_qty': quantity
                        })
                        print(f'Insufficient stock for product {product.name}: available {product.qty}, requested {quantity}')
                    else:
                        transaction_item = TransactionItem()
                        transaction_item.transaction = transaction
                        transaction_item.product_name = product.name
                        transaction_item.quantity = int(quantity)
                        transaction_item.price_per_item = product.price
                        transaction_item.full_clean()  # Validate
                        transaction_item.save()
                        
                        # Update product quantity
                        product.qty -= int(quantity)
                        product.full_clean()
                        product.save()
                        
                        # Calculate total price
                        total_price += int(product.price) * int(quantity)
                    
                except Product.DoesNotExist:
                    failed_items.append({
                        'product_id': product_id,
                        'available_qty': 0,
                        'requested_qty': quantity
                    })
                    print(f'Product with ID {product_id} does not exist')
            
            if total_price == 0:
                transaction.delete()  # Clean up the transaction if no items were added
                return JsonResponse({'success': False, 'message': 'No valid items to create transaction'}, status=400)
            else:
                # Update total price of the transaction
                transaction.total_price = total_price
                transaction.save()
            
            if failed_items:
                print(f'Failed items due to insufficient stock: {failed_items}')
                return JsonResponse({
                    'success': True,
                    'message': 'Trasaction created with some failed items due to insufficient stock',
                    'data': {
                        'transaction': {
                            'id': transaction.id,
                            'customer_name': transaction.customer_name,
                            'status': transaction.status,
                            'total_price': str(format_rupiah(transaction.total_price)),
                            'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                        },
                        'failed_items': failed_items
                    }
                }, status=200)

            return JsonResponse({
                'success': True,
                'message': 'Transaction created successfully',
                'data': {'transaction': {
                    'id': transaction.id,
                    'customer_name': transaction.customer_name,
                    'status': transaction.status,
                    'total_price': str(format_rupiah(transaction.total_price)),
                    'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                }}
            })
            
        except ValidationError as e:
            print(e)
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except ValueError as e:
            print(e)
            return JsonResponse({'success': False, 'message': f'Invalid data format: {str(e)}'}, status=400)

    @staticmethod
    def create_transaction_v2(request, data):
        """Create a new transaction - Version 2 (Placeholder)"""
        all_items = data.get('items', [])
        name = data.get('name', '')
        payment_term = data.get('payment_term', 'credit-three-day')
        transaction_date = data.get('datetime', None)
        
        # convert string → datetime
        schedule_time = datetime.strptime(
            transaction_date,
            '%Y-%m-%dT%H:%M'
        )
        
        
        
        print(f'Creating transaction (V2) for {name} with items: {all_items} and payment term: {payment_term}')
        
        if not all_items:
            return JsonResponse({'success': False, 'message': 'Transaction items are required'}, status=400)
        
        try:
            total_price = 0
            
            # Setup payment term and status
            if payment_term in ['CASH', 'cash']:
                tmp_status = PaymentStatus.objects.get(name='paid')
                payment_term = PaymentTerm.objects.get(name='cash')
            else:
                tmp_status = PaymentStatus.objects.get(name='unpaid')
                payment_term = PaymentTerm.objects.get(name=payment_term)
                
            transaction = Transaction(
                customer_name=name,
                tmp_status=tmp_status,
                payment_term=payment_term
            )
            
            # Setup due date if payment term is credit
            if payment_term.name.startswith('credit'):
                days = payment_term.name.split('-')[-2]  # Extract number of days from name
                if days == 'three':
                    days = 3
                elif days == 'seven':
                    days = 7
                elif days == 'fourteen':
                    days = 14
                else:
                    days = 30
                    
                due_date = timezone.now() + timezone.timedelta(days=days)
                transaction.due_date = due_date
                
            elif payment_term.name == 'cash':
                # set due date to transaction date for cash payments
                transaction.due_date = timezone.now()
                
            transaction.full_clean()  # Validate
            transaction.save()

            failed_items = []

            for item in all_items:
                product_id = item.get('product_id')
                quantity = item.get('qty', 0)

                try:
                    product = Product.objects.get(id=product_id)
                    if product.qty < int(quantity) or int(quantity) <= 0:
                        failed_items.append({
                            'product_id': product_id,
                            'available_qty': product.qty,
                            'requested_qty': quantity
                        })
                        print(f'Insufficient stock for product {product.name}: available {product.qty}, requested {quantity}')
                    else:
                        transaction_item = TransactionItem()
                        transaction_item.transaction = transaction
                        transaction_item.product_name = product.name
                        transaction_item.quantity = int(quantity)
                        transaction_item.price_per_item = product.price
                        transaction_item.full_clean()  # Validate
                        transaction_item.save()
                        
                        # Update product quantity
                        product.qty -= int(quantity)
                        product.full_clean()
                        product.save()
                        
                        # Calculate total price
                        total_price += int(product.price) * int(quantity)
                    
                except Product.DoesNotExist:
                    failed_items.append({
                        'product_id': product_id,
                        'available_qty': 0,
                        'requested_qty': quantity
                    })
                    print(f'Product with ID {product_id} does not exist')
            
            if total_price == 0:
                transaction.delete()  # Clean up the transaction if no items were added
                return JsonResponse({'success': False, 'message': 'No valid items to create transaction'}, status=400)
            else:
                # Update total price of the transaction
                transaction.total_price = total_price
                # Save date transaction
                if transaction_date is not None:
                    transaction.transaction_date = schedule_time
                    if schedule_time > datetime.now():
                        return JsonResponse({'success': False, 'message': 'Waktu transaksi melebihi batas hari ini'}, status=400)

                transaction.save()

                # Create receivable record for credit transactions (not cash)
                if AccountingReceivablePayment:
                    try:
                        # Get or create accounting payment status and term
                        receivable_status = AccountingPaymentStatus.objects.get(name=tmp_status.name)

                        receivable_term = AccountingPaymentTerm.objects.get(name=payment_term.name)

                        # Create receivable record
                        receivable = AccountingReceivablePayment.objects.create(
                            receivable_from='tr',  # 'tr' for Transaction
                            reference_id=transaction.id,
                            amount=total_price,
                            due_date=transaction.due_date,
                            status=receivable_status,
                            term=receivable_term
                        )
                        print(f"Created receivable record {receivable.id} for transaction {transaction.id}")

                    except Exception as e:
                        print(f"Warning: Failed to create receivable record: {e}")
                        # Don't fail the transaction if receivable creation fails
                        
                else:
                    # If AccountingReceivablePayment model does not exist, rollback transaction
                    for item in TransactionItem.objects.filter(transaction=transaction):
                        item.delete()
                    transaction.delete()
                    print("AccountingReceivablePayment service not available, rolling back transaction creation.")
                    return JsonResponse({'success': False, 'message': "AccountingReceivablePayment service not available, transaction rejected!"}, status=500)
            
            if failed_items:
                print(f'Failed items due to insufficient stock: {failed_items}')
                return JsonResponse({
                    'success': True,
                    'message': 'Trasaction created with some failed items due to insufficient stock',
                    'data': {
                        'transaction': {
                            'id': transaction.id,
                            'customer_name': transaction.customer_name,
                            'status': transaction.status,
                            'total_price': str(format_rupiah(transaction.total_price)),
                            'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                        },
                        'failed_items': failed_items
                    }
                }, status=200)

            return JsonResponse({
                'success': True,
                'message': 'Transaction created successfully',
                'data': {'transaction': {
                    'id': transaction.id,
                    'customer_name': transaction.customer_name,
                    'status': transaction.status,
                    'total_price': str(format_rupiah(transaction.total_price)),
                    'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                }}
            })
            
        except ValidationError as e:
            print(f"Error creating transaction V2: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except ValueError as e:
            print(f"Error creating transaction V2: {e}")
            return JsonResponse({'success': False, 'message': f'Invalid data format: {str(e)}'}, status=400)

    @staticmethod
    def update_transaction(request, data):
        """Update an existing transaction with proper inventory management"""
        transaction_id = data.get('id')
        customer_name = data.get('name')
        payment_status = data.get('payment_status')
        items = data.get('items', [])

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = Transaction.objects.get(id=transaction_id)

            # Get existing items before updating
            existing_items = TransactionItem.objects.filter(transaction=transaction)
            old_items_dict = {item.product_name: {'quantity': item.quantity, 'price': item.price_per_item} for item in existing_items}

            # Update fields if provided
            if customer_name is not None:
                transaction.customer_name = customer_name

            if payment_status is not None:
                # convert payment status to boolean
                if payment_status in ['true', 'True', True, 1, '1']:
                    transaction.status = 'lunas'
                else:
                    transaction.status = 'belum_lunas'

            # Update transaction items if provided
            if items:
                # Process inventory adjustments
                new_items_dict = {}
                for item in items:
                    product_name = item.get('product_name')
                    quantity = int(item.get('quantity', 0))
                    price_per_item = float(item.get('price_per_item', 0))
                    new_items_dict[product_name] = {'quantity': quantity, 'price': price_per_item}

                # Adjust inventory based on differences
                for product_name, new_data in new_items_dict.items():
                    old_quantity = old_items_dict.get(product_name, {}).get('quantity', 0)
                    new_quantity = new_data['quantity']

                    if new_quantity != old_quantity:
                        try:
                            # Find product by name (assuming product names are unique)
                            product = Product.objects.get(name=product_name)

                            if new_quantity > old_quantity:
                                # Quantity increased - subtract difference from stock
                                difference = new_quantity - old_quantity
                                if product.qty < difference:
                                    return JsonResponse({
                                        'success': False,
                                        'message': f'Insufficient stock for {product_name}. Available: {product.qty}, Needed: {difference}'
                                    }, status=400)
                                product.qty -= difference
                            else:
                                # Quantity decreased - add difference back to stock
                                difference = old_quantity - new_quantity
                                product.qty += difference

                            product.full_clean()
                            product.save()

                        except Product.DoesNotExist:
                            return JsonResponse({'success': False, 'message': f'Product {product_name} not found'}, status=400)

                # Check for removed items (items in old but not in new)
                for product_name, old_data in old_items_dict.items():
                    if product_name not in new_items_dict:
                        try:
                            # Add back the full quantity to stock
                            product = Product.objects.get(name=product_name)
                            product.qty += old_data['quantity']
                            product.full_clean()
                            product.save()
                        except Product.DoesNotExist:
                            return JsonResponse({'success': False, 'message': f'Product {product_name} not found'}, status=400)

                # Delete existing items and add new ones
                TransactionItem.objects.filter(transaction=transaction).delete()

                # Add new items and calculate total price
                total_price = 0
                for item in items:
                    product_name = item.get('product_name')
                    quantity = item.get('quantity', 0)
                    price_per_item = item.get('price_per_item', 0)

                    try:
                        transaction_item = TransactionItem()
                        transaction_item.transaction = transaction
                        transaction_item.product_name = product_name
                        transaction_item.quantity = int(quantity)
                        transaction_item.price_per_item = float(price_per_item)
                        transaction_item.full_clean()  # Validate
                        transaction_item.save()
                        total_price += float(price_per_item) * int(quantity)
                    except Exception as e:
                        return JsonResponse({'success': False, 'message': f'Error adding item {product_name}: {str(e)}'}, status=400)

                transaction.total_price = total_price

            transaction.full_clean()  # Validate
            transaction.save()

            return JsonResponse({
                'success': True,
                'message': 'Transaction updated successfully',
                'data': {
                    'id': transaction.id,
                    'customer_name': transaction.customer_name,
                    'status': transaction.get_status_display(),
                    'status_value': transaction.status,
                    'total_price': str(format_rupiah(transaction.total_price)),
                    'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                }
            })

        except Transaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)

    @staticmethod
    def get_transaction_chart(request):
        """Return transaction volume data for the last 7 days"""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        dates = []
        amounts = []

        for i in range(6, -1, -1):  # Last 7 days, from oldest to newest
            date = today - timedelta(days=i)
            total = Transaction.objects.filter(
                transaction_date__date=date
            ).aggregate(total=Sum('total_price'))['total'] or 0
            dates.append(date.strftime('%d-%m-%Y'))
            amounts.append(float(total))

        return JsonResponse({
            'success': True,
            'data': {
                'dates': dates,
                'amounts': amounts
            }
        })

    @staticmethod
    def get_daily_totals(request):
        """Return daily transaction totals for the last 7 days"""
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        daily_totals = []

        for i in range(6, -1, -1):  # Last 7 days, from oldest to newest
            date = today - timedelta(days=i)
            total = Transaction.objects.filter(
                transaction_date__date=date
            ).aggregate(total=Sum('total_price'))['total'] or 0
            daily_totals.append({
                'date': date.strftime('%d-%m-%Y'),
                'income': format_rupiah(total)
            })

        # Reverse sort (higher to lower)
        daily_totals.sort(key=lambda x: x['date'], reverse=True)

        return JsonResponse({
            'success': True,
            'data': {
                'daily_totals': daily_totals
            }
        })

    @staticmethod
    def delete_transaction(request, data):
        """Delete a transaction and restore inventory"""
        transaction_id = data.get('id')

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = Transaction.objects.get(id=transaction_id)

            # Get all transaction items before deleting
            transaction_items = TransactionItem.objects.filter(transaction=transaction)

            # Restore inventory for each item
            for item in transaction_items:
                try:
                    product = Product.objects.get(name=item.product_name)
                    product.qty += item.quantity  # Add back the quantity to stock
                    product.full_clean()
                    product.save()
                except Product.DoesNotExist:
                    # Log warning but continue - product might have been deleted
                    print(f"Warning: Product {item.product_name} not found when restoring inventory")

            # Delete the transaction (this will cascade delete transaction items)
            transaction.delete()

            return JsonResponse({
                'success': True,
                'message': 'Transaction deleted successfully and inventory restored'
            })

        except Transaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)
        