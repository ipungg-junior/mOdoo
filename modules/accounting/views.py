import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
  
  
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