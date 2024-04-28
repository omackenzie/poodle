from django.apps import AppConfig


class AssignmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assignments'

    def ready(self):
        # Import signals to ensure signal handling setup
        from .signals import delete_submission  # noqa: F401
