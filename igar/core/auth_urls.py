"""Authentication API URL routes for Igar."""

from django.urls import path

from igar.core.auth_views import (
    CSRFCookieAPIView,
    LoginAPIView,
    LogoutAPIView,
    RefreshAPIView,
    TwoFactorBackupCodesAPIView,
    TwoFactorConfirmAPIView,
    TwoFactorDisableAPIView,
    TwoFactorSetupAPIView,
    TwoFactorUsersAPIView,
    TwoFactorVerifyAPIView,
)

urlpatterns = [
    path("csrf/", CSRFCookieAPIView.as_view(), name="auth_csrf"),
    path("login/", LoginAPIView.as_view(), name="auth_login"),
    path("refresh/", RefreshAPIView.as_view(), name="auth_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="auth_logout"),
    path("2fa/setup/", TwoFactorSetupAPIView.as_view(), name="auth_2fa_setup"),
    path("2fa/confirm/", TwoFactorConfirmAPIView.as_view(), name="auth_2fa_confirm"),
    path("2fa/verify/", TwoFactorVerifyAPIView.as_view(), name="auth_2fa_verify"),
    path("2fa/backup-codes/", TwoFactorBackupCodesAPIView.as_view(), name="auth_2fa_backup_codes"),
    path("2fa/disable/", TwoFactorDisableAPIView.as_view(), name="auth_2fa_disable"),
    path("2fa/users/", TwoFactorUsersAPIView.as_view(), name="auth_2fa_users"),
]
