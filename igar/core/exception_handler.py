"""RFC 7807 Problem Details exception handler for DRF."""

from rest_framework.views import exception_handler as drf_exception_handler

from igar.core.exceptions import IgarException


def igar_exception_handler(exc, context):
    """Handle exceptions and return RFC 7807 Problem Details responses."""
    if isinstance(exc, IgarException):
        from rest_framework.response import Response

        data = {
            "type": f"https://igar.dev/errors/{exc.error_type}",
            "title": exc.error_type.replace("_", " ").title(),
            "status": exc.status_code,
            "detail": str(exc.detail),
        }
        if exc.extra:
            data["extensions"] = exc.extra
        return Response(data, status=exc.status_code)

    return drf_exception_handler(exc, context)
