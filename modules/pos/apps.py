from django.apps import AppConfig


class PosConfig(AppConfig):
    name = 'modules.pos'
    label = 'pos'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import PoSTransaction

        # Create permissions for PoS transactions
        content_type = ContentType.objects.get_for_model(PoSTransaction)

        permissions = [
            Permission.objects.get_or_create(
                codename='view_pos_transaction',
                name='Can view PoS transactions',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='add_pos_transaction',
                name='Can add PoS transactions',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='change_pos_transaction',
                name='Can change PoS transactions',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='delete_pos_transaction',
                name='Can delete PoS transactions',
                content_type=content_type,
            )[0],
        ]

        # Assign permissions to groups
        manager_group, _ = Group.objects.get_or_create(name='manager')
        user_group, _ = Group.objects.get_or_create(name='user')
        public_group, _ = Group.objects.get_or_create(name='public')

        # Manager gets all permissions
        for perm in permissions:
            manager_group.permissions.add(perm.id)

        # User gets view and add permissions
        user_group.permissions.add(permissions[0].id)  # view
        user_group.permissions.add(permissions[1].id)  # add

        # Public gets view permission
        public_group.permissions.add(permissions[0].id)  # view

        # Create cashier group for PoS operations
        cashier_group, _ = Group.objects.get_or_create(name='cashier')
        cashier_group.permissions.add(permissions[0].id)  # view
        cashier_group.permissions.add(permissions[1].id)  # add