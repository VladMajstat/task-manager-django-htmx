from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from service.forms import ProjectForm, TaskForm
from service.models import Project


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "main/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = (
            Project.objects.filter(owner=self.request.user)
            .prefetch_related("tasks")
            .order_by("-created_at")
        )
        context.update(
            {
                "projects": projects,
                "project_form": ProjectForm(owner=self.request.user),
                "task_form": TaskForm(),
                "due_soon_cutoff": timezone.localdate() + timezone.timedelta(days=1),
            }
        )
        return context
