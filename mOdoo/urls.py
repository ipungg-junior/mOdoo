
from django.contrib import admin
from django.urls import path, include
from django.apps import apps
from django.conf import settings
from django.urls.resolvers import get_resolver
import os
import importlib
import sys
from pathlib import Path

# Simpen last urlpatterns (after install module)
_current_urlpatterns = None

def get_dynamic_urlpatterns():
    global _current_urlpatterns

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('engine.urls')),
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

    _current_urlpatterns = urlpatterns
    return urlpatterns

def update_urlpatterns():
    global _current_urlpatterns

    # Mulai ulang runtime breeee
    if 'mOdoo.urls' in sys.modules:
        importlib.reload(sys.modules['mOdoo.urls'])
        
    _current_urlpatterns = get_dynamic_urlpatterns()
    resolver = get_resolver()
    resolver.url_patterns = _current_urlpatterns

urlpatterns = get_dynamic_urlpatterns()
