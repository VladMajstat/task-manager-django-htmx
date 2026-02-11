from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectUpdateView,
    TaskCreateView,
    TaskDeleteView,
    TaskMoveView,
    TaskToggleDoneView,
    TaskUpdateView,
)

app_name = "service"

urlpatterns = [
    # projects
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/<int:project_id>/update/", ProjectUpdateView.as_view(), name="project_update"),
    path("projects/<int:project_id>/delete/", ProjectDeleteView.as_view(), name="project_delete"),

    # tasks
    path("projects/<int:project_id>/tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:task_id>/update/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:task_id>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("tasks/<int:task_id>/toggle-done/", TaskToggleDoneView.as_view(), name="task_toggle_done"),
    path("tasks/<int:task_id>/move/<str:direction>/", TaskMoveView.as_view(), name="task_move"),
]
