from django.core.management.base import BaseCommand
from defects.models import Incident, Area, Section, Operation, Solution
import random
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.utils.lorem_ipsum import words, paragraphs


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--incidents", type=int, help="number of incidents to generate", default=0)
        parser.add_argument("--solutions", type=int, help="number of incidents to generate", default=0)

    def handle(self, *args, **options):

        areas = list(Area.objects.values_list("id", flat=True))
        sections = list(Section.objects.values_list("id", flat=True))
        operations = list(Operation.objects.values_list("id", flat=True))
        section_engineers = list(User.objects.filter(groups__name__in=["section_engineer"]).values_list("id", flat=True))

        for ix in range(options["incidents"]):
            i = Incident()
            i.created_by_id = 1
            i.equipment_id = random.randint(10, 10_000)
            i.code = Incident.generate_incident_code()
            start = now().replace(second=0, microsecond=0) - timedelta(days=random.randint(0, 600), hours=random.randint(0, 24), minutes=random.randint(0, 60))
            end = start + timedelta(hours=random.randint(0, 40), minutes=random.randint(0, 60))
            i.time_start = start
            i.time_end = end
            i.short_description = words(5, False)
            i.long_description = "\n\n".join(paragraphs(4, common=False))
            i.immediate_action_taken = "\n\n".join(paragraphs(2, common=False))
            i.remaining_risk = "\n\n".join(paragraphs(2, common=False))
            i.section_engineer_id = random.choice(section_engineers)
            i.area_id = random.choice(areas)
            i.section_id = random.choice(sections)
            i.operation_id = random.choice(operations)
            i.significant = random.random() > 0.5
            i.production_value_loss = random.randint(100, 1000)
            i.rand_value_loss = random.randint(0, 10_000_000)
            i.status = random.choice([c[0] for c in Incident.STATUS_CHOICES])
            i.trigger = random.choice([c[0] for c in Incident.TRIGGER_CHOICES])
            i.save()

        incident_ids = list(Incident.objects.all().values_list("id", flat=True))
        for ix in range(options["solutions"]):
            s = Solution()
            s.incident_id = random.choice(incident_ids)
            s.description = words(5, common=False)
            s.person_responsible = "Some Person"
            s.priority = random.choice([c[0] for c in Solution.PRIORITY_CHOICES])
            s.timeframe = random.choice([c[0] for c in Solution.TIMEFRAME_CHOICES])
            s.remarks = "\n\n".join(paragraphs(2, common=False))
            s.planned_completion_date = now() + timedelta(days=random.randint(10, 300))
            s.status = random.choice([c[0] for c in Solution.STATUS_CHOICES])
            s.save()
