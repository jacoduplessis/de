import enum
from typing import List
from .models import Incident, Approval
from dataclasses import dataclass
from datetime import datetime, timedelta
from django.utils.timezone import now


class Urgency(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"


def _urgency_value(x: Urgency):
    if x == Urgency.INFO:
        return 2
    if x == Urgency.WARNING:
        return 1
    if x == Urgency.DANGER:
        return 0
    return 9


@dataclass
class UserAction:
    urgency: Urgency
    message: str
    incident: Incident
    time_required: datetime


def reliability_engineer_actions(user_id) -> List[UserAction]:
    actions = []

    # load into list here and then iterate over
    incidents = list(
        Incident.objects.filter(
            created_by_id=user_id,
        )
        .prefetch_related("approvals", "solutions")
    )
    # might need to add another filter to only consider
    # incidents that are "recent"

    # 1  check for notification creation
    message = "Create 48H Notification"
    for i in incidents:
        if i.notification_time_published:
            continue
        time_required = i.time_end + timedelta(hours=48)
        time_remaining = time_required - now()
        if time_remaining < timedelta(hours=0):
            urgency = Urgency.DANGER
        elif timedelta(hours=0) < time_remaining < timedelta(hours=24):
            urgency = Urgency.WARNING
        else:
            urgency = Urgency.INFO
        actions.append(UserAction(message=message, time_required=time_required, urgency=urgency, incident=i))

    # 2 - text changed from SRS document
    message = "Resubmit Rejected 48H Notification"
    for i in incidents:
        if i.notification_rejected and not i.has_pending_approval(Approval.NOTIFICATION):
            actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.DANGER, incident=i))

    # 3
    message = "Upload RCA Report"
    for i in incidents:
        if not i.significant:
            continue
        if i.report_file != "":
            continue
        if i.notification_time_approved is None:
            continue
        time_required = i.notification_time_published + timedelta(days=14)
        time_remaining = time_required - now()
        if time_remaining < timedelta(hours=0):
            urgency = Urgency.DANGER
        elif time_remaining < timedelta(days=7):
            urgency = Urgency.WARNING
        else:
            urgency = Urgency.INFO
        actions.append(UserAction(message=message, urgency=urgency, incident=i, time_required=time_required))

    message = "Submit RCA Report to SnrAM"
    # todo: implement

    message = "Submit RCA Report to SEM"
    for i in incidents:
        if i.significant and Approval.objects.filter(incident=i, type=Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER).exists() and not i.has_pending_approval(Approval.RCA, role=Approval.SENIOR_ASSET_MANAGER) and not i.has_pending_approval(Approval.RCA, role=Approval.SECTION_ENGINEERING_MANAGER) :
            actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.INFO, incident=i))

    message = "Resubmit Rejected RCA Report"
    for i in incidents:
        if i.rca_report_rejected and not i.has_pending_approval(Approval.RCA):
            actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.DANGER, incident=i))

    message = "Publish Close-Out Slide"
    for i in incidents:
        if i.close_out_time_published is not None:
            continue
        if i.close_out_time_approved:
            continue
        if (i.significant and i.rca_report_time_approved) or (not i.significant):
            time_required = i.notification_time_published + timedelta(days=14)
            time_remaining = time_required - now()
            if time_remaining < timedelta(hours=0):
                urgency = Urgency.DANGER
            elif time_remaining < timedelta(days=7):
                urgency = Urgency.WARNING
            else:
                urgency = Urgency.INFO

            actions.append(UserAction(message=message, incident=i, urgency=urgency, time_required=time_required))

    message = "Resubmit Rejected Close-Out Slide"
    for i in incidents:
        if i.close_out_rejected and not i.has_pending_approval(Approval.CLOSE_OUT):
            actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.DANGER, incident=i))

    message = "Add Solutions"
    for i in incidents:
        if i.close_out_time_approved and len(i.solutions.all()) == 0:
            actions.append(UserAction(message=message, time_required=i.close_out_time_approved + timedelta(days=14), urgency=Urgency.INFO, incident=i))

    message = "Verify Completion Date"
    for i in incidents:
        if not i.close_out_time_approved:
            continue
        for s in i.solutions.all():
            if s.planned_completion_date and s.planned_completion_date <= now().date() and not s.date_verified:
                actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.INFO, incident=i))

    return actions

def get_user_actions(user) -> List[UserAction]:
    groups = list([g.name for g in user.groups.all()])
    actions = []
    if "reliability_engineer" in groups:
        actions += reliability_engineer_actions(user.id)

    return sorted(actions, key=lambda x: _urgency_value(x.urgency))
