
from django.contrib import admin
from django.urls import path, include
from engine.models import Module

def get_dynamic_urlpatterns():
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('module/', include('engine.urls')),
    ]
    installed_modules = Module.objects.filter(is_installed=True)
    for module in installed_modules:
        try:
            urlpatterns.append(path(f'{module.name}/', include(f'modules.{module.name}.urls')))
        except ImportError:
            pass  # Module might not have urls.py
    return urlpatterns

urlpatterns = get_dynamic_urlpatterns()
