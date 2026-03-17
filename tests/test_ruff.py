"""Verify Ruff linting passes on Igar code."""

import shutil
import subprocess
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent

ruff_available = shutil.which("ruff") is not None


@pytest.mark.skipif(not ruff_available, reason="ruff not installed")
def test_ruff_check_passes():
    """Verify ruff check returns 0 errors on igar/ code."""
    result = subprocess.run(
        ["ruff", "check", "."],
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Ruff check failed:\n{result.stdout}\n{result.stderr}"
    )


@pytest.mark.skipif(not ruff_available, reason="ruff not installed")
def test_ruff_format_check_passes():
    """Verify ruff format --check returns no reformatting needed."""
    result = subprocess.run(
        ["ruff", "format", "--check", "."],
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"
    )
