"""Canonical locations of the repository's data trees.

Everything resolves relative to the repo root so the CLI works from any
working directory inside the project.
"""

from __future__ import annotations

from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Walk upward until we find the schemas/ directory that marks the root."""
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "schemas").is_dir() and (candidate / "kelston").is_dir():
            return candidate
    # Fall back to the package's parent (installed-editable layout).
    return Path(__file__).resolve().parent.parent


ROOT = repo_root()
SCHEMAS_DIR = ROOT / "schemas"
META_SCHEMA = SCHEMAS_DIR / "_meta" / "ksl.schema.yaml"
CORE_DIR = SCHEMAS_DIR / "core"
VOCAB_DIR = SCHEMAS_DIR / "vocabularies"
SECTORS_DIR = SCHEMAS_DIR / "sectors"
REGISTRY_DIR = ROOT / "registry"
MANIFEST = REGISTRY_DIR / "manifest.yaml"
ARCHIVE_DIR = REGISTRY_DIR / "archive"
MIGRATIONS_DIR = REGISTRY_DIR / "migrations"
CHANGELOG_DIR = REGISTRY_DIR / "changelog"
WORLD_DIR = ROOT / "world"
DATA_DIR = ROOT / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"
LEGACY_FIXTURES_DIR = FIXTURES_DIR / "legacy"
DB_PATH = DATA_DIR / "kelston.db"
REPORTS_DIR = DATA_DIR / "reports"
