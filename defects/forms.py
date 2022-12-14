from django import forms
from django.forms import widgets
from .models import ReliabilityIncident

EQUIPMENT_CHOICES = (
    ('x-123-abc', 'Pump #12 (ID xxx)'),
    ('x-234-abc', 'Mill #6 (ID xxx)'),
    ('x-345-abc', 'Motor #44 (ID xxx)'),
    ('x-456-abc', 'Hoist #1 (ID xxx)'),
)

AREA_CHOICES = (
    ('aps', 'APS'),
    ('concentrators', 'Concentrators'),
    ('dishaba', 'Dishaba'),
    ('tumela', 'Tumela'),
)

SECTION_CHOICES = (
    ('phoko', 'Phoko Substation'),
    ('merensky-bunkers', 'Merensky Bunkers'),
)

SECTION_ENGINEER_CHOICES = (
    ('a', 'Alice'),
    ('b', 'Bob'),
    ('c', 'Chris'),
    ('d', 'Dennis'),
)

EFFECT_CHOICES = (
    ('repair', 'Estimated cost of Repair > R 250K'),
    ('production_loss', 'Production Loss > 3 hours'),
    ('shift_loss', 'Loss of Full Production shift or Evacuation of shift'),
)


class RILogForm(forms.ModelForm):
    preliminary_findings = forms.FileField(required=False)
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
        model = ReliabilityIncident
        fields = [
            'short_description',
            'equipment',
            'section',
            'section_engineer',
            'time_start',
            'time_end',
        ]
        labels = {
            'short_description': 'Short Description',
            'section_engineer': 'Section Engineer',
            'time_start': 'Incident Start Time',
            'time_end': 'Incident End Time',
            'equipment': 'Equipment (from SAP)'
        }
        widgets = {
            'section': widgets.Select(
                choices=SECTION_CHOICES
            ),
            'section_engineer': widgets.Select(
                choices=SECTION_ENGINEER_CHOICES
            ),
            'equipment': widgets.Select(
                choices=EQUIPMENT_CHOICES
            ),
        }


class RINotificationForm(forms.ModelForm):
    pictures = forms.FileField(
        required=False,
        help_text='If applicable.',
        widget=widgets.FileInput(
            attrs={'multiple': True},
        ))

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
        model = ReliabilityIncident
        fields = [
            'area',
            'section',
            'section_engineer',
            'equipment',
            'time_start',
            'time_end',
            'short_description',
            'long_description',
            'possible_effect',
            'production_value_loss',
            'immediate_action_taken',
            'remaining_risk',
            'rand_value_loss',
            'significant',
        ]
        labels = {
            'short_description': 'Short Description',
            'long_description': 'Incident Description',
            'section_engineer': 'Section Engineer',
            'time_start': 'Incident Start Time',
            'time_end': 'Incident End Time',
            'equipment': 'Equipment (from SAP)',
        }
        help_texts = {
            'significant': 'Is this a significant incident?',
            'remaining_risk': 'Indicate the remaining risk after immediate action was taken.',
            'immediate_action_taken': 'Describe the immediate action taken.',
            'long_description': 'Production Loss, Asset Damage, Theft, Fire, Etc.',
        }
        widgets = {
            'area': widgets.Select(
                choices=AREA_CHOICES
            ),
            'section': widgets.Select(
                choices=SECTION_CHOICES
            ),
            'section_engineer': widgets.Select(
                choices=SECTION_ENGINEER_CHOICES
            ),
            'long_description': widgets.Textarea(
                attrs={
                    'rows': 10,
                }
            ),
            'equipment': widgets.Select(
                choices=EQUIPMENT_CHOICES
            ),
            'possible_effect': widgets.CheckboxSelectMultiple(
                choices=EFFECT_CHOICES
            )
        }


class RINotificationApprovalSendForm(forms.Form):

    sem = forms.ChoiceField(
        choices=SECTION_ENGINEER_CHOICES,
        required=False,
        label='Section Engineering Manager'
    )

