
from django.db import models
from users.models import User

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects",)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="uniq_project_name_per_owner",)]

    def __str__(self) -> str:
        return f"{self.name} ({self.owner_id})"


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks",)
    name = models.CharField(max_length=255)
    is_done = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_done", "priority", "-created_at"]
        indexes = [
            models.Index(fields=["project", "priority"]),
            models.Index(fields=["project", "is_done"]),
        ]

    def __str__(self) -> str:
        return self.name