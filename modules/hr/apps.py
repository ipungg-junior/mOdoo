from django.apps import AppConfig

class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.hr'
    label = 'hr'
    
    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Employee

        # Create permissions
        content_type = ContentType.objects.get_for_model(Employee)
        permissions = [
            Permission.objects.get_or_create(
                codename='view_employee',
                name='Can view employee',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='add_employee',
                name='Can add employee',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='change_employee',
                name='Can change employee',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='delete_employee',
                name='Can delete employee',
                content_type=content_type,
            )[0],
        ]

        # Create groups and assign permissions
        manager_group, _ = Group.objects.get_or_create(name='manager')
        manager_group.permissions.set(permissions)

        user_group, _ = Group.objects.get_or_create(name='user')
        user_group.permissions.set([
            permissions[0],  # view
            permissions[1],  # add
            permissions[2],  # change
        ])
