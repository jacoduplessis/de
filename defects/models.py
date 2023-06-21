from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


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
    code = models.CharField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} – {self.name}"


class ReliabilityIncident(models.Model):
    operation = models.CharField(max_length=200, default="AMB")
    area = models.CharField(max_length=200, blank=True)
    section = models.CharField(max_length=200, blank=True)
    section_engineer = models.CharField(max_length=200, blank=True)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    significant = models.BooleanField(default=False)
    equipment = models.CharField(max_length=200, blank=True)
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


class Solution(models.Model):
    reliability_incident = models.ForeignKey(ReliabilityIncident, on_delete=models.SET_NULL, null=True, blank=True)
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

    reliability_incident = models.ForeignKey(ReliabilityIncident, on_delete=models.SET_NULL, null=True)

    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    outcome = models.CharField(max_length=100, choices=OUTCOME_CHOICES)
    comment = models.TextField(blank=True)
