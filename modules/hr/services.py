import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Employee
from django.contrib.auth.models import User


class EmployeeService:

    @staticmethod
    def process_get(request, json_request):
        """Handle GET requests for employee operations"""
        action = json_request.get('action')

        if action == 'list':
            return EmployeeService.list_employees(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown GET action: {action}'}, status=400)

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for employee operations"""
        action = json_request.get('action')

        if action == 'list_employee':
            return EmployeeService.list_employees(request)
        elif action == 'create':
            return EmployeeService.create_employee(request, json_request)
        elif action == 'update':
            return EmployeeService.update_employee(request, json_request)
        elif action == 'delete':
            return EmployeeService.delete_employee(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def list_employees(request):
        """List all employees with user information"""
        employees = Employee.objects.select_related('user').all()
        employee_data = []

        for employee in employees:
            employee_data.append({
                'id': employee.id,
                'user': {
                    'id': employee.user.id,
                    'username': employee.user.username,
                    'email': employee.user.email,
                    'first_name': employee.user.first_name,
                    'last_name': employee.user.last_name,
                    'get_full_name': employee.user.get_full_name() or employee.user.username,
                    'is_active': employee.user.is_active
                },
                'position': employee.position,
                'hire_date': str(employee.hire_date),
                'is_active': employee.user.is_active
            })

        return JsonResponse({
            'success': True,
            'data': employee_data
        })

    @staticmethod
    def create_employee(request, data):
        """Create a new employee"""
        user_id = data.get('user_id')
        position = data.get('position')
        hire_date = data.get('hire_date')

        if not user_id or not position or not hire_date:
            return JsonResponse({'success': False, 'message': 'User ID, position, and hire date are required'}, status=400)

        try:
            # Check if user exists
            user = User.objects.get(id=user_id)

            # Check if employee already exists for this user
            if Employee.objects.filter(user=user).exists():
                return JsonResponse({'success': False, 'message': 'Employee already exists for this user'}, status=400)

            employee = Employee(
                user=user,
                position=position,
                hire_date=hire_date
            )

            employee.full_clean()  # Validate
            employee.save()

            return JsonResponse({
                'success': True,
                'message': 'Employee created successfully',
                'data': {
                    'id': employee.id,
                    'user': {
                        'id': employee.user.id,
                        'username': employee.user.username,
                        'email': employee.user.email,
                        'first_name': employee.user.first_name,
                        'last_name': employee.user.last_name,
                        'get_full_name': employee.user.get_full_name() or employee.user.username,
                        'is_active': employee.user.is_active
                    },
                    'position': employee.position,
                    'hire_date': str(employee.hire_date),
                    'is_active': employee.user.is_active
                }
            })

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def update_employee(request, data):
        """Update an existing employee"""
        employee_id = data.get('id')
        position = data.get('position')
        hire_date = data.get('hire_date')

        if not employee_id:
            return JsonResponse({'success': False, 'message': 'Employee ID is required'}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)

            # Update fields if provided
            if position is not None:
                employee.position = position
            if hire_date is not None:
                employee.hire_date = hire_date

            employee.full_clean()  # Validate
            employee.save()

            return JsonResponse({
                'success': True,
                'message': 'Employee updated successfully',
                'data': {
                    'id': employee.id,
                    'user': {
                        'id': employee.user.id,
                        'username': employee.user.username,
                        'email': employee.user.email,
                        'first_name': employee.user.first_name,
                        'last_name': employee.user.last_name,
                        'get_full_name': employee.user.get_full_name() or employee.user.username,
                        'is_active': employee.user.is_active
                    },
                    'position': employee.position,
                    'hire_date': str(employee.hire_date),
                    'is_active': employee.user.is_active
                }
            })

        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Employee not found'}, status=404)
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    @staticmethod
    def delete_employee(request, data):
        """Delete an employee"""
        employee_id = data.get('id')

        if not employee_id:
            return JsonResponse({'success': False, 'message': 'Employee ID is required'}, status=400)

        try:
            employee = Employee.objects.get(id=employee_id)
            employee.delete()

            return JsonResponse({
                'success': True,
                'message': 'Employee deleted successfully'
            })

        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Employee not found'}, status=404)