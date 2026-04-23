from django.apps import AppConfig


class KanbanAppConfig(AppConfig):

    """
    Application configuration for the Kanban app.

    This class defines metadata and initialization behavior for the
    `kanban_app` Django application. Django automatically loads this
    configuration when the app is included in INSTALLED_APPS.

    Attributes:
        name (str): The full Python path to the application.
    """

    name = 'kanban_app'
