from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .forms import ProjectForm, TaskForm
from .models import Project, Task


def _is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


@login_required
def project_create(request):
    if request.method == "GET":
        form = ProjectForm(owner=request.user)
        return render(request, "partials/project_card_new.html", {"form": form})
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
            {
                "project": project,
                "task_form": task_form,
                "due_soon_cutoff": _due_soon_cutoff(),
            },
        )

    # Повертаємо форму з помилками
    return render(request, "partials/project_form.html", {"form": form})


@login_required
def project_update(request, project_id: int):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == "GET":
        if request.GET.get("mode") == "view":
            return render(request, "partials/project_header.html", {"project": project})
        form = ProjectForm(instance=project, owner=request.user)
        return render(
            request,
            "partials/project_header_form.html",
            {"form": form, "project": project},
        )

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project, owner=request.user)
        if form.is_valid():
            project = form.save()
            return render(
                request,
                "partials/project_header.html",
                {"project": project},
            )
        return render(
            request,
            "partials/project_header_form.html",
            {"form": form, "project": project},
        )

    return HttpResponseBadRequest("Unsupported method")


@login_required
def project_delete(request, project_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.delete()
    if not Project.objects.filter(owner=request.user).exists():
        return render(request, "partials/project_empty.html")
    return HttpResponse("")


@login_required
def task_create(request, project_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    project = get_object_or_404(Project, id=project_id, owner=request.user)

    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        max_priority = (
            Task.objects.filter(project=project, is_done=False).aggregate(Max("priority"))[
                "priority__max"
            ]
            or 0
        )
        task.priority = max_priority + 1
        task.save()
        return render(
            request,
            "partials/task_row.html",
            {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
        )

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
            return render(
                request,
                "partials/task_row.html",
                {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
            )
        return render(request, "partials/task_form.html", {"form": form, "task": task})

    return HttpResponseBadRequest("Unsupported method")


@login_required
def task_delete(request, task_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    project = task.project
    task.delete()
    if project and not project.tasks.exists():
        return render(request, "partials/task_empty.html", {"project": project})
    return HttpResponse("")


@login_required
def task_toggle_done(request, task_id: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    task.is_done = not task.is_done
    max_priority = (
        Task.objects.filter(project=task.project, is_done=task.is_done).aggregate(Max("priority"))[
            "priority__max"
        ]
        or 0
    )
    task.priority = max_priority + 1
    task.save(update_fields=["is_done", "priority"])
    return render(
        request,
        "partials/task_row.html",
        {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
    )


@login_required
def task_move(request, task_id: int, direction: str):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    if direction not in {"up", "down"}:
        return HttpResponseBadRequest("Invalid direction")

    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    with transaction.atomic():
        tasks = list(
            Task.objects.select_for_update()
            .filter(project=task.project, is_done=task.is_done)
            .order_by("priority", "created_at", "id")
        )
        try:
            index = next(i for i, item in enumerate(tasks) if item.id == task.id)
        except StopIteration:
            return HttpResponseBadRequest("Task not found")

        if direction == "up" and index > 0:
            prev_task = tasks[index - 1]
            task.priority, prev_task.priority = prev_task.priority, task.priority
            task.save(update_fields=["priority"])
            prev_task.save(update_fields=["priority"])
        elif direction == "down" and index < len(tasks) - 1:
            next_task = tasks[index + 1]
            task.priority, next_task.priority = next_task.priority, task.priority
            task.save(update_fields=["priority"])
            next_task.save(update_fields=["priority"])

    return render(
        request,
        "partials/task_list.html",
        {"project": task.project, "due_soon_cutoff": _due_soon_cutoff()},
    )


def _due_soon_cutoff():
    return timezone.localdate() + timezone.timedelta(days=1)
