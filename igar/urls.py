"""Root URL configuration for Igar platform."""

from django.urls import include, path

from igar.core.health import health_check_view

urlpatterns = [
    path("health", health_check_view, name="health"),
    # Igar API v1
    path(
        "api/v1/",
        include(
            [
                # App URLs will be added as apps are implemented
                # path("vault/", include("igar.apps.vault.urls")),
                # path("intelligence/", include("igar.apps.intelligence.urls")),
                # path("capture/", include("igar.apps.capture.urls")),
                # path("compliance/", include("igar.apps.compliance.urls")),
                # path("viewer/", include("igar.apps.viewer.urls")),
                # path("licensing/", include("igar.apps.licensing.urls")),
                path("auth/", include("igar.core.auth_urls")),
            ]
        ),
    ),
    # Include Mayan EDMS URLs
    path("", include("mayan.urls")),
]
