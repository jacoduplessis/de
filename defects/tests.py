from django.test import TestCase
from django.core.management import call_command

# Create your tests here.
from defects.models import Incident, Approval
from defects.actions import get_user_actions, Urgency
from auditlog.models import LogEntry
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta


class TestAuditLog(TestCase):
    fixtures = [
        "defects/fixtures/groups.json",
        "defects/fixtures/users.json",
    ]

    def setUp(self):
        call_command("generate_example_data")
        self.incident = Incident.objects.first()
        self.user = User.objects.create_user(username="test", password="test")
        self.client.force_login(self.user)

    def test_incident_detail_view_adds_accessed_log_entry(self):
        self.assertEqual(self.incident.history.count(), 0)
        url = reverse("incident_detail", args=[self.incident.pk])
        self.client.get(url)
        self.assertEqual(self.incident.history.count(), 1)
        self.assertEqual(self.incident.history.last().action, LogEntry.Action.ACCESS)


class TestApprovals(TestCase):
    fixtures = [
        "defects/fixtures/groups.json",
        "defects/fixtures/users.json",
    ]

    def test_notification_approval_updates_time(self):
        re_user = User.objects.get(username="reliability_engineer")
        sem_user = User.objects.get(username="section_engineering_manager")

        incident = Incident.objects.create(created_by=re_user, time_start=now(), code=Incident.generate_incident_code("TEST"))
        approval = Approval.objects.create(user=sem_user, created_by=re_user, incident=incident, type=Approval.NOTIFICATION)

        self.assertIsNone(incident.notification_time_approved)

        self.client.force_login(sem_user)

        url = reverse("approval_detail", args=[approval.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {
                "outcome": Approval.ACCEPTED,
                "comment": "test",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        incident.refresh_from_db()
        self.assertIsNotNone(incident.notification_time_approved)


class TestUserActions(TestCase):
    fixtures = [
        "defects/fixtures/groups.json",
        "defects/fixtures/users.json",
    ]

    def test_notification_user_action(self):
        re_user = User.objects.get(username="reliability_engineer")
        incident = Incident.objects.create(created_by=re_user, time_start=now(), time_end=now(), code=Incident.generate_incident_code("TEST"))

        ua = get_user_actions(re_user)
        self.assertEqual(len(ua), 1)
        action = ua[0]

        self.assertEqual(action.incident.id, incident.id)
        self.assertIn("notification", action.message.lower())
        self.assertEqual(action.urgency, Urgency.INFO)

        incident.time_start = now() - timedelta(hours=22)
        incident.time_end = now() - timedelta(hours=22)
        incident.save()
        self.assertEqual(get_user_actions(re_user)[0].urgency, Urgency.INFO)

        incident.time_start = now() - timedelta(hours=25)
        incident.time_end = now() - timedelta(hours=25)
        incident.save()
        self.assertEqual(get_user_actions(re_user)[0].urgency, Urgency.WARNING)

        incident.time_start = now() - timedelta(hours=50)
        incident.time_end = now() - timedelta(hours=50)
        incident.save()
        self.assertEqual(get_user_actions(re_user)[0].urgency, Urgency.DANGER)


class TestIncidentCalculations(TestCase):
    def test_notification_overdue(self):
        ten_hours_ago = now() - timedelta(hours=10)
        sixty_hours_ago = now() - timedelta(hours=60)
        incident = Incident.objects.create(time_start=ten_hours_ago, time_end=ten_hours_ago, code=Incident.generate_incident_code("TEST"))
        self.assertFalse(incident.notification_overdue)
        incident.time_start = sixty_hours_ago
        incident.time_end = sixty_hours_ago
        self.assertTrue(incident.notification_overdue)
        incident.notification_time_published = now()
        self.assertFalse(incident.notification_overdue)

