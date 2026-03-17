"""Production settings for Igar platform."""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

# ---------------------------------------------------------------------------
# Middleware — add CSP middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = list(MIDDLEWARE) + [  # noqa: F405
    "csp.middleware.CSPMiddleware",
]

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# ---------------------------------------------------------------------------
# Database — PostgreSQL production
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "igar"),
        "USER": os.environ.get("DB_USER", "igar"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Content Security Policy (django-csp)
# ---------------------------------------------------------------------------
CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# ---------------------------------------------------------------------------
# SSE-C — Server-Side Encryption with Customer-provided keys (MinIO/S3)
# ---------------------------------------------------------------------------
AWS_S3_ENCRYPTION_ALGORITHM = os.environ.get("SSE_C_ALGORITHM", "AES256")
AWS_S3_SSE_CUSTOMER_KEY = os.environ.get("SSE_C_KEY", "")
AWS_S3_SSE_CUSTOMER_KEY_MD5 = os.environ.get("SSE_C_KEY_MD5", "")

# ---------------------------------------------------------------------------
# CORS — strict in production
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_ROOT = os.environ.get("STATIC_ROOT", "/var/www/igar/static/")

# ---------------------------------------------------------------------------
# Cache & Celery — from env
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),
    }
}
