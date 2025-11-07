from django.apps import AppConfig
import os
from pathlib import Path


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Module

        # Get content type for Module
        content_type = ContentType.objects.get_for_model(Module)

        # Scan modules directory
        BASE_DIR = Path(__file__).resolve().parent.parent
        modules_dir = BASE_DIR / 'modules'
        if modules_dir.exists():
            for module_name in os.listdir(modules_dir):
                module_path = modules_dir / module_name
                if os.path.isdir(module_path) and os.path.exists(module_path / '__init__.py'):
                    # Create permission for accessing the module
                    perm_codename = f'access_{module_name}'
                    perm_name = f'Can access {module_name} module'
                    permission, created = Permission.objects.get_or_create(
                        codename=perm_codename,
                        name=perm_name,
                        content_type=content_type,
                    )
                    
                    # Add grouping
                    access_group, _ = Group.objects.get_or_create(name=f'group_access_{module_name}')
                    access_group.permissions.add(permission.id)
                    access_group.save()
                    
                    if created:
                        print(f'Created permission: {perm_codename}')
