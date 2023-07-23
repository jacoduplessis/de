from dataclasses import dataclass
from datetime import datetime

from django.utils.timezone import now


@dataclass
class TimelineEntry:
    time: datetime = now()
    until: datetime = None
    title: str = ""
    icon: str = "clock"
    icon_classes: str = ""
    link_url: str = "#"
    link_text: str = ""
    secondary_link_url: str = ""
    secondary_link_text: str = ""
    text: str = ""
