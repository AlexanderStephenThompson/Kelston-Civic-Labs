"""Write the generated town to disk: JSONL fixtures (committed, diffable),
a legacy snapshot for the upgrade demo, and the SQLite database."""

from __future__ import annotations

import shutil

from kelston import paths
from kelston.db.schema_to_sql import build_database
from kelston.generate.context import GenContext
from kelston.ksl.validator import write_jsonl

LEGACY_PLOT_VERSION = "1.2.0"


def emit_fixtures(ctx: GenContext) -> None:
    if paths.FIXTURES_DIR.exists():
        shutil.rmtree(paths.FIXTURES_DIR)
    for schema_name in sorted(ctx.instances):
        short = schema_name.rsplit(".", 1)[-1]
        write_jsonl(paths.FIXTURES_DIR / f"{short}.jsonl", ctx.instances[schema_name])
    _emit_legacy_plots(ctx)


def _emit_legacy_plots(ctx: GenContext) -> None:
    """Snapshot the growing plots as they would have been recorded under the
    1.x standard - the demo corpus for `kelston upgrade`.

    The legacy standard used `keeper` instead of `steward`, had no
    drainage_class, and folded drainage into combined soil codes
    (loam_wet / loam_dry / clay_heavy)."""
    legacy = []
    for plot in ctx.instances["kelston.agriculture.growing_plot"]:
        old = dict(plot)
        old["conforms_to"] = f"kelston.agriculture.growing_plot@{LEGACY_PLOT_VERSION}"
        if "steward" in old:
            old["keeper"] = old.pop("steward")
        drainage = old.pop("drainage_class", "moderate")
        if old["soil_class"] == "loam" and drainage == "water_holding":
            old["soil_class"] = "loam_wet"
        elif old["soil_class"] == "loam" and drainage == "free_draining":
            old["soil_class"] = "loam_dry"
        elif old["soil_class"] == "clay":
            old["soil_class"] = "clay_heavy"
        legacy.append(old)
    write_jsonl(
        paths.LEGACY_FIXTURES_DIR / f"growing_plot@{LEGACY_PLOT_VERSION}.jsonl", legacy
    )


def emit_database(ctx: GenContext) -> None:
    build_database(ctx.instances, ctx.catalog, paths.DB_PATH)
