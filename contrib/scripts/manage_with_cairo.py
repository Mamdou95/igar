#!/usr/bin/env python3
"""Run Django management commands with a macOS Cairo preload."""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path


def _prepend_env_path(var_name: str, path_value: str) -> None:
    current = os.environ.get(var_name, "")
    parts = [part for part in current.split(":") if part]
    if path_value not in parts:
        parts.insert(0, path_value)
    os.environ[var_name] = ":".join(parts)


def _preload_cairo_on_macos() -> None:
    candidate_dirs = ("/opt/homebrew/lib", "/usr/local/lib")
    candidate_libs = (
        "/opt/homebrew/lib/libcairo.2.dylib",
        "/usr/local/lib/libcairo.2.dylib",
    )

    for candidate_dir in candidate_dirs:
        if os.path.isdir(candidate_dir):
            _prepend_env_path("DYLD_FALLBACK_LIBRARY_PATH", candidate_dir)
            _prepend_env_path("DYLD_LIBRARY_PATH", candidate_dir)

    for candidate_lib in candidate_libs:
        if os.path.exists(candidate_lib):
            ctypes.CDLL(candidate_lib)
            break


def main() -> int:
    backend_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(backend_root))

    _preload_cairo_on_macos()

    from django.core.management import execute_from_command_line

    argv = ["manage.py", *sys.argv[1:]]
    execute_from_command_line(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
