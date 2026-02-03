from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Project, Task


class ProjectTaskFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner",
            password="pass12345",
        )
        self.other = get_user_model().objects.create_user(
            username="other",
            password="pass12345",
        )
        self.client.force_login(self.user)

    def test_create_project(self):
        response = self.client.post(reverse("service:project_create"), {"name": "Inbox"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Project.objects.filter(owner=self.user, name="Inbox").exists())

    def test_project_name_required(self):
        response = self.client.post(reverse("service:project_create"), {"name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_project_name_unique_per_owner(self):
        Project.objects.create(owner=self.user, name="Inbox")
        response = self.client.post(reverse("service:project_create"), {"name": "Inbox"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You already have a project with this name.")

    def test_project_update(self):
        project = Project.objects.create(owner=self.user, name="Old")
        response = self.client.post(
            reverse("service:project_update", args=[project.id]),
            {"name": "New"},
        )
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.name, "New")

    def test_project_delete_only_owner(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        self.client.force_login(self.other)
        response = self.client.post(reverse("service:project_delete", args=[project.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Project.objects.filter(id=project.id).exists())

    def test_project_delete_last_returns_empty_state(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        response = self.client.post(reverse("service:project_delete", args=[project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects yet.")

    def test_task_create_sets_priority(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        response = self.client.post(
            reverse("service:task_create", args=[project.id]),
            {"name": "First task"},
        )
        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(project=project, name="First task")
        self.assertEqual(task.priority, 1)

    def test_task_create_for_other_owner_forbidden(self):
        project = Project.objects.create(owner=self.other, name="Other")
        response = self.client.post(
            reverse("service:task_create", args=[project.id]),
            {"name": "Nope"},
        )
        self.assertEqual(response.status_code, 404)

    def test_task_update_deadline_validation(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        task = Task.objects.create(project=project, name="Task")
        past_date = timezone.localdate() - timedelta(days=1)
        response = self.client.post(
            reverse("service:task_update", args=[task.id]),
            {"name": "Task", "deadline": past_date.isoformat()},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deadline cannot be in the past.")

    def test_task_update_only_owner(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        task = Task.objects.create(project=project, name="Task")
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("service:task_update", args=[task.id]),
            {"name": "Other"},
        )
        self.assertEqual(response.status_code, 404)

    def test_task_toggle_done(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        task = Task.objects.create(project=project, name="Task")
        response = self.client.post(reverse("service:task_toggle_done", args=[task.id]))
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertTrue(task.is_done)

    def test_task_move_up(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        first = Task.objects.create(project=project, name="First", priority=1)
        second = Task.objects.create(project=project, name="Second", priority=2)
        response = self.client.post(reverse("service:task_move", args=[second.id, "up"]))
        self.assertEqual(response.status_code, 200)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.priority, 2)
        self.assertEqual(second.priority, 1)

    def test_task_delete_last_returns_empty_state(self):
        project = Project.objects.create(owner=self.user, name="Inbox")
        task = Task.objects.create(project=project, name="Task")
        response = self.client.post(reverse("service:task_delete", args=[task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No tasks yet.")
