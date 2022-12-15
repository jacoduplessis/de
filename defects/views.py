import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from defects.models import Solution, ReliabilityIncident
from django.contrib import messages
from .forms import RILogForm, RINotificationForm, RINotificationApprovalSendForm, RICloseForm
from django.utils.timezone import now
from datetime import timedelta
from django.utils.lorem_ipsum import words


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
    """
    Possible States:

    0 - as in initial demo
    1 - after initial log of RI

    """

    state = request.GET.get('state', '0')

    template_name = f'defects/incident_detail_{state}.html'

    return render(request, template_name=template_name)


def incident_create(request):
    if request.method == 'POST':
        messages.success(request, 'Incident created with RI Number TUM_2022_009')

        return HttpResponseRedirect(
            reverse('incident_detail') + '?state=1'
        )

    context = {
        'form': RILogForm(),
    }
    return render(request, 'defects/incident_create.html', context)


def incident_notification_form(request):
    if request.method == 'POST':
        return HttpResponseRedirect(
            reverse('incident_detail') + '?state=2'
        )

    initial = {
        'time_start': now() - timedelta(hours=5),
        'time_end': now(),
        'short_description': words(8)
    }

    context = {
        'form': RINotificationForm(initial=initial),
    }
    return render(request, 'defects/incident_notification_form.html', context)


def incident_close_form(request):
    if request.method == 'POST':

        return HttpResponseRedirect(
            reverse('incident_detail')  # todo: add state
        )

    initial = {
        'incident_date': now(),
        'short_description': words(8)
    }

    context = {
        'form': RICloseForm(initial=initial),
    }
    return render(request, 'defects/incident_close_form.html', context)


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


def incident_notification_approval_send(request):

    if request.method == 'POST':
        messages.success(request, 'Notification report has be sent to SEM for approval.')

        return HttpResponseRedirect(
            reverse('incident_detail') + '?state=3'
        )

    context = {
        'form': RINotificationApprovalSendForm()
    }

    return render(request, 'defects/incident_notification_approval_send.html', context)



def login(request):
    return render(request, 'defects/login.html')
