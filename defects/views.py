import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import modelform_factory
from defects.models import Solution, ReliabilityIncident
from django.forms import widgets
from django.contrib import messages


def index(request):
    return HttpResponseRedirect(reverse('login'))


def apps(request):
    return render(request, 'defects/apps.html')


def home(request):
    return render(request, 'defects/index.html')


def about(request):
    return render(request, 'defects/about.html')


def _badge_generator():
    badges = [
        {'class': "text-bg-primary", 'name': 'active'},
        {'class': "text-bg-secondary", 'name': 'ongoing'},
        {'class': "text-bg-success", 'name': 'complete'},
        {'class': "text-bg-danger", 'name': 'overdue'},
        {'class': "text-bg-warning", 'name': 'incomplete'},
    ]

    while True:
        yield random.choice(badges)


def incident_list(request):
    incidents = ReliabilityIncident.objects.all()

    context = {
        'incidents': zip(incidents, _badge_generator())
    }

    return render(request, 'defects/incident_list.html', context)


def incident_detail(request):
    return render(request, 'defects/incident_detail.html')


def incident_create(request):
    if request.method == 'POST':
        messages.success(request, 'Incident created with RI Number TUM_2022_009')

        return HttpResponseRedirect(
            reverse('incident_detail')
        )

    form_class = modelform_factory(
        ReliabilityIncident,
        fields=[
            'description',
            'time_start',
            'time_end',
            'significant',
            'section',
            'section_engineer',
            'equipment',
            'production_value_loss',
            'rand_value_loss',
        ],
        widgets={
            'section': widgets.Select(
                choices=(
                    ('ams', 'AMS'),
                    ('concentrators', 'Concentrators'),
                    ('dishaba', 'Dishaba'),
                    ('tumela', 'Tumela'),
                )
            ),
            'description': widgets.Textarea(
                attrs={
                    'rows': 3,
                }
            )
        },
        help_texts={
            'significant': 'Is this a significant incident?'
        }
    )

    context = {
        'form': form_class(),
    }
    return render(request, 'defects/incident_create.html', context)


def anniversary_list(request):
    return render(request, 'defects/anniversary_list.html')


def value_dashboard(request):
    return render(request, 'defects/value_dashboard.html')


def compliance_dashboard(request):
    return render(request, 'defects/compliance_dashboard.html')


def solution_list(request):
    context = {
        'solutions': Solution.objects.all()
    }

    return render(request, 'defects/solutions_list.html', context)


def login(request):
    return render(request, 'defects/login.html')
