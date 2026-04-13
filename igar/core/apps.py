"""Django app configuration for igar.core."""

from django.apps import AppConfig


class IgarCoreConfig(AppConfig):
    """Configuration for the igar.core app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'igar.core'
    label = 'igar_core'
    verbose_name = 'Igar Core'

    def ready(self):
        """Initialize app on Django startup."""
        # Import signals if needed
        pass
