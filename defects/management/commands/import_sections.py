from django.core.management.base import BaseCommand
from django.utils.text import slugify
from defects.models import Section
import pathlib


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('file')
        parser.add_argument('area_id')

    def handle(self, *args, **options):

        rows = pathlib.Path(options['file']).read_text().splitlines()

        objs = []

        for row in rows:
            if not row:
                continue

            objs.append(Section(name=row, code=slugify(row), area_id=options['area_id']))

        Section.objects.bulk_create(objs)
