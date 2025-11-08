from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import Module
import os
from pathlib import Path
from modules.updater import ModuleUpdater
from django.core.exceptions import PermissionDenied

BASE_DIR = Path(__file__).resolve().parent.parent

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('module_list')
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('module_list')
        else:
            messages.error(request, 'Invalid username or password.')
            return self.get(request)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class ModuleListView(View):
    def get(self, request):
        modules = []
        modules_dir = BASE_DIR / 'modules'

        if modules_dir.exists():
            for module_name in os.listdir(modules_dir):
                module_path = modules_dir / module_name
                if os.path.isdir(module_path) and (module_path / '__init__.py').exists():
                    module_obj, _ = Module.objects.get_or_create(name=module_name)

                    if request.user.is_authenticated:
                        # Jika user terotentikasi, cek izin akses
                        if request.user.has_perm(f'engine.access_{module_name}'):
                            modules.append(module_obj)
                    else:
                        # Jika tidak terotentikasi, tampilkan semua modul
                        modules.append(module_obj)

        return render(request, 'module_list.html', {'modules': modules})

class InstallModuleView(View):
    def get(self, request, module_name):
        if request.user.is_superuser:
            success = ModuleUpdater.install_module(module_name, request)
            return redirect('module_list')
        else:
            raise PermissionDenied

class UninstallModuleView(View):
    def get(self, request, module_name):
        if request.user.is_superuser:
            success = ModuleUpdater.uninstall_module(module_name, request)
            return redirect('module_list')
        else:
            raise PermissionDenied

class UpgradeModuleView(View):
    def get(self, request, module_name):
        success = ModuleUpdater.upgrade_module(module_name, request)
        return redirect('module_list')