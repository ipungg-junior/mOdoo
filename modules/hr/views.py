from django.shortcuts import render, redirect
from django.views import View
from .models import Employee
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

class EmployeeListView(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    group_required = ['group_access_hr']

    def get(self, request):
        if not request.user.groups.filter(name__in=self.group_required).exists():
            raise PermissionDenied
        employees = Employee.objects.select_related('user').all()
        return render(request, 'hr_list.html', {'employees': employees})

class SyncEmployeesView(PermissionRequiredMixin, View):
    permission_required = ['hr.add_employee']
    group_required = ['group_access_hr']

    def get(self, request):
        if not request.user.groups.filter(name__in=self.group_required).exists():
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