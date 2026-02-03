from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user1",
            password="pass12345",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("main:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_dashboard_shows_projects_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("main:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task manager")
