from rest_framework.routers import DefaultRouter

from django.urls import path


from kanban_app.api.views import BoardViewSet, TaskAssignedToMeView, TaskReviewerView, TaskViewSet, TaskCommentView



router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
router.register('tasks', TaskViewSet, basename='tasks')


urlpatterns = [
    path('tasks-assigned-to-me/', TaskAssignedToMeView.as_view(), name='tasks-assigned-to-me'),
    path('tasks-reviewing/', TaskReviewerView.as_view(), name='tasks-reviewing'),
    path('tasks/<int:task_id>/comments/', TaskCommentView.as_view()),
    path('tasks/<int:task_id>/comments/comments<id>/', TaskCommentView.as_view()),
]

urlpatterns += router.urls



