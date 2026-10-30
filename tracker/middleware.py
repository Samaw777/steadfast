from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.utils import timezone


class BrowserTimezoneMiddleware:
    """Use the timezone the browser reports (via the `tz` cookie set in base.html),
    so "today" and the greeting match the person's own clock."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_name = request.COOKIES.get("tz")
        try:
            timezone.activate(ZoneInfo(tz_name)) if tz_name else timezone.deactivate()
        except (ZoneInfoNotFoundError, ValueError):
            timezone.deactivate()
        return self.get_response(request)
