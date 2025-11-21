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

        if action == 'list_employee':
            return EmployeeService.list_employees(request)
        elif action is None:
            # Default action for backward compatibility
            return EmployeeService.list_employees(request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown GET action: {action}'}, status=400)

    @staticmethod
    def process_post(request, json_request):
        """Handle POST requests for employee operations"""
        action = json_request.get('action')

        if action == 'list_employee':
            return EmployeeService.list_employees(request, json_request)
        elif action == 'create_employee':
            return EmployeeService.create_employee(request, json_request)
        elif action == 'update_employee':
            return EmployeeService.update_employee(request, json_request)
        elif action == 'delete_employee':
            return EmployeeService.delete_employee(request, json_request)
        else:
            return JsonResponse({'success': False, 'message': f'Unknown POST action: {action}'}, status=400)

    @staticmethod
    def list_employees(request, data):
        """List all employees with user information and pagination support"""
        from django.core.paginator import Paginator

        # Get pagination parameters infomation
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 10))

        # Validate page_size
        if page_size not in [5, 10, 25, 50]:
            page_size = 10

        employees = Employee.objects.select_related('user').all().order_by('user__username')
        paginator = Paginator(employees, page_size)

        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
            page = 1

        try:
            employee_data = []

            for employee in page_obj:
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
                'data': {
                    'employees': employee_data,
                    'pagination': {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'page_size': page_size,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                        'start_index': page_obj.start_index(),
                        'end_index': page_obj.end_index()
                    }
                }
                
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

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