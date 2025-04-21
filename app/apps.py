from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        # Import signals to register them
        import notifications.signals