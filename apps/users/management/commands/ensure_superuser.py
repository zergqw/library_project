import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates or updates a superuser from environment variables.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    'DJANGO_SUPERUSER_PASSWORD is not set. Superuser creation skipped.'
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )
        user.set_password(password)
        user.save(update_fields=['password'])

        action = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" {action}.'))
