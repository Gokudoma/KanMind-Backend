from django.apps import AppConfig


class UserAuthAppConfig(AppConfig):
    """
    Configuration for the user authentication application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_auth_app'