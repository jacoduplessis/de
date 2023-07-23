from django.test import TestCase
from django.core.management import call_command
# Create your tests here.
from defects.models import Incident
from auditlog.models import LogEntry
from django.urls import reverse
from django.contrib.auth.models import User

class TestAuditLog(TestCase):

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



