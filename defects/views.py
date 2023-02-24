import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from defects.models import Solution, ReliabilityIncident
from django.contrib import messages
from .forms import RILogForm, RINotificationForm, RINotificationApprovalSendForm, RICloseForm
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.utils.lorem_ipsum import words
from dataclasses import dataclass


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


@dataclass
class TimelineEntry:
    time: datetime = now()
    until: datetime = None
    title: str = ''
    icon: str = 'clock'
    icon_classes: str = ''
    link_url: str = '#'
    link_text: str = ''
    secondary_link_text: str = ''
    text: str = ''


def incident_detail(request):
    """
    """

    state = request.GET.get('state', '0')
    state = int(state)

    """
    TimelineEntry(
        icon="",
        title="",
        time=datetime.fromisoformat(''),
        text="",
    )
    TimelineEntry(
        icon="",
        title="",
        time=datetime.fromisoformat(''),
        text="",
    )
    TimelineEntry(
        icon="",
        title="",
        time=datetime.fromisoformat(''),
        text="",
    )
    TimelineEntry(
        icon="",
        title="",
        time=datetime.fromisoformat(''),
        text="",
    )
    TimelineEntry(
        icon="",
        title="",
        time=datetime.fromisoformat(''),
        text="",
    )
    """
    actions = []

    reports = {
        'notification': False,
        'rca': False,
        'close': False
    }

    timeline = [
        TimelineEntry(
            icon='alert-triangle',
            title='Incident Occurrence',
            time=datetime.fromisoformat('2022-10-14 09:18'),
            until=datetime.fromisoformat('2022-10-14 11:09'),
            text='Downtime',
        ),
        TimelineEntry(
            icon="log-in",
            title="Incident Logged",
            time=datetime.fromisoformat('2022-10-14 18:30'),
            text="Created by Name Surname.",
        )
    ]

    if state == 1:
        actions = [
            TimelineEntry(
                icon='clock',
                title='Create 48-hour notification report',
                time=datetime.fromisoformat('2023-10-16'),
                text='12 hours of deadline remaining',
                link_text='Add Information',
                link_url=reverse('incident_notification_form')
            )
        ]

    if state >= 2:
        timeline.append(
            TimelineEntry(
                icon="file",
                title="48-hour notification report created",
                time=datetime.fromisoformat('2022-10-15 14:13'),
                text="Created by Name Surname.",
                link_url='#',
                link_text='View Report'
            )
        )
        reports['notification'] = True

    if state == 2:
        actions = [
            TimelineEntry(
                title='Send 48-hr notification report to SEM for approval',
                time=datetime.fromisoformat('2022-10-16 09:00'),
                text='12 hours of deadline remaining',
                link_url=reverse('incident_notification_approval_send'),
                link_text='Send Report',
            )
        ]

    if state >= 3:
        timeline.append(
            TimelineEntry(
                title="48-hr notification report sent to SEM for approval",
                time=datetime.fromisoformat('2022-10-16 09:00'),
                text="Status: Awaiting Approval",
                link_text='View Report'
            )
        )
    if state == 3:
        actions = [
            TimelineEntry(
                title='Demo: Mark as Approved from SEM',
                time=datetime.fromisoformat('2022-10-16 09:00'),
                link_url=reverse('incident_detail') + '?state=4',
                link_text='Proceed',
            )
        ]

    if state >= 4:
        timeline.append(
            TimelineEntry(
                icon='check',
                title='48Hr Notification approved by SEM and circulated to AS&R Team',
                time=datetime.fromisoformat('2022-10-17 12:15'),
                text='alternatively – 48Hr Notification rejected by SEM and not circulated to AS&R Team. Please read SEM comments and resubmit.'
            )
        )

    if state == 4:
        actions = [
            TimelineEntry(
                time=datetime.fromisoformat('2022-10-17 12:15'),
                title='Is a full RCA Report required?',
                text='Note that full RCA investigation must be scheduled, conducted and the full RCA report must be submitted within 14 days of submitting the 48-hr Notification Report.',
                link_text='Mark incident as requiring RCA',
                link_url=reverse('incident_detail') + '?state=5',
                secondary_link_text='RCA Report not required'
            )
        ]

    if state >= 5:
        timeline.append(
            TimelineEntry(
                title='Incident marked as requiring an RCA report'
            )
        )
    if state == 5:
        actions = [
            TimelineEntry(
                title='Upload RCA report',
                link_text='Upload report',
                link_url=reverse('incident_detail') + '?state=6'
            )
        ]

    if state >= 6:
        timeline.append(
            TimelineEntry(
                icon='file',
                title='RCA report uploaded',
                text='Uploaded by Name Surname.',
                link_text='View RCA report',
            )
        )
        reports['rca'] = True
    if state == 6:
        actions = [
            TimelineEntry(
                title='Send full RCA Report to SE and SEM for approval',
                link_text='Send Report',
                link_url=reverse('incident_detail') + '?state=7'
            )
        ]

    if state >= 7:
        timeline.append(
            TimelineEntry(
                title='RCA report sent to SE and SEM for approval',
                text='Status: awaiting approval. SE: John Smith. SEM: Jane Doe.'
            )
        )
    if state == 7:
        actions = [
            TimelineEntry(
                title='Demo: Mark as approved',
                link_text='Proceed',
                link_url=reverse('incident_detail') + '?state=8'
            )
        ]

    if state >= 8:
        timeline.append(
            TimelineEntry(
                icon='check',
                title='RCA Report approved by SE and SEM',
                text='alternatively – RCA Report rejected by SE and/or SEM. Please read comments and resubmit.'
            )
        )

    if state == 8:
        actions = [
            TimelineEntry(
                title='Send RCA Report to Snr AM to approve and forward to the Snr EM for review',
                link_text='Send report',
                link_url=reverse('incident_detail') + '?state=9'
            )
        ]

    if state >= 9:
        timeline.append(
            TimelineEntry(
                title='RCA Report submitted to Snr AM for approval'
            )
        )

    if state == 9:
        actions = [
            TimelineEntry(
                title='Demo: Mark as approved',
                link_text='Proceed',
                link_url=reverse('incident_detail') + '?state=10'
            )
        ]

    if state >= 10:
        timeline.append(
            TimelineEntry(
                icon='check',
                title='RCA Report approved by senior AM'
            )
        )

    if state == 10:
        actions = [
            TimelineEntry(
                title='Create Close Out Slide',
                link_text='Add Data',
                link_url=reverse('incident_close_form')
            )
        ]

    if state >= 11:
        timeline.append(
            TimelineEntry(
                title='Close out confidence submitted to SE and SEM for ranking',
                link_text='View Close-Out Slide'
            )
        )
        reports['close'] = True

    if state == 11:
        actions = [
            TimelineEntry(
                title='Demo: Mark as approved',
                link_url=reverse('incident_detail') + '?state=12',
                link_text='Proceed',
            )
        ]

    if state >= 12:
        timeline.append(
            TimelineEntry(
                icon="check",
                icon_classes="bg-success text-white",
                title='Incident Closed: This incident has a close out confidence ranking of "X" stars. This is above the 2-star minumum threshold.',
                text='alternatively – Incident Not Closed: This incident has a close out confidence ranking of "X" stars. This is below the 2-star minumum threshold. Please read SE and/or SEM comments and resubmit.'
            )
        )
    if state == 12:
        actions = [
            TimelineEntry(
                title='Send Close Out Slide to Scheduler',
                link_text='Send',
                link_url=reverse('incident_detail') + '?state=13'
            )
        ]

    if state >= 13:
        timeline.append(
            TimelineEntry(
                icon='check',
                title='Close-out slide sent to scheduler.',
                text='Scheduler: Name Surname',
            )
        )
    if state == 13:
        actions = [
            TimelineEntry(
                icon="clock",
                title="One-Year Anniversary Review",
                time=datetime.fromisoformat('2023-10-16'),
                text=words(20, common=False)
            )
        ]

    context = {
        'timeline': timeline,
        'actions': actions,
        'reports': reports,
    }

    return render(request, 'defects/incident_detail.html', context=context)


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
        messages.success(request, message='48-hour Notification Report created.')
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
        messages.success(request, 'Close-out slide created.')
        return HttpResponseRedirect(
            reverse('incident_detail') + '?state=11'
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
    incidents = ReliabilityIncident.objects.all()[:10]

    context = {
        'incidents': incidents
    }

    return render(request, 'defects/anniversary_list.html', context=context)

def solution_schedule(request):

    if request.method == 'GET':

        context = {
            'solutions': Solution.objects.all()[:5]
        }

        return render(request, 'defects/solutions_schedule.html', context=context)

    if request.method == 'POST':
        messages.success(request, '5 solutions have been scheduled.')
        return HttpResponseRedirect(
            reverse('solution_list') + '?filter=1&solution_status=scheduled'
        )

def solution_completion(request):

    if request.method == 'GET':

        context = {
            'solutions': Solution.objects.all()[:5]
        }

        return render(request, 'defects/solutions_completion.html', context=context)

    if request.method == 'POST':
        messages.success(request, '5 solutions have been processed.')
        return HttpResponseRedirect(
            reverse('solution_list') + '?filter=1&solution_status=complete'
        )

def value_dashboard(request):
    return render(request, 'defects/value_dashboard.html')


def compliance_dashboard(request):
    return render(request, 'defects/compliance_dashboard.html')


def solution_list(request):

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'completion':
            return HttpResponseRedirect(
                reverse('solution_completion')
            )

        if action == 'schedule':
            return HttpResponseRedirect(
                reverse('solution_schedule')
            )

    qs = Solution.objects.all()
    if request.GET.get('filter'):
        qs = qs[:6]

    context = {
        'solutions': qs
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
