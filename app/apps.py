# Core Django imports
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    verbose_name = "School Management System"

    def ready(self):
        """
        Import signals when the app is ready
        """
        # Import signals to ensure they are registered
        import app.signals
