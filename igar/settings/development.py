"""Development settings for Igar platform."""

import os

from .base import *  # noqa: F401, F403

DEBUG = True

# ---------------------------------------------------------------------------
# Database — PostgreSQL local
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "igar_dev"),
        "USER": os.environ.get("DB_USER", "igar"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "igar"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/1"),
    }
}

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://minio:9000")
ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")

# ---------------------------------------------------------------------------
# CORS — permissive in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Email — console backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

IGAR_AUTH_2FA_BYPASS = os.environ.get("IGAR_AUTH_2FA_BYPASS", "false").lower() == "true"
OTP_TOTP_ISSUER = os.environ.get("OTP_TOTP_ISSUER", "Igar")
