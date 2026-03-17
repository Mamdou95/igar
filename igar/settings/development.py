"""Development settings for Igar platform."""

from .base import *  # noqa: F401, F403

DEBUG = True

# ---------------------------------------------------------------------------
# Database — PostgreSQL local
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "igar_dev",
        "USER": "igar",
        "PASSWORD": "igar",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# ---------------------------------------------------------------------------
# CORS — permissive in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Email — console backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
