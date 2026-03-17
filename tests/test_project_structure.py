"""Verify project structure matches architecture specification."""

from pathlib import Path

# Backend root
BACKEND_ROOT = Path(__file__).resolve().parent.parent

# Expected Igar apps
IGAR_APPS = ["vault", "intelligence", "capture", "compliance", "viewer", "licensing"]

# Expected files per app
APP_FILES = [
    "__init__.py",
    "apps.py",
    "models.py",
    "serializers.py",
    "views.py",
    "services.py",
    "tasks.py",
    "urls.py",
    "admin.py",
    "factories.py",
]


def test_igar_root_exists():
    """Verify igar/ directory exists with __init__.py."""
    assert (BACKEND_ROOT / "igar" / "__init__.py").exists()


def test_igar_apps_directory_exists():
    """Verify igar/apps/ exists."""
    assert (BACKEND_ROOT / "igar" / "apps" / "__init__.py").exists()


def test_all_igar_apps_exist():
    """Verify all 6 Igar apps are created."""
    for app_name in IGAR_APPS:
        app_dir = BACKEND_ROOT / "igar" / "apps" / app_name
        assert app_dir.is_dir(), f"App directory missing: {app_name}"


def test_app_files_exist():
    """Verify each app has all required files."""
    for app_name in IGAR_APPS:
        app_dir = BACKEND_ROOT / "igar" / "apps" / app_name
        for filename in APP_FILES:
            filepath = app_dir / filename
            assert filepath.exists(), f"Missing {filename} in {app_name}"


def test_app_tests_directory_exists():
    """Verify each app has a tests/ directory with __init__.py."""
    for app_name in IGAR_APPS:
        tests_init = BACKEND_ROOT / "igar" / "apps" / app_name / "tests" / "__init__.py"
        assert tests_init.exists(), f"Missing tests/__init__.py in {app_name}"


def test_igar_core_exists():
    """Verify igar/core/ has all required files."""
    core_files = [
        "__init__.py",
        "models.py",
        "exceptions.py",
        "permissions.py",
        "audit.py",
        "pagination.py",
        "exception_handler.py",
        "storage.py",
    ]
    for filename in core_files:
        filepath = BACKEND_ROOT / "igar" / "core" / filename
        assert filepath.exists(), f"Missing core/{filename}"


def test_igar_settings_exist():
    """Verify igar/settings/ has all required files."""
    settings_files = [
        "__init__.py",
        "base.py",
        "development.py",
        "production.py",
        "test.py",
    ]
    for filename in settings_files:
        filepath = BACKEND_ROOT / "igar" / "settings" / filename
        assert filepath.exists(), f"Missing settings/{filename}"


def test_igar_urls_wsgi_asgi_routing_exist():
    """Verify igar/urls.py, wsgi.py, asgi.py and routing.py exist."""
    for filename in ["urls.py", "wsgi.py", "asgi.py", "routing.py"]:
        filepath = BACKEND_ROOT / "igar" / filename
        assert filepath.exists(), f"Missing igar/{filename}"


def test_pyproject_toml_exists():
    """Verify pyproject.toml exists at backend root."""
    assert (BACKEND_ROOT / "pyproject.toml").exists()


def test_requirements_igar_exist():
    """Verify requirements/igar/ directory has all required files."""
    req_files = ["base.txt", "development.txt", "test.txt", "production.txt"]
    for filename in req_files:
        filepath = BACKEND_ROOT / "requirements" / "igar" / filename
        assert filepath.exists(), f"Missing requirements/igar/{filename}"


def test_mayan_apps_not_modified():
    """Verify mayan/ directory still exists (fork preserved)."""
    assert (BACKEND_ROOT / "mayan" / "apps").is_dir()


def test_manage_py_uses_igar_settings():
    """Verify manage.py uses igar.settings.development."""
    manage_content = (BACKEND_ROOT / "manage.py").read_text()
    assert "igar.settings.development" in manage_content
