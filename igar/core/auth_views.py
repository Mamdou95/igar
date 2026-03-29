"""JWT authentication endpoints for Igar API v1."""

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import get_token
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from igar.core.exceptions import AuthenticationFailedError, InvalidRequestError

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


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


class CSRFCookieAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        get_token(request)
        return Response({"detail": "CSRF cookie set"})


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

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

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response(
            {
                "access": access,
                "user": {
                    "id": user.id,
                    "username": user.get_username(),
                },
            }
        )
        _set_refresh_cookie(response=response, refresh_token=str(refresh))
        response["Cache-Control"] = "no-store"
        return response


class RefreshAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

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
