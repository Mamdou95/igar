"""URL configuration for the capture app."""

from django.urls import path

from igar.apps.capture.views import TusHookAPIView

app_name = "capture"

urlpatterns = [
	path("tus-hook/", TusHookAPIView.as_view(), name="tus_hook"),
]
