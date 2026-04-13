"""Base settings for Igar platform — extends Mayan EDMS settings."""

import os
from datetime import timedelta

import structlog

from mayan.settings.base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Igar apps — added after Mayan's INSTALLED_APPS
# ---------------------------------------------------------------------------
IGAR_APPS = [
    "igar.core.apps.IgarCoreConfig",
    # "igar.apps.vault",
    # "igar.apps.intelligence",
    "igar.apps.capture",
    # "igar.apps.compliance",
    # "igar.apps.viewer",
    # "igar.apps.licensing",
]

IGAR_AUTH_APPS = [
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
]

INSTALLED_APPS = list(INSTALLED_APPS) + IGAR_AUTH_APPS + IGAR_APPS  # noqa: F405

# ---------------------------------------------------------------------------
# Core Django overrides
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "igar.urls"
WSGI_APPLICATION = "igar.wsgi.application"
ASGI_APPLICATION = "igar.asgi.application"
MIDDLEWARE = list(MIDDLEWARE) + ["django_otp.middleware.OTPMiddleware"]  # noqa: F405

IGAR_CHANNEL_LAYER_URL = os.environ.get("IGAR_CHANNEL_LAYER_URL")
if IGAR_CHANNEL_LAYER_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [IGAR_CHANNEL_LAYER_URL],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

# ---------------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "igar.core.pagination.IgarPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "igar.core.exception_handler.igar_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

IGAR_AUTH_REFRESH_COOKIE = os.environ.get("IGAR_AUTH_REFRESH_COOKIE", "igar_refresh_token")
IGAR_AUTH_COOKIE_PATH = os.environ.get("IGAR_AUTH_COOKIE_PATH", "/api/v1/auth/")
IGAR_AUTH_COOKIE_SAMESITE = os.environ.get("IGAR_AUTH_COOKIE_SAMESITE", "Lax")
IGAR_AUTH_COOKIE_SECURE = os.environ.get("IGAR_AUTH_COOKIE_SECURE", "false").lower() == "true"
IGAR_AUTH_2FA_ENABLED = os.environ.get("IGAR_AUTH_2FA_ENABLED", "true").lower() == "true"
IGAR_AUTH_2FA_BYPASS = os.environ.get("IGAR_AUTH_2FA_BYPASS", "false").lower() == "true"
IGAR_AUTH_2FA_CHALLENGE_TTL_SECONDS = int(os.environ.get("IGAR_AUTH_2FA_CHALLENGE_TTL_SECONDS", "600"))
IGAR_AUTH_2FA_CHALLENGE_SALT = os.environ.get("IGAR_AUTH_2FA_CHALLENGE_SALT", "igar.auth.2fa.challenge")
IGAR_AUTH_2FA_MAX_ATTEMPTS = int(os.environ.get("IGAR_AUTH_2FA_MAX_ATTEMPTS", "5"))
OTP_TOTP_ISSUER = os.environ.get("OTP_TOTP_ISSUER", "Igar")
OTP_TOTP_INITIAL_TOLERANCE = int(os.environ.get("OTP_TOTP_INITIAL_TOLERANCE", "1"))

# ---------------------------------------------------------------------------
# Logging — structlog JSON
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "igar": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# ---------------------------------------------------------------------------
# Cache — Redis
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
    }
}

# ---------------------------------------------------------------------------
# Auth — explicitly declared for clarity (inherited from Mayan)
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "auth.User"

# Public endpoints excluded from django-stronghold auth redirects.
STRONGHOLD_PUBLIC_URLS = tuple(STRONGHOLD_PUBLIC_URLS) + (  # noqa: F405
    r"^/health$",
    r"^/health/$",
    r"^/api/v1/auth/csrf/?$",
    r"^/api/v1/auth/login/?$",
    r"^/api/v1/auth/refresh/?$",
    r"^/api/v1/auth/2fa/.+$",
)

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True
