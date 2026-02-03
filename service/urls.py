from django.urls import path

from . import views

app_name = "service"

urlpatterns = [
    # projects
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:project_id>/update/", views.project_update, name="project_update"),
    path("projects/<int:project_id>/delete/", views.project_delete, name="project_delete"),

    # tasks
    path("projects/<int:project_id>/tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:task_id>/update/", views.task_update, name="task_update"),
    path("tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<int:task_id>/toggle-done/", views.task_toggle_done, name="task_toggle_done"),
    path("tasks/<int:task_id>/move/<str:direction>/", views.task_move, name="task_move"),
]
