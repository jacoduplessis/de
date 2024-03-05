import enum
from typing import List

from .models import Incident
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
        ).prefetch_related("approvals")
    )
    # might need to add another filter to only consider
    # incidents that are "recent"

    # 1  check for notification creation
    message = "Create 48H Notification"
    for i in incidents:
        if i.notification_time_published:
            continue
        time_required = i.time_start + timedelta(hours=48)
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
        if i.notification_rejected:
            actions.append(UserAction(message=message, time_required=now(), urgency=Urgency.DANGER, incident=i))

    # 3
    message = "Upload RCA Report"
    for i in incidents:
        if not i.significant:
            continue
        if i.report_file != "":
            continue
        if i.notification_time_published is None:
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

    return actions


def get_user_actions(user) -> List[UserAction]:
    groups = list([g.name for g in user.groups.all()])
    actions = []
    if "reliability_engineer" in groups:
        actions += reliability_engineer_actions(user.id)

    return sorted(actions, key=lambda x: _urgency_value(x.urgency))
