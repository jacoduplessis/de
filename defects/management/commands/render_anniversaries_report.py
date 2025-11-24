from django.core.management.base import BaseCommand
from defects.reports import render_anniversary_report_pptx

class Command(BaseCommand):


    def handle(self, *args, **options):

        operation_name = "Testing"
        month = "2025-11"
        actions = []
        incidents = []
        gaps = []

        render_anniversary_report_pptx(
            target="report.pptx",
            operation_name=operation_name,
            month=month,
            incidents=incidents,
            actions=actions,
            gaps=gaps
        )


