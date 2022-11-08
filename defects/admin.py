from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from .models import Solution, ReliabilityIncident


@admin.register(ReliabilityIncident)
class ReliabilityIncidentAdmin(ImportExportModelAdmin):
    pass


class SolutionResource(ModelResource):
    class Meta:
        model = Solution


@admin.register(Solution)
class SolutionAdmin(ImportExportModelAdmin):
    resource_class = SolutionResource
    search_fields = [
        'planned_completion_date_string',
        'actual_completion_date_string',
        'dr_number',
    ]

    list_display = [
        'reliability_incident_name',
        'description',
        'status',
        'planned_completion_date_string',
        'planned_completion_date',
        'area',
        'dr_number'
    ]
