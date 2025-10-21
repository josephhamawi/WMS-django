import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_inventory.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('admin123')
admin.save()
print('Admin password set to: admin123')
print('Username: admin')
print('Access admin at: http://127.0.0.1:8000/admin/')
