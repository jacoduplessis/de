from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.crypto import get_random_string


class Section(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SectionEngineer(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class SectionEngineeringManager(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class SeniorAssetManager(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Equipment(models.Model):
    code = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} – {self.name}"


class Incident(models.Model):
    code = models.CharField(unique=True, max_length=200)  # also known as RI_Number
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    operation = models.CharField(max_length=200, default="AMB")
    area = models.CharField(max_length=200, blank=True)
    section = models.ForeignKey(Section, blank=True, null=True, on_delete=models.SET_NULL, related_name="incidents")
    section_engineer = models.ForeignKey(SectionEngineer, blank=True, null=True, on_delete=models.SET_NULL)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    significant = models.BooleanField(default=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.TextField(blank=True)
    ri_number = models.CharField(max_length=200, blank=True)
    notification_time_received = models.DateTimeField(blank=True, null=True)
    notification_am_reviewed = models.BooleanField(default=False)
    notification_circulated = models.BooleanField(default=False)
    notification_file = models.FileField(blank=True)
    close_out_file = models.FileField(blank=True)
    report_file = models.FileField(blank=True)
    production_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=10, default=Decimal("0.00"))
    rand_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=2, default=Decimal("0.00"))
    possible_effect = models.TextField(blank=True)
    immediate_action_taken = models.TextField(blank=True)
    remaining_risk = models.TextField(blank=True)


    @classmethod
    def generate_incident_code(cls):
        return get_random_string(length=12)


class Solution(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True)
    reliability_incident_name = models.CharField(max_length=500, blank=True)
    priority = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500)
    person_responsible = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=200, blank=True)
    planned_completion_date = models.DateField(blank=True, null=True)
    planned_completion_date_string = models.CharField(max_length=200, blank=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    actual_completion_date_string = models.CharField(max_length=200, blank=True)
    incident_date_string = models.CharField(max_length=200, blank=True)
    dr_number = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)
    area = models.CharField(max_length=200, blank=True)


class Approval(models.Model):
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    OUTCOME_CHOICES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )

    NOTIFICATION = "notification"
    RCA = "rca"

    TYPE_CHOICES = (
        (NOTIFICATION, "Notification"),
        (RCA, "RCA"),
    )

    ENGINEERING_MANAGER = "engineering_manager"
    SECTION_ENGINEERING_MANAGER = "section_engineering_manager"
    SENIOR_ASSET_MANAGER = "senior_asset_manager"

    ROLE_CHOICES = (
        (ENGINEERING_MANAGER, "EM"),
        (SECTION_ENGINEERING_MANAGER, "SEM"),
        (SENIOR_ASSET_MANAGER, "Senior AM"),
    )

    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    outcome = models.CharField(max_length=100, choices=OUTCOME_CHOICES)
    comment = models.TextField(blank=True)


class UserAction(models.Model):
    """
    Stores actions that users are required to perform.

    Used to populate the actions on the dashboard page.
    """

    time_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    time_required = models.DateTimeField(blank=True, null=True)
    time_dismissed = models.DateTimeField(blank=True, null=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)

    @property
    def urgency(self):
        """
        Three possible classes: info, warning, danger
        """
        if not self.time_required:
            return "info"

        time_remaining = self.time_required - now()

        if time_remaining > timedelta(days=2):
            return "info"

        elif time_remaining > timedelta(hours=1):
            return "warning"

        return "danger"
