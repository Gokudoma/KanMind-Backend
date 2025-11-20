from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register(r'boards', views.BoardViewSet, basename='board')
router.register(r'tasks', views.TaskViewSet, basename='task')
tasks_router = routers.NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', views.CommentViewSet, basename='task-comments')

urlpatterns = [
    path(
        'tasks/assigned-to-me/',
        views.AssignedTasksView.as_view(),
        name='tasks-assigned'
    ),
    path(
        'tasks/reviewing/',
        views.ReviewingTasksView.as_view(),
        name='tasks-reviewing'
    ),

    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]