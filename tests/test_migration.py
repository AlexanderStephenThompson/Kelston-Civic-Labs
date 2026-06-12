"""The versioning thesis, as a test: a legacy corpus walks through its
migration and lands exactly on the current records, fully valid."""

from kelston import paths
from kelston.ksl.loader import load_catalog, load_yaml
from kelston.ksl.validator import Store, read_jsonl, validate_instance
from kelston.registry.diff import diff_schema
from kelston.registry.migrate import load_migrations, upgrade_instance

CATALOG = load_catalog()
PLOT_SCHEMA = "kelston.agriculture.growing_plot"


def test_diff_classifies_growing_plot_change_as_major():
    old = load_yaml(paths.ARCHIVE_DIR / PLOT_SCHEMA / "1.2.0.yaml")
    new = CATALOG.schemas[PLOT_SCHEMA].raw
    level, changes = diff_schema(old, new)
    assert level == "major"
    assert any("keeper" in change for change in changes)


def test_legacy_plots_roundtrip_to_current_records():
    legacy_path = paths.LEGACY_FIXTURES_DIR / "growing_plot@1.2.0.jsonl"
    current_path = paths.FIXTURES_DIR / "growing_plot.jsonl"
    if not legacy_path.exists():
        import pytest

        pytest.skip("fixtures not generated yet - run `kelston generate`")
    migrations = load_migrations(PLOT_SCHEMA)
    assert migrations, "growing_plot 2.0.0 migration must exist"

    current_by_id = {row["id"]: row for row in read_jsonl(current_path)}
    store = Store.from_fixture_dir(paths.FIXTURES_DIR)
    for legacy in read_jsonl(legacy_path):
        upgraded, applied = upgrade_instance(legacy, migrations)
        assert applied == ["2.0.0"]
        assert upgraded == current_by_id[upgraded["id"]]
        assert validate_instance(upgraded, CATALOG, store) == []
