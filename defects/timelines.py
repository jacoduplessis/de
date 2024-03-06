from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from django.utils.timezone import now


@dataclass
class Link:
    text: str
    url: str
    attrs: str = ""
    cls: str = "primary"


@dataclass
class TimelineEntry:
    time: datetime = now()
    until: datetime = None
    title: str = ""
    icon: str = "clock"
    icon_classes: str = ""
    links: list[Link] = field(default_factory=list)
    text: str = ""
