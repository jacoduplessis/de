from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils.functional import cached_property

from defects.timelines import TimelineEntry

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class Operation(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class SectionEngineer(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Section Engineer"
        verbose_name_plural = "Section Engineers"


class SectionEngineeringManager(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Section Engineering Manager"
        verbose_name_plural = "Section Engineering Managers"


class SeniorAssetManager(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    code = models.CharField(unique=True, max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.code} – {self.name}"

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"


class Incident(models.Model):
    ACTIVE = "active"
    ONGOING = "ongoing"
    COMPLETE = "complete"
    OVERDUE = "overdue"
    INCOMPLETE = "incomplete"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (ONGOING, "Ongoing"),
        (COMPLETE, "Complete"),
        (OVERDUE, "Overdue"),
        (INCOMPLETE, "Incomplete"),
    )

    code = models.CharField(unique=True, max_length=200)  # also known as RI_Number
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=ACTIVE)
    operation = models.ForeignKey(Operation, null=True, blank=True, on_delete=models.SET_NULL)
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, related_name="incidents")
    section = models.ForeignKey(Section, blank=True, null=True, on_delete=models.SET_NULL, related_name="incidents")
    section_engineer = models.ForeignKey(SectionEngineer, blank=True, null=True, on_delete=models.SET_NULL)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    significant = models.BooleanField(default=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.TextField(blank=True)
    preliminary_findings = models.FileField(upload_to="files/", null=True, blank=True)
    notification_time_published = models.DateTimeField(blank=True, null=True)
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

    history = AuditlogHistoryField(delete_related=False)

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"

    def __str__(self):
        return self.code

    @classmethod
    def generate_incident_code(cls):
        allowed_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        return now().strftime("%Y%m") + "_" + get_random_string(length=6, allowed_chars=allowed_chars)

    @property
    def status_class(self):
        _map = {self.ACTIVE: "primary", self.ONGOING: "secondary", self.COMPLETE: "success", self.OVERDUE: "danger", self.INCOMPLETE: "warning"}

        return _map.get(self.status)

    @property
    def timeline(self):
        """
        select_related: created_by
        """
        entries = [
            TimelineEntry(
                icon="alert-triangle",
                title="Incident Occurrence",
                time=self.time_start,
                until=self.time_end,
                text="Downtime",
            ),
            TimelineEntry(
                icon="log-in",
                title="Incident Logged",
                time=self.time_created,
                text=f"Created by {self.created_by.email}.",
            ),
        ]

        if self.notification_time_published:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title="48-hour notification report published",
                    time=self.notification_time_published,
                    link_text="View Notification Report",
                    link_url=reverse("incident_notification", args=[self.pk]),
                )
            )
            if self.notification_approval.outcome == Approval.ACCEPTED:
                entries.append(
                    TimelineEntry(
                        icon="clock",
                        title="48-hour notification report approved by SEM",
                        time=self.notification_approval.time_modified,
                        text=f"Comment: {self.notification_approval.comment}",
                    )
                )
            if self.notification_approval.outcome == Approval.REJECTED:
                entries.append(
                    TimelineEntry(
                        icon="clock",
                        title="48-hour notification report rejected by SEM",
                        time=self.notification_approval.time_modified,
                        text=f"Comment: {self.notification_approval.comment}",
                    )
                )
        return entries

    @cached_property
    def notification_approval(self):
        for approval in self.approvals.all():
            if approval.role == Approval.SECTION_ENGINEERING_MANAGER and approval.type == Approval.NOTIFICATION:
                return approval

    @property
    def actions(self):
        actions = []
        if not self.notification_time_published:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Create 48-hour notification report",
                    time=self.time_start + timedelta(hours=48),
                    text="xxx hours of deadline remaining.",  # TODO: implement
                    link_text="Add Information",
                    link_url=reverse("incident_update", args=[self.pk]),
                    secondary_link_url=reverse("incident_notification_publish", args=[self.pk]),
                    secondary_link_text="Publish & Submit For Review",
                )
            )

        if self.notification_time_published is not None:
            if not self.notification_approval.outcome == Approval.ACCEPTED:
                actions.append(
                    TimelineEntry(
                        icon="clock",
                        title="Awaiting SEM approval for 48h Notification",
                        text=f"SEM reviewing: {self.notification_approval.name}",
                        link_text="Approval Link",
                        link_url=reverse("approval_detail", args=[self.notification_approval.id]),
                    )
                )

        return actions


class IncidentImage(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="images", blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    index = models.PositiveIntegerField(default=0, help_text="Change these values to alter ordering of images")
    image = models.ImageField(upload_to="images/")
    description = models.TextField(blank=True)


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

    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, related_name="approvals")

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


auditlog.register(
    Incident,
    include_fields=[
        "status",
        "production_value_loss",
        "rand_value_loss",
        "short_description",
        "long_description",
        "significant",
        "time_start",
        "time_end",
        "section_engineer",
        "notification_time_received",
        "immediate_action_taken",
        "equipment",
    ],
    serialize_data=True,
    serialize_auditlog_fields_only=True,
)
