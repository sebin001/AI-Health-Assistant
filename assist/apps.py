from django.apps import AppConfig


class AssistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assist"

    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()