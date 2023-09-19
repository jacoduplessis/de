from decimal import Decimal
from typing import Optional

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
    COMPLETE = "complete"
    OVERDUE = "overdue"
    SCHEDULED = "scheduled"

    STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (COMPLETE, "Complete"),
        (OVERDUE, "Overdue"),
        (SCHEDULED, "Scheduled"),
    )

    REPAIR = "repair"
    PRODUCTION_LOSS = "production_loss"
    SHIFT_LOSS = "shift_loss"

    TRIGGER_CHOICES = (
        (REPAIR, "Estimated cost of Repair > R 250K"),
        (PRODUCTION_LOSS, "Production Loss > 3 hours"),
        (SHIFT_LOSS, "Loss of Full Production shift or Evacuation of shift"),
    )

    code = models.CharField(unique=True, max_length=200)  # also known as RI_Number
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=ACTIVE)
    operation = models.ForeignKey(Operation, null=True, blank=True, on_delete=models.SET_NULL, related_name="incidents")
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, related_name="incidents")
    section = models.ForeignKey(Section, blank=True, null=True, on_delete=models.SET_NULL, related_name="incidents")
    section_engineer = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    significant = models.BooleanField(default=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.TextField(blank=True)
    preliminary_findings = models.FileField(upload_to="files/", blank=True)
    notification_time_published = models.DateTimeField(blank=True, null=True)
    notification_time_approved = models.DateTimeField(blank=True, null=True)
    close_out_file = models.FileField(blank=True)
    report_file = models.FileField(blank=True, upload_to="files/")  # RCA report
    production_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=4, default=Decimal("0.00"))
    rand_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=2, default=Decimal("0.00"))
    trigger = models.CharField(max_length=200, blank=True, choices=TRIGGER_CHOICES)
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
        _map = {self.ACTIVE: "primary", self.COMPLETE: "success", self.OVERDUE: "danger", "incomplete": "warning", self.SCHEDULED: "warning"}
        return _map.get(self.status)

    @property
    def duration_delta(self) -> Optional[timedelta]:
        if not self.time_end:
            return None
        return self.time_end - self.time_start

    @property
    def duration_text(self) -> str:
        d = self.duration_delta
        if not d:
            return "---"
        seconds = d.total_seconds()
        hours, rem = divmod(seconds, 3600)
        minutes, rem = divmod(rem, 60)
        if hours == 0:
            return f"{minutes:.0f} minutes"
        return f"{hours:.0f} hours, {minutes:.0f} minutes"

    @property
    def notification_overdue(self):
        # todo: implement
        return False

    @property
    def report_overdue(self):
        # todo: implement
        return False

    @property
    def has_overdue_solutions(self):
        # todo: implement
        return False

    @property
    def has_ongoing_solutions(self):
        # todo: implement
        return False

    @property
    def is_complete(self):
        # todo: implement
        return False

    @property
    def status_computed(self):
        # todo: use a periodic background task of sorts to store the result of this property in the db column

        if any([self.notification_overdue, self.report_overdue, self.has_overdue_solutions]):
            return Incident.OVERDUE

        if self.has_ongoing_solutions:
            return Incident.SCHEDULED

        if self.is_complete:
            return Incident.COMPLETE

        return Incident.ACTIVE

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
                text=f"Downtime, duration: {self.duration_text}",
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
                    link_attrs="up-follow",
                )
            )
            for approval in self.approvals.filter(type=Approval.NOTIFICATION).order_by("time_created"):
                if approval.outcome == "":
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="Awaiting SEM approval for 48h Notification",
                            text=f"SEM reviewing: {approval.name}",
                            link_text="Approval Link",
                            link_url=reverse("approval_detail", args=[approval.id]),
                        )
                    )

                if approval.outcome == Approval.ACCEPTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="48-hour notification report approved by SEM",
                            time=approval.time_modified,
                            text=f"Comment: {approval.comment}",
                        )
                    )
                if approval.outcome == Approval.REJECTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="48-hour notification report rejected by SEM",
                            time=approval.time_modified,
                            text=f"Comment: {approval.comment}",
                        )
                    )

        if self.notification_approved:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title="RCA Report",
                    text="Is a full RCA Report required? Note that full RCA investigation must be scheduled, conducted and the full RCA report must be submitted within 14 days of submitting the 48Hr Notification Report.",
                    secondary_link_text="Not Required",
                    secondary_link_url="#",
                    link_text="Mark Incident As Significant",
                    link_url="#",
                )
            )
        return entries

    @cached_property
    def notification_approved(self):
        return self.approvals.filter(type=Approval.NOTIFICATION, outcome=Approval.ACCEPTED).exists()

    @property
    def notification_deadline_text(self):
        deadline_time = self.time_start + timedelta(hours=48)
        remaining = deadline_time - now()
        if remaining > timedelta(seconds=1):
            return f"{int(remaining.total_seconds() / 3600)} hours until deadline"
        return "Deadline has expired"

    @property
    def actions(self):
        actions = []
        if not self.notification_time_published:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Create 48-hour notification report",
                    time=self.time_start + timedelta(hours=48),
                    text=self.notification_deadline_text,  # TODO: implement
                    link_text="Add Information",
                    link_url=reverse("incident_update", args=[self.pk]),
                    link_attrs="up-layer=new up-size=large",
                    secondary_link_url=reverse("incident_notification_publish", args=[self.pk]),
                    secondary_link_text="Publish & Submit For Review",
                    secondary_link_attrs="up-layer=new",
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
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"

    TIMEFRAME_CHOICES = (
        (SHORT_TERM, "Short Term"),
        (MEDIUM_TERM, "Medium Term"),
        (LONG_TERM, "Long Term"),
    )

    PRIORITY_CHOICES = (
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
    )

    IDENTIFIED = "identified"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"

    STATUS_CHOICES = (
        (IDENTIFIED, "Identified"),
        (COMPLETED, "Completed"),
        (SCHEDULED, "Scheduled"),
    )

    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="solutions")
    priority = models.CharField(max_length=200, blank=True, choices=PRIORITY_CHOICES, default="A")
    timeframe = models.CharField(max_length=200, blank=True, choices=TIMEFRAME_CHOICES, default=SHORT_TERM)
    description = models.CharField(max_length=500)
    person_responsible = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=200, blank=True, choices=STATUS_CHOICES, default=IDENTIFIED)
    planned_completion_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    dr_number = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)

    @property
    def status_class(self):
        _map = {self.SCHEDULED: "primary", self.COMPLETED: "success", self.IDENTIFIED: "secondary"}
        return _map.get(self.status)


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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    outcome = models.CharField(max_length=100, choices=OUTCOME_CHOICES)
    comment = models.TextField(blank=True)


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


class Feedback(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    dismissed = models.BooleanField(default=False)


class ResourcePrice(models.Model):
    """
    Tracks the ZAR market price of one ounce of PGM.
    """

    time_created = models.DateTimeField(auto_now_add=True)
    rate = models.DecimalField(decimal_places=2, max_digits=10, help_text="Price in ZAR of the resource per ounce.")

    @classmethod
    def rand_cost(cls, ounces: Decimal) -> Decimal:
        most_recent = cls.objects.order_by("-time_created").first()
        return (ounces * most_recent.rate).quantize(Decimal("1.00"))
