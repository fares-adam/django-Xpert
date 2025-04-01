from django.core.management.base import BaseCommand
from user.models import User

class Command(BaseCommand):
    help = 'Creates a default application admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin',
                role='admin',
                is_staff = 1,
                is_active=1
            )
            self.stdout.write(self.style.SUCCESS('Default application admin created'))
        else:
            self.stdout.write(self.style.WARNING('Application admin already exists'))