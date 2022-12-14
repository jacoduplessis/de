from decimal import Decimal

from django.db import models


class ReliabilityIncident(models.Model):
    operation = models.CharField(max_length=200, default='AMB')
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
    production_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=10, default=Decimal('0.00'))
    rand_value_loss = models.DecimalField(blank=True, max_digits=20, decimal_places=2, default=Decimal('0.00'))
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
