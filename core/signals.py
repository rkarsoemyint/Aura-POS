from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_user_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from .models import Product, Category

    manager_group, _ = Group.objects.get_or_create(name='Manager')
    cashier_group, _ = Group.objects.get_or_create(name='Cashier')

    prod_ct = ContentType.objects.get_for_model(Product)
    cat_ct = ContentType.objects.get_for_model(Category)
    
    manager_permissions = Permission.objects.filter(content_type__in=[prod_ct, cat_ct])

    manager_group.permissions.set(manager_permissions)

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        post_migrate.connect(create_user_groups, sender=self)