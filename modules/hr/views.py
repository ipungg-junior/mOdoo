from django.shortcuts import render, redirect
from django.views import View
from .models import Employee
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

class EmployeeListView(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    group_required = ['group_access_hr']
    
    def get(self, request):
        if not request.user.groups.filter(name__in=self.group_required).exists():
            raise PermissionDenied
        employees = Employee.objects.all()
        return render(request, 'hr_list.html', {'employees': employees})