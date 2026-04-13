import base64
import json

import pyotp
import pytest
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from igar.core.models import TwoFactorResetEvent

User = get_user_model()


def _totp_from_device(device: TOTPDevice) -> str:
    secret = base64.b32encode(device.bin_key).decode("ascii").rstrip("=")
    return pyotp.TOTP(secret).now()


@pytest.mark.django_db
def test_login_requires_2fa_challenge(client):
    User.objects.create_user(username="alice", password="StrongPassword123!")

    response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "alice", "password": "StrongPassword123!"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["2fa_required"] is True
    assert payload["next_action"] == "setup"
    assert isinstance(payload["challenge_token"], str)
    assert payload["access"] is None


@pytest.mark.django_db
def test_setup_and_confirm_2fa_returns_tokens(client):
    User.objects.create_user(username="alice", password="StrongPassword123!")

    login_response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "alice", "password": "StrongPassword123!"}),
        content_type="application/json",
    )
    challenge_token = login_response.json()["challenge_token"]

    setup_response = client.post(
        "/api/v1/auth/2fa/setup/",
        data=json.dumps({"challenge_token": challenge_token}),
        content_type="application/json",
    )

    assert setup_response.status_code == 200
    setup_payload = setup_response.json()
    assert isinstance(setup_payload["secret"], str)
    assert setup_payload["qr_code"].startswith("data:image/png;base64,")

    otp_code = pyotp.TOTP(setup_payload["secret"]).now()
    confirm_response = client.post(
        "/api/v1/auth/2fa/confirm/",
        data=json.dumps({"challenge_token": challenge_token, "otp_code": otp_code}),
        content_type="application/json",
    )

    assert confirm_response.status_code == 200
    confirm_payload = confirm_response.json()
    assert isinstance(confirm_payload["access"], str)
    assert confirm_payload["2fa_verified"] is True
    assert "igar_refresh_token" in confirm_response.cookies


@pytest.mark.django_db
def test_verify_2fa_with_existing_device(client):
    user = User.objects.create_user(username="alice", password="StrongPassword123!")
    device = TOTPDevice.objects.create(user=user, name="igar-default", key=random_hex(20), confirmed=True)

    login_response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "alice", "password": "StrongPassword123!"}),
        content_type="application/json",
    )

    payload = login_response.json()
    assert payload["next_action"] == "verify"

    otp_code = _totp_from_device(device)
    verify_response = client.post(
        "/api/v1/auth/2fa/verify/",
        data=json.dumps({"challenge_token": payload["challenge_token"], "otp_code": otp_code}),
        content_type="application/json",
    )

    assert verify_response.status_code == 200
    verify_payload = verify_response.json()
    assert isinstance(verify_payload["access"], str)
    assert verify_payload["2fa_verified"] is True


@pytest.mark.django_db
def test_verify_2fa_invalid_code_returns_rfc7807(client):
    user = User.objects.create_user(username="alice", password="StrongPassword123!")
    TOTPDevice.objects.create(user=user, name="igar-default", key=random_hex(20), confirmed=True)

    login_response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "alice", "password": "StrongPassword123!"}),
        content_type="application/json",
    )
    challenge_token = login_response.json()["challenge_token"]

    verify_response = client.post(
        "/api/v1/auth/2fa/verify/",
        data=json.dumps({"challenge_token": challenge_token, "otp_code": "000000"}),
        content_type="application/json",
    )

    assert verify_response.status_code == 401
    payload = verify_response.json()
    assert payload["type"] == "https://igar.dev/errors/otp_invalid"


@pytest.mark.django_db
def test_admin_can_disable_user_2fa(client, settings):
    settings.IGAR_AUTH_2FA_BYPASS = True
    settings.IGAR_AUTH_2FA_ENABLED = False

    admin = User.objects.create_superuser(username="admin", password="StrongPassword123!", email="admin@example.com")
    target = User.objects.create_user(username="alice", password="StrongPassword123!")
    TOTPDevice.objects.create(user=target, name="igar-default", key=random_hex(20), confirmed=True)

    login_response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "admin", "password": "StrongPassword123!"}),
        content_type="application/json",
    )
    admin_access = login_response.json()["access"]

    disable_response = client.post(
        "/api/v1/auth/2fa/disable/",
        data=json.dumps({"user_id": target.pk}),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {admin_access}",
    )

    assert disable_response.status_code == 200
    assert TOTPDevice.objects.filter(user=target, confirmed=True).count() == 0
    assert TwoFactorResetEvent.objects.filter(target_user=target).count() == 1

    cache.clear()

    users_response = client.get(
        "/api/v1/auth/2fa/users/",
        HTTP_AUTHORIZATION=f"Bearer {admin_access}",
    )

    assert users_response.status_code == 200
    results = users_response.json()["results"]
    target_payload = next(item for item in results if item["id"] == target.pk)
    assert target_payload["two_factor_reset_history"]
    assert target_payload["last_2fa_reset_at"] == target_payload["two_factor_reset_history"][-1]


@pytest.mark.django_db
def test_2fa_is_mandatory_without_bypass(client, settings):
    settings.IGAR_AUTH_2FA_BYPASS = False
    settings.IGAR_AUTH_2FA_ENABLED = True
    User.objects.create_user(username="alice", password="StrongPassword123!")

    response = client.post(
        "/api/v1/auth/login/",
        data=json.dumps({"username": "alice", "password": "StrongPassword123!"}),
        content_type="application/json",
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["2fa_required"] is True
    assert payload["access"] is None
