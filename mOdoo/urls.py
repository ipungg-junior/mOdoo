
from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from django.conf import settings
import os
from pathlib import Path

def get_dynamic_urlpatterns():
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('module/', include('engine.urls')),
    ]

    if apps.is_installed('engine') and 'engine' in settings.INSTALLED_APPS:
        try:
            from engine.models import Module
            installed_modules = Module.objects.filter(is_installed=True)
            for module in installed_modules:
                try:
                    urlpatterns.append(path(f'{module.name}/', include(f'modules.{module.name}.urls')))
                except ImportError:
                    pass
        except:
            # Database not ready yet, scan modules directory 
            BASE_DIR = Path(__file__).resolve().parent.parent
            modules_dir = BASE_DIR / 'modules'
            if modules_dir.exists():
                for module_name in os.listdir(modules_dir):
                    module_path = modules_dir / module_name
                    if os.path.isdir(module_path) and os.path.exists(module_path / '__init__.py'):
                        try:
                            urlpatterns.append(path(f'{module_name}/', include(f'modules.{module_name}.urls')))
                        except ImportError:
                            pass

    return urlpatterns

urlpatterns = get_dynamic_urlpatterns()
