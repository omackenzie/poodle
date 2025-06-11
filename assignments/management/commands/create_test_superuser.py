from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create a superuser for testing purposes'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = 'admin'
        password = 'password'
        email = 'admin@example.com'
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created superuser "{username}" with password "{password}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Superuser "{username}" already exists'
                    )
                )
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating superuser: {e}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Unexpected error: {e}'
                )
            )
