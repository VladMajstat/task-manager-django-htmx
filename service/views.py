from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from .forms import ProjectForm, TaskForm
from .models import Project, Task


def _is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


@login_required
def project_create(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    form = ProjectForm(request.POST or None, owner=request.user)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        task_form = TaskForm()
        return render(
            request,
            "partials/project_card.html",
            {"project": project, "task_form": task_form},
        )

    # Повертаємо форму з помилками
    return render(request, "partials/project_form.html", {"form": form})


@login_required
def project_update(request, project_id: int):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == "GET":
        form = ProjectForm(instance=project, owner=request.user)
        return render(request, "partials/project_form.html", {"form": form, "project": project})

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project, owner=request.user)
        if form.is_valid():
            project = form.save()
            task_form = TaskForm()
            return render(
                request,
                "partials/project_card.html",
                {"project": project, "task_form": task_form},
            )
        return render(request, "partials/project_form.html", {"form": form, "project": project})

    return HttpResponseBadRequest("Unsupported method")


@login_required
def project_delete(request, project_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.delete()
    return HttpResponse(status=204)


@login_required
def task_create(request, project_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    project = get_object_or_404(Project, id=project_id, owner=request.user)

    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.save()
        return render(request, "partials/task_row.html", {"task": task})

    return render(request, "partials/task_form.html", {"form": form, "project": project})


@login_required
def task_update(request, task_id: int):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    if request.method == "GET":
        form = TaskForm(instance=task)
        return render(request, "partials/task_form.html", {"form": form, "task": task})

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return render(request, "partials/task_row.html", {"task": task})
        return render(request, "partials/task_form.html", {"form": form, "task": task})

    return HttpResponseBadRequest("Unsupported method")


@login_required
def task_delete(request, task_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    task.delete()
    return HttpResponse(status=204)


@login_required
def task_toggle_done(request, task_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    task.is_done = not task.is_done
    task.save(update_fields=["is_done"])
    return render(request, "partials/task_row.html", {"task": task})
