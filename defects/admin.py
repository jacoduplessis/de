from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from .models import Solution, Incident, Equipment, SectionEngineer, SectionEngineeringManager

admin.site.site_header = "Anglo DE Tool Admin"
admin.site.site_title = "Anglo DE Tool"
admin.site.index_title = "Administration"
admin.site


@admin.register(Incident)
class ReliabilityIncidentAdmin(ImportExportModelAdmin):
    pass


@admin.register(Equipment)
class EquipmentAdmin(ImportExportModelAdmin):
    pass


class SolutionResource(ModelResource):
    class Meta:
        model = Solution


@admin.register(Solution)
class SolutionAdmin(ImportExportModelAdmin):
    resource_class = SolutionResource
    search_fields = [
        "planned_completion_date_string",
        "actual_completion_date_string",
        "dr_number",
    ]

    list_display = [
        "reliability_incident_name",
        "description",
        "status",
        "planned_completion_date_string",
        "planned_completion_date",
        "area",
        "dr_number",
    ]


@admin.register(SectionEngineer)
class SectionEngineerAdmin(admin.ModelAdmin):
    list_display = ["name", "user"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(SectionEngineeringManager)
class SectionEngineeringManagerAdmin(admin.ModelAdmin):
    list_display = ["name", "user"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
