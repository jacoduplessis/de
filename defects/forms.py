from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe

from .models import Incident, Approval, Area, Operation, Section, Solution, ResourcePrice
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from decimal import Decimal
from collections import defaultdict

EFFECT_CHOICES = (
    ("repair", "Estimated cost of Repair > R 250K"),
    ("production_loss", "Production Loss > 3 hours"),
    ("shift_loss", "Loss of Full Production shift or Evacuation of shift"),
)


class IncidentCreateForm(forms.ModelForm):
    """
    Incident description headline	Freeform text input field
    Equipment Type	                Dropdown searchable list (motor, pump, mill, etc)
    Equipment ID	                Dropdown searchable list (from SAP)
    Section	Dropdown                searchable list (Phoko Substation, 2#, etc)
    Section Engineer	            Dropdown searchable list of section engineers
    Date of Incident Occurrence	    Date and time selector (yyyy:mm:dd as well as hh:mm)
    Reliability Incident Number	    Auto generated reliability incident number

    If available, upload preliminary findings (5-Why's) conducted by SE and Repair Team.	Attachment icon to upload file

    """

    class Meta:
        model = Incident
        fields = [
            "short_description",
            "equipment",
            "operation",
            "area",
            "section",
            "section_engineer",
            "time_start",
            "time_end",
            "preliminary_findings",
        ]

        labels = {
            "short_description": "Incident Description Header",
            "section_engineer": "Section Engineer",
            "time_start": "Incident Start Time",
            "time_end": "Incident End Time",
            "equipment": "Functional Location",
            "preliminary_findings": "Preliminary Findings",
        }

        help_texts = {"preliminary_findings": "Upload 5-why’s (or any preliminary findings)."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].choices = []  # load options with ajax
        self.fields["section_engineer"].queryset = User.objects.filter(groups__name__in=["section_engineer"]).distinct()

        self.fields["time_start"].widget.attrs.update({"historic": ""})
        self.fields["time_end"].widget.attrs.update({"historic": ""})


    def clean(self):
        super().clean()
        time_start = self.cleaned_data.get("time_start")
        time_end = self.cleaned_data.get("time_end")

        if not time_end:
            return

        if time_end < time_start:
            msg = "End time must be later than start time"
            self.add_error("time_start", msg)
            self.add_error("time_end", msg)


class IncidentUpdateForm(forms.ModelForm):
    resource_price = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=13,
        label="ZAR price for 1 Pt Ounce.",
    )

    class Meta:
        model = Incident
        fields = [
            "short_description",
            "long_description",
            "equipment",
            "operation",
            "area",
            "section",
            "section_engineer",
            "time_start",
            "time_end",
            "trigger",
            "production_value_loss",
            "resource_price",
            "rand_value_loss",
            "repair_cost",
            "immediate_action_taken",
            "remaining_risk",
        ]
        labels = {
            "short_description": "Incident Description Header",
            "long_description": "Incident Description (Production Loss, Asset Damage, Theft, Fire, etc.)",
            "section_engineer": "Section Engineer",
            "time_start": "Incident Start Time",
            "time_end": "Incident End Time",
            "equipment": "Functional Location",
            "trigger": "Reliability Incident Effect",
            "production_value_loss": "Production Value Loss",
            "repair_cost": "Repair Cost",
            "immediate_action_taken": "Immediate Action That Was Taken (Describe the Immediate Action Taken)",
            "remaining_risk": "Indicate the Remaining Risk (After Immediate Action Was Taken)",
        }

        help_texts = {
            "significant": "Is this a significant incident?",
            "production_value_loss": "In Pt Ounces",
            "repair_cost": "In South African Rand (ZAR)",
            "trigger": "Choose the reliability incident effect (i.e. trigger) that occurred first."
        }

        widgets = {
            "long_description": widgets.Textarea(
                attrs={
                    "rows": 6,
                }
            ),
            "rand_value_loss": widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [] if not self.instance else [(self.instance.equipment_id, str(self.instance.equipment))]
        self.fields["equipment"].choices = choices  # load options with ajax
        conditions = Q(groups__name__in=["section_engineer"])
        if self.instance:
            conditions = conditions | Q(id=self.instance.section_engineer_id)
        self.fields["section_engineer"].queryset = User.objects.filter(conditions)

        rp = ResourcePrice.objects.order_by("-time_created").select_related("created_by").first()
        rp_date = rp.time_created.strftime("%Y-%m-%d")
        self.fields["resource_price"].help_text = mark_safe(
            f"Resource price was last updated on <strong>{rp_date}</strong> "
            f"by {rp.created_by.email} to be <strong>R{rp.rate}</strong>. Changing this value will store a new default resource price."
        )

        self.initial["resource_price"] = rp.rate

    def clean(self):
        super().clean()
        time_start = self.cleaned_data.get("time_start")
        time_end = self.cleaned_data.get("time_end")

        if not time_end:
            return

        if time_end < time_start:
            msg = "End time must be later than start time"
            self.add_error("time_start", msg)
            self.add_error("time_end", msg)

    def clean_rand_value_loss(self):
        return (self.cleaned_data["production_value_loss"] * self.cleaned_data["resource_price"]).quantize(Decimal("1.00"))


class IncidentNotificationApprovalSendForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name__in=["section_engineering_manager"]),
        label="Section Engineering Manager",
        required=True,
    )


class IncidentCloseApprovalSendForm(forms.Form):
    se_user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name__in=["section_engineer"]),
        label="Section Engineer",
        required=True,
    )

    sem_user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name__in=["section_engineering_manager"]),
        label="Section Engineering Manager",
        required=True,
    )


class IncidentRCAApprovalSendForm(forms.Form):


    def __init__(self, *args, **kwargs):

        role = kwargs.pop("role")

        super().__init__(*args, **kwargs)

        if role == Approval.SENIOR_ASSET_MANAGER:
            self.fields["user"].label = "Senior Asset Manager"
            self.fields["user"].queryset = User.objects.filter(groups__name__in=["senior_asset_manager"])
        elif role == Approval.SECTION_ENGINEERING_MANAGER:
            self.fields["user"].label = "Section Engineering Manager"
            self.fields["user"].queryset = User.objects.filter(groups__name__in=["section_engineering_manager"])

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="User",
        required=True,
    )

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = [
            "score",
            "outcome",
            "comment",
        ]

        labels = {
            "score": "Confidence Rating"
        }

        help_texts = {
            "score": "A rating of 3+ (out of 5) suggests you are confident that the root cause has been identified and sufficiently addressed.",
            "comment": "A comment should be provided in the case of rejecting an approval request."
        }

        widgets = {
            "score": widgets.Select(
                choices=[(f"{x}", f"{x}") for x in range(1, 6)],
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.type in [Approval.NOTIFICATION, Approval.RCA]:
            del self.fields["score"]
        if self.instance.type == Approval.CLOSE_OUT and self.instance.role == Approval.SECTION_ENGINEER:
            del self.fields["outcome"]
            # todo: add RE score as initial value for SE close-out approval


    def clean(self):
        super().clean()
        comment = self.cleaned_data.get("comment")
        outcome = self.cleaned_data.get("outcome")

        if outcome == Approval.REJECTED and comment == "":
            self.add_error("comment", "A comment must be provided when an approval request is rejected.")

        # todo: if SE close-out, comment must be given if score not equal to RE score

class IncidentFilterForm(forms.Form):
    section = forms.ModelChoiceField(Section.objects.all(), required=False)
    operation = forms.ModelChoiceField(Operation.objects.all(), required=False)
    area = forms.ModelChoiceField(Area.objects.all(), required=False)
    status = forms.ChoiceField(
        choices=[
            ("", "---------"),
        ]
        + list(Incident.STATUS_CHOICES),
        required=False,
    )


class SolutionFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            ("", "---------"),
        ]
        + [
            (Solution.SCHEDULED, "Scheduled"),
            (Solution.COMPLETED, "Completed"),
        ],
        required=False,
    )

    timeframe = forms.ChoiceField(
        choices=[
            ("", "---------"),
        ]
        + list(Solution.TIMEFRAME_CHOICES),
        required=False,
    )


class IncidentSignificanceUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "significant",
        ]


class IncidentCloseOutForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "close_out_immediate_cause",
            "close_out_root_cause",
            "close_out_short_term_actions",
            "close_out_short_term_date",
            "close_out_medium_term_actions",
            "close_out_medium_term_date",
            "close_out_long_term_actions",
            "close_out_long_term_date",
            "close_out_confidence",
        ]

        help_texts = {
            "close_out_short_term_actions": "One action per line",
            "close_out_medium_term_actions": "One action per line",
            "close_out_long_term_actions": "One action per line",
            "close_out_short_term_date": "Format: YYYY-MM-DD",
            "close_out_medium_term_date": "Format: YYYY-MM-DD",
            "close_out_long_term_date": "Format: YYYY-MM-DD",
            "close_out_confidence": "A rating of 3+ (out of 5) suggests you are confident that the root cause has been identified and sufficiently addressed.",
        }

        labels = {
            "close_out_immediate_cause": "Immediate Cause",
            "close_out_root_cause": "Root Cause",
            "close_out_short_term_actions": "Short-Term Actions (complete in 3 months)",
            "close_out_short_term_date": "Short-Term Date",
            "close_out_medium_term_actions": "Medium-Term Actions (complete in 3-6 months)",
            "close_out_medium_term_date": "Medium-Term Date",
            "close_out_long_term_actions": "Long-Term Actions (complete in 6-12 months)",
            "close_out_long_term_date": "Long-Term Date",
            "close_out_confidence": "RE Confidence Rating",
        }

        widgets = {
            "close_out_confidence": widgets.Select(
                choices=[(f"{x}", f"{x}") for x in range(1, 6)],
            )
        }


def conditional_forms_payload():
    """
    This data is used to dynamically alter the available options
    when selecting the "area" and "section" when creating a new incident.

    All keys and values are cast to string as it will be used in a browser HTML context
    """

    sections_qs = Section.objects.all().only("id", "area_id")
    areas_qs = Area.objects.all().only("id", "operation_id")

    sections = defaultdict(list)
    areas = defaultdict(list)

    for section in sections_qs:
        key = "" if section.area_id is None else str(section.area_id)
        sections[key].append(str(section.id))

    for area in areas_qs:
        key = "" if area.operation_id is None else str(area.operation_id)
        areas[key].append(str(area.id))

    return {
        "areas": dict(areas),
        "sections": dict(sections)
    }
