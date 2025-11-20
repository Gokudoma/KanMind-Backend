from django.apps import AppConfig


class KanbanBoardAppConfig(AppConfig):
    """
    Configuration for the Kanban board application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kanban_board_app'