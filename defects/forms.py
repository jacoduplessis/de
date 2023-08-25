from django import forms
from django.forms import widgets
from .models import Incident, SectionEngineeringManager, Approval, Area, Operation, Section
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

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
            "short_description": "Short Description",
            "section_engineer": "Section Engineer",
            "time_start": "Incident Start Time",
            "time_end": "Incident End Time",
            "equipment": "Equipment (from SAP)",
            "preliminary_findings": "Preliminary Findings",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].choices = []  # load options with ajax
        self.fields["section_engineer"].queryset = User.objects.filter(groups__name__in=["section_engineer"])


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
            "possible_effect",
            "production_value_loss",
            "rand_value_loss",
            "immediate_action_taken",
            "remaining_risk",
            "significant",
        ]
        labels = {
            "short_description": "Short Description",
            "long_description": "Long Description",
            "section_engineer": "Section Engineer",
            "time_start": "Incident Start Time",
            "time_end": "Incident End Time",
            "equipment": "Equipment (from SAP)",
        }

        help_texts = {
            "significant": "Is this a significant incident?",
            "remaining_risk": "Indicate the remaining risk after immediate action was taken.",
            "immediate_action_taken": "Describe the immediate action taken.",
            "long_description": "Production Loss, Asset Damage, Theft, Fire, Etc.",
        }

        widgets = {
            "long_description": widgets.Textarea(
                attrs={
                    "rows": 10,
                }
            ),
            "possible_effect": widgets.CheckboxSelectMultiple(choices=EFFECT_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [] if not self.instance else [(self.instance.equipment_id, str(self.instance.equipment))]
        self.fields["equipment"].choices = choices  # load options with ajax
        conditions = Q(groups__name__in=["section_engineer"])
        if self.instance:
            conditions = conditions | Q(id=self.instance.section_engineer_id)
        self.fields["section_engineer"].queryset = User.objects.filter(conditions)

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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class IncidentNotificationForm(forms.ModelForm):
    """
    Operation	                                Greyed out field (Prepoulated with Amandelbult Complex)	Non-negotiable?
    Area	                                    Dropdown searchable list (APS, Concentrator, Dishaba Upper, Disbha Lower, etc.)	Non-negotiable?
    Section	                                    Greyed out field. Can override, but with warning. (from Log Notification.)	Non-negotiable?
    Functional location 	                    Dropdown searchable list (from SAP)	Non-negotiable?
    Reliability notification no.	            Greyed out field. (from Log Notification.)	Non-negotiable?
    Incident Start Date	                        yyyy:mm:dd Greyed out field. Can override, but with warning. (from Log Notification.)	Non-negotiable?
    Incident start time	                        hh:mm Greyed out field. Can override, but with warning. (from Log Notification.)	Non-negotiable?
    Incident End Date	                        yyyy:mm:dd 	Non-negotiable?
    Incident End Time	                        hh:mm 	Non-negotiable?
    Section Engineer	                        Greyed out field. Can override, but with warning. (from Log Notification.)	Non-negotiable?
    Incident Description                        (Production Loss,Asset Damage, Theft, Fire, Etc.)	Freeform text input field
    Possible Reliability Incident Effect	    Radio button or Checkbox? (ask Thomas what to do if multipe conditons are met) (Estimated cost of Repair > R 250K ; Production Loss > 3 hours ; Loss of Full Production shift or Evacuation of shift)
    Recorded Production loss (Pt Ounces)        (Built in production loss calculator to calculated ounces lost and rand value lost)
    Immediate action that was taken             (Describe the immediate action taken)	Bullet list entries
    Indicate the remaining risk                 (After immediate action was taken)	Bullet list entries
    Pictures (If applicable)	                Upload images and add captions
    Is this a significant incident?	            Radio button. (Yes / No) Add info pop to describe what is considered significant	Non-negotiable?

    """

    class Meta:
        model = Incident
        fields = [
            "area",
            "section",
            "section_engineer",
            "equipment",
            "time_start",
            "time_end",
            "short_description",
            "long_description",
            "possible_effect",
            "production_value_loss",
            "rand_value_loss",
            "immediate_action_taken",
            "remaining_risk",
            "significant",
        ]
        labels = {
            "short_description": "Short Description",
            "long_description": "Incident Description",
            "section_engineer": "Section Engineer",
            "time_start": "Incident Start Time",
            "time_end": "Incident End Time",
            "equipment": "Equipment (from SAP)",
        }
        help_texts = {
            "significant": "Is this a significant incident?",
            "remaining_risk": "Indicate the remaining risk after immediate action was taken.",
            "immediate_action_taken": "Describe the immediate action taken.",
            "long_description": "Production Loss, Asset Damage, Theft, Fire, Etc.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [] if not self.instance else [(self.instance.equipment_id, str(self.instance.equipment))]
        self.fields["equipment"].choices = choices  # load options with ajax
        conditions = Q(groups__name__in=["section_engineer"])
        if self.instance:
            conditions = conditions | Q(id=self.instance.section_engineer_id)
        self.fields["section_engineer"].queryset = User.objects.filter(conditions)

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


class IncidentNotificationApprovalSendForm(forms.Form):

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name__in=["section_engineering_manager"]),
        label="Section Engineering Manager",
        required=True,
    )



class IncidentCloseForm(forms.Form):
    """
    Incident description headline	Greyed out field. (from Log Notification.)
    Date of Incident Ocurrance	    Greyed out field. (from Log Notification.)
    Immediate Cause	                Freeform text input field. Info pop up icon showing "Incident Description (Production Loss, Asset Damage, Theft, Fire, Etc.)" (from Create 48H Notification Report). Ability to upload photos or pull in  photo(s) from Create 48H Notification Report.
    Root Cause	                    Freeform text input field.
    Downtime & Repair Cost	        "Precalculate downtime from incident start and end times in Create 48H Notification Report.
                                    Precaculate ounces values lost and rand value lost from Create 48H Notification Report.
                                    Ability to override if necessary for some additional cost / downtime to be incorporated."
    Short Term Action	            Bullet list entries with accompanying date when to implement dd:mm
    Medium Term Action	            Bullet list entries with accompanying date when to implement dd:mm
    Long Term Action	            Bullet list entries with accompanying date when to implement dd:mm
    Reliability Engineering
    Close Out Confidence	        Rating out of 5 Stars
    Email the following people
    to rate Close out confidience	Dropdown searchable list of other SE and SEM to complete close out rating
    """

    short_description = forms.CharField(required=False)
    incident_date = forms.DateField(required=False)
    immediate_cause = forms.CharField(widget=widgets.Textarea(), required=False)
    root_cause = forms.CharField(widget=widgets.Textarea(), required=False)
    downtime_repair_cost = forms.CharField(widget=widgets.Textarea(), required=False)
    short_term_action = forms.CharField(widget=widgets.Textarea(), required=False)
    medium_term_action = forms.CharField(widget=widgets.Textarea(), required=False)
    long_term_action = forms.CharField(widget=widgets.Textarea(), required=False)
    re_close_out_confidence_rating = forms.ChoiceField(
        choices=[(f"{x}", f"{x}") for x in range(1, 6)],
        label="RE Close-Out Confidence rating",
        required=False,
        help_text="Provide confidence rating out of 5.",
    )
    se_close_out_confidence = forms.ChoiceField(
        choices=[],
        required=False,
        label="SE Close-Out Confidence",
        help_text="The SE selected here will be notified and asked to provide a confidence rating.",
    )
    sem_close_out_confidence = forms.ChoiceField(
        choices=[],
        required=False,
        label="SEM Close-Out Confidence",
        help_text="The SEM selected here will be notified and asked to provide a confidence rating.",
    )


class ApprovalForm(forms.ModelForm):
    class Meta:
        model = Approval
        fields = [
            "outcome",
            "comment",
        ]


class IncidentFilterForm(forms.Form):

    section = forms.ModelChoiceField(Section.objects.all(), required=False)
    operation = forms.ModelChoiceField(Operation.objects.all(), required=False)
    area = forms.ModelChoiceField(Area.objects.all(), required=False)
