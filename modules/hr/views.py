from django.shortcuts import render, redirect
from django.views import View
from .models import Employee
from django.contrib.auth.mixins import PermissionRequiredMixin

class Landing(PermissionRequiredMixin, View):
    permission_required = ['hr.view_employee']
    def get(self, request):
        employees = Employee.objects.all()
        return render(request, 'hr_list.html', {'employees': employees})