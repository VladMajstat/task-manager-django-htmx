from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from service.models import Project


@login_required
def dashboard(request):
    projects = (
        Project.objects.filter(owner=request.user).prefetch_related("tasks").order_by("-created_at")
    )
    return render(request, "main/dashboard.html", {"projects": projects})