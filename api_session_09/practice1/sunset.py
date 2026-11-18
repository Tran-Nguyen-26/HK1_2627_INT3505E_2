from datetime import datetime, timezone
from email.utils import format_datetime


def http_date(dt):
    return format_datetime(dt, usegmt=True)


def add_sunset_headers(response, sunset_date, successor):
    response.headers["Sunset"] = http_date(sunset_date)
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = f'<{successor}>; rel="successor-version"'
    return response
