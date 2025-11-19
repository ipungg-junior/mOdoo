from django.shortcuts import render, redirect
from django.views import View
from .models import Employee
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .services import EmployeeService
import json

class EmployeeListView(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    group_required = 'group_access_hr'

    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied
        employees = Employee.objects.select_related('user').all()
        return render(request, 'hr_index.html', {'employees': employees})

class SyncEmployeesView(PermissionRequiredMixin, View):
    permission_required = ['hr.add_employee']
    group_required = 'group_access_hr'

    def get(self, request):
        if not request.user.groups.filter(name__icontains=self.group_required):
            raise PermissionDenied

        # Sync all users to employees if they don't exist
        synced_count = 0
        for user in User.objects.all():
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'position': 'Employee',
                    'hire_date': user.date_joined.date()
                }
            )
            if created:
                synced_count += 1

        return redirect('list_view')
    
class APIView(View):
    """
    Unified API view for handling all hr operations
    """
    group_required = 'group_access_hr'
    context = ''

    def get(self, request):
        """Handle GET requests"""
        return EmployeeService.process_get(request, request.GET)

    def post(self, request):
        """
        Handle POST requests - process JSON actions
        """
        try:
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