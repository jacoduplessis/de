from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Solution, Incident, UserAction, Section, Equipment
from django.contrib import messages
from .forms import IncidentCreateForm, IncidentNotificationForm, RINotificationApprovalSendForm, RICloseForm, IncidentUpdateForm
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.utils.lorem_ipsum import words
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.db.models.aggregates import Count
from auditlog.signals import accessed

from .timelines import TimelineEntry


def index(request):
    return HttpResponseRedirect(reverse("login"))


@login_required()
def apps(request):
    return render(request, "defects/apps.html")


@login_required()
def home(request):
    context = {
        "sections": (Section.objects.annotate(count=Count("incidents")).all().values_list("name", "count", named=True)),
        "equipment": (
            Equipment.objects.filter(incidents__time_start__gte=now() - timedelta(days=365))
            .annotate(count=Count("incidents"))
            .filter(count__gte=1)
            .values_list("name", "count", named=True)
        ),
        "user_actions": (UserAction.objects.select_related("incident").filter(user=request.user, time_dismissed=None).order_by("time_required")),
    }

    return render(request, template_name="defects/index.html", context=context)


@login_required()
def about(request):
    return render(request, "defects/about.html")


@login_required()
def incident_list(request):
    incidents = Incident.objects.select_related("created_by", "equipment", "section", "section_engineer").all()

    context = {"incidents": incidents}

    return render(request, "defects/incident_list.html", context)


@login_required()
def incident_detail(request, pk):
    incident = (
        Incident.objects
        .select_related("section", "created_by", "section_engineer", "equipment")
        .get(pk=pk)
    )

    accessed.send(Incident, instance=incident)

    context = {"incident": incident}

    return render(request, template_name="defects/incident_detail.html", context=context)


@login_required()
def incident_detail_demo(request):
    """ """

    state = request.GET.get("state", "0")
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

    reports = {"notification": False, "rca": False, "close": False}

    timeline = [
        TimelineEntry(
            icon="alert-triangle",
            title="Incident Occurrence",
            time=datetime.fromisoformat("2022-10-14 09:18"),
            until=datetime.fromisoformat("2022-10-14 11:09"),
            text="Downtime",
        ),
        TimelineEntry(
            icon="log-in",
            title="Incident Logged",
            time=datetime.fromisoformat("2022-10-14 18:30"),
            text="Created by Name Surname.",
        ),
    ]

    if state == 1:
        actions = [
            TimelineEntry(
                icon="clock",
                title="Create 48-hour notification report",
                time=datetime.fromisoformat("2023-10-16"),
                text="12 hours of deadline remaining",
                link_text="Add Information",
                link_url=reverse("incident_notification_form"),
            )
        ]

    if state >= 2:
        timeline.append(
            TimelineEntry(
                icon="file",
                title="48-hour notification report created",
                time=datetime.fromisoformat("2022-10-15 14:13"),
                text="Created by Name Surname.",
                link_url="#",
                link_text="View Report",
            )
        )
        reports["notification"] = True

    if state == 2:
        actions = [
            TimelineEntry(
                title="Send 48-hr notification report to SEM for approval",
                time=datetime.fromisoformat("2022-10-16 09:00"),
                text="12 hours of deadline remaining",
                link_url=reverse("incident_notification_approval_send"),
                link_text="Send Report",
            )
        ]

    if state >= 3:
        timeline.append(
            TimelineEntry(
                title="48-hr notification report sent to SEM for approval",
                time=datetime.fromisoformat("2022-10-16 09:00"),
                text="Status: Awaiting Approval",
                link_text="View Report",
            )
        )
    if state == 3:
        actions = [
            TimelineEntry(
                title="Demo: Mark as Approved from SEM",
                time=datetime.fromisoformat("2022-10-16 09:00"),
                link_url=reverse("incident_detail_demo") + "?state=4",
                link_text="Proceed",
            )
        ]

    if state >= 4:
        timeline.append(
            TimelineEntry(
                icon="check",
                title="48Hr Notification approved by SEM and circulated to AS&R Team",
                time=datetime.fromisoformat("2022-10-17 12:15"),
                text="alternatively – 48Hr Notification rejected by SEM and not circulated to AS&R Team. Please read SEM comments and resubmit.",
            )
        )

    if state == 4:
        actions = [
            TimelineEntry(
                time=datetime.fromisoformat("2022-10-17 12:15"),
                title="Is a full RCA Report required?",
                text="Note that full RCA investigation must be scheduled, conducted and the full RCA report must be submitted within 14 days of submitting the 48-hr Notification Report.",
                link_text="Mark incident as requiring RCA",
                link_url=reverse("incident_detail_demo") + "?state=5",
                secondary_link_text="RCA Report not required",
            )
        ]

    if state >= 5:
        timeline.append(TimelineEntry(title="Incident marked as requiring an RCA report"))
    if state == 5:
        actions = [TimelineEntry(title="Upload RCA report", link_text="Upload report", link_url=reverse("incident_detail_demo") + "?state=6")]

    if state >= 6:
        timeline.append(
            TimelineEntry(
                icon="file",
                title="RCA report uploaded",
                text="Uploaded by Name Surname.",
                link_text="View RCA report",
            )
        )
        reports["rca"] = True
    if state == 6:
        actions = [
            TimelineEntry(
                title="Send full RCA Report to SE and SEM for approval",
                link_text="Send Report",
                link_url=reverse("incident_detail_demo") + "?state=7",
            )
        ]

    if state >= 7:
        timeline.append(
            TimelineEntry(title="RCA report sent to SE and SEM for approval", text="Status: awaiting approval. SE: John Smith. SEM: Jane Doe.")
        )
    if state == 7:
        actions = [TimelineEntry(title="Demo: Mark as approved", link_text="Proceed", link_url=reverse("incident_detail_demo") + "?state=8")]

    if state >= 8:
        timeline.append(
            TimelineEntry(
                icon="check",
                title="RCA Report approved by SE and SEM",
                text="alternatively – RCA Report rejected by SE and/or SEM. Please read comments and resubmit.",
            )
        )

    if state == 8:
        actions = [
            TimelineEntry(
                title="Send RCA Report to Snr AM to approve and forward to the Snr EM for review",
                link_text="Send report",
                link_url=reverse("incident_detail_demo") + "?state=9",
            )
        ]

    if state >= 9:
        timeline.append(TimelineEntry(title="RCA Report submitted to Snr AM for approval"))

    if state == 9:
        actions = [TimelineEntry(title="Demo: Mark as approved", link_text="Proceed", link_url=reverse("incident_detail_demo") + "?state=10")]

    if state >= 10:
        timeline.append(TimelineEntry(icon="check", title="RCA Report approved by senior AM"))

    if state == 10:
        actions = [TimelineEntry(title="Create Close Out Slide", link_text="Add Data", link_url=reverse("incident_close_form"))]

    if state >= 11:
        timeline.append(TimelineEntry(title="Close out confidence submitted to SE and SEM for ranking", link_text="View Close-Out Slide"))
        reports["close"] = True

    if state == 11:
        actions = [
            TimelineEntry(
                title="Demo: Mark as approved",
                link_url=reverse("incident_detail_demo") + "?state=12",
                link_text="Proceed",
            )
        ]

    if state >= 12:
        timeline.append(
            TimelineEntry(
                icon="check",
                icon_classes="bg-success text-white",
                title='Incident Closed: This incident has a close out confidence ranking of "X" stars. This is above the 2-star minumum threshold.',
                text='alternatively – Incident Not Closed: This incident has a close out confidence ranking of "X" stars. This is below the 2-star minumum threshold. Please read SE and/or SEM comments and resubmit.',
            )
        )
    if state == 12:
        actions = [TimelineEntry(title="Send Close Out Slide to Scheduler", link_text="Send", link_url=reverse("incident_detail_demo") + "?state=13")]

    if state >= 13:
        timeline.append(
            TimelineEntry(
                icon="check",
                title="Close-out slide sent to scheduler.",
                text="Scheduler: Name Surname",
            )
        )
    if state == 13:
        actions = [
            TimelineEntry(icon="clock", title="One-Year Anniversary Review", time=datetime.fromisoformat("2023-10-16"), text=words(20, common=False))
        ]

    context = {
        "timeline": timeline,
        "actions": actions,
        "reports": reports,
    }

    return render(request, "defects/incident_detail_demo.html", context=context)


@login_required
def incident_create(request):
    if request.method == "POST":
        form = IncidentCreateForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Please correct the form inputs and submit again.")
            context = {"form": form}
            return render(request, "defects/incident_create.html", context)
        obj = form.save(commit=False)
        obj.code = Incident.generate_incident_code()
        obj.created_by = request.user
        obj.save()
        messages.success(request, f"Incident created with RI Number {obj.code}")
        return HttpResponseRedirect(reverse("incident_detail", args=[obj.pk]))

    if request.method == "GET":
        context = {
            "form": IncidentCreateForm(),
        }
        return render(request, "defects/incident_create.html", context)


@login_required
def incident_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        form = IncidentUpdateForm(request.POST, request.FILES, instance=incident)
        if not form.is_valid():
            messages.error(request, "Please correct the form inputs and submit again.")
            context = {"form": form}
            return render(request, "defects/incident_update.html", context)
        obj = form.save()
        messages.success(request, "Incident updated.")
        return HttpResponseRedirect(reverse("incident_detail", args=[obj.pk]))

    if request.method == "GET":
        context = {
            "form": IncidentUpdateForm(instance=incident),
        }
        return render(request, "defects/incident_update.html", context)


def incident_notification_form(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":
        form = IncidentNotificationForm(request.POST, request.FILES, instance=incident)
        if not form.is_valid():
            messages.error(request, "Please correct the form inputs and submit again.")
            context = {"form": form}
            return render(request, "defects/incident_notification_form.html", context)

        form.save()
        action = request.POST.get("action", "").lower()
        if action == "save":
            # redirect to self
            return HttpResponseRedirect(reverse("incident_notification_form", args=[incident.pk]))
        if "download" in action:
            # todo: build a file
            response = HttpResponse(content_type="")
            response.headers["content-disposition"] = 'attachment; filename="filename.jpg"'
            return


    if request.method == "GET":
        context = {
            "form": IncidentNotificationForm(instance=incident),
        }
        return render(request, "defects/incident_notification_form.html", context)


def incident_close_form(request):
    if request.method == "POST":
        messages.success(request, "Close-out slide created.")
        return HttpResponseRedirect(reverse("incident_detail_demo") + "?state=11")

    initial = {"incident_date": now(), "short_description": words(8)}

    context = {
        "form": RICloseForm(initial=initial),
    }
    return render(request, "defects/incident_close_form.html", context)


def anniversary_list(request):
    incidents = Incident.objects.all()[:10]

    context = {"incidents": incidents}

    return render(request, "defects/anniversary_list.html", context=context)


def solution_schedule(request):
    if request.method == "GET":
        context = {"solutions": Solution.objects.all()[:5]}

        return render(request, "defects/solutions_schedule.html", context=context)

    if request.method == "POST":
        messages.success(request, "5 solutions have been scheduled.")
        return HttpResponseRedirect(reverse("solution_list") + "?filter=1&solution_status=scheduled")


@login_required()
def solution_completion(request):
    if request.method == "GET":
        context = {"solutions": Solution.objects.all()[:5]}

        return render(request, "defects/solutions_completion.html", context=context)

    if request.method == "POST":
        messages.success(request, "5 solutions have been processed.")
        return HttpResponseRedirect(reverse("solution_list") + "?filter=1&solution_status=complete")


@login_required()
def value_dashboard(request):
    return render(request, "defects/value_dashboard.html")


@login_required()
def compliance_dashboard(request):
    return render(request, "defects/compliance_dashboard.html")


@login_required()
def solution_list(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "completion":
            return HttpResponseRedirect(reverse("solution_completion"))

        if action == "schedule":
            return HttpResponseRedirect(reverse("solution_schedule"))

    qs = Solution.objects.all()
    if request.GET.get("filter"):
        qs = qs[:6]

    context = {"solutions": qs}

    return render(request, "defects/solutions_list.html", context)


@login_required()
def incident_notification_approval_send(request):
    if request.method == "POST":
        messages.success(request, "Notification report has be sent to SEM for approval.")

        return HttpResponseRedirect(reverse("incident_detail_demo") + "?state=3")

    context = {"form": RINotificationApprovalSendForm()}

    return render(request, "defects/incident_notification_approval_send.html", context)


class LoginView(BaseLoginView):
    template_name = "defects/login.html"
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    pass


def login(request):
    return render(request, "defects/login.html")


def equipment_search(request):
    query = request.GET.get("q")

    qs = Equipment.objects.filter(Q(code=query) | Q(name__icontains=query))[:50]

    return JsonResponse({
        "items": [{"id": x.id, "name": str(x)} for x in qs],
    })
