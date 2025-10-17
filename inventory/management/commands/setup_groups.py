"""
Management command to set up user role groups for the warehouse system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Set up user role groups with appropriate permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user role groups...')

        # Define role groups
        groups_permissions = {
            'Requester': {
                'description': 'Basic users who can view inventory and create requests',
                'permissions': [
                    # View permissions
                    'view_product',
                    'view_itemrequest',
                    'view_itemrequestline',
                    # Add permissions for their own requests
                    'add_itemrequest',
                    'add_itemrequestline',
                ]
            },
            'Department Head': {
                'description': 'Department managers who can manage requests for their department',
                'permissions': [
                    # All requester permissions
                    'view_product',
                    'view_itemrequest',
                    'view_itemrequestline',
                    'add_itemrequest',
                    'add_itemrequestline',
                    # Additional permissions
                    'change_itemrequest',
                    'change_itemrequestline',
                    'delete_itemrequest',
                    'delete_itemrequestline',
                ]
            },
            'Warehouse Staff': {
                'description': 'Warehouse staff who can view all transactions',
                'permissions': [
                    # View all warehouse transactions
                    'view_product',
                    'view_itemrequest',
                    'view_itemrequestline',
                    'view_receiving',
                    'view_receivingitem',
                    'view_itemissuance',
                    'view_itemissuanceline',
                    'view_purchaseorder',
                    'view_purchaseorderitem',
                ]
            },
            'Warehouse Supervisor': {
                'description': 'Warehouse supervisors who can add items and issue items',
                'permissions': [
                    # All warehouse staff permissions
                    'view_product',
                    'view_itemrequest',
                    'view_itemrequestline',
                    'view_receiving',
                    'view_receivingitem',
                    'view_itemissuance',
                    'view_itemissuanceline',
                    'view_purchaseorder',
                    'view_purchaseorderitem',
                    # Additional permissions
                    'add_product',
                    'change_product',
                    'add_receiving',
                    'add_receivingitem',
                    'add_itemissuance',
                    'add_itemissuanceline',
                ]
            },
            'Warehouse Manager': {
                'description': 'Warehouse managers with full permissions',
                'permissions': 'all'  # Will get all permissions
            }
        }

        for group_name, group_data in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(f'Group already exists: {group_name}')
                group.permissions.clear()  # Clear existing permissions

            if group_data['permissions'] == 'all':
                # Give all permissions to Warehouse Manager
                all_permissions = Permission.objects.all()
                group.permissions.set(all_permissions)
                self.stdout.write(f'  - Assigned ALL permissions to {group_name}')
            else:
                # Assign specific permissions
                permissions_assigned = 0
                for perm_codename in group_data['permissions']:
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        group.permissions.add(permission)
                        permissions_assigned += 1
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  - Permission not found: {perm_codename}'
                            )
                        )

                self.stdout.write(f'  - Assigned {permissions_assigned} permissions to {group_name}')

        self.stdout.write(self.style.SUCCESS('\nUser role groups set up successfully!'))
        self.stdout.write('\nRole Summary:')
        self.stdout.write('- Requester: Can view inventory and create requests')
        self.stdout.write('- Department Head: Can manage requests for their department')
        self.stdout.write('- Warehouse Staff: Can view all warehouse transactions')
        self.stdout.write('- Warehouse Supervisor: Can add items and issue items (pending approval)')
        self.stdout.write('- Warehouse Manager: Has all permissions')
