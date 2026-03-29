"""Authentication API URL routes for Igar."""

from django.urls import path

from igar.core.auth_views import CSRFCookieAPIView, LoginAPIView, LogoutAPIView, RefreshAPIView

urlpatterns = [
    path("csrf/", CSRFCookieAPIView.as_view(), name="auth_csrf"),
    path("login/", LoginAPIView.as_view(), name="auth_login"),
    path("refresh/", RefreshAPIView.as_view(), name="auth_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="auth_logout"),
]
