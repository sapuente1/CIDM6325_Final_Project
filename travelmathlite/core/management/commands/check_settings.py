"""Management command to print key settings for quick ops checks."""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Prints a concise summary of important Django settings for quick inspection."

    def handle(self, *args, **options):
        self.stdout.write("Settings quick-check:\n")
        self.stdout.write(f"DJANGO_SETTINGS_MODULE: {settings.SETTINGS_MODULE}\n")
        self.stdout.write(f"DEBUG: {getattr(settings, 'DEBUG', None)}\n")
        self.stdout.write(f"ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', None)}\n")
        self.stdout.write(
            f"SECRET_KEY present: {bool(getattr(settings, 'SECRET_KEY', None) and 'change-me' not in getattr(settings, 'SECRET_KEY'))}\n"
        )
        self.stdout.write(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', None)}\n")
        self.stdout.write(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', None)}\n")
        self.stdout.write(f"USE_WHITENOISE: {getattr(settings, 'USE_WHITENOISE', None)}\n")
        self.stdout.write(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', None)}\n")
        self.stdout.write(f"MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', None)}\n")
        self.stdout.write("\nNote: This command is a quick operator aid and does not change any config.")
