from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource
from .models import Solution, Incident, Equipment, Section, Area, Operation, Feedback, ResourcePrice

admin.site.site_header = "DE Tool Admin"
admin.site.site_title = "DE Tool"
admin.site.index_title = "Administration"


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
        "dr_number",
    ]

    list_display = [
        "incident",
        "description",
        "status",
        "planned_completion_date",
        "dr_number",
    ]

    list_display_links = ["description"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("incident")


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "order_index",
        "operation",
        "code",
    ]
    ordering = ["order_index"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("operation")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "order_index",
        "area",
    ]

    ordering = ["order_index"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("area")


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "order_index",
    ]

    ordering = ["order_index"]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass


@admin.register(ResourcePrice)
class ResourcePriceAdmin(admin.ModelAdmin):

    list_display = [
        "time_created",
        "rate",
        "created_by",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by")
