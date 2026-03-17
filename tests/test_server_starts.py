"""Smoke test: verify Django starts correctly."""

import django


def test_django_setup():
    """Verify Django can be set up without errors."""
    django.setup()
    from django.conf import settings

    assert settings.configured


def test_django_check():
    """Verify Django system checks pass."""
    from io import StringIO

    from django.core.management import call_command

    out = StringIO()
    call_command("check", stdout=out, stderr=StringIO())
    output = out.getvalue()
    assert "no issues" in output.lower() or output == ""


def test_root_urlconf_is_igar():
    """Verify ROOT_URLCONF points to igar.urls."""
    from django.conf import settings

    assert settings.ROOT_URLCONF == "igar.urls"


def test_settings_module_is_test():
    """Verify we are using igar.settings.test."""
    import os

    assert os.environ.get("DJANGO_SETTINGS_MODULE") == "igar.settings.test"
