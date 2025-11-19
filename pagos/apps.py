from django.apps import AppConfig


class PagosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pagos'
    def ready(self):
        # import signals to ensure they are registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
