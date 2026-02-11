from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from .forms import ProjectForm, TaskForm
from .models import Project, Task


class ProjectCreateView(LoginRequiredMixin, View):
    def get(self, request):
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        form = ProjectForm(owner=request.user)
        return render(request, "partials/project_card_new.html", {"form": form})

    def post(self, request):
        form = ProjectForm(request.POST or None, owner=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            task_form = TaskForm()
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(
                request,
                "partials/project_card.html",
                {
                    "project": project,
                    "task_form": task_form,
                    "due_soon_cutoff": _due_soon_cutoff(),
                },
            )

        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(request, "partials/project_form.html", {"form": form})


class ProjectUpdateView(LoginRequiredMixin, View):
    def get(self, request, project_id: int):
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        if request.GET.get("mode") == "view":
            return render(request, "partials/project_header.html", {"project": project})
        form = ProjectForm(instance=project, owner=request.user)
        return render(
            request,
            "partials/project_header_form.html",
            {"form": form, "project": project},
        )

    def post(self, request, project_id: int):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        form = ProjectForm(request.POST, instance=project, owner=request.user)
        if form.is_valid():
            project = form.save()
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(
                request,
                "partials/project_header.html",
                {"project": project},
            )
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(
            request,
            "partials/project_header_form.html",
            {"form": form, "project": project},
        )


class ProjectDeleteView(LoginRequiredMixin, View):
    def post(self, request, project_id: int):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        project.delete()
        if not Project.objects.filter(owner=request.user).exists():
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(request, "partials/project_empty.html")
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return HttpResponse("")


class TaskCreateView(LoginRequiredMixin, View):
    def post(self, request, project_id: int):
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
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(
                request,
                "partials/task_row.html",
                {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
            )

        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(request, "partials/task_form.html", {"form": form, "project": project})


class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, task_id: int):
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        task = get_object_or_404(Task, id=task_id, project__owner=request.user)
        form = TaskForm(instance=task)
        return render(request, "partials/task_form.html", {"form": form, "task": task})

    def post(self, request, task_id: int):
        task = get_object_or_404(Task, id=task_id, project__owner=request.user)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(
                request,
                "partials/task_row.html",
                {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
            )
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(request, "partials/task_form.html", {"form": form, "task": task})


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, task_id: int):
        task = get_object_or_404(Task, id=task_id, project__owner=request.user)
        project = task.project
        task.delete()
        if project and not project.tasks.exists():
            if not getattr(request, "htmx", False):
                return redirect("main:dashboard")
            return render(request, "partials/task_empty.html", {"project": project})
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return HttpResponse("")


class TaskToggleDoneView(LoginRequiredMixin, View):
    def post(self, request, task_id: int):
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
        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(
            request,
            "partials/task_row.html",
            {"task": task, "due_soon_cutoff": _due_soon_cutoff()},
        )


class TaskMoveView(LoginRequiredMixin, View):
    def post(self, request, task_id: int, direction: str):
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

        if not getattr(request, "htmx", False):
            return redirect("main:dashboard")
        return render(
            request,
            "partials/task_list.html",
            {"project": task.project, "due_soon_cutoff": _due_soon_cutoff()},
        )


def _due_soon_cutoff():
    # Date threshold for "due soon" (today + 1 day).
    return timezone.localdate() + timezone.timedelta(days=1)
