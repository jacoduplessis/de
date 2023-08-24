import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    """
    We set the `current_timezone` to UTC+2 as the app will be running in one location in SA only.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(zoneinfo.ZoneInfo("Africa/Johannesburg"))
        return self.get_response(request)
