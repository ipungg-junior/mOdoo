import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from .services import ProductService, CategoryService, TransactionService
from engine.utils import format_rupiah


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
            # For GET requests, parse query parameters or use empty dict
            json_request = dict(request.GET.items()) if request.GET else {}

            if self.context == 'category_api':
                # Category Service handling request
                return CategoryService.process_get(request, json_request)
            elif self.context == 'product_api':
                # Product Service handling request
                return ProductService.process_get(request, json_request)
            else:
                # Return 400 Bad request
                return JsonResponse({'success': False, 'message': 'Invalid API context'}, status=400)

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    def post(self, request):
        """
        Handle POST requests - process JSON actions or file uploads
        """
        try:
            # Check if this is a file upload request (multipart/form-data)
            if request.FILES:
                # Handle file upload requests
                action = request.POST.get('action')
                if action == 'upload_image' and self.context == 'product_api':
                    return ProductService.upload_image(request)
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid file upload action'}, status=400)
            else:
                # Parse JSON data from request body for regular API calls
                json_request = json.loads(request.body.decode('utf-8'))

                if self.context == 'category_api':
                    # Category Service handling request
                    return CategoryService.process_post(request, json_request)
                elif self.context == 'product_api':
                    # Product Service handling request
                    return ProductService.process_post(request, json_request)
                elif self.context == 'product_transaction_api':
                    # Transaction Service handling request
                    return TransactionService.process_post(request, json_request)
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
        total_amount = format_rupiah(ProductService.get_product_total_amount(request))
        income_today = format_rupiah(TransactionService._get_income_today(request))
        return render(request, 'index.html', context={'total_amount': total_amount, 'income_today': income_today})


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
    
    
class ProductTransactionPageView(PermissionRequiredMixin, View):
    """
    View for transaction management page
    """
    group_required = 'group_access_product'
    permission_required = 'product.view_product'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the transaction management page"""
        # Calculate total transaction today for display
        from django.utils import timezone
        from django.db.models import Sum
        from .models import Transaction

        # Summary data
        volume_transaction = format_rupiah(TransactionService._get_income_today(request))
        cash_on_hand = format_rupiah(TransactionService._get_paid_transaction_today())
        pending_payment = format_rupiah(TransactionService._get_pending_payment())

        return render(request, 'product_transaction.html', {'volume_transaction': volume_transaction, 'cash_on_hand': cash_on_hand, 'pending_payment': pending_payment})
    

class ProductTransactionFilterPageView(PermissionRequiredMixin, View):
    """
    View for filter transaction
    """
    group_required = 'group_access_product'
    permission_required = 'product.view_product'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'product_transaction_filter.html')