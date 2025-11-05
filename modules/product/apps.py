from django.apps import AppConfig

class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.product'
    label = 'product'

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import Product

        # Create permissions
        content_type = ContentType.objects.get_for_model(Product)
        permissions = [
            Permission.objects.get_or_create(
                codename='view_product',
                name='Can view product',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='add_product',
                name='Can add product',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='change_product',
                name='Can change product',
                content_type=content_type,
            )[0],
            Permission.objects.get_or_create(
                codename='delete_product',
                name='Can delete product',
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

        public_group, _ = Group.objects.get_or_create(name='public')
        public_group.permissions.set([permissions[0]])  # view only