from django.shortcuts import render, redirect
from django.views import View
from .models import Employee
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .services import EmployeeService
import json

class EmployeeIndex(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    group_required = 'group_access_hr'

    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        employees = Employee.objects.select_related('user').all()
        return render(request, 'hr_index.html', {'employees': employees})
    

class EmployeeCreatePage(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee', 'hr.create_employee']
    group_required = 'group_access_hr'

    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        # No longer passing users - they will be fetched via JavaScript API
        return render(request, 'hr_create.html')
    

class EmployeeListPage(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    group_required = 'group_access_hr'

    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        # No longer passing users - they will be fetched via JavaScript API
        return render(request, 'hr_list.html')


class APIView(View):
    """
    Unified API view for handling all hr operations through single endpoint
    """
    group_required = 'group_access_hr'
    context = ''

    def get(self, request):
        """Handle GET requests"""
        return JsonResponse({'success': False, 'message': 'Invalid HTTP Method'}, status=400)

    def post(self, request):
        """
        Handle POST requests - process JSON actions
        """
        try:
            # Check permissions for API access
            if not request.user.groups.filter(name__icontains=self.group_required):
                raise PermissionDenied

            # Parse JSON data from request body
            json_request = json.loads(request.body.decode('utf-8'))

            if self.context == 'employee_api':
            # Employee Service handling request
                return EmployeeService.process_post(request, json_request)
            else:
                # Return 400 Bad request
                return JsonResponse({'success': False, 'message': 'Invalid API context'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)