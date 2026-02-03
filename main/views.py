from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from service.forms import ProjectForm, TaskForm
from service.models import Project


@login_required
def dashboard(request):
    projects = (
        Project.objects.filter(owner=request.user).prefetch_related("tasks").order_by("-created_at")
    )
    project_form = ProjectForm(owner=request.user)
    task_form = TaskForm()
    due_soon_cutoff = timezone.localdate() + timezone.timedelta(days=1)
    return render(
        request,
        "main/dashboard.html",
        {
            "projects": projects,
            "project_form": project_form,
            "task_form": task_form,
            "due_soon_cutoff": due_soon_cutoff,
        },
    )
