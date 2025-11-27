import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Product, Category
from django.contrib.auth.models import User


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
    def list_products(request):
        """List all products with category information"""
        products = Product.objects.select_related('category').all()
        product_data = []
        for product in products:
            product_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'category': {
                    'id': product.category.id if product.category else None,
                    'name': product.category.name if product.category else None
                } if product.category else None,
                'price': str(product.price),
                'is_active': product.is_active,
                'created_at': product.created_at.isoformat() if product.created_at else None,
                'updated_at': product.updated_at.isoformat() if product.updated_at else None,
            })

        return JsonResponse({
            'success': True,
            'data': product_data
        })

    @staticmethod
    def create_product(request, data):
        """Create a new product"""
        # Handle both JSON and FormData
        if hasattr(data, 'get'):  # JSON/FormData
            name = data.get('name')
            price = data.get('price')
            description = data.get('description', '')
            category_id = data.get('category_id')
            is_active = data.get('is_active', True)
        else:  # Direct dictionary
            name = data.get('name')
            price = data.get('price')
            description = data.get('description', '')
            category_id = data.get('category_id')
            is_active = data.get('is_active', True)

        if not name or price is None:
            return JsonResponse({'success': False, 'message': 'Name and price are required'}, status=400)

        try:
            # Convert price to float if it's a string
            if isinstance(price, str):
                price = float(price)

            product = Product(
                name=name,
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

            product.full_clean()  # Validate
            product.save()

            return JsonResponse({
                'success': True,
                'message': 'Product created successfully',
                'data': {
                    'id': product.id,
                    'name': product.name,
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
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except ValueError as e:
            return JsonResponse({'success': False, 'message': f'Invalid price format: {str(e)}'}, status=400)

    @staticmethod
    def update_product(request, data):
        """Update an existing product"""
        product_id = data.get('id')
        name = data.get('name')
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