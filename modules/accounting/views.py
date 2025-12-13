import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from .services import AccountReceivable, MasterDataService
  
  
# View for accounting index page  (home)
class AccountingPageView(PermissionRequiredMixin, View):
    """
    View for rendering accounting management page
    """
    group_required = 'group_access_accounting'
    permission_required = 'accounting.view_accounting'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the main accounting management page"""
        return render(request, 'accounting_index.html')
    
    
# View for accounts payable report page
class AccountingPayablePage(PermissionRequiredMixin, View):
    """
    View for rendering accounts payable report page
    """
    group_required = 'group_access_accounting'
    permission_required = 'accounting.view_accounting'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the accounts payable report page"""
        return render(request, 'accounting_payable.html')
    

# View for accounts receivable report page
class AccountingReceivablePage(PermissionRequiredMixin, View):
    """
    View for rendering accounts receivable report page
    """
    group_required = 'group_access_accounting'
    permission_required = 'accounting.view_accounting'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the accounts receivable report page"""
        return render(request, 'accounting_receivable.html')


class APIView(View):
    """
    Unified API view for handling accounting operations
    """
    group_required = 'group_access_accounting'
    context = ''

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            json_request = json.loads(request.body.decode('utf-8'))

            if self.context == 'receivable_api':
                return AccountReceivable.process_post(request, json_request)
            elif self.context == 'master_data_api':
                return MasterDataService.process_post(request, json_request)
            else:
                return JsonResponse({'success': False, 'message': 'Invalid API context'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


class AccountingCreateARPageView(PermissionRequiredMixin, View):
    """
    View for creating new receivable payments
    """
    group_required = 'group_access_accounting'
    permission_required = 'accounting.view_accounting'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name__icontains=self.group_required).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render the create receivable page"""
        return render(request, 'accounting_create_ar.html')