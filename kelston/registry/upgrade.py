"""`kelston upgrade`: walk legacy-stamped instances through their
migrations to the current standard, re-validate every one, and write an
upgrade report. The project's thesis as a command."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from kelston import paths
from kelston.ksl.loader import Catalog
from kelston.ksl.validator import Store, read_jsonl, validate_instance, write_jsonl
from kelston.registry.migrate import load_migrations, upgrade_instance


def run_upgrade(catalog: Catalog, in_place: bool = False) -> dict:
    """Upgrade every instance in data/fixtures/legacy/. Returns a summary.

    Upgraded files are written to data/upgraded/ (or back into the legacy
    directory with --in-place), and a markdown report to data/reports/.
    """
    store = Store.from_fixture_dir(paths.FIXTURES_DIR)
    summary = {
        "scanned": 0,
        "upgraded": 0,
        "already_current": 0,
        "failures": [],
        "files": [],
        "migrations_applied": set(),
    }
    output_dir = paths.LEGACY_FIXTURES_DIR if in_place else paths.DATA_DIR / "upgraded"
    for legacy_file in sorted(paths.LEGACY_FIXTURES_DIR.glob("*.jsonl")):
        instances = read_jsonl(legacy_file)
        if not instances:
            continue
        schema_name = instances[0]["conforms_to"].split("@", 1)[0]
        migrations = load_migrations(schema_name)
        current_version = catalog.schemas[schema_name].version
        upgraded_rows = []
        for instance in instances:
            summary["scanned"] += 1
            upgraded, applied = upgrade_instance(instance, migrations)
            if applied:
                summary["upgraded"] += 1
                summary["migrations_applied"].update(
                    f"{schema_name}@{version}" for version in applied
                )
            else:
                summary["already_current"] += 1
            stamped = upgraded["conforms_to"].split("@", 1)[1]
            if stamped != current_version:
                summary["failures"].append(
                    f"{upgraded['id']}: no migration path from "
                    f"{instance['conforms_to']} to {current_version}"
                )
            else:
                problems = validate_instance(upgraded, catalog, store)
                summary["failures"].extend(problems)
            upgraded_rows.append(upgraded)
        out_path = output_dir / legacy_file.name.replace(
            legacy_file.name.split("@")[1].removesuffix(".jsonl"), current_version
        )
        write_jsonl(out_path, upgraded_rows)
        summary["files"].append(str(out_path))
    _write_report(summary)
    return summary


def _write_report(summary: dict) -> Path:
    paths.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    report_path = paths.REPORTS_DIR / f"upgrade-{today}.md"
    lines = [
        f"# Upgrade report - {today}",
        "",
        f"- instances scanned: {summary['scanned']}",
        f"- upgraded: {summary['upgraded']}",
        f"- already current: {summary['already_current']}",
        f"- validation failures: {len(summary['failures'])}",
        "",
    ]
    if summary["migrations_applied"]:
        lines.append("## Migrations applied")
        lines.extend(f"- {m}" for m in sorted(summary["migrations_applied"]))
        lines.append("")
    if summary["files"]:
        lines.append("## Output")
        lines.extend(f"- {f}" for f in summary["files"])
        lines.append("")
    if summary["failures"]:
        lines.append("## Failures")
        lines.extend(f"- {f}" for f in summary["failures"][:50])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
