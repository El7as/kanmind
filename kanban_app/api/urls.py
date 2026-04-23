from rest_framework.routers import DefaultRouter

from django.urls import path


from kanban_app.api.views import BoardViewSet, TaskAssignedToMeView, TaskReviewerView, TaskViewSet, TaskCommentView



router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
router.register('tasks', TaskViewSet, basename='tasks')


urlpatterns = [
    path('tasks/assigned-to-me/', TaskAssignedToMeView.as_view()),
    path('tasks/reviewing/', TaskReviewerView.as_view()),
    path('tasks/<int:task_id>/comments/', TaskCommentView.as_view()),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentView.as_view()),
]

urlpatterns += router.urls


"""
URL configuration for the Kanban API.

This module defines all API endpoints for boards, tasks, comments,
and user‑specific task views. It combines DRF routers for ViewSets
with manually defined paths for custom API endpoints.

Endpoints:
    /boards/                     - CRUD operations for boards
    /tasks/                      - CRUD operations for tasks
    /tasks/assigned-to-me/       - Lists tasks assigned to the current user
    /tasks/reviewing/            - Lists tasks where the user is reviewer
    /tasks/<task_id>/comments/   - List and create comments for a task
    /tasks/<task_id>/comments/<comment_id>/ - Retrieve or delete a comment
"""



