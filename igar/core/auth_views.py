"""JWT authentication endpoints for Igar API v1."""

import base64
from io import BytesIO

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.cache import cache
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import pyotp
import qrcode
import structlog
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from igar.core.exceptions import (
    AuthenticationFailedError,
    InvalidRequestError,
    OTPAlreadySetupError,
    OTPChallengeInvalidError,
    OTPInvalidError,
    OTPRateLimitedError,
    OTPSetupRequiredError,
)
from igar.core.models import TwoFactorResetEvent

User = get_user_model()
logger = structlog.get_logger(__name__)


def _challenge_signer() -> signing.TimestampSigner:
    return signing.TimestampSigner(salt=settings.IGAR_AUTH_2FA_CHALLENGE_SALT)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class OTPChallengeSerializer(serializers.Serializer):
    challenge_token = serializers.CharField()


class OTPCodeSerializer(OTPChallengeSerializer):
    otp_code = serializers.RegexField(r"^\d{6}$")


class OTPDisableSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        key=settings.IGAR_AUTH_REFRESH_COOKIE,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=settings.IGAR_AUTH_COOKIE_SECURE,
        samesite=settings.IGAR_AUTH_COOKIE_SAMESITE,
        path=settings.IGAR_AUTH_COOKIE_PATH,
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.IGAR_AUTH_REFRESH_COOKIE,
        path=settings.IGAR_AUTH_COOKIE_PATH,
        samesite=settings.IGAR_AUTH_COOKIE_SAMESITE,
    )


def _issue_tokens(user) -> tuple[str, str]:
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    return access, str(refresh)


def _auth_payload(user, access_token: str) -> dict:
    return {
        "access": access_token,
        "2fa_required": False,
        "2fa_verified": True,
        "next_action": None,
        "user": {
            "id": user.id,
            "username": user.get_username(),
        },
    }


def _build_challenge_token(user) -> str:
    return _challenge_signer().sign(str(user.pk))


def _get_challenge_user(raw_token: str):
    try:
        unsigned = _challenge_signer().unsign(raw_token, max_age=settings.IGAR_AUTH_2FA_CHALLENGE_TTL_SECONDS)
        user = User.objects.get(pk=int(unsigned))
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist, ValueError, TypeError):
        raise OTPChallengeInvalidError("Session 2FA invalide ou expiree.")

    if not user.is_active:
        raise AuthenticationFailedError("Identifiants invalides.")
    return user


def _failure_cache_key(user_id: int, phase: str) -> str:
    return f"igar:2fa:failures:{phase}:{user_id}"


def _assert_not_rate_limited(user_id: int, phase: str) -> None:
    key = _failure_cache_key(user_id, phase)
    if cache.get(key, 0) >= settings.IGAR_AUTH_2FA_MAX_ATTEMPTS:
        raise OTPRateLimitedError("Trop de tentatives OTP. Reessayez dans une minute.")


def _register_failure(user_id: int, phase: str) -> None:
    key = _failure_cache_key(user_id, phase)
    failures = int(cache.get(key, 0)) + 1
    cache.set(key, failures, 60)
    if failures >= settings.IGAR_AUTH_2FA_MAX_ATTEMPTS:
        raise OTPRateLimitedError("Trop de tentatives OTP. Reessayez dans une minute.")


def _clear_failures(user_id: int, phase: str) -> None:
    cache.delete(_failure_cache_key(user_id, phase))


def _totp_secret(device: TOTPDevice) -> str:
    return base64.b32encode(device.bin_key).decode("ascii").rstrip("=")


def _make_qr_data_url(content: str) -> str:
    image = qrcode.make(content)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _get_confirmed_device(user) -> TOTPDevice | None:
    return TOTPDevice.objects.filter(user=user, confirmed=True).order_by("-id").first()


def _two_factor_reset_history(user) -> list[str]:
    return [
        event.created_at.isoformat()
        for event in TwoFactorResetEvent.objects.filter(target_user=user).order_by("created_at", "id")
    ]


class CSRFCookieAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        get_token(request)
        return Response({"detail": "CSRF cookie set"})


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @method_decorator(csrf_protect)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete d'authentification invalide.")

        credentials = serializer.validated_data
        user = authenticate(
            request=request,
            username=credentials["username"],
            password=credentials["password"],
        )

        if user is None or not user.is_active:
            raise AuthenticationFailedError("Identifiants invalides.")

        if settings.IGAR_AUTH_2FA_ENABLED and not settings.IGAR_AUTH_2FA_BYPASS:
            has_confirmed_device = _get_confirmed_device(user) is not None
            next_action = "verify" if has_confirmed_device else "setup"
            challenge_token = _build_challenge_token(user)
            response = Response(
                {
                    "access": None,
                    "2fa_required": True,
                    "2fa_verified": False,
                    "next_action": next_action,
                    "challenge_token": challenge_token,
                    "challenge_ttl_seconds": settings.IGAR_AUTH_2FA_CHALLENGE_TTL_SECONDS,
                    "user": {
                        "id": user.id,
                        "username": user.get_username(),
                    },
                }
            )
            response["Cache-Control"] = "no-store"
            return response

        access, refresh = _issue_tokens(user)
        response = Response(_auth_payload(user, access))
        _set_refresh_cookie(response=response, refresh_token=refresh)
        response["Cache-Control"] = "no-store"
        return response


class RefreshAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @method_decorator(csrf_protect)
    def post(self, request):
        raw_refresh_token = request.COOKIES.get(settings.IGAR_AUTH_REFRESH_COOKIE)
        if not raw_refresh_token:
            raise AuthenticationFailedError("Session invalide.")

        try:
            refresh_token = RefreshToken(raw_refresh_token)
            user = User.objects.get(pk=refresh_token["user_id"])
        except (TokenError, User.DoesNotExist, KeyError):
            raise AuthenticationFailedError("Session invalide.")

        access_token = str(refresh_token.access_token)
        response = Response(
            {
                "access": access_token,
                "user": {
                    "id": user.id,
                    "username": user.get_username(),
                },
            }
        )
        response["Cache-Control"] = "no-store"
        return response


class LogoutAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @method_decorator(csrf_protect)
    def post(self, request):
        raw_refresh_token = request.COOKIES.get(settings.IGAR_AUTH_REFRESH_COOKIE)
        if raw_refresh_token:
            try:
                refresh_token = RefreshToken(raw_refresh_token)
                if hasattr(refresh_token, "blacklist"):
                    refresh_token.blacklist()
            except TokenError:
                pass

        response = Response(status=204)
        _delete_refresh_cookie(response)
        return response


class TwoFactorSetupAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = OTPChallengeSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete 2FA invalide.")

        user = _get_challenge_user(serializer.validated_data["challenge_token"])
        if _get_confirmed_device(user):
            raise OTPAlreadySetupError("Le 2FA est deja configure pour cet utilisateur.")

        device, _ = TOTPDevice.objects.get_or_create(user=user, name="igar-default", defaults={"confirmed": False})
        device.key = random_hex(20)
        device.confirmed = False
        device.save(update_fields=["key", "confirmed"])

        secret = _totp_secret(device)
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(
            name=user.get_username(), issuer_name=settings.OTP_TOTP_ISSUER
        )

        logger.info("auth.2fa.setup.generated", user_id=user.id)
        return Response(
            {
                "secret": secret,
                "qr_code": _make_qr_data_url(provisioning_uri),
                "issuer": settings.OTP_TOTP_ISSUER,
            }
        )


class TwoFactorConfirmAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = OTPCodeSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete de confirmation 2FA invalide.")

        user = _get_challenge_user(serializer.validated_data["challenge_token"])
        phase = "confirm"
        _assert_not_rate_limited(user.id, phase)

        device = TOTPDevice.objects.filter(user=user, confirmed=False).order_by("-id").first()
        if not device:
            if _get_confirmed_device(user):
                raise OTPAlreadySetupError("Le 2FA est deja configure pour cet utilisateur.")
            raise OTPSetupRequiredError("Configuration 2FA requise avant confirmation.")

        otp_code = serializer.validated_data["otp_code"]
        if not device.verify_token(otp_code):
            logger.warning("auth.2fa.confirm.failed", user_id=user.id)
            _register_failure(user.id, phase)
            raise OTPInvalidError("Code OTP invalide.")

        device.confirmed = True
        device.save(update_fields=["confirmed"])
        _clear_failures(user.id, phase)

        access, refresh = _issue_tokens(user)
        response = Response(_auth_payload(user, access))
        _set_refresh_cookie(response=response, refresh_token=refresh)
        response["Cache-Control"] = "no-store"
        logger.info("auth.2fa.confirm.success", user_id=user.id, otp_device_id=device.id)
        return response


class TwoFactorVerifyAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = OTPCodeSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete de verification 2FA invalide.")

        user = _get_challenge_user(serializer.validated_data["challenge_token"])
        phase = "verify"
        _assert_not_rate_limited(user.id, phase)

        device = _get_confirmed_device(user)
        if not device:
            raise OTPSetupRequiredError("Le 2FA doit etre configure pour cet utilisateur.")

        otp_code = serializer.validated_data["otp_code"]
        if not device.verify_token(otp_code):
            logger.warning("auth.2fa.verify.failed", user_id=user.id, otp_device_id=device.id)
            _register_failure(user.id, phase)
            raise OTPInvalidError("Code OTP invalide.")

        _clear_failures(user.id, phase)
        access, refresh = _issue_tokens(user)
        response = Response(_auth_payload(user, access))
        _set_refresh_cookie(response=response, refresh_token=refresh)
        response["Cache-Control"] = "no-store"
        logger.info("auth.2fa.verify.success", user_id=user.id, otp_device_id=device.id)
        return response


class TwoFactorBackupCodesAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = OTPChallengeSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete de backup codes invalide.")

        user = _get_challenge_user(serializer.validated_data["challenge_token"])
        if not _get_confirmed_device(user):
            raise OTPSetupRequiredError("Le 2FA doit etre configure avant de generer des codes de secours.")

        static_device, _ = StaticDevice.objects.get_or_create(user=user, name="igar-backup")
        static_device.token_set.all().delete()

        backup_codes: list[str] = []
        for _ in range(5):
            code = random_hex(4).upper()
            StaticToken.objects.create(device=static_device, token=code)
            backup_codes.append(code)

        logger.info("auth.2fa.backup_codes.generated", user_id=user.id)
        return Response({"backup_codes": backup_codes})


class TwoFactorDisableAPIView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request):
        serializer = OTPDisableSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidRequestError("Requete de reinitialisation 2FA invalide.")

        try:
            target_user = User.objects.get(pk=serializer.validated_data["user_id"])
        except User.DoesNotExist:
            raise InvalidRequestError("Utilisateur introuvable.")

        TOTPDevice.objects.filter(user=target_user).delete()
        StaticDevice.objects.filter(user=target_user).delete()
        TwoFactorResetEvent.objects.create(target_user=target_user, actor=request.user)
        reset_history = _two_factor_reset_history(target_user)
        logger.info("auth.2fa.disabled", admin_id=request.user.id, user_id=target_user.id)

        return Response({"detail": "2FA reinitialise.", "user_id": target_user.id, "reset_history": reset_history})


class TwoFactorUsersAPIView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        users = User.objects.order_by("username")
        payload = []
        for user in users:
            reset_history = _two_factor_reset_history(user)
            payload.append(
                {
                    "id": user.id,
                    "username": user.get_username(),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "has_2fa": _get_confirmed_device(user) is not None,
                    "last_2fa_reset_at": reset_history[-1] if reset_history else None,
                    "two_factor_reset_history": reset_history,
                }
            )
        return Response({"results": payload})
