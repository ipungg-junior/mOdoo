import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from .services import ProductService, CategoryService


class APIView(View):
    """
    Unified API view for handling all product and category operations
    """
    group_required = 'group_access_product'
    context = ''
    
    def get(self, request):
        """
        Handle GET requests - return data based on context
        """
        try:
            # Parse JSON data from request body
            json_request = json.loads(request.body.decode('utf-8'))

            if self.context == 'category_api':
                # Category Service handling request
                return CategoryService.process_get(request, json_request)
            elif self.context == 'product_api':
                # Product Service handling request
                return ProductService.process_get(request, json_request)
            else:
                # Return 400 Bad request
                return JsonResponse({'success': False, 'message': 'Invalid API context'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def post(self, request):
        """
        Handle POST requests - process JSON actions
        """
        try:
            # Parse JSON data from request body
            json_request = json.loads(request.body.decode('utf-8'))

            if self.context == 'category_api':
                # Category Service handling request
                return CategoryService.process_post(request, json_request)
            elif self.context == 'product_api':
                # Product Service handling request
                return ProductService.process_post(request, json_request)
            else:
                # Return 400 Bad request
                return JsonResponse({'success': False, 'message': 'Invalid API context'}, status=400)

        except json.JSONDecodeError:
            print("Invalid JSON data received in POST request")
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            print(f"Error processing POST request: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


class ProductPageView(PermissionRequiredMixin, View):
    """
    View for rendering product management pages
    """
    group_required = 'group_access_product'
    permission_required = 'product.view_product'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the main product management page"""
        # Get total amount of products
        total_amount = ProductService.get_product_total_amount(request)
        return render(request, 'index.html', context={'total_amount': total_amount})


class ProductCreatePageView(PermissionRequiredMixin, View):
    """
    View for creating new products
    """
    group_required = 'group_access_product'
    permission_required = 'product.add_product'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the create product page"""
        return render(request, 'product_create.html')