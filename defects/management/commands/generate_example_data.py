from django.core.management.base import BaseCommand
from defects.models import UserAction, Incident, Section, SectionEngineer, Equipment, Operation, Area, SectionEngineeringManager
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.db import transaction
from django.utils.lorem_ipsum import words, paragraphs
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    UG2_RI_2022_20 	Confirm solution implementation 	1w overdue
    UG1_RI_2022_58 	Upload 48h notification 	3h overdue
    UG2_RI_2022_31 	Upload final report 	2d overdue
    Mer_RI_2022_37 	Review 1-year anniversary 	2d
    UG1_RI_2022_55 	Upload 48h notification 	14h
    UG1_RI_2022_12 	Distribute 48h notification 	7h
    UG1_RI_2022_09 	Upload close-out slide 	1d
    UG1_RI_2022_31 	Update significant status 	3d
    UG2_RI_2022_49 	Sign-off required from SEM 	4d
    UG1_RI_2022_02 	3 solutions to review 	4d
    UG1_RI_2022_14 	Record solution confidence 	2w
    UG2_RI_2022_20 	Confirm solution implementation 	4w

    <tr>
            <td><a href="{% url 'incident_detail' %}?state=17&solutions=1" class="text-black">UG2_RI_2022_20</a></td>
            <td><span class="colored-dot bg-danger"></span> Confirm solution implementation</td>
            <td>1w overdue</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_58</a></td>
            <td><span class="colored-dot bg-danger"></span> Upload 48h notification</td>
            <td>3h overdue</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG2_RI_2022_31</a></td>
            <td><span class="colored-dot bg-danger"></span> Upload final report</td>
            <td>2d overdue</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">Mer_RI_2022_37</a></td>
            <td><span class="colored-dot bg-warning"></span> Review 1-year anniversary</td>
            <td>2d</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_55</a></td>
            <td><span class="colored-dot bg-warning"></span> Upload 48h notification</td>
            <td>14h</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_12</a></td>
            <td><span class="colored-dot bg-warning"></span> Distribute 48h notification</td>
            <td>7h</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_09</a></td>
            <td><span class="colored-dot bg-warning"></span> Upload close-out slide</td>
            <td>1d</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_31</a></td>
            <td><span class="colored-dot bg-info"></span> Update significant status</td>
            <td>3d</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG2_RI_2022_49</a></td>
            <td><span class="colored-dot bg-info"></span> Sign-off required from SEM</td>
            <td>4d</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_02</a></td>
            <td><span class="colored-dot bg-info"></span> 3 solutions to review</td>
            <td>4d</td>
          </tr>

          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG1_RI_2022_14</a></td>
            <td><span class="colored-dot bg-info"></span> Record solution confidence</td>
            <td>2w</td>
          </tr>
          <tr>
            <td><a href="{% url 'incident_detail' %}" class="text-black">UG2_RI_2022_20</a></td>
            <td><span class="colored-dot bg-info"></span> Confirm solution implementation</td>
            <td>4w</td>
          </tr>
    """

    def add_arguments(self, parser):
        parser.add_argument("--user", type=int, default=1)

    def execute(self, *args, **options):
        user_id = options["user"]

        with transaction.atomic():
            amb = Operation.objects.create(name="AMB")

            tumela = Section.objects.create(name="Tumela")
            dishaba = Section.objects.create(name="Dishaba")
            concentrators = Section.objects.create(name="Concentrators")
            aps = Section.objects.create(name="APS")

            se = User.objects.filter(groups__name__in=["section_engineer"]).first()

            winder = Equipment.objects.create(name="Winder", code=get_random_string(length=8))
            motor = Equipment.objects.create(name="Motor", code=get_random_string(length=8))
            pump = Equipment.objects.create(name="pump", code=get_random_string(length=8))

            incidents = [
                Incident(
                    code=Incident.generate_incident_code(),
                    section=tumela,
                    operation=amb,
                    status=Incident.ACTIVE,
                    created_by_id=user_id,
                    section_engineer=se,
                    equipment=motor,
                    time_start=now() - timedelta(days=100, hours=5),
                    time_end=now() - timedelta(days=100),
                    short_description=words(8, common=False),
                    long_description="\n\n".join(paragraphs(3, common=False)),
                ),
                Incident(
                    code=Incident.generate_incident_code(),
                    section=aps,
                    operation=amb,
                    status=Incident.ACTIVE,
                    created_by_id=user_id,
                    section_engineer=se,
                    equipment=motor,
                    time_start=now() - timedelta(days=50, hours=4),
                    time_end=now() - timedelta(days=50),
                    short_description=words(8, common=False),
                    long_description="\n\n".join(paragraphs(3, common=False)),
                ),
                Incident(
                    code=Incident.generate_incident_code(),
                    section=dishaba,
                    operation=amb,
                    status=Incident.ONGOING,
                    created_by_id=user_id,
                    section_engineer=se,
                    equipment=winder,
                    time_start=now() - timedelta(days=20, hours=2),
                    time_end=now() - timedelta(days=20),
                    short_description=words(8, common=False),
                    long_description="\n\n".join(paragraphs(3, common=False)),
                ),
                Incident(
                    code=Incident.generate_incident_code(),
                    section=concentrators,
                    operation=amb,
                    status=Incident.OVERDUE,
                    created_by_id=user_id,
                    section_engineer=se,
                    equipment=pump,
                    time_start=now() - timedelta(days=5, hours=20),
                    time_end=now() - timedelta(days=5),
                    short_description=words(8, common=False),
                    long_description="\n\n".join(paragraphs(3, common=False)),
                ),
            ]

            Incident.objects.bulk_create(incidents)

            UserAction.objects.create(
                user_id=user_id,
                incident_id=1,
                description="Confirm solution implementation",
                time_required=now() - timedelta(days=7),
            )

            UserAction.objects.create(
                user_id=user_id,
                incident_id=2,
                description="Upload 48h notification",
                time_required=now() - timedelta(hours=3),
            )

            UserAction.objects.create(
                user_id=user_id,
                incident_id=3,
                description="Upload final report",
                time_required=now() + timedelta(days=1),
            )

            UserAction.objects.create(
                user_id=user_id,
                incident_id=4,
                description="Review 1-year anniversary",
                time_required=now() + timedelta(days=21),
            )
