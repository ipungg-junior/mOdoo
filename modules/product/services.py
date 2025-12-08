import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Sum
from .models import Product, Category, Transaction, TransactionItem
from django.contrib.auth.models import User
from engine.utils import format_rupiah


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
            return TransactionService.list_transaction(request)
        elif action == 'create':
            return TransactionService.create_transaction(request, json_request)
        elif action == 'update':
            return TransactionService.update_transaction(request, json_request)
        elif action == 'delete':
            return TransactionService.delete_transaction(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def list_transaction(request):
        """List all transactions with their items"""
        transactions = Transaction.objects.select_related().all().order_by('-transaction_date')
        transaction_data = []

        # Calculate total transaction today
        from django.utils import timezone
        today = timezone.now().date()
        total_today = Transaction.objects.filter(
            transaction_date__date=today
        ).aggregate(total=Sum('total_price'))['total'] or 0

        for transaction in transactions:
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
                'status': transaction.get_status_display(),
                'status_value': transaction.status,
                'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d %H:%M:%S') if transaction.transaction_date else None,
                'items': items_data,
                'items_count': len(items_data)
            })

        return JsonResponse({
            'success': True,
            'data': {
                'transactions': transaction_data,
                'total_transaction_today': str(format_rupiah(total_today))
            }
        })

    @staticmethod
    def create_transaction(request, data):
        """Create a new transaction"""
        all_items = data.get('items', [])
        name = data.get('name', '')
        payment_status = data.get('payment_status', 'false')
        
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
                status=payment_status
            )
            transaction.full_clean()  # Validate
            transaction.save()

            for item in all_items:
                product_id = item.get('product_id')
                quantity = item.get('qty', 0)

                try:
                    product = Product.objects.get(id=product_id)
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
                    return JsonResponse({'success': False, 'message': f'Product with ID {product_id} not found'}, status=400)
                
            transaction.total_price = total_price
            transaction.save()

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
    def update_transaction(request, data):
        """Update an existing transaction"""
        transaction_id = data.get('id')
        customer_name = data.get('name')
        payment_status = data.get('payment_status')
        items = data.get('items', [])

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = Transaction.objects.get(id=transaction_id)

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
                # Delete existing items
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
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def delete_transaction(request, data):
        """Delete a transaction"""
        transaction_id = data.get('id')

        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Transaction ID is required'}, status=400)

        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.delete()

            return JsonResponse({
                'success': True,
                'message': 'Transaction deleted successfully'
            })

        except Transaction.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transaction not found'}, status=404)
        