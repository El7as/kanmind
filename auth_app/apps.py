from django.apps import AppConfig


class AuthAppConfig(AppConfig):

    """
    Application configuration for the authentication app.

    This class defines metadata and initialization behavior for the
    `auth_app` Django application. Django automatically loads this
    configuration when the app is included in INSTALLED_APPS.

    Attributes:
        name (str): The full Python path to the application.
    """

    name = 'auth_app'
