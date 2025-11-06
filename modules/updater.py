import importlib
import sys
from pathlib import Path
from django.urls.resolvers import get_resolver
from django.core.management import call_command
from django.contrib import messages
from django.apps import apps
from django.conf import settings
from django.template import engines
from engine.models import Module
from mOdoo.urls import get_dynamic_urlpatterns

class ModuleUpdater:

    @staticmethod
    def reload_file(module_name):
        
        modules_to_reload = [
            f'modules.{module_name}',
            f'modules.{module_name}.models',
            f'modules.{module_name}.views',
            f'modules.{module_name}.forms',
            f'modules.{module_name}.urls',
            f'modules.{module_name}.apps',
        ]

        reloaded = []
        for module_path in modules_to_reload:
            try:
                if module_path in sys.modules:
                    importlib.reload(sys.modules[module_path])
                    reloaded.append(module_path)
                    print(f'Reloaded: {module_path}')
                else:
                    # Kalo belum diimport, import dulu
                    importlib.import_module(module_path)
                    reloaded.append(module_path)
                    print(f'Imported: {module_path}')
            except ImportError as e:
                print(f'Could not reload {module_path}: {e}')
            except Exception as e:
                print(f'Error reloading {module_path}: {e}')

        return reloaded

    @staticmethod
    def reload_url_patterns():

        try:
            # Reload base urls module
            if 'mOdoo.urls' in sys.modules:
                importlib.reload(sys.modules['mOdoo.urls'])

            # Force URL resolver to reload
            resolver = get_resolver()
            resolver.url_patterns = get_dynamic_urlpatterns()
            print('URL patterns reloaded successfully')
            return True
        except Exception as e:
            print(f'Error reloading URL patterns: {e}')
            return False

    @staticmethod
    def reload_templates():
        
        try:
            from django.template import engines
            from django.template.loaders.filesystem import Loader as FilesystemLoader
            from django.template.loaders.app_directories import Loader as AppDirectoriesLoader
            from django.core.cache import cache

            # Clear Django's general cache
            cache.clear()

            # Clear template caches for all engines
            for engine in engines.all():
                if hasattr(engine, 'cache'):
                    engine.cache.clear()

                # Clear template loader caches
                if hasattr(engine, 'template_loaders'):
                    for loader in engine.template_loaders:
                        if hasattr(loader, 'cache'):
                            loader.cache.clear()
                        if hasattr(loader, 'reset'):
                            loader.reset()
                        # Force template rediscovery for filesystem and app directories loaders
                        if isinstance(loader, (FilesystemLoader, AppDirectoriesLoader)):
                            if hasattr(loader, '_cached_templates'):
                                loader._cached_templates = {}
                            if hasattr(loader, '_template_cache'):
                                loader._template_cache = {}

            # Force template rediscovery by clearing template source caches
            from django.template.base import Template
            if hasattr(Template, 'template_cache'):
                Template.template_cache.clear()

            print('Template caches cleared successfully')
            return True
        except Exception as e:
            print(f'Error clearing template caches: {e}')
            return False

    @staticmethod
    def reload_app_config(module_name):
        
        try:
            app_config_path = f'modules.{module_name}.apps'
            if app_config_path in sys.modules:
                importlib.reload(sys.modules[app_config_path])
                print(f'App config reloaded: {app_config_path}')
                return True
            else:
                importlib.import_module(sys.modules[app_config_path])
                print(f'New import module config runtime: {app_config_path}')
                return True
        except Exception as e:
            print(f'Error reloading app config: {e}')
        return False

    @staticmethod
    def install_module(module_name, request=None):
        """
        Install a module with full runtime reloading
        """
        try:
            module = Module.objects.get(name=module_name)
            
            # Mark as installed
            module.is_installed = True
            module.save()

            # Reload everything
            ModuleUpdater.reload_file(module_name)
            ModuleUpdater.reload_app_config(module_name)
            ModuleUpdater.reload_url_patterns()
            ModuleUpdater.reload_module_templates(module_name)
            
            # Run migrations for the app label
            call_command('makemigrations', module_name)
            call_command('migrate', module_name)

            print(f'Module {module_name} installed with runtime reload')
            return True

        except Exception as e:
            error_msg = f'Failed to install module {module_name}: {str(e)}'
            if request:
                messages.error(request, error_msg)
            print(error_msg)
            return False

    @staticmethod
    def uninstall_module(module_name, request=None):
        """
        Uninstall a module with cleanup
        """
        try:
            module = Module.objects.get(name=module_name)
            module.is_installed = False
            module.save()

            # Reload URL patterns to remove module URLs
            ModuleUpdater.reload_url_patterns()

            if request:
                messages.success(request, f'Module {module_name} uninstalled successfully.')

            print(f'Module {module_name} uninstalled')
            return True

        except Exception as e:
            error_msg = f'Failed to uninstall module {module_name}: {str(e)}'
            print(error_msg)
            return False

    @staticmethod
    def upgrade_module(module_name, request=None):
        try:
            module = Module.objects.get(name=module_name)

            if not module.is_installed:
                if request:
                    messages.warning(request, f'Module {module_name} is not installed.')
                return False

            # Reload all module files and configs
            ModuleUpdater.reload_file(module_name)
            ModuleUpdater.reload_app_config(module_name)
            ModuleUpdater.reload_url_patterns()
            ModuleUpdater.reload_module_templates(module_name)

            # Run migrations for the app label
            call_command('makemigrations', module_name)
            call_command('migrate', module_name)

            print(f'Module {module_name} upgraded with runtime reload')
            return True

        except Exception as e:
            error_msg = f'Failed to upgrade module {module_name}: {str(e)}'
            if request:
                messages.error(request, error_msg)
            print(error_msg)
            return False

    @staticmethod
    def reload_all_modules():

        try:
            installed_modules = Module.objects.filter(is_installed=True)
            for module in installed_modules:
                ModuleUpdater.reload_file(module.name)
                ModuleUpdater.reload_app_config(module.name)

            ModuleUpdater.reload_url_patterns()
            ModuleUpdater.reload_templates()
            print('All modules reloaded successfully')
            return True

        except Exception as e:
            print(f'Error reloading all modules: {e}')
            return False

    @staticmethod
    def reload_module_templates(module_name):
        
        try:
            # Clear template caches
            ModuleUpdater.reload_templates()

            # Force template re-discovery by clearing origin cache
            from django.template.loaders.app_directories import Loader as AppLoader

            for engine in engines.all():
                if hasattr(engine, 'template_loaders'):
                    for loader in engine.template_loaders:
                        if isinstance(loader, AppLoader):
                            # Clear the origin cache which stores template locations
                            if hasattr(loader, 'origin_cache'):
                                loader.origin_cache.clear()
                            # Reset template cache
                            if hasattr(loader, 'template_cache'):
                                loader.template_cache.clear()
                        if hasattr(loader, 'reset'):
                            loader.reset()

            print(f'Templates reloaded for module: {module_name}')
            return True
        except Exception as e:
            print(f'Error reloading templates for {module_name}: {e}')
            return False