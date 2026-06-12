"""The kelston command line: validate, generate, registry, upgrade, query."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import click
import yaml

from kelston import paths
from kelston.ksl.loader import load_catalog, load_yaml
from kelston.ksl.metaschema import check_catalog
from kelston.ksl.validator import Store, validate_store
from kelston.registry import diff as diff_mod
from kelston.registry import manifest as manifest_mod
from kelston.registry.upgrade import run_upgrade


@click.group()
def main() -> None:
    """Kelston Civic Labs - idealized civic data systems."""


@main.command()
@click.option("--all", "check_all", is_flag=True, help="Include the determinism check.")
def validate(check_all: bool) -> None:
    """Validate the standards, the registry, and every instance in town."""
    catalog = load_catalog()
    failed = False

    meta_errors = check_catalog(catalog)
    failed |= _report("meta (schemas conform to KSL)", meta_errors)

    if paths.MANIFEST.exists():
        registry_errors = manifest_mod.verify_manifest(
            manifest_mod.load_manifest(), catalog
        )
    else:
        registry_errors = ["registry/manifest.yaml is missing - run `kelston registry init`"]
    failed |= _report("registry (manifest agrees with files)", registry_errors)

    if paths.FIXTURES_DIR.exists():
        store = Store.from_fixture_dir(paths.FIXTURES_DIR)
        instance_errors = validate_store(store, catalog)
        label = f"instances ({len(store.by_id)} records conform to their stamps)"
    else:
        instance_errors = ["data/fixtures/ is missing - run `kelston generate`"]
        label = "instances"
    failed |= _report(label, instance_errors)

    if check_all:
        failed |= _report("determinism (seed regenerates fixtures exactly)", _determinism())

    sys.exit(1 if failed else 0)


def _report(layer: str, errors: list[str]) -> bool:
    status = "FAIL" if errors else "ok"
    click.echo(f"[{status:>4}] {layer}")
    for error in errors[:40]:
        click.echo(f"       - {error}")
    if len(errors) > 40:
        click.echo(f"       ... and {len(errors) - 40} more")
    return bool(errors)


def _determinism() -> list[str]:
    from kelston.generate.pipeline import generate

    meta = _generation_meta()
    ctx = generate(seed=meta["seed"], population_size=meta["population"])
    errors = []
    for schema_name, instances in sorted(ctx.instances.items()):
        short = schema_name.rsplit(".", 1)[-1]
        path = paths.FIXTURES_DIR / f"{short}.jsonl"
        expected = "".join(
            json.dumps(i, sort_keys=True, default=str) + "\n" for i in instances
        )
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            errors.append(f"{short}.jsonl differs from a fresh seed-{meta['seed']} run")
    return errors


def _generation_meta() -> dict:
    meta_path = paths.FIXTURES_DIR / "generation.yaml"
    if meta_path.exists():
        return load_yaml(meta_path)
    return {"seed": 42, "population": 5000}


@main.command()
@click.option("--seed", default=42, show_default=True)
@click.option("--population", default=5000, show_default=True)
def generate(seed: int, population: int) -> None:
    """Generate the synthetic town: fixtures and the SQLite database."""
    from kelston.generate.pipeline import generate_and_emit

    ctx = generate_and_emit(seed=seed, population_size=population)
    meta_path = paths.FIXTURES_DIR / "generation.yaml"
    meta_path.write_text(
        yaml.safe_dump({"seed": seed, "population": population}), encoding="utf-8"
    )
    total = sum(len(rows) for rows in ctx.instances.values())
    click.echo(f"Generated {total} instances across {len(ctx.instances)} standards.")
    for schema_name in sorted(ctx.instances):
        click.echo(f"  {schema_name}: {len(ctx.instances[schema_name])}")
    click.echo(f"Database: {paths.DB_PATH}")


@main.command("build-site")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: site/).",
)
def build_site(output) -> None:
    """Render the static civic portal from the catalog, registry, and fixtures."""
    from kelston.site.build import build_site as run_build

    count = run_build(output)
    click.echo(f"Built {count} pages into {output or paths.SITE_DIR}")


@main.group()
def registry() -> None:
    """Inspect and maintain the standards registry."""


@registry.command()
@click.option("--force", is_flag=True, help="Overwrite an existing manifest.")
@click.option("--as-of", default=None, help="Date to record for initial history entries.")
def init(force: bool, as_of: str | None) -> None:
    """Build a fresh manifest from the schema files."""
    if paths.MANIFEST.exists() and not force:
        raise click.ClickException("manifest exists; use --force to rebuild")
    catalog = load_catalog()
    manifest_mod.save_manifest(manifest_mod.build_manifest(catalog, as_of=as_of))
    click.echo(f"Wrote {paths.MANIFEST}")


@registry.command()
def status() -> None:
    """Verify that the manifest and the schema files agree."""
    catalog = load_catalog()
    if not paths.MANIFEST.exists():
        raise click.ClickException("registry/manifest.yaml is missing")
    errors = manifest_mod.verify_manifest(manifest_mod.load_manifest(), catalog)
    if errors:
        for error in errors:
            click.echo(f"- {error}")
        sys.exit(1)
    manifest = manifest_mod.load_manifest()
    click.echo(
        f"Registry clean: {len(manifest['schemas'])} schemas, "
        f"{len(manifest['vocabularies'])} vocabularies."
    )


@registry.command()
@click.argument("name")
def diff(name: str) -> None:
    """Diff the newest archived version of a standard against the current file."""
    catalog = load_catalog()
    archive_dir = paths.ARCHIVE_DIR / name
    archives = sorted(archive_dir.glob("*.yaml")) if archive_dir.is_dir() else []
    if not archives:
        raise click.ClickException(f"no archived versions of {name}")
    old = load_yaml(archives[-1])
    if name in catalog.schemas:
        new = catalog.schemas[name].raw
        level, changes = diff_mod.diff_schema(old, new)
        old_version, new_version = old.get("version"), catalog.schemas[name].version
    elif name in catalog.vocabularies:
        new = load_yaml(catalog.vocabularies[name].path)
        level, changes = diff_mod.diff_vocabulary(old, new)
        old_version, new_version = old.get("version"), catalog.vocabularies[name].version
    else:
        raise click.ClickException(f"unknown standard {name}")
    click.echo(f"{name}: {old_version} -> {new_version}  [{level.upper()}]")
    for change in changes:
        click.echo(f"  - {change}")
    paths.CHANGELOG_DIR.mkdir(parents=True, exist_ok=True)
    changelog = paths.CHANGELOG_DIR / f"{name}.md"
    changelog.write_text(
        f"# {name}\n\n## {old_version} -> {new_version} ({level})\n\n"
        + "".join(f"- {c}\n" for c in changes),
        encoding="utf-8",
    )
    click.echo(f"Changelog: {changelog}")


@registry.command()
@click.argument("name")
@click.argument("level", type=click.Choice(["patch", "minor", "major"]))
@click.option("--as-of", default=None, help="Date to record in history.")
def bump(name: str, level: str, as_of: str | None) -> None:
    """Record an already-edited standard's new version in the manifest."""
    catalog = load_catalog()
    manifest = manifest_mod.load_manifest()
    manifest_mod.record_bump(manifest, name, catalog, level, as_of=as_of)
    manifest_mod.save_manifest(manifest)
    click.echo(f"Recorded {name} at its current file version ({level} change).")


@main.command()
@click.option("--in-place", is_flag=True, help="Rewrite the legacy files themselves.")
def upgrade(in_place: bool) -> None:
    """Bring legacy-stamped instances up to the current standards."""
    catalog = load_catalog()
    summary = run_upgrade(catalog, in_place=in_place)
    click.echo(
        f"Scanned {summary['scanned']} legacy instances: "
        f"{summary['upgraded']} upgraded, {summary['already_current']} already current, "
        f"{len(summary['failures'])} failures."
    )
    for failure in summary["failures"][:10]:
        click.echo(f"  - {failure}")
    sys.exit(1 if summary["failures"] else 0)


@main.command()
@click.argument("sql")
def query(sql: str) -> None:
    """Run a read-only SQL query against data/kelston.db."""
    if not paths.DB_PATH.exists():
        raise click.ClickException("data/kelston.db is missing - run `kelston generate`")
    connection = sqlite3.connect(f"file:{paths.DB_PATH}?mode=ro", uri=True)
    try:
        cursor = connection.execute(sql)
        if cursor.description:
            click.echo("\t".join(col[0] for col in cursor.description))
        for row in cursor.fetchall():
            click.echo("\t".join(str(v) for v in row))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
