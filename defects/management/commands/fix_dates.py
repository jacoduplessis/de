from django.core.management.base import BaseCommand
from defects.models import Solution
from datetime import datetime
from xlrd import xldate_as_tuple


class Command(BaseCommand):

    def handle(self, *args, **options):

        count = 0
        for obj in Solution.objects.exclude(actual_completion_date_string='').filter(actual_completion_date=None):
            try:
                xl_date = float(obj.actual_completion_date_string)
            except ValueError:
                print('fucked up date: ', obj.actual_completion_date_string)
                continue
            obj.actual_completion_date = datetime(*xldate_as_tuple(xl_date, 0))
            obj.save()
            count += 1
        print(count)
