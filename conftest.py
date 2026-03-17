"""Root pytest configuration for Igar."""

import os

# Ensure Django settings are configured before any test collection
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "igar.settings.test")

# Ensure cairo library is found on macOS
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib")
