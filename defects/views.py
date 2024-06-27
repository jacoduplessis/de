import json
from datetime import timedelta

from auditlog.models import LogEntry
from auditlog.signals import accessed
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Prefetch, OuterRef, Subquery, Value
from django.db.models.aggregates import Count
from django.forms import modelformset_factory, modelform_factory, Textarea, Select
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.lorem_ipsum import words
from django.utils.timezone import now
from django.views.decorators.http import require_POST, require_GET

from .exports import export_table_csv
from .forms import (
    IncidentCreateForm,
    IncidentNotificationApprovalSendForm,
    IncidentUpdateForm,
    ApprovalForm,
    IncidentFilterForm,
    SolutionFilterForm,
    IncidentSignificanceUpdateForm,
    IncidentCloseOutForm,
    IncidentCloseApprovalSendForm,
    IncidentRCAApprovalSendForm,
)
from .models import Solution, Incident, Section, Equipment, IncidentImage, Approval, Area, Feedback, Operation, ResourcePrice
from .actions import get_user_actions


def index(request):
    return HttpResponseRedirect(reverse("login"))


@login_required()
def apps(request):
    return render(request, "defects/apps.html")


@login_required()
def home(request):
    def _subquery(q_kwarg):
        filters = {q_kwarg: OuterRef("pk")}

        return Subquery(Incident.objects.filter(**filters, status=Incident.ACTIVE).values(q_kwarg).annotate(count=Count("*")).values("count"))

    overdue_anniversaries = (
        Incident.objects.prefetch_related("solutions")
        .filter(time_start__lt=now() - timedelta(days=365))
        .filter(time_anniversary_reviewed=None)
        .order_by("time_start")
        .annotate(anniversary_status=Value("overdue"))
    )

    upcoming_anniversaries = (
        Incident.objects.prefetch_related("solutions")
        .filter(time_start__gte=now() - timedelta(days=365), time_start__lte=now() - timedelta(days=334))
        .filter(time_anniversary_reviewed=None)
        .order_by("time_start")
        .annotate(anniversary_status=Value("upcoming"))
    )

    anniversaries = list(overdue_anniversaries) + list(upcoming_anniversaries)

    context = {
        "sections": (Section.objects.annotate(count=_subquery("section_id")).values_list("name", "count", named=True)),
        "areas": (Area.objects.annotate(count=_subquery("area_id")).values_list("name", "count", named=True)),
        "operations": (Operation.objects.annotate(count=_subquery("operation_id")).values_list("name", "count", named=True)),
        "equipment": (
            Equipment.objects.filter(incidents__time_start__gte=now() - timedelta(days=365))
            .annotate(count=Count("incidents"))
            .filter(count__gte=1)
            .values_list("name", "count", named=True)
        ),
        "user_actions": get_user_actions(request.user),
        "approvals": (
            Approval.objects
                .select_related("incident", "created_by")
                .filter(user=request.user)
                .filter(Q(outcome="", type__in=[Approval.RCA, Approval.NOTIFICATION]) | Q(score=0, type=Approval.CLOSE_OUT))
        ),
        "anniversaries": anniversaries
    }

    return render(request, template_name="defects/index.html", context=context)


@login_required()
def about(request):
    return render(request, "defects/about.html")


@login_required()
def incident_list(request):
    incidents = Incident.objects.select_related("created_by", "equipment", "section", "section_engineer").order_by("-time_start")

    query = request.GET.get("query", "")

    if query:
        search_filters = (
            Q(short_description__icontains=query) | Q(long_description__icontains=query) | Q(code__exact=query) | Q(equipment__name__icontains=query)
        )
        incidents = incidents.filter(search_filters)

    area_id = request.GET.get("area")
    if area_id:
        incidents = incidents.filter(area_id=area_id)

    section_id = request.GET.get("section")
    if section_id:
        incidents = incidents.filter(section_id=section_id)

    operation_id = request.GET.get("operation")
    if operation_id:
        incidents = incidents.filter(operation_id=operation_id)

    status = request.GET.get("status")
    if status:
        incidents = incidents.filter(status=status)

    context = {"incidents": incidents, "query": query}

    return render(request, "defects/incident_list.html", context)


@login_required
def incident_detail(request, pk):
    incident = (
        Incident.objects.select_related("section", "created_by", "section_engineer", "equipment")
        .prefetch_related("images", "approvals", "solutions")
        .get(pk=pk)
    )
    accessed.send(Incident, instance=incident)

    context = {"incident": incident}

    return render(request, template_name="defects/incident_detail.html", context=context)


def incident_notification(request, pk):
    incident = Incident.objects.select_related("section", "created_by", "section_engineer", "equipment").prefetch_related("images").get(pk=pk)

    context = {"incident": incident, "images": incident.images.all().order_by("index")}

    LogEntry.objects.log_create(instance=incident, action=LogEntry.Action.ACCESS, changes="View incident 48h-notification")

    return render(request, template_name="defects/incident_notification.html", context=context)


def incident_notification_approval_request(request, pk):
    """
    Rendered in modal.
    """

    incident = Incident.objects.select_related("section", "created_by", "section_engineer", "equipment").prefetch_related("images").get(pk=pk)

    if request.method == "GET":
        form = IncidentNotificationApprovalSendForm()

        context = {
            "incident": incident,
            "form": form,
        }

        return render(request, template_name="defects/incident_notification_approval_request.html", context=context)

    if request.method == "POST":
        form = IncidentNotificationApprovalSendForm(request.POST)

        if not form.is_valid():
            context = {
                "incident": incident,
                "form": form,
            }
            return render(request, template_name="defects/incident_notification_approval_request.html", context=context)

        else:
            user = form.cleaned_data["user"]

            # create an approval object
            Approval.objects.create(
                created_by=request.user,
                name=user.username,
                user=user,
                role=Approval.SECTION_ENGINEERING_MANAGER,
                type=Approval.NOTIFICATION,
                incident=incident,
            )
            incident.notification_time_published = now()
            incident.save()
            # set notification time published

            messages.success(request, "Notification report has be sent to SEM for approval.")
            return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))


@login_required
@permission_required("defects.add_incident")
def incident_create(request):
    """
    Rendered in modal.
    """
    template_name = "defects/incident_create_modal.html"

    if request.method == "POST":
        form = IncidentCreateForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, "Please correct the form inputs and submit again.")
            context = {"form": form}
            return render(request, template_name, context=context, status=422)
        obj = form.save(commit=False)

        section_id = obj.section_id
        section_code = "XXX"
        try:
            assert section_id is not None
            section_code = Section.objects.get(id=section_id).code
            assert section_code != ""
        except (AssertionError, Section.DoesNotExist):
            pass

        obj.code = Incident.generate_incident_code(section_code=section_code, incident_type="RI")
        obj.created_by = request.user
        obj.save()
        messages.success(request, f"Incident created with RI Number {obj.code}")
        return HttpResponseRedirect(reverse("incident_detail", args=[obj.pk]))

    if request.method == "GET":
        context = {
            "form": IncidentCreateForm(initial={"time_start": now() - timedelta(hours=2), "time_end": now()}),
        }
        return render(request, template_name, context)


@login_required
def incident_update(request, pk):
    """
    Renders in modal.
    """
    template_name = "defects/incident_update_modal.html"

    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "POST":
        form = IncidentUpdateForm(request.POST, request.FILES, instance=incident)
        if not form.is_valid():
            messages.error(request, "Please correct the form inputs and submit again.")
            context = {"form": form}
            return render(request, template_name, context)
        obj = form.save()

        most_recent_resource_price = ResourcePrice.objects.order_by("-time_created").select_related("created_by").first()
        submitted_resource_price = form.cleaned_data["resource_price"]
        if submitted_resource_price != most_recent_resource_price.rate:
            ResourcePrice.objects.create(rate=submitted_resource_price, created_by=request.user)
            messages.success(request, "Default resource price updated.")
        messages.success(request, "Incident updated.")
        return HttpResponseRedirect(reverse("incident_detail", args=[obj.pk]))

    if request.method == "GET":
        context = {
            "form": IncidentUpdateForm(instance=incident),
        }
        return render(request, template_name, context)


@login_required
def incident_images(request, pk):
    """
    Renders in modal.
    """
    images_prefetch = Prefetch("images", queryset=IncidentImage.objects.order_by("index"))

    incident = Incident.objects.prefetch_related(images_prefetch).get(pk=pk)

    formset_class = modelformset_factory(
        model=IncidentImage,
        fields=[
            "image",
            "description",
        ],
        extra=3,
        can_order=False,
        widgets={"description": Textarea(attrs={"rows": 2})},
    )

    if request.method == "GET":
        context = {
            "formset": formset_class(queryset=IncidentImage.objects.none()),
            "incident": incident,
            "images": incident.images.all(),
        }
        return render(request, "defects/incident_images.html", context=context)

    if request.method == "POST":
        formset = formset_class(request.POST, request.FILES)

        if not formset.is_valid():
            context = {
                "formset": formset,
                "incident": incident,
            }
            return render(request, "defects/incident_images.html", context=context)

        else:
            objs = formset.save(commit=False)
            for obj in objs:
                obj.created_by = request.user
                obj.incident_id = pk
                obj.save()

            messages.success(request, "Images uploaded.")

        return HttpResponseRedirect(reverse("incident_images", args=[pk]))


@login_required
def incident_notification_pdf(request, pk):
    from weasyprint import HTML
    from .reports import url_fetcher

    qs = Incident.objects.prefetch_related("images").select_related("section")

    incident = get_object_or_404(qs, pk=pk)

    context = {"incident": incident, "images": incident.images.all()}

    markup = render_to_string("defects/reports/notification.html", context=context, request=request)

    file_name = f"AMB 48H RI - {incident.section.code} - {incident.short_description} - ({incident.time_start.strftime("%d.%m.%Y")}).pdf"

    response = HttpResponse(
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": f'filename="{file_name}"',
        }
    )

    doc = HTML(string=markup, url_fetcher=url_fetcher)
    doc.write_pdf(target=response)
    return response


@login_required
def incident_anniversary_pdf(request, pk):
    from weasyprint import HTML
    from .reports import url_fetcher

    qs = Incident.objects.prefetch_related("solutions")

    incident = get_object_or_404(qs, pk=pk)

    context = {"incident": incident}

    markup = render_to_string("defects/reports/anniversary.html", context=context, request=request)

    response = HttpResponse(
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": f'filename="anniversary-{incident.code}.pdf"',
        }
    )

    doc = HTML(string=markup, url_fetcher=url_fetcher)
    doc.write_pdf(target=response)
    return response


@login_required
def incident_anniversary_detail(request, pk):
    """
    Renders in modal
    """
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == "GET":
        return render(request, "defects/incident_anniversary_detail.html", context={"incident": incident})

    if request.method == "POST":
        "this marks the anniversary as reviewed"
        incident.time_anniversary_reviewed = now()
        incident.anniversary_reviewed_by = request.user
        incident.save()
        messages.success(request, "Anniversary has been marked as reviewed.")
        return HttpResponseRedirect(reverse("anniversary_list"))


@login_required
def incident_close_pdf(request, pk):
    from weasyprint import HTML
    from .reports import url_fetcher

    incident = get_object_or_404(Incident, pk=pk)

    se_approval = Approval.objects.select_related("user").order_by("-time_modified").filter(incident=incident, role=Approval.SECTION_ENGINEER, type=Approval.CLOSE_OUT).first()
    sem_approval = Approval.objects.select_related("user").order_by("-time_modified").filter(incident=incident, role=Approval.SECTION_ENGINEERING_MANAGER, type=Approval.CLOSE_OUT).first()

    # ["name", 1, <date>|<datetime>]
    ratings = {
        "re": [incident.created_by.username, incident.close_out_confidence, incident.close_out_time_published],
        "se": ["---", 0, None] if se_approval is None else [se_approval.user.username, se_approval.score, sem_approval.time_modified],
        "sem": ["---", 0, None] if sem_approval is None else [sem_approval.user.username, sem_approval.score, sem_approval.time_modified],
    }

    context = {"incident": incident, "ratings": ratings}

    markup = render_to_string("defects/reports/closeout.html", context=context, request=request)

    if request.GET.get("html") == "1":
        markup = markup.replace("static:", "/static/")
        return HttpResponse(markup, headers={"content-type": "text/html"})

    response = HttpResponse(
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": f'filename="close-{incident.code}.pdf"',
        }
    )

    doc = HTML(string=markup, url_fetcher=url_fetcher)
    doc.write_pdf(target=response)
    return response


@login_required
def incident_close_form(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "GET":
        initial = {
            "close_out_short_term_date": incident.time_start + timedelta(days=90),
            "close_out_medium_term_date": incident.time_start + timedelta(days=180),
            "close_out_long_term_date": incident.time_start + timedelta(days=365),
        }

        context = {
            "incident": incident,
            "form": IncidentCloseOutForm(instance=incident, initial=initial),
        }

        return render(request, "defects/incident_close_form.html", context=context)

    if request.method == "POST":
        form = IncidentCloseOutForm(request.POST, request.FILES, instance=incident)

        if not form.is_valid():
            context = {
                "incident": incident,
                "form": form,
            }

            return render(request, "defects/incident_close_form.html", context=context, status=422)
        form.save()
        messages.success(request, "Close-out slide info saved.")
        return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))

    initial = {"incident_date": now(), "short_description": words(8)}

    context = {
        "form": IncidentCloseOutForm(initial=initial),
    }
    return render(request, "defects/incident_close_form.html", context)


@login_required
def anniversary_list(request):
    incidents = (
        Incident.objects.prefetch_related("solutions")
        .filter(time_start__lt=now() - timedelta(days=360))
        .filter(time_anniversary_reviewed=None)
    )

    context = {"incidents": incidents}

    return render(request, "defects/anniversary_list.html", context=context)


@login_required
def solution_schedule(request):
    if request.method == "GET":
        context = {"solutions": Solution.objects.all()[:5]}

        return render(request, "defects/solutions_schedule.html", context=context)

    if request.method == "POST":
        messages.success(request, "5 solutions have been scheduled.")
        return HttpResponseRedirect(reverse("solution_list") + "?filter=1&solution_status=scheduled")


@login_required
def solution_completion(request):
    if request.method == "GET":
        context = {"solutions": Solution.objects.all()[:5]}

        return render(request, "defects/solutions_completion.html", context=context)

    if request.method == "POST":
        messages.success(request, "5 solutions have been processed.")
        return HttpResponseRedirect(reverse("solution_list") + "?filter=1&solution_status=complete")


@login_required
def value_dashboard(request):
    return render(request, "defects/value_dashboard.html")


@login_required
def compliance_dashboard(request):
    grouping = request.GET.get("grouping")

    return render(request, "defects/compliance_dashboard.html")


@login_required
def solution_list(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "completion":
            return HttpResponseRedirect(reverse("solution_completion"))

        if action == "schedule":
            return HttpResponseRedirect(reverse("solution_schedule"))

    solutions = Solution.objects.select_related("incident").exclude(incident=None)
    context = {}

    query = request.GET.get("query", "")

    if query:
        search_filters = Q(description__icontains=query) | Q(remarks__icontains=query) | Q(person_responsible__icontains=query)
        solutions = solutions.filter(search_filters)

    # todo: this filter needs to be fixed since the db column was removed
    # status = request.GET.get("status")
    # if status:
    #     solutions = solutions.filter(status=status)

    timeframe = request.GET.get("timeframe")
    if timeframe:
        solutions = solutions.filter(timeframe=timeframe)

    incident_id = request.GET.get("incident_id")
    if incident_id:
        context["incident"] = Incident.objects.get(id=incident_id)
        solutions = solutions.filter(incident_id=incident_id)

    context["solutions"] = solutions

    return render(request, "defects/solution_list.html", context)


class LoginView(BaseLoginView):
    template_name = "defects/login.html"
    redirect_authenticated_user = True


class LogoutView(BaseLogoutView):
    pass


def login(request):
    return render(request, "defects/login.html")


@login_required
def equipment_search(request):
    query = request.GET.get("q")

    qs = Equipment.objects.filter(Q(code=query) | Q(name__icontains=query))[:50]

    return JsonResponse(
        {
            "items": [{"id": x.id, "name": str(x)} for x in qs],
        }
    )


@login_required
def incident_history(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    context = {"history": incident.history}
    return render(request, "defects/object_history.html", context=context)


@login_required
def approval_detail(request, pk):
    """
    Rendered in modal.
    """
    approval = Approval.objects.select_related("incident").get(id=pk)

    if request.user.id != approval.user_id:
        return HttpResponseForbidden("Not Allowed.")

    if request.method == "GET":
        context = {
            "approval": approval,
            "incident": approval.incident,
            "form": ApprovalForm(instance=approval),
        }

        return render(request, "defects/approval.html", context=context)

    if request.method == "POST":
        form = ApprovalForm(request.POST, instance=approval)

        if not form.is_valid():
            context = {
                "approval": approval,
                "incident": approval.incident,
                "form": form,
            }
            messages.error(request, "Please correct the errors and try again.")
            return render(request, "defects/approval.html", context=context, status=422)

        else:
            with transaction.atomic():
                obj = form.save()
                if obj.outcome == Approval.ACCEPTED and obj.type == Approval.NOTIFICATION:
                    obj.incident.notification_time_approved = now()
                    obj.incident.save()

                if obj.outcome == Approval.ACCEPTED and obj.type == Approval.RCA:

                    sam_approved = obj.incident.approvals.filter(outcome=Approval.ACCEPTED, type=Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER).exists()
                    sem_approved = obj.incident.approvals.filter(outcome=Approval.ACCEPTED, type=Approval.RCA, role=Approval.SECTION_ENGINEERING_MANAGER).exists()

                    if sam_approved and sem_approved:
                        obj.incident.rca_report_time_approved = now()
                        obj.incident.save()

                if obj.outcome == Approval.ACCEPTED and obj.type == Approval.CLOSE_OUT and obj.role == Approval.SECTION_ENGINEERING_MANAGER:

                    obj.incident.close_out_time_approved = now()
                    obj.incident.close_out_rating = obj.score
                    obj.incident.save()

            messages.success(request, "Approval outcome has been saved.")
            return HttpResponseRedirect(reverse("home"))


@login_required
def about_users(request):
    users = User.objects.all().prefetch_related("groups").order_by("email")

    context = {"users": [{"email": u.email, "username": u.username, "groups": [g.name for g in u.groups.all()]} for u in users]}

    return render(request, "defects/about_users.html", context=context)


@login_required
def feedback(request):
    Form = modelform_factory(Feedback, fields=["description"], help_texts={"description": "Please submit a detailed and descriptive summary."})

    if request.method == "POST":
        form = Form(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Feedback submitted.")
            return HttpResponseRedirect(reverse("feedback"))

        else:
            context = {
                "form": form,
            }
            return render(request, "defects/feedback.html", context=context)

    if request.method == "GET":
        context = {"submissions": Feedback.objects.select_related("created_by").filter(dismissed=False).order_by("-time_created"), "form": Form()}

        return render(request, "defects/feedback.html", context=context)


@require_GET
@login_required
def image_delete(request, pk):
    """
    Technically this should be a POST but this would require an intermediary
    form with a CSRF token so to keep things simple we just use GET
    """

    image = IncidentImage.objects.get(id=pk)
    incident_id = image.incident_id
    image.image.delete()
    image.delete()
    messages.info(request, "Image has been deleted.")
    return HttpResponseRedirect(reverse("incident_detail", args=[incident_id]))


@login_required
def image_update(request, pk):
    """
    Renders in modal.
    """
    image = IncidentImage.objects.get(id=pk)

    Form = modelform_factory(IncidentImage, fields=["description", "index"], labels={"index": "Order"})

    if request.method == "POST":
        form = Form(request.POST, instance=image)
        if not form.is_valid():
            return render(request, "defects/incident_image_update.html", context={"form": form, "image": image})
        form.save()
        return HttpResponseRedirect(reverse("incident_images", args=[image.incident_id]))

    if request.method == "GET":
        form = Form(instance=image)
        context = {
            "form": form,
            "image": image,
        }

        return render(request, "defects/incident_image_update.html", context=context)


def incident_solution_create(request, pk):
    """
    Renders in modal
    """
    incident = Incident.objects.get(pk=pk)

    section_engineer_choices = [
        (x.username, x.username) for x in User.objects.filter(groups__name__in=["section_engineer"]).distinct()
    ]

    Form = modelform_factory(
        Solution,
        fields=[
            "timeframe",
            "priority",
            "description",
            "person_responsible",
            "planned_completion_date",
            "remarks",
        ],
        widgets={
            "person_responsible": Select(choices=section_engineer_choices)
        }
    )

    if request.method == "GET":
        form = Form(initial={
            "planned_completion_date": now() + timedelta(days=90),
        })
        context = {
            "incident": incident,
            "form": form,
        }
        return render(request, "defects/incident_solution_create.html", context=context)

    if request.method == "POST":
        form = Form(request.POST)
        if not form.is_valid():
            context = {
                "form": form,
                "incident": incident,
            }
            return render(request, template_name="defects/incident_solution_create.html", context=context, status=422)

        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.incident = incident
        obj.save()
        return HttpResponseRedirect(reverse("incident_detail", args=[pk]))


@login_required
def incident_rca_report_upload(request, pk):
    """
    Renders in modal.
    """
    incident = get_object_or_404(Incident, id=pk)
    context = {
        "incident": incident,
    }

    Form = modelform_factory(
        Incident,
        fields=[
            "report_file",
        ],
        labels={"report_file": "Upload RCA Report"},
    )

    if request.method == "GET":
        context["form"] = Form(instance=incident)
        return render(request, "defects/incident_rca_upload.html", context=context)

    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=incident)
        if not form.is_valid():
            context["form"] = form
            return render(request, "defects/incident_rca_upload.html", context=context, status=422)

        form.save()
        messages.success(request, "Incident RCA Report uploaded.")
        return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))

@login_required
def incident_findings_upload(request, pk):
    """
    Renders in modal.
    """
    incident = get_object_or_404(Incident, id=pk)
    context = {
        "incident": incident,
    }

    Form = modelform_factory(
        Incident,
        fields=[
            "preliminary_findings",
        ],
        labels={"preliminary_findings": "Upload Preliminary Findings"},
    )

    if request.method == "GET":
        context["form"] = Form(instance=incident)
        return render(request, "defects/incident_findings_upload.html", context=context)

    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=incident)
        if not form.is_valid():
            context["form"] = form
            return render(request, "defects/incident_findings_upload.html", context=context, status=422)

        form.save()
        messages.success(request, "Incident preliminary findings uploaded.")
        return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))

@login_required
def incident_list_export(request):
    response = HttpResponse(
        headers={"Content-Type": "text/csv", "Content-Disposition": f"attachment; filename=\"incidents-{now().strftime('%Y-%m-%d')}.csv\""}
    )

    return export_table_csv(response, Incident._meta.db_table)


@login_required
def solution_list_export(request):
    response = HttpResponse(
        headers={"Content-Type": "text/csv", "Content-Disposition": f"attachment; filename=\"solutions-{now().strftime('%Y-%m-%d')}.csv\""}
    )

    return export_table_csv(response, Solution._meta.db_table)


@require_GET
@login_required
def incident_list_filter(request):
    """
    Renders in modal.

    Because this is a search form using GET, we use the context as workaround to detect
    whether the form is submitted or loaded.
    """
    form_submission = json.loads(request.headers.get("X-Up-Context", "{}")).get("action", "") == "submit"
    if form_submission:
        return HttpResponseRedirect(reverse("incident_list") + "?" + request.GET.urlencode())

    form = IncidentFilterForm(data=request.GET)
    return render(request, "defects/incident_list_filter.html", context={"form": form})


@require_GET
@login_required
def solution_list_filter(request):
    """
    Renders in modal.

    Because this is a search form using GET, we use the context as workaround to detect
    whether the form is submitted or loaded.
    """
    form_submission = json.loads(request.headers.get("X-Up-Context", "{}")).get("action", "") == "submit"
    if form_submission:
        return HttpResponseRedirect(reverse("solution_list") + "?" + request.GET.urlencode())

    form = SolutionFilterForm(data=request.GET)
    return render(request, "defects/solution_list_filter.html", context={"form": form})


@login_required
def solution_update(request, pk):
    solution = get_object_or_404(Solution, pk=pk)

    context = {
        "solution": solution,
    }

    Form = modelform_factory(
        Solution,
        fields=[
            "description",
            "timeframe",
            "priority",
            "person_responsible",
            "planned_completion_date",
            "actual_completion_date",
            "remarks",
            "dr_number",
            "date_verified",
            "verification_comment",
        ],
        labels={
            "dr_number": "DR Number",
            "date_verified": "Date Verified",
        },
        help_texts={"date_verified": "Add a date here to mark the solution as verified. Format: YYYY-MM-DD"},
    )

    if request.method == "GET":
        form = Form(instance=solution)
        context["form"] = form
        return render(request, "defects/solution_update.html", context=context)

    if request.method == "POST":
        form = Form(request.POST, request.FILES, instance=solution)
        if not form.is_valid():
            context["form"] = form
            return render(request, "defects/solution_update.html", context=context, status=422)

        form.save()
        messages.success(request, "Solution updated.")
        return HttpResponseRedirect(
            reverse("solution_list"),
        )


@login_required
def incident_significance_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == "POST":
        form = IncidentSignificanceUpdateForm(request.POST, instance=incident)
        if not form.is_valid():
            return HttpResponseBadRequest()
        form.save()
        return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))


@login_required
def incident_close_approval_request(request, pk):
    """
    Rendered in modal.
    """

    incident = Incident.objects.select_related("section", "created_by", "section_engineer", "equipment").prefetch_related("images").get(pk=pk)

    if request.method == "GET":
        form = IncidentCloseApprovalSendForm()

        context = {
            "incident": incident,
            "form": form,
        }

        return render(request, template_name="defects/incident_close_approval_request.html", context=context)

    if request.method == "POST":
        form = IncidentCloseApprovalSendForm(request.POST)

        if not form.is_valid():
            context = {
                "incident": incident,
                "form": form,
            }
            return render(request, template_name="defects/incident_close_approval_request.html", context=context)

        else:
            sem_user = form.cleaned_data["sem_user"]
            se_user = form.cleaned_data["se_user"]

            with transaction.atomic():
                # create an approval object for SEM
                Approval.objects.create(
                    created_by=request.user,
                    name=sem_user.username,
                    user=sem_user,
                    role=Approval.SECTION_ENGINEERING_MANAGER,
                    type=Approval.CLOSE_OUT,
                    incident=incident,
                )

                Approval.objects.create(
                    created_by=request.user,
                    name=se_user.username,
                    user=se_user,
                    role=Approval.SECTION_ENGINEER,
                    type=Approval.CLOSE_OUT,
                    incident=incident,
                )

                incident.close_out_time_published = now()
                incident.save()

            messages.success(request, "Close-Out slide has be sent to SE & SEM for approval.")
            return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))


@login_required
def incident_rca_approval_request(request, pk):
    """
    Rendered in modal.
    """

    incident = Incident.objects.select_related("section", "created_by", "section_engineer", "equipment").prefetch_related("images").get(pk=pk)

    role = Approval.SENIOR_ASSET_MANAGER
    if Approval.objects.filter(inciden=incident, role=Approval.SENIOR_ASSET_MANAGER, outcome=Approval.ACCEPTED).exists():
        role = Approval.SECTION_ENGINEERING_MANAGER

    if request.method == "GET":
        form = IncidentRCAApprovalSendForm(role=role)

        context = {
            "incident": incident,
            "form": form,
        }

        return render(request, template_name="defects/incident_rca_approval_request.html", context=context)

    if request.method == "POST":
        form = IncidentRCAApprovalSendForm(request.POST, role=role)

        if not form.is_valid():
            context = {
                "incident": incident,
                "form": form,
            }
            return render(request, template_name="defects/incident_rca_approval_request.html", context=context)

        else:
            user = form.cleaned_data["user"]

            with transaction.atomic():
                # create an approval object
                approval = Approval.objects.create(
                    created_by=request.user,
                    name=user.username,
                    user=user,
                    role=role,
                    type=Approval.RCA,
                    incident=incident,
                )

                incident.rca_report_time_published = now()
                incident.save()

            messages.success(request, f"RCA report has be sent to {approval.get_role_display()} for approval.")
            return HttpResponseRedirect(reverse("incident_detail", args=[incident.pk]))
