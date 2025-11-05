from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from .models import Module
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def login_view(request):
    if request.user.is_authenticated:
        return redirect('module_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('module_list')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def module_list(request):
    modules = []
    modules_dir = BASE_DIR / 'modules'
    if modules_dir.exists():
        for module_name in os.listdir(modules_dir):
            module_path = modules_dir / module_name
            if os.path.isdir(module_path) and os.path.exists(module_path / '__init__.py'):
                module_obj, created = Module.objects.get_or_create(name=module_name)
                modules.append(module_obj)
    return render(request, 'module_list.html', {'modules': modules})

@login_required
def install_module(request, module_name):
    module = get_object_or_404(Module, name=module_name)
    if not module.is_installed:
        try:
            call_command('makemigrations', f'modules.{module_name}')
            call_command('migrate', f'modules.{module_name}')
            module.is_installed = True
            module.save()
            messages.success(request, f'Module {module_name} installed successfully.')
        except Exception as e:
            messages.error(request, f'Failed to install module {module_name}: {str(e)}')
    else:
        messages.warning(request, f'Module {module_name} is already installed.')
    return redirect('module_list')

@login_required
def uninstall_module(request, module_name):
    module = get_object_or_404(Module, name=module_name)
    if module.is_installed:
        module.is_installed = False
        module.save()
        messages.success(request, f'Module {module_name} uninstalled successfully.')
    else:
        messages.warning(request, f'Module {module_name} is not installed.')
    return redirect('module_list')

@login_required
def upgrade_module(request, module_name):
    module = get_object_or_404(Module, name=module_name)
    if module.is_installed:
        try:
            call_command('makemigrations', f'modules.{module_name}')
            call_command('migrate', f'modules.{module_name}')
            messages.success(request, f'Module {module_name} upgraded successfully.')
        except Exception as e:
            messages.error(request, f'Failed to upgrade module {module_name}: {str(e)}')
    else:
        messages.warning(request, f'Module {module_name} is not installed.')
    return redirect('module_list')
