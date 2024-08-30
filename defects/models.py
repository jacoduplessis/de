from decimal import Decimal
from typing import Optional

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta, datetime, time, timezone
import zoneinfo
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils.functional import cached_property

from defects.timelines import TimelineEntry, Link

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


"""
Hierarchy
Operation > Area > Section
"""

class Operation(models.Model):
    name = models.CharField(max_length=200)
    order_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_index"]


class Area(models.Model):
    name = models.CharField(max_length=200)
    order_index = models.PositiveIntegerField(default=0)
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_index"]


class Section(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=100, blank=True)
    order_index = models.PositiveIntegerField(default=0)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_index"]


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
    significant = models.BooleanField(default=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")
    short_description = models.CharField(max_length=200, blank=True)
    long_description = models.TextField(blank=True)
    preliminary_findings = models.FileField(upload_to="files/", blank=True)
    notification_time_published = models.DateTimeField(blank=True, null=True)
    notification_time_approved = models.DateTimeField(blank=True, null=True)
    close_out_file = models.FileField(blank=True)
    report_file = models.FileField(blank=True, upload_to="files/")  # RCA report
    rca_report_time_published = models.DateTimeField(blank=True, null=True)
    rca_report_time_approved = models.DateTimeField(blank=True, null=True)
    production_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=4, default=Decimal("0.00"))
    rand_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=2, default=Decimal("0.00"))
    repair_cost = models.DecimalField(blank=True, max_digits=20, decimal_places=2, default=Decimal("0.00"))
    trigger = models.CharField(max_length=200, blank=True, choices=TRIGGER_CHOICES)
    immediate_action_taken = models.TextField(blank=True)
    remaining_risk = models.TextField(blank=True)
    time_anniversary_reviewed = models.DateTimeField(null=True, blank=True, help_text="Records when the 1-year anniversary review was completed.")
    anniversary_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    anniversary_success = models.BooleanField(default=False, help_text="Indicates whether the RI root cause was resolved")

    close_out_immediate_cause = models.TextField(blank=True)
    close_out_root_cause = models.TextField(blank=True)
    close_out_short_term_date = models.DateField(blank=True, null=True)
    close_out_short_term_actions = models.TextField(blank=True)
    close_out_medium_term_date = models.DateField(null=True, blank=True)
    close_out_medium_term_actions = models.TextField(blank=True)
    close_out_long_term_date = models.DateField(null=True, blank=True)
    close_out_long_term_actions = models.TextField(blank=True)
    close_out_confidence = models.PositiveIntegerField(default=0)  # RE score
    close_out_time_published = models.DateTimeField(blank=True, null=True)
    close_out_time_approved = models.DateTimeField(blank=True, null=True)
    close_out_rating = models.PositiveIntegerField(default=0, editable=False)  # SEM rating / Final Score

    history = AuditlogHistoryField(delete_related=False)

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        permissions = (("request_notification_approval", "Can request approval of incident notification"),)

    def __str__(self):
        return self.code

    def calculate_status(self):

        if self.time_anniversary_reviewed:
            return self.COMPLETE

        if not self.notification_time_published:
            return self.ACTIVE

        if not self.notification_time_published and (self.time_end + timedelta(hours=48)) < now():
            return self.OVERDUE

        if self.significant and not self.rca_report_time_published and (self.notification_time_published + timedelta(days=14)) > now():
            return self.OVERDUE

        solutions = list(self.solutions.all())
        if len(solutions) > 0:
            if all([x.status == Solution.COMPLETED for x in solutions]):
                return self.COMPLETE
            return self.SCHEDULED

        return self.ACTIVE

    def save(self, *args, **kwargs):
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    @classmethod
    def generate_incident_code(cls, section_code, incident_type="RI", count=None):
        prefix = f"{section_code}_{incident_type}_{now().strftime("%Y")}"
        if count is None:
            count = 1 + Incident.objects.filter(code__startswith=prefix).count()
        return f"{prefix}_{count}"

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
        if not self.time_end:
            return True

        return self.notification_time_published is None and (self.time_end + timedelta(hours=48)) < now()

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
                    links=[
                        Link(
                            text="View Notification Report",
                            url=reverse("incident_notification", args=[self.pk]),
                            attrs="up-follow",
                        )
                    ],
                )
            )
            for approval in self.approvals.filter(type=Approval.NOTIFICATION).order_by("time_created"):
                if approval.outcome == "":
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="Awaiting SEM approval for 48h Notification",
                            time=self.notification_time_published + timedelta(minutes=1),
                            text=f"SEM reviewing: {approval.name}",
                            links=[Link(text="Copy Approval Link", url=reverse("approval_detail", args=[approval.id]), attrs="clipboard-copy-link")],
                        )
                    )

                if approval.outcome == Approval.ACCEPTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="48-hour notification report approved by SEM",
                            time=approval.time_modified,
                            text=f"Comment by {approval.name}: {approval.comment or None}",
                        )
                    )
                if approval.outcome == Approval.REJECTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title="48-hour notification report rejected by SEM",
                            time=approval.time_modified,
                            text=f"Comment by {approval.name}: {approval.comment or None}",
                        )
                    )

        if self.rca_report_time_published:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title="RCA report published",
                    time=self.notification_time_published,
                    links=[
                        Link(
                            text="View RCA Report",
                            url=self.report_file.url,
                            attrs="target=_blank",
                        )
                    ],
                )
            )
            for approval in self.approvals.filter(type=Approval.RCA).order_by("time_created"):
                if approval.outcome == "":
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            time=self.rca_report_time_published + timedelta(minutes=1),
                            title=f"Awaiting {approval.get_role_display()} approval for RCA report",
                            text=f"{approval.get_role_display()} reviewing: {approval.name}",
                            links=[Link(text="Copy Approval Link", url=reverse("approval_detail", args=[approval.id]), attrs="clipboard-copy-link")],
                        )
                    )

                if approval.outcome == Approval.ACCEPTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title=f"RCA report approved by {approval.get_role_display()}",
                            time=approval.time_modified,
                            text=f"Comment by {approval.name}: {approval.comment or None}",
                        )
                    )
                if approval.outcome == Approval.REJECTED:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title=f"RCA report rejected by {approval.get_role_display()}",
                            time=approval.time_modified,
                            text=f"Comment by {approval.name}: {approval.comment or None}",
                        )
                    )

        if self.close_out_time_published:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title="Close-out slide published",
                    time=self.close_out_time_published,
                    text="Close-out submitted for ranking by SE & SEM.",
                    links=[
                        Link(
                            text="View Close-Out Slide PDF",
                            url=reverse("incident_close_pdf", args=[self.pk]),
                            attrs="target=_blank",
                        )
                    ],
                )
            )

            for approval in self.approvals.filter(type=Approval.CLOSE_OUT).order_by("time_created"):
                if approval.score == 0:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            time=self.close_out_time_published + timedelta(minutes=1),
                            title=f"Awaiting {approval.get_role_display()} close-out rating",
                            text=f"{approval.get_role_display()} reviewing: {approval.name}",
                            links=[Link(text="Copy Approval Link", url=reverse("approval_detail", args=[approval.id]), attrs="clipboard-copy-link")],
                        )
                    )

                else:
                    entries.append(
                        TimelineEntry(
                            icon="clock",
                            title=f"Close-out rated by {approval.get_role_display()}",
                            time=approval.time_modified,
                            text=f"Score: {approval.score}/5. Comment: {approval.comment or None}",
                        )
                    )

        if self.close_out_time_approved:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title=f"Close-out approved by SE and SEM",
                    time=self.close_out_time_approved,
                )
            )

        for solution in self.solutions.all():
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title=f"Solution Created",
                    time=solution.time_created,
                    text=f"{solution.description}",
                )
            )
            if solution.date_verified:
                text = f"Solution: {solution.description}"
                if solution.verification_comment:
                    text += f"\n\nVerification Comment: {solution.verification_comment}"
                entries.append(
                    TimelineEntry(
                        icon="clock",
                        title=f"Solution Verified",
                        time=datetime.combine(solution.date_verified, time(hour=12, minute=0, tzinfo=timezone.utc)),
                        text=text,
                    )
                )

        if self.time_anniversary_reviewed:
            entries.append(
                TimelineEntry(
                    icon="clock",
                    title=f"Incident Anniversary Review Completed",
                    time=self.time_anniversary_reviewed,
                    text=f"Review completed by {self.anniversary_reviewed_by.email}",
                )
            )

        return sorted(entries, key=lambda x: x.time)

    def has_pending_approval(self, approval_type, role=None):
        for approval in self.approvals.all():
            if role is not None and approval.role != role:
                continue
            if approval.type == approval_type:
                if approval_type in (Approval.RCA, Approval.NOTIFICATION) and approval.outcome == "":
                    return True
                if approval_type == Approval.CLOSE_OUT and approval.score == 0:
                    return True
        return False

    @property
    def notification_notice_text(self):
        return """The Reliability Engineer (RE) and the Section Engineer (SE) must collaborate
        to create the 48H notification report, which requires both parties to agree on its content
        before the RE submits it to the Section Engineering Manager (SEM) for approval."""


    @property
    def rca_notice_text(self):
        return """The Reliability Engineer (RE) and the Section Engineer (SE) must collaborate
        to create the RCA Report, which requires both parties to agree on its content.
        Moreover, before the RE submits it to the Senior Asset Manager (SnrAM) for approval,
        the RCA Report must have been reviewed by a Senior Reliability Engineer."""

    @cached_property
    def notification_approved(self):
        return self.approvals.filter(type=Approval.NOTIFICATION, outcome=Approval.ACCEPTED).exists()

    @cached_property
    def notification_rejected(self):
        return (
            self.notification_time_published is not None
            and self.approvals.filter(type=Approval.NOTIFICATION).exclude(outcome="").count() > 0
            and not self.notification_approved
        )

    def most_recent_approval_outcome_for_role(self, approval_type, role):

        approvals = sorted([x for x in self.approvals.all() if x.type == approval_type and x.role == role], key=lambda x: x.time_modified, reverse=True)
        if len(approvals) == 0:
            return None
        return approvals[0].outcome

    @cached_property
    def rca_report_rejected(self):
        if not self.significant:
            return False

        if self.rca_report_time_approved:
            return False

        if not self.rca_report_time_published:
            return False

        sam_rejected = self.most_recent_approval_outcome_for_role(approval_type=Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER) == Approval.REJECTED
        sem_rejected = self.most_recent_approval_outcome_for_role(approval_type=Approval.RCA, role=Approval.SECTION_ENGINEERING_MANAGER) == Approval.REJECTED

        return sam_rejected or sem_rejected


    @cached_property
    def rca_report_approved_by_senior_asset_manager(self):
        if not self.significant:
            return False

        return (
            self.rca_report_time_published
            and self.approvals.filter(type=Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER, outcome=Approval.ACCEPTED).count() > 0
        )


    @cached_property
    def close_out_rejected(self):
        return (
            self.close_out_time_published
            and self.approvals.filter(type=Approval.CLOSE_OUT).exclude(score=0).count() > 1
            and not self.close_out_time_approved
        )

    @property
    def notification_deadline_text(self):
        deadline_time = self.time_end + timedelta(hours=48)
        remaining = deadline_time - now()
        if remaining > timedelta(seconds=1):
            return f"{int(remaining.total_seconds() / 3600)} hours until deadline"
        return "Deadline has expired"

    @property
    def close_out_short_term_actions_list(self):
        return self.close_out_short_term_actions.strip().split("\n")

    @property
    def close_out_medium_term_actions_list(self):
        return self.close_out_medium_term_actions.strip().split("\n")

    @property
    def close_out_long_term_actions_list(self):
        return self.close_out_long_term_actions.strip().split("\n")

    @property
    def close_out_confidence_filled_stars(self):
        return range(self.close_out_rating)

    @property
    def close_out_confidence_empty_stars(self):
        return range(5, self.close_out_rating, -1)

    @property
    def anniversary_date(self):
        return self.time_end + timedelta(days=365)

    @property
    def actions(self):
        actions = []

        # no more actions once a anniversary review has been completed
        if self.time_anniversary_reviewed:
            return []

        if not self.notification_time_published:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Create 48H notification report",
                    time=self.time_end + timedelta(hours=48),
                    text=self.notification_deadline_text + "\n\n" + self.notification_notice_text,
                    links=[
                        Link(
                            text="Add Information",
                            url=reverse("incident_update", args=[self.pk]),
                            attrs="up-layer=new up-size=large",
                        ),
                        Link(
                            text="Add Images",
                            url=reverse("incident_images", args=[self.pk]),
                            attrs="up-layer=new up-size=large",
                        ),
                        Link(
                            url=reverse("incident_notification_publish", args=[self.pk]),
                            text="Publish & Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if self.notification_approved:

            # check for RCA Requirement
            if self.significant and not self.report_file:

                actions.append(
                    TimelineEntry(
                        icon="clock",
                        title="Upload RCA Report",
                        time=self.notification_time_approved + timedelta(minutes=1),
                        text="Is a full RCA Report required? Note that full RCA investigation must be scheduled, conducted and the full RCA report must be submitted within 14 days of submitting the 48H Notification Report. If not required, update the incident's significance.",
                        links=[
                            Link(
                                text="Upload RCA Report",
                                url=reverse("incident_rca_report_upload", args=[self.pk]),
                                attrs="up-layer=new"
                            ),
                            Link(
                                text="RCA Not Required",
                                url="#",
                                cls="secondary",
                                attrs="id=trigger-form-incident-not-significant",
                            ),

                        ],
                    )
                )

        if self.notification_approved and self.significant and self.report_file and not self.rca_report_time_published:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Publish RCA Report and Submit for Senior Asset Manager (SnrAM) approval",
                    text=self.rca_notice_text,
                    time=self.notification_time_approved + timedelta(minutes=1),
                    links=[
                        Link(
                            url=reverse("incident_rca_publish", args=[self.pk]),
                            text="Publish & Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if (self.rca_report_time_published
            and Approval.objects.filter(incident=self, type=Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER, outcome=Approval.ACCEPTED).exists()
            and not Approval.objects.filter(incident=self, type=Approval.RCA, role=Approval.SECTION_ENGINEERING_MANAGER).exists()
            and not self.rca_report_time_approved):
            # RCA has been approved by SAM but not yet by SEM
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Submit RCA Report for SEM approval",
                    time=self.notification_time_approved + timedelta(minutes=1),
                    links=[
                        Link(
                            url=reverse("incident_rca_publish", args=[self.pk]),
                            text="Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if self.rca_report_rejected and not self.has_pending_approval(Approval.RCA):
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Resubmit RCA Report",
                    time=self.rca_report_time_published + timedelta(minutes=1),
                    links=[
                        Link(
                            text="Upload Updated RCA Report",
                            url=reverse("incident_rca_report_upload", args=[self.pk]),
                            attrs="up-layer=new"
                        ),
                        Link(
                            url=reverse("incident_rca_publish", args=[self.pk]),
                            text="Publish & Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if self.notification_approved and (not self.significant or self.rca_report_time_approved) and not self.close_out_time_published:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Create Close-Out Slide",
                    time=self.notification_time_approved + timedelta(minutes=1),
                    text="The Reliability Engineer (RE) and the Section Engineer (SE) must collaborate to create the Close-Out Slide, which requires both parties to agree on its content before the RE submits it to the Section Engineering Manager (SEM) for approval.",
                    links=[
                        Link(text="Add Information", url=reverse("incident_close_form", args=[self.pk]), attrs="up-layer=new"),
                        Link(
                            url=reverse("incident_close_publish", args=[self.pk]),
                            text="Publish & Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if self.close_out_rejected and not self.has_pending_approval(Approval.CLOSE_OUT):
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Resubmit Close-Out Slide",
                    time=self.close_out_time_published + timedelta(minutes=1),
                    links=[
                        Link(text="Edit Close-Out Slide", url=reverse("incident_close_form", args=[self.pk]), attrs="up-layer=new"),
                        Link(
                            url=reverse("incident_close_publish", args=[self.pk]),
                            text="Publish & Submit For Review",
                            attrs="up-layer=new",
                            cls="secondary",
                        ),
                    ],
                )
            )

        if self.close_out_time_approved:
            actions.append(
                TimelineEntry(
                    icon="clock",
                    title="Create Solutions",
                    time=self.close_out_time_approved + timedelta(minutes=1),
                    text="Since the close-out slide has been approved, you can now create solutions for this incident.",
                    links=[
                        Link(
                            url=reverse("incident_solution_create", args=[self.pk]),
                            text="Add solution",
                            attrs="up-layer=new",
                        ),
                        Link(
                            url=reverse("solution_list") + f"?incident_id={self.pk}",
                            text="View in Solution Tracker",
                            attrs="target=_blank",
                            cls="secondary",
                        )
                    ]
                )
            )

        return actions

    @property
    def num_completed_solutions(self):
        # do the filtering in python to avoid additional db queries
        return len([s for s in self.solutions.all() if s.status == Solution.COMPLETED])


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
        (SHORT_TERM, "Short-Term Actions (complete in 3 months)"),
        (MEDIUM_TERM, "Medium-Term Actions (complete in 3-6 months)"),
        (LONG_TERM, "Long-Term Actions (complete in 6-12 months)"),
    )

    PRIORITY_CHOICES = (
        ("a", "A"),
        ("b", "B"),
        ("c", "C"),
    )

    COMPLETED = "completed"
    SCHEDULED = "scheduled"

    STATUS_CHOICES = (
        (COMPLETED, "Completed"),
        (SCHEDULED, "Scheduled"),
    )

    time_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True, blank=True, related_name="solutions")
    priority = models.CharField(max_length=200, blank=True, choices=PRIORITY_CHOICES, default="A")
    timeframe = models.CharField(max_length=200, blank=True, choices=TIMEFRAME_CHOICES, default=SHORT_TERM)
    description = models.CharField(max_length=500)
    person_responsible = models.CharField(max_length=200, blank=True)
    planned_completion_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    dr_number = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, default=SCHEDULED, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    date_verified = models.DateField(blank=True, null=True)
    verification_comment = models.TextField(blank=True)

    @property
    def status_class(self):
        _map = {self.SCHEDULED: "primary", self.COMPLETED: "success"}
        return _map.get(self.status)

    def save(self, *args, **kwargs):
        if self.date_verified is not None:
            self.status = self.COMPLETED
        super().save(*args, **kwargs)

class Approval(models.Model):
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    OUTCOME_CHOICES = (
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    )

    NOTIFICATION = "notification"
    RCA = "rca"
    CLOSE_OUT = "close_out"

    TYPE_CHOICES = (
        (NOTIFICATION, "Notification"),
        (RCA, "RCA"),
        (CLOSE_OUT, "Close-Out"),
    )

    SECTION_ENGINEER = "section_engineer"
    ENGINEERING_MANAGER = "engineering_manager"
    SECTION_ENGINEERING_MANAGER = "section_engineering_manager"
    SENIOR_ASSET_MANAGER = "senior_asset_manager"

    ROLE_CHOICES = (
        (SECTION_ENGINEER, "SE"),
        (ENGINEERING_MANAGER, "EM"),
        (SECTION_ENGINEERING_MANAGER, "SEM"),
        (SENIOR_ASSET_MANAGER, "Senior AM"),
    )

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True, related_name="approvals")
    time_created = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="+")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, choices=ROLE_CHOICES)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    outcome = models.CharField(max_length=100, choices=OUTCOME_CHOICES)
    comment = models.TextField(blank=True)
    score = models.PositiveIntegerField(default=0, blank=True)  # only approvals of type CLOSE_OUT will have a score (1-5 inclusive).


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
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @classmethod
    def rand_cost(cls, ounces: Decimal) -> Decimal:
        most_recent = cls.objects.order_by("-time_created").first()
        return (ounces * most_recent.rate).quantize(Decimal("1.00"))
