from django.contrib import admin


from kanban_app.models import Board, Column, Task



admin.site.register(Board)
"""
    Admin configuration for the Board model.

    Provides:
        - Basic list display of boards.
        - Default Django admin behavior.
    """


admin.site.register(Column)
"""
    Admin configuration for the Column model.

    Provides:
        - Display of columns with board and position.
        - Ordering by position.
    """

admin.site.register(Task)
"""
    Admin configuration for the Task model.

    Automatically sets `created_by` to the logged‑in user when a task
    is created through the Django admin interface.

    Provides:
        - Display of tasks with board, status, priority, and assignee.
        - Search and filtering options.
    """




def save_model(self, request, obj, form, change):
        
    """
        Overrides the default save behavior to automatically assign
        the logged-in user as the creator of the task when it is
        created via the Django admin interface.

        Args:
            request: The current HTTP request.
            obj (Task): The task instance being saved.
            form: The submitted form.
            change (bool): Indicates whether this is an update (True)
                           or a new object (False).
        """

    if not obj.pk:
        obj.created_by = request.user
    super().save_model(request, obj, form, change)
