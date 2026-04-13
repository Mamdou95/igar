import ctypes
import os


def _prepend_env_path(var_name: str, path: str) -> None:
    """Prefixe un chemin dans une variable de type PATH sans doublon."""
    current = os.environ.get(var_name, "")
    items = [item for item in current.split(os.pathsep) if item]

    if path in items:
        return

    os.environ[var_name] = os.pathsep.join([path, *items]) if items else path


def _configure_macos_cairo() -> None:
    """Force la resolution libcairo via DYLD_FALLBACK_LIBRARY_PATH pour les tests."""
    if os.name != "posix":
        return

    for candidate_dir in ("/opt/homebrew/lib", "/usr/local/lib"):
        if os.path.isdir(candidate_dir):
            _prepend_env_path("DYLD_FALLBACK_LIBRARY_PATH", candidate_dir)

    for candidate_path in (
        "/opt/homebrew/lib/libcairo.2.dylib",
        "/usr/local/lib/libcairo.2.dylib",
    ):
        if os.path.exists(candidate_path):
            ctypes.cdll.LoadLibrary(candidate_path)
            break

# 1. Configurer Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "igar.settings.test")

# 2. Correctif macOS obligatoire pour les tests (export DYLD_FALLBACK_LIBRARY_PATH)
# Ce bloc doit s'exécuter AVANT tout import de cairocffi ou weasyprint.
try:
    _configure_macos_cairo()
except Exception:
    pass
