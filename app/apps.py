# Core Django imports
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        import app.signals  # Import signals when app is ready
