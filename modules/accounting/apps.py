from django.apps import AppConfig

class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.accounting'
    label = 'accounting'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import accounting

        # Create permissions
        content_type = ContentType.objects.get_for_model(accounting)
        permissions = [
            Permission.objects.get_or_create(
                codename='view_accounting',
                name='Can view accounting',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='add_accounting',
                name='Can add accounting',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='change_accounting',
                name='Can change accounting',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='delete_accounting',
                name='Can delete accounting',
                content_type=content_type,
            )[0],
        ]

        # Create groups and assign permissions
        manager_group, _ = Group.objects.get_or_create(name='manager')
        for p in permissions:
            manager_group.permissions.add(p.id)
        manager_group.save()

        user_group, _ = Group.objects.get_or_create(name='user')
        user_list = [permissions[0], permissions[1], permissions[2]]  # view, add, change
        for p in user_list:
            user_group.permissions.add(p.id)
        user_group.save()

        public_group, _ = Group.objects.get_or_create(name='public')
        public_group.permissions.add(permissions[0].id)  # view only
        public_group.save()